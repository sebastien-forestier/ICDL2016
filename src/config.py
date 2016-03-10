import numpy as np

from explauto.utils.config import make_configuration
from explauto.sensorimotor_model.non_parametric import NonParametric
from supervisor import Supervisor
from environment import CogSci2016Environment


class Config(object):
    def __init__(self, 
                 name=None, 
                 hierarchy_type=0, 
                 babbling_name="goal", 
                 supervisor_name="interest", 
                 supervisor_explo="motor", 
                 supervisor_n_explo_points = 0,
                 supervisor_ccm="competence", 
                 supervisor_ccl="local", 
                 tdd=False,
                 ns=False,
                 perturbation=None,
                 from_log=None,
                 iterations=None):
              
        ################################### EXPERIMENT CONFIG ###################################
    
        self.name = name or 'Experiment'
        self.init_rest_trial = False
        self.bootstrap = 100
        self.bootstrap_range_div = 1.
        self.iter = iterations or 50
        self.log_each = self.iter #must be <= iter
        self.eval_at = []
        self.n_eval = 0
        self.eval_modes = []
        
        self.gui = False
        
        self.hierarchy_type = hierarchy_type
        self.babbling_name = babbling_name
        if self.babbling_name == "goal":
            self.motor_babbling_n_iter = 0
        else:
            self.motor_babbling_n_iter = self.iter
            
        self.from_log = from_log
        
        ################################### AGENT CONFIG ###################################
        
        self.n_dyn_motors = 4
        self.n_dmps = self.n_dyn_motors
        self.dmp_use_initial = False
        self.dmp_use_goal = True
        self.n_bfs = 2
        self.n_static_motor = 0
        self.rest_position = np.zeros(self.n_dmps + self.n_static_motor)
        
        self.motor_n_dims = self.n_dyn_motors * self.n_bfs + self.n_static_motor
        if self.dmp_use_initial: 
            self.motor_n_dims = self.motor_n_dims +  self.n_dmps
        if self.dmp_use_goal:
            self.motor_n_dims = self.motor_n_dims +  self.n_dmps
             
        
        self.move_steps = 50
        self.motor_dims = range(self.motor_n_dims)
        
        if self.hierarchy_type <= 1:
            self.s_n_dims = 5 * self.n_bfs + 5
        elif self.hierarchy_type == 2:
            self.s_n_dims = 7 * self.n_bfs + 5
        else:
            raise NotImplementedError
        
        self.sensori_dims = range(self.motor_n_dims, self.motor_n_dims + self.s_n_dims)
        self.used_dims = self.motor_n_dims + self.s_n_dims
        
        self.im_name = 'miscRandom_local'
        self.choose_children_local = (supervisor_ccl == 'local')
        
        self.sms = {
            'knn1': (NonParametric, {'fwd': 'NN', 'inv': 'NN', 'sigma_explo_ratio':0.01}),
        }
          
          
        sm = 'knn1'
        im_mode = 'sg'
        self.std_range = [-1.,1.]
        
        
        m = self.motor_dims
        s = self.sensori_dims
        
        self.operators = ["par"]
        
        if self.hierarchy_type == 0:
            self.m_spaces = dict(m=m)
            self.s_spaces = dict(s=s)
            
            self.modules = dict(mod1 = dict(m = m,
                                          s = s,     
                                          m_list = [m],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                )
        elif self.hierarchy_type == 1:
            self.m_spaces = dict(m_arm=range(12))
            self.s_spaces = dict(s_h=range(self.motor_n_dims + 0, self.motor_n_dims + 9),
                                 s_t1=range(self.motor_n_dims + 9, self.motor_n_dims + 15),
                                 s_t2=range(self.motor_n_dims + 15, self.motor_n_dims + 21),
                                 s_o=range(self.motor_n_dims + 21, self.motor_n_dims + 23),
                                 s_b=range(self.motor_n_dims + 23, self.motor_n_dims + 25))

            self.modules = dict(mod1 = dict(m = self.m_spaces["m_arm"],
                                          s = self.s_spaces["s_h"],     
                                          m_list = [self.m_spaces["m_arm"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod2 = dict(m = self.s_spaces["s_h"],
                                          s = self.s_spaces["s_t1"],     
                                          m_list = [self.s_spaces["s_h"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod3 = dict(m = self.s_spaces["s_t1"],
                                          s = self.s_spaces["s_o"],     
                                          m_list = [self.s_spaces["s_t1"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod4 = dict(m = self.s_spaces["s_o"],
                                          s = self.s_spaces["s_b"],     
                                          m_list = [self.s_spaces["s_o"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod5 = dict(m = self.s_spaces["s_h"],
                                          s = self.s_spaces["s_t2"],     
                                          m_list = [self.s_spaces["s_h"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod6 = dict(m = self.s_spaces["s_t2"],
                                          s = self.s_spaces["s_o"],     
                                          m_list = [self.s_spaces["s_t2"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                )
        else:
            raise NotImplementedError
        
        
        self.supervisor_name = supervisor_name
        self.supervisor_explo = supervisor_explo
        self.supervisor_n_explo_points = supervisor_n_explo_points
        self.supervisor_ccm = supervisor_ccm
        self.supervisor_ccl = supervisor_ccl
        
        if self.supervisor_name == "random":
            self.supervisor_cls = Supervisor
            self.supervisor_config = dict(choice="random",
                                          llb=False,
                                          explo=self.supervisor_explo,
                                          n_explo_points=self.supervisor_n_explo_points,
                                          choose_children_mode=self.supervisor_ccm,
                                          choose_children_local=self.supervisor_ccl)
        elif self.supervisor_name == "interest":
            self.supervisor_cls = Supervisor
            self.supervisor_config = dict(choice="prop",
                                          llb=False,
                                          explo=self.supervisor_explo,
                                          n_explo_points=self.supervisor_n_explo_points,
                                          choose_children_mode=self.supervisor_ccm,
                                          choose_children_local=self.supervisor_ccl)
        elif self.supervisor_name == "interest_greedy":
            self.supervisor_cls = Supervisor
            self.supervisor_config = dict(choice="greedy",
                                          llb=False,
                                          explo=self.supervisor_explo,
                                          n_explo_points=self.supervisor_n_explo_points,
                                          choose_children_mode=self.supervisor_ccm,
                                          choose_children_local=self.supervisor_ccl)
        elif self.supervisor_name == "interest_bias":
            self.supervisor_cls = Supervisor
            self.supervisor_config = dict(choice="prop",
                                          llb=True,
                                          explo=self.supervisor_explo,
                                          n_explo_points=self.supervisor_n_explo_points,
                                          choose_children_mode=self.supervisor_ccm,
                                          choose_children_local=self.supervisor_ccl)
        else:
            raise NotImplementedError
        
        
        self.eval_dims = s[-4:-2]
        self.eval_explo_dims = s[-4:-2]
        
        self.eval_range = np.array([[-1.],
                                 [1.]])
        self.eval_explo_eps = 0.02
        self.eval_explo_comp_eps = 0.02
        
        
        ################################### Env CONFIG ###################################
                
        self.max_param = 500. # max DMP weight 
        self.max_params = self.max_param * np.ones((self.n_dmps * self.n_bfs,))  

        if self.dmp_use_initial: 
            self.max_params = np.append([1]*self.n_dmps, self.max_params)
        if self.dmp_use_goal:
            self.max_params = np.append(self.max_params, [1]*self.n_dmps)

        self.env_cls = CogSci2016Environment
        self.env_cfg = dict(move_steps=self.move_steps, 
                            max_params=self.max_params,
                            perturbation=perturbation,
                            gui=self.gui)
        
        self.rest_position = [0.] * self.motor_n_dims
        
        self.m_mins = [-1.] * (self.n_dyn_motors * (self.n_bfs+1))
        self.m_maxs = [1.] * (self.n_dyn_motors * (self.n_bfs+1))
        
        self.s_mins = [-1.] * (3 * (self.n_bfs+1)) + [-1.5] * (self.n_bfs+1) + [0.] * (self.n_bfs+1) + [-1.5] * (self.n_bfs+1) + [0.] * (self.n_bfs+1) + [-2., -2., 0., 0.]
        self.s_maxs = [1.] * (3 * (self.n_bfs+1)) + [1.5, 1.5] * (self.n_bfs+1) + [1.5, 1.5] * (self.n_bfs+1) + [2., 2., 10., 0.3]
        
        
        ################################### Process CONFIG ###################################
        
        self.agent = make_configuration(self.m_mins, 
                                        self.m_maxs, 
                                        self.s_mins, 
                                        self.s_maxs)
        self.tag = self.name
        self.log_dir = ''#determined later
    
     

configs = {}

#################### EXPERIMENT  ####################

iterations = 1000

config_list = {"xp1":["F-RmB",
                      "F-RGB",
                      "H-RGB-RMB",
                      "H-RGB-P-AMB",
                      "H-RGB-GR-AMB",
                      "H-RGB-P-AMB-PGITC",
                      ]}

config = Config(name="F-RmB", hierarchy_type=0, babbling_name="motor", iterations=iterations)
configs[config.name] = config

config = Config(name="F-RGB", hierarchy_type=0, iterations=iterations)
configs[config.name] = config

config = Config(name="H-RGB-P-AMB", hierarchy_type=1, supervisor_name="interest", iterations=iterations)
configs[config.name] = config

config = Config(name="H-RGB-RMB", hierarchy_type=1, supervisor_name="random", iterations=iterations)
configs[config.name] = config

config = Config(name="H-RGB-GR-AMB", hierarchy_type=1, supervisor_name="interest_greedy", iterations=iterations)
configs[config.name] = config

config = Config(name="H-RGB-P-AMB-PGITC", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="interest_prop", supervisor_ccl="global", iterations=iterations)
configs[config.name] = config
