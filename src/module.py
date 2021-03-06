import cPickle
import Queue
import numpy as np
import time

from numpy import array, hstack, random

from explauto.agent import Agent
from explauto import InterestModel
from explauto.utils import rand_bounds
from explauto.utils.config import make_configuration
from explauto.exceptions import ExplautoBootstrapError


class Module(Agent):
    def __init__(self, config, mid):
            
        self.config = config #global config
        self.mconf = config.modules[mid] # module config
        if mid[0:3] == 'mod':
            self.mid = mid
        else:
            raise ValueError('Module name must begin with mod')
        #bounds config
        #print mid, self.mconf['m'], self.mconf['s']
        self.conf = make_configuration(self.config.agent.mins[self.mconf['m']], 
                                       self.config.agent.maxs[self.mconf['m']], 
                                       self.config.agent.mins[self.mconf['s']],
                                       self.config.agent.maxs[self.mconf['s']])
        
        #print self.mconf['m'], self.mconf['s'], self.conf
        self.im_dims = self.conf.m_dims if self.mconf['babbling_name'] == 'motor' else self.conf.s_dims        
#         self.im = InterestModel.from_configuration(self.conf, 
#                                                    self.im_dims, 
#                                                    self.mconf['im_name'])
        
        self.im_mode = self.mconf["im_mode"]
        self.s = None
        self.sp = None
        self.snn = None
        self.su = None
        
        im_cls, im_kwargs = config.ims[self.mconf['im_name']]
        im_kwargs['mode'] = self.im_mode
        self.im = im_cls(self.conf, self.im_dims, **im_kwargs)
        
        sm_cls, sm_kwargs = config.sms[self.mconf['sm_name']]
        self.sm = sm_cls(self.conf, **sm_kwargs)
        #print self.mconf['s'], self.config.agent.s_dims
        #self.s_filter = [self.config.agent.s_dims.index(sd) for sd in self.mconf['s']]
        
        Agent.__init__(self, self.conf, self.sm, self.im, context_mode=self.mconf['context_mode'])
        
        if self.mconf['from_log'] is not None:
            from_log_dir = self.mconf['from_log'][0]
            with open(from_log_dir + '/{}'.format('log.pickle'), 'r') as f:
                log = cPickle.load(f)
                f.close()
                
            from_log_mod = self.mconf['from_log'][1]
            self.fast_forward_models(log, from_log_mod, self.mconf['from_log'][2])
        
        #self.controled_vars = set(self.mconf['m'])
        self.overall_interest = 0
        self.social_interest = 0
        self.top_down_interest = 0 
        self.top_down_points = Queue.Queue()
        self.own_interest = 0
        
        #init_position = self.environment.rest_position()
        
    def fast_forward_models(self, log, ms_list=None, from_log_mod=None, forward_im=False):
        if ms_list is not None:
            m_list = list(ms_list[:,self.mconf['m']])
            s_list = list(ms_list[:,self.mconf['s']])
            self.sensorimotor_model.update_batch(m_list, s_list)
        if forward_im:
            for t in log.logs['im_update' + '_' + from_log_mod]:
                #print t, self.mconf['m'], self.mconf['s']
                self.interest_model.update(*t)

    def motor_babbling(self):
        return rand_bounds(self.conf.m_bounds)[0]
        
    def goal_babbling(self):
        s = rand_bounds(self.conf.s_bounds)[0]
        m = self.sm.infer(self.conf.s_dims, self.conf.m_dims, s)
        return m
            
    def get_m(self, ms):
        """ Get sensory dimensions used by module
        """
        return array(ms[self.mconf['m']])
        
    def get_s(self, ms):
        """ Get sensory dimensions used by module
        """
        return array(ms[self.mconf['s']])
        
    def set_one_m(self, ms, m):
        """ Set motor dimensions used by module
        """
        ms = array(ms)
        ms[self.mconf['m']] = m
        
    def set_m(self, ms, m):
        """ Set motor dimensions used by module on one ms
        """
        self.set_one_m(ms, m)
        if self.mconf['operator'] == "seq":
            return [array(ms), array(ms)]
        elif self.mconf['operator'] == "par":
            return ms
        else:
            raise NotImplementedError
    
    def set_m_seq(self, ms_seq, m):
        """ Set motor dimensions used by module on a seq of ms
        """
        return map(lambda x: self.set_m(x, m), ms_seq)
    
    def set_s(self, ms, s):
        """ Set sensory dimensions used by module
        """
        ms = array(ms)
        ms[self.mconf['s']] = s
        return ms    
    
    def set_s_seq(self, ms, s):
        return map(lambda x: self.set_s(x, s), ms)        
    
    def inverse(self, s, s_dims=None, pref=''):
        s_dims = s_dims or self.conf.s_dims
        m = self.infer(s_dims, self.conf.m_dims, s, pref='')
        return self.motor_primitive(m)
        
    def choose(self, context_ms=None):
        """ Returns a point chosen by the interest model
        """
        try:
            if self.context_mode is None:
                x = self.interest_model.sample()
            else:
                x = np.hstack((context_ms, self.interest_model.sample_given_context(context_ms, range(self.context_mode["context_n_dims"]))))
        except ExplautoBootstrapError:
            x = rand_bounds(self.conf.bounds[:, self.expl_dims]).flatten()
        return x
    
    def infer(self, expl_dims, inf_dims, x, pref='', mode='sg'):
        """ Use the sensorimotor model to compute the expected value on inf_dims given that the value on expl_dims is x.

        .. note:: This corresponds to a prediction if expl_dims=self.conf.m_dims and inf_dims=self.conf.s_dims and to inverse prediction if expl_dims=self.conf.s_dims and inf_dims=self.conf.m_dims.
        """        
        try:
            if self.n_bootstrap > 0:
                self.n_bootstrap -= 1
                raise ExplautoBootstrapError
            #t0 = time.time()
            m = self.sensorimotor_model.infer(expl_dims,
                                              inf_dims,
                                              x.flatten())
            #print "time infer", time.time() - t0
            
            self.emit(pref + 'inference' + '_' + self.mid, m)
            #print "module", self.mid, "inference"
        except ExplautoBootstrapError:
            #logger.warning('Sensorimotor model not bootstrapped yet')
            m = rand_bounds(self.conf.bounds[:, inf_dims]).flatten()
        return m
            
    def produce(self, context_ms=None):
        """ Exploration (see the `Explauto introduction <about.html>`__ for more detail):

        * Choose a value x on expl_dims according to the interest model
        * Infer a value y on inf_dims from x using the :meth:`~explauto.agent.agent.Agent.infer` method
        * Extract the motor m and sensory s parts of x, y
        * generate a movement from m

        :returns: the generated movement

        .. note:: This correspond to motor babbling if expl_dims=self.conf.m_dims and inf_dims=self.conf.s_dims 
                    and to goal babbling if expl_dims=self.conf.s_dims and inf_dims=self.conf.m_dims.
        """
        if self.t < self.mconf['motor_babbling_n_iter']:
            self.m = self.motor_babbling()
            self.s = np.zeros(len(self.mconf['s']))
            #print "Motor babbling ", self.mid, self.m
        else:
            self.x = self.choose(context_ms) 
            self.y = self.infer(self.expl_dims, self.inf_dims, self.x)
            #print "mod produce self.y", self.y
            #print self.expl_dims, self.inf_dims
            #self.m, self.s = self.extract_ms(self.x, self.y)
            self.m, sg = self.extract_ms(self.x, self.y)
            self.m = self.motor_primitive(self.m)
            
            if self.im_mode == "sg":
                self.s = sg
            elif self.im_mode == "sp":
                self.s = self.sp
            elif self.im_mode == "sg_snn":
