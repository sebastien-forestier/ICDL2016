import Queue
import numpy as np

from numpy import zeros
from explauto.utils.observer import Observable
from explauto.utils import rand_bounds, bounds_min_max, softmax_choice, prop_choice, greedy

from hierarchy import Hierarchy
from module import Module
from action import Action


class Supervisor(Observable):
    def __init__(self, config, environment, choice="prop", llb=False, explo="babbling", n_explo_points=0, choose_children_mode='competence', choose_children_local=True):
            
        Observable.__init__(self)
        
        self.config = config
        self.environment = environment
        self.choice = choice
        self.llb = llb
        self.explo = explo
        self.n_explo_points = n_explo_points
        self.choose_children_mode = choose_children_mode
        self.ccm_local = choose_children_local
        
        self.conf = self.config.agent
        self.expl_dims = self.config.agent.m_dims
        self.inf_dims = self.config.agent.s_dims

        self.t = 1
        self.modules = {}
        self.chosen_modules = {}
        self.chosen_spaces = {}
        for s_space in self.config.s_spaces:
            self.chosen_spaces[s_space] = 0
            
        self.mid_control = ''
        self.last_space_children_choices = {}
        self.credit_tool_move = {}
        self.credit_hand_move = {}
        
        self.hierarchy = Hierarchy() # Build Hierarchy
        for motor_space in self.config.m_spaces.values():
            self.hierarchy.add_motor_space(motor_space)
            
        for mid in self.config.modules.keys(): # Build modules
            self.init_module(mid)
            #[set.add(self.modules[mid].controled_vars, cvar) for cmid in self.config.modules[mid]['children'] if self.hierarchy.is_mod(cmid) for cvar in self.modules[cmid].controled_vars]             
            
        for mid in self.modules.keys():
            self.last_space_children_choices[mid] = Queue.Queue()
            self.credit_tool_move[mid] = 0
            self.credit_hand_move[mid] = 0
            
        
    def init_module(self, mid):
        self.modules[mid] = Module(self.config, mid)
        self.chosen_modules[mid] = 0
        self.hierarchy.add_module(mid)  
#         for space in self.config.modules[mid]['m_list']:
#             self.hierarchy.add_motor_space(space) 
        self.hierarchy.add_sensori_space(self.config.modules[mid]['s'])
        for space in self.config.modules[mid]['m_list']:
            self.hierarchy.add_edge_space_module(mid, space)
        self.hierarchy.add_edge_module_space(mid, self.config.modules[mid]['s'])
                
                
    def choose_interesting_space(self, mode='softmax'):
        s_spaces = self.config.s_spaces
        interests = {}
        for s_space in s_spaces.keys():
            if s_space == "s_h":
                interests[s_space] = self.modules["mod1"].interest()
            elif s_space == "s_t1":
                interests[s_space] = self.modules["mod2"].interest()
#             elif s_space == "s_t2":
#                 interests[s_space] = self.modules["mod3"].interest()
            elif s_space == "s_o":
                interests[s_space] = np.sum([self.modules[mid].interest() for mid in ["mod3", "mod4"]])
        
        self.emit('interests', [self.t, interests])
        
        if mode == 'random':
            s_space = np.random.choice(self.interests.keys())
        elif mode == 'greedy':
            eps = 0.2
            if np.random.random() < eps:
                s_space = np.random.choice(self.interests.keys())
            else:
                s_space = max(interests, key=interests.get)
        elif mode == 'softmax':
            temperature = 0.1
            w = interests.values()
            s_space = s_spaces.keys()[softmax_choice(w, temperature)]
        
        elif mode == 'prop':
            w = interests.values()
            s_space = s_spaces.keys()[prop_choice(w, eps=0.2)]
            if self.t % 200 == 1:
                print
                print 'iterations', self.t - 1
                print "competences", np.array([self.modules[mid].competence() for mid in self.modules.keys()])
                print "progresses", np.array([self.modules[mid].interest_model.current_progress for mid in self.modules.keys()])
                print "interests", np.array([self.modules[mid].interest() for mid in self.modules.keys()])
                print "sm db n points", [len(self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset) for mid in self.modules.keys()]
                print "im db n points", [len(self.modules[mid].interest_model.data_xc) for mid in self.modules.keys()]
                print self.chosen_modules
                print "made tool moved object", self.credit_tool_move
                print "made hand moved object", self.credit_hand_move
        
        self.chosen_spaces[s_space] = self.chosen_spaces[s_space] + 1
        return s_space
        
        
