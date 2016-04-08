import numpy as np

from explauto.utils.config import make_configuration
from explauto.sensorimotor_model.non_parametric import NonParametric, ContextNonParametric
from supervisor import Supervisor
from environment import ICCM2016Environment
from explauto.environment.context_environment import ContextEnvironment
from explauto.interest_model.random import MiscRandomInterest, ContextRandomInterest, competence_dist, competence_exp


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
                 im_model='miscRandom_local',
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
        
        self.n_dyn_motors = 3
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
             
        self.n_context_dims = 2
        
        self.context_mode = dict(mode='mcs',
                            reset_iterations=20,
                            context_n_dims=self.n_context_dims,
                            context_sensory_bounds=np.array([[-1.5, -1.5],[1.5, 1.5]]))

        self.move_steps = 50
        self.motor_dims = range(self.motor_n_dims)
        
        self.s_n_dims = 17
        
        self.sensori_dims = range(self.motor_n_dims, self.motor_n_dims + self.s_n_dims)
        self.used_dims = self.motor_n_dims + self.s_n_dims
        
        self.im_model = im_model
        self.im_name = self.im_model        
        
        self.ims = {'miscRandom_local': (MiscRandomInterest, {
                                  'competence_measure': competence_dist,
                                  #'competence_measure': lambda target, reached, dist_max:competence_exp(target, reached, dist_min=0.01, dist_max=dist_max, power=20.),
                                   'win_size': 1000,
                                   'competence_mode': 'knn',
                                   'k': 20,
                                   'progress_mode': 'local'}),
                    'context_miscRandom_local': (ContextRandomInterest, {
                                  #'competence_measure': lambda target, reached, dist_max:competence_exp(target, reached, dist_min=0.01, dist_max=dist_max, power=20.),
                                   'win_size': 1000,
                                   'competence_mode': 'knn',
                                   'k': 20,
                                   'progress_mode': 'local',
                                   'context_mode': self.context_mode}),
            }
        
        self.choose_children_local = (supervisor_ccl == 'local')
        
        self.sms = {
            'knn1': (NonParametric, {'fwd': 'NN', 'inv': 'NN', 'sigma_explo_ratio':0.01}),
            'context_knn': (ContextNonParametric, {'fwd': 'NN', 'inv': 'NN', 'sigma_explo_ratio':0.01,'context_mode': self.context_mode}),
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
                                          context_mode=self.context_mode,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                )
        elif self.hierarchy_type == 1:
            self.m_spaces = dict(m_arm=range(9))
            self.s_spaces = dict(s_h=range(self.motor_n_dims + self.n_context_dims + 0, self.motor_n_dims + self.n_context_dims + 6),
                                 s_t1=range(self.motor_n_dims + self.n_context_dims + 6, self.motor_n_dims + self.n_context_dims + 12),
                                 #s_t2=range(self.motor_n_dims + self.n_context_dims + 15, self.motor_n_dims + self.n_context_dims + 21),
                                 s_o=range(self.motor_n_dims, self.motor_n_dims + 2) + range(self.motor_n_dims + self.n_context_dims + 12, self.motor_n_dims + self.n_context_dims + 15))

            self.modules = dict(mod1 = dict(m = self.m_spaces["m_arm"],
                                          s = self.s_spaces["s_h"],     
                                          m_list = [self.m_spaces["m_arm"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = sm,
                                          im_name = self.im_name,
                                          im_mode = im_mode,
                                          from_log = None,
                                          context_mode=None,
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
                                          context_mode=None,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
#                                 mod3 = dict(m = self.s_spaces["s_h"],
#                                           s = self.s_spaces["s_t2"],     
#                                           m_list = [self.s_spaces["s_h"]],      
#                                           operator = "par",                            
#                                           babbling_name = "goal",
#                                           sm_name = sm,
#                                           im_name = self.im_name,
#                                           im_mode = im_mode,
#                                           from_log = None,
#                                           context_mode=None,
#                                           motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                
                                mod3 = dict(m = self.s_spaces["s_h"],
                                          s = self.s_spaces["s_o"],     
                                          m_list = [self.s_spaces["s_h"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = 'context_knn',
                                          im_name = 'context_miscRandom_local',
                                          im_mode = im_mode,
                                          from_log = None,
                                          context_mode=self.context_mode,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
                                mod4 = dict(m = self.s_spaces["s_t1"],
                                          s = self.s_spaces["s_o"],     
                                          m_list = [self.s_spaces["s_t1"]],      
                                          operator = "par",                            
                                          babbling_name = "goal",
                                          sm_name = 'context_knn',
                                          im_name = 'context_miscRandom_local',
                                          im_mode = im_mode,
                                          from_log = None,
                                          context_mode=self.context_mode,
                                          motor_babbling_n_iter=self.motor_babbling_n_iter),
                                
#                                 mod6 = dict(m = self.s_spaces["s_t2"],
#                                           s = self.s_spaces["s_o"],     
#                                           m_list = [self.s_spaces["s_t2"]],      
#                                           operator = "par",                            
#                                           babbling_name = "goal",
#                                           sm_name = 'context_knn',
#                                           im_name = 'context_miscRandom_local',
#                                           im_mode = im_mode,
#                                           from_log = None,
#                                           context_mode=self.context_mode,
#                                           motor_babbling_n_iter=self.motor_babbling_n_iter),
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
                
        self.max_param = 300. # max DMP weight 
        self.max_params = self.max_param * np.ones((self.n_dmps * self.n_bfs,))  

        if self.dmp_use_initial: 
            self.max_params = np.append([1]*self.n_dmps, self.max_params)
        if self.dmp_use_goal:
            self.max_params = np.append(self.max_params, [1]*self.n_dmps)

            


        
        iccm_conf = dict(move_steps=self.move_steps, 
                            max_params=self.max_params,
                            gui=self.gui)



        self.context_mode = dict(mode='mcs',
                            reset_iterations=10,
                            context_n_dims=2,
                            context_sensory_bounds=np.array([[-1.5, -1.5],[1.5, 1.5]]))



        self.env_cls = ContextEnvironment
        self.env_cfg = dict(env_cls=ICCM2016Environment, 
                            env_conf=iccm_conf, 
                            context_mode=self.context_mode)
        
        self.rest_position = [0.] * self.motor_n_dims
        
        self.m_mins = [-1.] * (self.n_dyn_motors * (self.n_bfs+1))
        self.m_maxs = [1.] * (self.n_dyn_motors * (self.n_bfs+1))
        
        self.s_mins = [-1.5] * (17)
        self.s_maxs = [1.5] * (17)
        
        ################################### Process CONFIG ###################################
        
        self.agent = make_configuration(self.m_mins, 
                                        self.m_maxs, 
                                        self.s_mins, 
                                        self.s_maxs)
        self.tag = self.name
        self.log_dir = ''#determined later
    
     

configs = {}

#################### EXPERIMENT  ####################

iterations = 20000

config_list = {"xp1":[#"F-RmB",
                      #"F-RGB",
                      "H-AMB-RDM",
                      "H-AMB-GC",
                      "H-AMB-MC",
                      "H-AMB-GI",
                      "H-AMB-MI",
                      ]}


config = Config(name="H-AMB-GC", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="competence", supervisor_ccl="local", iterations=iterations)
configs[config.name] = config

config = Config(name="H-AMB-MC", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="competence_prop", supervisor_ccl="local", iterations=iterations)
configs[config.name] = config

config = Config(name="H-AMB-GI", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="interest", supervisor_ccl="local", iterations=iterations)
configs[config.name] = config

config = Config(name="H-AMB-MI", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="interest_prop", supervisor_ccl="local", iterations=iterations)
configs[config.name] = config

config = Config(name="H-AMB-RDM", hierarchy_type=1, supervisor_name="interest", supervisor_ccm="random", supervisor_ccl="global", iterations=iterations)
configs[config.name] = config
