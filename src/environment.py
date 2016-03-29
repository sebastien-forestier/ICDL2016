import numpy as np
import matplotlib
import matplotlib.pyplot as plt

#matplotlib.use('QT4Agg')

from combined_env import CombinedEnvironment, HierarchicallyCombinedEnvironment
from dynamic_env import DynamicEnvironment


from explauto.utils import bounds_min_max
from explauto.environment.environment import Environment
from explauto.environment.simple_arm.simple_arm import joint_positions
from explauto.utils.utils import rand_bounds

import brewer2mpl
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors
 
colors_config = {
                 "stick":colors[3],
                 "gripper":colors[1],
                 "magnetic":colors[2],
                 "scratch":colors[4],
                 }

class GripArmEnvironment(Environment):
    use_process = True

    def __init__(self, m_mins, m_maxs, s_mins, s_maxs,
                 lengths, angle_shift, rest_state):
        
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)

        self.lengths = lengths
        self.angle_shift = angle_shift
        self.rest_state = rest_state
        self.reset()
        
    def reset(self):
        #print "reset gripper"
        self.gripper = self.rest_state[3]
        self.logs = []
        
    def compute_motor_command(self, m):
        return bounds_min_max(m, self.conf.m_mins, self.conf.m_maxs)
        #return m

    def compute_sensori_effect(self, m):
        a = self.angle_shift + np.cumsum(np.array(m[:-1]))
        a_pi = np.pi * a 
        hand_pos = np.array([np.sum(np.cos(a_pi)*self.lengths), np.sum(np.sin(a_pi)*self.lengths)])
        if m[-1] >= 0.:
            new_gripper = 1. 
        else:
            new_gripper = -1.
        gripper_change = (self.gripper - new_gripper) / 2.
        self.gripper = new_gripper
        angle = np.mod(a[-1] + 1, 2) - 1
        self.logs.append(m)
        return [hand_pos[0], hand_pos[1], angle, gripper_change, self.gripper]
    
    
    def plot(self, ax, i, **kwargs_plot):
        m = self.logs[i]
        angles = m[:-1]
        angles[0] += self.angle_shift
        x, y = joint_positions(angles, self.lengths, 'std')
        x, y = [np.hstack((0., a)) for a in x, y]
        ax.plot(x, y, 'grey', lw=4, **kwargs_plot)
        ax.plot(x[0], y[0], 'ok', ms=12, **kwargs_plot)
        for i in range(len(self.lengths)-1):
            ax.plot(x[i+1], y[i+1], 'ok', ms=12, **kwargs_plot)
        ax.plot(x[-1], y[-1], 'or', ms=4, **kwargs_plot)
        #ax.axis([-1.6, 2.1, -1., 2.1])        

#         ax.set_xlabel('X')
#         ax.set_ylabel('Y')
        self.plot_gripper(ax, x[-1], y[-1], np.cumsum(m[:-1]), m[-1] >= 0., **kwargs_plot)
        
    def plot_gripper(self, ax, x, y, angle, gripper_open, **kwargs_plot):
        if gripper_open:
            if kwargs_plot.has_key("alpha"):
                color=matplotlib.colors.ColorConverter().to_rgba('b', alpha=kwargs_plot["alpha"])
            else:
                color = colors_config['gripper']
            ax.plot(x, y, 'o', markerfacecolor='none', markeredgewidth=6, markeredgecolor=color, ms=26, **kwargs_plot)
                
        else:
            color = colors_config['gripper']
            ax.plot(x, y, 'o', color=color, ms=18, **kwargs_plot)
        
       