#     def choose_babbling_module(self, auto_create=False, progress_threshold=1e-2, mode='softmax', weight_by_level=False):
#         interests = {}
#         for mid in self.modules.keys():
#             interests[mid] = self.modules[mid].interest()
#             self.emit('interest_' + mid, [self.t, interests[mid]])
#             self.emit('competence_' + mid, [self.t, self.modules[mid].competence()])
#         max_progress = max(interests.values())
#         
# #         self.emit('babbling_module', "mod2")
# #         return "mod2"
#     
#         #print "max_progress", max_progress
#         if not auto_create or max_progress > progress_threshold:
#             if mode == 'random':
#                 mid = np.random.choice(self.modules.keys())
#             elif mode == 'greedy':
#                 eps = 0.1
#                 if np.random.random() < eps:
#                     mid = np.random.choice(self.modules.keys())
#                 else:
#                     mid = max(interests, key=interests.get)
#             elif mode == 'softmax':
#                 temperature = 0.1
#                 mids = interests.keys()
#                 w = interests.values()
#                 #print "progresses", w
#                 #print "competences", [mod.competence() for mod in self.modules.values()]
#                 if weight_by_level:
#                     levels = self.hierarchy.module_levels()
#                     for i in range(len(mids)):
#                         f = 2.0
#                         w[i] = w[i] * np.power(f, max(levels.values()) - levels[mids[i]])
#                 #print w
#                 mid = mids[softmax_choice(w, temperature)]
#             
#             elif mode == 'prop':
#                 mids = interests.keys()
#                 w = interests.values()
#                 if self.t % 200 == 1:
#     #                 print
#     #                 print "influence ", self.influence
#                     print
#                     print 'iterations', self.t - 1
#                     print "competences", np.array([self.modules[mid].competence() for mid in self.modules.keys()])
#                     if sum(w) > 0:
#                         print "interests", np.array(w)
# #                         print "interesting objects:", int(((w[3] + w[6]) / sum(w))*100), "%"
# #                         print "cumulated:", int((self.chosen_modules["mod4"] + self.chosen_modules["mod7"]) / float(sum(self.chosen_modules.values())) * 100), "%"
#                     print "sm db n points", [len(self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset) for mid in self.modules.keys()]
#                     print "im db n points", [len(self.modules[mid].interest_model.data_xc) for mid in self.modules.keys()]
#                     print self.chosen_modules
#                     #print self.babbling_module
#                 
#                 if weight_by_level:
#                     levels = self.hierarchy.module_levels()
#                     for i in range(len(mids)):
#                         f = 10.0
#                         w[i] = w[i] * np.power(f, max(levels.values()) - levels[mids[i]])
#                 #print w
#                 mid = mids[prop_choice(w, eps=0.1)]
#             
#             self.chosen_modules[mid] = self.chosen_modules[mid] + 1
#             #print self.chosen_modules
#             self.emit('babbling_module', mid)
#             return mid
#         else:
#             return self.create_module()
                        
    def fast_forward(self, log, forward_im=False):
        #ms_list = []
        for m,s in zip(log.logs['motor'], log.logs['sensori']):
            ms = np.append(m,s)
            self.update_sensorimotor_models(ms)
            #ms_list += [ms]
        for mid, mod in self.modules.iteritems():
            mod.fast_forward_models(log, ms_list=None, from_log_mod=mid, forward_im=forward_im)        
        
    def eval_mode(self): 
        self.sm_modes = {}
        for mod in self.modules.values():
            self.sm_modes[mod.mid] = mod.sensorimotor_model.mode
            mod.sensorimotor_model.mode = 'exploit'
                
    def learning_mode(self): 
        for mod in self.modules.values():
            mod.sensorimotor_model.mode = self.sm_modes[mod.mid]
                
    def check_bounds_dmp(self, m_ag):
        return bounds_min_max(m_ag, self.conf.m_mins, self.conf.m_maxs)
        
    def motor_babbling(self):
        return rand_bounds(self.conf.m_bounds)[0]
    
    def motor_primitive(self, m): return m
        
    def rest_params(self): return self.environment.rest_params()
    
    def sensory_primitive(self, s): return s    
    
    def get_eval_dims(self, s): return self.set_ms(s = s)[self.config.eval_dims]  
        
    def set_ms(self, m=None, s=None):
        ms = zeros(self.conf.ndims)
        if m is not None:
            ms[self.conf.m_dims] = m
        if s is not None:
            ms[self.conf.s_dims] = s
        return ms
    
    def set_ms_seq(self, m=None, s=None):
        ms = zeros(self.conf.ndims)
        if m is not None:
            ms[self.conf.m_dims] = m
        if s is not None:
            ms[self.conf.s_dims] = s
        return [ms]
        
    def get_m(self, ms): return ms[self.conf.m_dims]
    def get_s(self, ms): return ms[self.conf.s_dims]
                
    def update_sensorimotor_models(self, ms):
            
        #print 'ms', ms
        for mid in ["mod1", "mod2"]:
            self.modules[mid].update_sm(self.modules[mid].get_m(ms), self.modules[mid].get_s(ms))
            
        #print 'ms2', ms
        obj_end_pos_y = ms[10] + ms[-1]
        tool1_moved = (abs(ms[-6] - ms[-4]) > 0.0001)
        #tool2_moved = (abs(ms[-5] - ms[-3]) > 0.0001)
        tool1_touched_obj = tool1_moved and (abs(ms[-4] - obj_end_pos_y) < 0.0001)
        #tool2_touched_obj = tool2_moved and (abs(ms[-3] - obj_end_pos_y) < 0.0001)
        obj_moved = abs(ms[-1]) > 0.0001
        obj_moved_with_hand = obj_moved and (not tool1_touched_obj)# and (not tool2_touched_obj)
        if tool1_touched_obj:
            if not self.mid_control  == '': 
                self.credit_tool_move[self.mid_control] += 1
        if obj_moved_with_hand:
            if not self.mid_control  == '': 
                self.credit_hand_move[self.mid_control] += 1
        
        if tool1_touched_obj or (tool1_moved and not obj_moved_with_hand):
            self.modules["mod4"].update_sm(self.modules["mod4"].get_m(ms), self.modules["mod4"].get_s(ms))
            #print ms
            #print "tool1 moved"
            return "mod4"