#                 if self.mid == "mod2":
#                     print "sg", sg
#                     print "snn", self.snn
#                     print "sp", self.sp
                self.s = sg - self.snn + self.sp
                self.su = sg
            else:
                raise NotImplementedError
            #self.emit('movement' + '_' + self.mid, self.m)
            #print "module", self.mid," choose x ", self.x, "infer y ", self.y, "m", self.m, "s", self.s            
        return self.m        
    
    def update_sm(self, m, s):
        #self.emit('perception' + '_' + self.mid, s)
        self.sensorimotor_model.update(m, s)   
        self.t += 1 
    
    def update_im(self, m, s):
        #print self.mid, self.s, s
        if self.t >= self.mconf['motor_babbling_n_iter']:
            if self.im_mode == "sg" or self.im_mode == "sp":
                self.interest_model.update(hstack((m, self.s)), hstack((m, s)))
                #self.emit('im_update_' + self.mid, (hstack((m, self.s)), hstack((m, s))))
            else:
                raise NotImplementedError
        
    def competence_reached(self, s):
        if self.sensorimotor_model.size() > 0:
            return self.sensorimotor_model.competence_for_context(s[:self.context_mode["context_n_dims"]])
        else:
            return - np.inf
        
    def competence_pt(self, m): return self.interest_model.competence_pt(m)
    def interest_pt(self, m): return self.sensorimotor_model.interest_pt(m)
        
    def competence(self):        
        return self.interest_model.competence()
        
    def interest(self, interest_weights=[1., 0.000, 1.]):
        self.own_interest = interest_weights[0] * self.interest_model.interest()
        #print "Own Interest ", self.mid, self.own_interest
        self.top_down_interest = interest_weights[1] * self.top_down_points.qsize() 
        self.social_interest = interest_weights[2] * 0 #Not Implemented
        
        self.overall_interest = (self.own_interest + 
                                 self.top_down_interest + 
                                 self.social_interest)
        return self.overall_interest

    def perceive(self, m, s, context=None, has_control=True):
        """ Learning (see the `Explauto introduction <about.html>`__ for more detail):

        * update the sensorimotor model with (m, s)
        * update the interest model with (x, y, m, s)
          (x, y are stored in self.ms in :meth:`~explauto.agent.agent.Agent.production`)
        """
        self.update_sm(m, s)
        if has_control:
            self.update_im(m, s)