class Stick(Environment):
    def __init__(self, m_mins, m_maxs, s_mins, s_maxs,
                 length, type, handle_tol, handle_noise, rest_state):
        
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)

        self.length = length
        self.type = type
        self.handle_tol = handle_tol
        self.handle_tol_sq = handle_tol * handle_tol
        self.handle_noise = handle_noise
        self.rest_state = rest_state
        
        self.reset()


    def reset(self):
        #print "reset Stick"
        self.held = False
        self.handle_pos = np.array(self.rest_state[0:2])
        self.angle = self.rest_state[2]
        self.compute_end_pos()
        self.logs = []
        
    def compute_end_pos(self):
        a = np.pi * self.angle
        self.end_pos = [self.handle_pos[0] + np.cos(a) * self.length, 
                        self.handle_pos[1] + np.sin(a) * self.length]
                
    def compute_motor_command(self, m):
        #return bounds_min_max(m, self.conf.m_mins, self.conf.m_maxs)
        return m

    def compute_sensori_effect(self, m):
        hand_pos = m[0:2]
        hand_angle = m[2]
        gripper_change = m[3]
        
        if not self.held:
            if gripper_change == 1. and (hand_pos[0] - self.handle_pos[0]) ** 2. + (hand_pos[1] - self.handle_pos[1]) ** 2. < self.handle_tol_sq:
                self.handle_pos = hand_pos
                self.angle = np.mod(hand_angle + self.handle_noise * np.random.randn() + 1, 2) - 1
                self.compute_end_pos()
                self.held = True
        else:
            if gripper_change == 0:
                self.handle_pos = hand_pos
                self.angle = np.mod(hand_angle + self.handle_noise * np.random.randn() + 1, 2) - 1
                self.compute_end_pos()
            else:
                self.held = False
        
        #print "Stick log added"
        self.logs.append([self.handle_pos, 
                          self.angle, 
                          self.end_pos, 
                          self.held])
        #print "Tool hand_pos:", hand_pos, "hand_angle:", hand_angle, "gripper_change:", gripper_change, "self.handle_pos:", self.handle_pos, "self.angle:", self.angle, "self.held:", self.held 
        return list(self.end_pos) # Tool pos
    
    def plot(self, ax, i, **kwargs_plot):
        handle_pos = self.logs[i][0]
        end_pos = self.logs[i][2]
        
        
        ax.plot([handle_pos[0], end_pos[0]], [handle_pos[1], end_pos[1]], '-', color=colors_config['stick'], lw=6, **kwargs_plot)
        ax.plot(handle_pos[0], handle_pos[1], 'o', color = colors_config['gripper'], ms=12, **kwargs_plot)
        if self.type == "magnetic":
            ax.plot(end_pos[0], end_pos[1], 'o', color = colors_config['magnetic'], ms=12, **kwargs_plot)
        else:
            ax.plot(end_pos[0], end_pos[1], 'o', color = colors_config['scratch'], ms=12, **kwargs_plot)
                    
    

class Object(Environment):
    def __init__(self, m_mins, m_maxs, s_mins, s_maxs,
                 object_tol, bounds):
        
        Environment.__init__(self, m_mins, m_maxs, s_mins, s_maxs)

        self.object_tol_sq = object_tol * object_tol
        self.bounds = bounds
        self.reset()
        
        
    def reset(self):
        #print "reset object"
        self.move = 0
        self.pos = rand_bounds(self.bounds)[0]
        self.logs = []
        
    def compute_motor_command(self, m):
        #return bounds_min_max(m, self.conf.m_mins, self.conf.m_maxs)
        return m

    def compute_sensori_effect(self, m):
        gripper_change = m[2]
        if (gripper_change == 0 and self.move == 1) or (gripper_change == 1 and (m[0] - self.pos[0]) ** 2 + (m[1] - self.pos[1]) ** 2 < self.object_tol_sq):
            self.pos = m[0:2]
            self.move = 1
        if gripper_change == -1:
            self.move = 0
            #print "object moved by hand"
        if self.move == 2 or (self.move == 0 and (m[3] - self.pos[0]) ** 2 + (m[4] - self.pos[1]) ** 2 < self.object_tol_sq):
            self.pos = m[3:5]
            self.move = 2
            #print "object moved by tool1"
        if self.move == 3 or (self.move == 0 and (m[5] - self.pos[0]) ** 2 + (m[6] - self.pos[1]) ** 2 < self.object_tol_sq):
            self.pos = m[5:7]
            self.move = 3
            #print "object moved by tool2"
        self.logs.append([self.pos,
                          self.move])
        return list(self.pos)
    
    def plot(self, ax, i, **kwargs_plot):
        self.logs = self.logs[-50:]
        pos = self.logs[i][0]        
        rectangle = plt.Rectangle((pos[0] - 0.05, pos[1] - 0.05), 0.1, 0.1, **kwargs_plot)
        ax.add_patch(rectangle) 