#         elif tool2_touched_obj or (tool2_moved and not obj_moved_with_hand):
#             self.modules["mod6"].update_sm(self.modules["mod6"].get_m(ms), self.modules["mod6"].get_s(ms))
#             #print ms
#             #print "tool2 moved"
#             return "mod6"
        else:
            self.modules["mod3"].update_sm(self.modules["mod3"].get_m(ms), self.modules["mod3"].get_s(ms))
            #print "no tool moved"
            return "mod3" if obj_moved else None
              
        
    def choose_space_child(self, s_space, s, mode="competence", local="local", k=1):
        """ 
        Choose the children of space s_space among modules that have
        the good sensori spaces, maximizing competence.
        """
        try:
            possible_mids = self.hierarchy.space_children(s_space)
        except KeyError:
            print "s_space not found in hierarchy"
            return None
        if len(possible_mids) == 1:
            mid = possible_mids[0]  
            return mid 
        
        eps = 0.05
        if mode == "competence":
            if local:
#                 for mid in ["mod2", "mod5", 'mod6']:
#                     dists, idxs = self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.nn_y(s, k=1)
#                     print mid, dists, idxs, self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.get_xy(idxs[0]), y, s
                competences = [self.modules[pmid].competence_reached(s) for pmid in possible_mids]
#                 print "sm db n points", [len(self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset) for mid in self.modules.keys()]
            else:
                competences = [self.modules[pmid].competence() for pmid in possible_mids]
            #print "choose space child", competences
            if k == 1:
                mid = possible_mids[greedy(competences, eps)]
                #print "chosen mid", mid
                return mid
            else:
                mid = possible_mids[greedy(competences)]
                return [(1. - (eps/2.) if pmid == mid else eps/2.) for pmid in possible_mids]
        
        if mode == "competence_prop":
            if local:
#                 for mid in ["mod2", "mod5", 'mod6']:
#                     dists, idxs = self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.nn_y(s, k=1)
#                     print mid, dists, idxs, self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.get_xy(idxs[0]), y, s
                competences = [self.modules[pmid].competence_reached(s) for pmid in possible_mids]
                #print "choose space child", competences
#                 print "sm db n points", [len(self.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset) for mid in self.modules.keys()]
            else:
                competences = [self.modules[pmid].competence() for pmid in possible_mids]
            if k == 1:
                mid = possible_mids[prop_choice(competences, eps)]
                return mid
            else:
                rectified = 1. / np.array(competences)
                probas = rectified / np.sum(rectified)
                return ((1. - eps) * probas + eps/2.)
            
        elif mode == "interest":  
            if local=="local":
                interests = [self.modules[pmid].interest_pt(s) for pmid in possible_mids]
            else:
                interests = [self.modules[pmid].interest() for pmid in possible_mids]
            #print "choose space child", interests
            if k == 1:
                mid = possible_mids[greedy(interests, eps=eps)]
                #print "chosen mid", mid
                return mid
            else:
                mid = possible_mids[greedy(interests)]
                return [(1. - (eps/2.) if pmid == mid else eps/2.) for pmid in possible_mids]
            
        elif mode == "interest_prop":  
            if local=="local":
                interests = [self.modules[pmid].interest_pt(s) for pmid in possible_mids]
            else:
                interests = [self.modules[pmid].interest() for pmid in possible_mids]
            #print "choose space child", interests
            if k == 1:
                mid = possible_mids[prop_choice(interests, eps=eps)]
                #print "chosen mid", mid
                return mid
            else:
                return ((1. - eps) * (np.array(interests) / np.sum(interests)) + eps/2.)
            
        elif mode == "random":   
            mid = np.random.choice(possible_mids)
            self.chosen_modules[mid] = self.chosen_modules[mid] + 1
            return mid
        
    def get_mid_children(self, mid, m, mode="competence", local="local"):
        children = []
        i = 0
        for space in self.config.modules[mid]['m_list']:
            if self.hierarchy.is_motor_space(space):
                children.append(space)
            else:
                s = m[i:i + len(space)] # TO TEST
                i = i + len(space)
                children.append(self.choose_space_child(space, s, mode, local))         
        self.last_space_children_choices[mid].put(children)     
        self.emit('chidren_choice_' + mid, [self.t, children])
        #print "Choice of children of mid", mid, children 
        return children
    
    def produce_module(self, mid, babbling=True, s=None, s_dims=None, allow_explore=False, explore=None, n_explo_points=0, context_ms=None):
        mod = self.modules[mid]  
        #print "produce module ", mid, babbling, s, allow_explore, n_explo_points
        if self.explo == "all":
            mod.sensorimotor_model.mode = 'explore'
        elif self.explo == "babbling" and babbling:
            mod.sensorimotor_model.mode = 'explore'
        elif self.explo == "motor":
            expl = True
            m_list = self.hierarchy.module_children(mid)
            for m_space in m_list:
                if not m_space in self.hierarchy.motor_spaces:

                    expl = False
            if expl:
                mod.sensorimotor_model.mode = 'explore'
            else:
                mod.sensorimotor_model.mode = 'exploit'
        elif allow_explore:
            mod.sensorimotor_model.mode = 'explore'
        else:
            mod.sensorimotor_model.mode = 'exploit'
            
        if explore is not None:
            mod.sensorimotor_model.mode = 'explore' if explore else 'exploit'
            
        if babbling:
            m_deps = mod.produce(context_ms=context_ms)
            #print "Produce babbling", mid, "s =", mod.s, "m=", m_deps
        else:
            m_deps = mod.inverse(s, s_dims=s_dims)
            #print "Produce not babbling", mid, "m =", m_deps
        
        mod.sensorimotor_model.mode = 'exploit'
        
        #print m_deps
        
        lower_explore = not (hasattr(mod.sensorimotor_model, "context_was_new") and mod.sensorimotor_model.context_was_new)
        if not lower_explore:
            explore = False
        #print "produce module", mid, "lower_explore", lower_explore, "explore", explore
        
        if self.choose_children_mode == 'interest_babbling':
            if babbling:
                ccm = "interest"
            else:
                ccm = "competence"  
        else:
            ccm = self.choose_children_mode           
        
        children = self.get_mid_children(mid, m_deps, mode=ccm, local=self.ccm_local)
            
        deps_actions = []
        i = 0
        for dep in children:
            if self.hierarchy.is_module(dep):
                m_dep = m_deps[i:i+len(self.config.modules[dep]['s'])]
                i = i + len(self.config.modules[dep]['s'])
                #self.modules[dep].top_down_points.put(m_dep)
                deps_actions.append(self.produce_module(dep, babbling=False, s=m_dep, allow_explore=False, explore=explore))
            else:
                m_dep = m_deps[i:i+len(dep)]
                i = i + len(dep)
                #print "Action prim mod", mid, "m_dims", dep, "m_deps", m_dep
                deps_actions.append(Action(m_dep, m_dims=dep))
        
        #print "Action mod", mid, "operator", self.config.modules[mid]['operator'], "m_deps", m_deps, 'actions=',deps_actions
        return Action(m_deps, operator=self.config.modules[mid]['operator'], actions=deps_actions)
        
        
    def produce(self, context_ms=None):
        for mid in self.modules.keys():
            self.last_space_children_choices[mid] = Queue.Queue()
            