class ICCM2016Environment(DynamicEnvironment):
    def __init__(self, move_steps=50, max_params=None, noise=0, gui=False):

            
        gripArm_cfg = dict(m_mins=[-1, -1, -1, -1],  # joints pos + gripper state
                             m_maxs=[1, 1, 1, 1], 
                             s_mins=[-1, -1, -1, -1, -1], # hand pos + hand angle + gripper_change + gripper state
                             s_maxs=[1, 1, 1, 1, 1], 
                             lengths=[0.5, 0.3, 0.2], 
                             angle_shift=0.5,
                             rest_state=[0., 0., 0., 0.])
        
        
        stick1_cfg = dict(m_mins=[-1, -1, -1, -1, -1], 
                         m_maxs=[1, 1, 1, 1, 1], 
                         s_mins=[-2, -2],  # Tool pos
                         s_maxs=[2, 2],
                         length=0.3, 
                         type="1",
                         handle_tol=0.2, 
                         handle_noise=0.1 if noise == 1 else 0., 
                         rest_state=[-0.75, 0.25, 0.75])
        
        stick2_cfg = dict(m_mins=[-1, -1, -1, -1, -1], 
                         m_maxs=[1, 1, 1, 1, 1], 
                         s_mins=[-2, -2], 
                         s_maxs=[2, 2],
                         length=0.2, 
                         type="2",
                         handle_tol=0.2, 
                         handle_noise=0.1 if noise == 1 else 0., 
                         rest_state=[0.75, 0.25, 0.25])
        
        sticks_cfg = dict(
                        s_mins = [-2, -2, -2, -2],
                        s_maxs = [2, 2, 2, 2],
                        envs_cls = [Stick, Stick],
                        envs_cfg = [stick1_cfg, stick2_cfg],
                        combined_s = lambda s:s  # from s:  Tool1 end pos + Tool2 end pos
                        )
        
        arm_stick_cfg = dict(m_mins=list([-1.] * 4), # 3DOF + gripper
                             m_maxs=list([1.] * 4),
                             s_mins=list([-2.] * 8),
                             s_maxs=list([2.] * 8),
                             top_env_cls=CombinedEnvironment, 
                             lower_env_cls=GripArmEnvironment, 
                             top_env_cfg=sticks_cfg, 
                             lower_env_cfg=gripArm_cfg, 
                             fun_m_lower= lambda m:m,
                             fun_s_lower=lambda m,s:s+s,  # (hand pos + hand angle + gripper_change + gripper state) * 2 tools
                             fun_s_top=lambda m,s_lower,s:s_lower[0:2] + s_lower[3:5] + s) # from s: Tool1 end pos + Tool2 end pos  from m: hand_pos + gripper_change + gripper state
        
        
        
        object_cfg = dict(m_mins = list([-1.] * 7), 
                          m_maxs = list([1.] * 7), 
                          s_mins = [-2., -2.], # new pos
                          s_maxs = [2., 2.],
                          object_tol = 0.1, 
                          bounds = np.array([[-0.5, -0.5],
                                                 [0.5, 0.5]]))
        
        
        def sensory_noise(s):
            return np.random.random(len(s)) * 0.1 + np.array(s)
        
        
        arm_sticks_object_cfg = dict(
                                   m_mins=arm_stick_cfg['m_mins'],
                                   m_maxs=arm_stick_cfg['m_maxs'],
                                   s_mins=list([-2.] * 9),
                                   s_maxs=list([2.] * 9), # (hand pos + gripper state + tool1 end pos + tool2 end pos + last objects pos
                                   top_env_cls=Object, 
                                   lower_env_cls=HierarchicallyCombinedEnvironment, 
                                   top_env_cfg=object_cfg, 
                                   lower_env_cfg=arm_stick_cfg, 
                                   fun_m_lower= lambda m:m,
                                   fun_s_lower=lambda m,s:s[:3] + s[4:],
                                   fun_s_top=lambda m,s_lower,s: sensory_noise(s_lower[:2] + s_lower[3:] + s) if noise == 2 else s_lower[:2] + s_lower[3:] + s)
        
        
        denv_cfg = dict(env_cfg=arm_sticks_object_cfg,
                        env_cls=HierarchicallyCombinedEnvironment,
                        m_mins=[-1.] * 4 * 3, 
                        m_maxs=[1.] * 4 * 3, 
                        s_mins=[-1.5] * 9 * 3,
                        s_maxs=[1.5] * 9 * 3,
                        n_bfs = 2,
                        n_motor_traj_points=3, 
                        n_sensori_traj_points=3, 
                        move_steps=move_steps, 
                        n_dynamic_motor_dims=4,
                        n_dynamic_sensori_dims=9, 
                        max_params=max_params,
                        motor_traj_type="DMP", 
                        sensori_traj_type="samples",
                        optim_initial_position=False, 
                        optim_end_position=True, 
                        default_motor_initial_position=[0.]*4, 
                        default_motor_end_position=[0.]*4,
                        default_sensori_initial_position=[0., 1., 0., 0., -0.85, 0.35, 0., 0., 0.], 
                        default_sensori_end_position=[0., 1., 0., 0., -0.85, 0.35, 0., 0., 0.],
                        gui=gui)
            
        
        DynamicEnvironment.__init__(self, **denv_cfg)
        
        
    @property
    def current_context(self):
        return self.env.top_env.pos
    
    # Change object sensory space to be 2D as relative change of position ds
    def compute_sensori_effect(self, m_traj):
        c = self.current_context
        s = DynamicEnvironment.compute_sensori_effect(self, m_traj)
        s_o_end = s[[-4,-1]]
        res = list(s[:-6]) + list(np.array(s_o_end) - np.array(c))
        self.env.lower_env.reset() # reset arm and tools but not object
        self.env.top_env.move = 0 # tools have been reset so object must not follow them
        return res
    
        