#         mid = self.choose_babbling_module(mode=self.choice, weight_by_level=self.llb)
#         self.mid_control = mid   
#         action = self.produce_module(mid, n_explo_points=self.n_explo_points, context_ms=context_ms)
#         self.action = action
#         #print "Action", action.n_iterations, "mid", mid
#         #self.action.print_action()
#         m_seq = action.get_m_seq(len(self.conf.m_dims))
        s_space = self.choose_interesting_space(mode=self.choice)
        #print "chosen s_space", s_space
        
        if s_space == "s_o":
            s = - np.array([0.] + context_ms)
        else:
            s = rand_bounds(np.array([self.conf.mins[self.config.s_spaces[s_space]], self.conf.maxs[self.config.s_spaces[s_space]]]))[0]
            
        #print "m_seq", m_seq
        self.m_seq = self.inverse(s_space, s, babbling=True, context=context_ms)
        #print "Produce ", self.t
        self.t = self.t + 1
        return self.m_seq
                
    
    def inverse(self, s_space, s, babbling=False, context=None, explore=None):
        if s_space == "s_o":
            s = np.array(list(context) + list(s))
        else:
            s = np.array(s)
            
        ccm = self.choose_children_mode           
        
        
        mid = self.choose_space_child(self.config.s_spaces[s_space], s, mode=ccm, local=self.ccm_local)
        self.chosen_modules[mid] = self.chosen_modules[mid] + 1
        #print "chosen mid", mid
        if babbling:
            self.mid_control = mid
            #print self.mid_control
            self.modules[mid].s = s
        else:
            self.mid_control = None
        action = self.produce_module(mid, babbling=False, s=s, explore=explore)
        self.m_seq = action.get_m_seq(len(self.conf.m_dims))
        return self.m_seq
    
    def perceive(self, s_seq_, context=None, higher_module_perceive=True):
        s_seq = self.sensory_primitive(s_seq_)
        self.ms_seq = []
        for m, s in zip(self.m_seq, s_seq):
            ms = self.set_ms(m, s)
            self.ms_seq.append(ms)
#             self.emit('agentM', m)
#             self.emit('agentS', s)
            
        last_ms = self.ms_seq[-1]
#         if abs(ms[-1]) > 0.01:
#             print self.t, "ms", last_ms
        mid = self.update_sensorimotor_models(last_ms)
        
        #print "mid_control", self.mid_control
        if self.mid_control is not None and (mid == self.mid_control or mid is None or self.mid_control in ["mod1", "mod2"]):
            self.modules[self.mid_control].update_im(self.modules[self.mid_control].get_m(last_ms), self.modules[self.mid_control].get_s(last_ms))
            #print "mid control upd"
        
    def subscribe_topics_mids(self, topics, observer):
        for topic in topics:
            for mid in self.modules.keys():
                self.subscribe(topic + '_' + mid, observer)
                
    def subscribe_topics_mods(self, topics, observer):
        for topic in topics:
            for mod in self.modules.values():
                mod.subscribe(topic + '_' + mod.mid, observer)
        