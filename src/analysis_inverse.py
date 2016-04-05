import cPickle
import numpy as np
import sys

from experiment import ToolsExperiment
from explauto.experiment.log import ExperimentLog
from config import configs
from explauto.utils import rand_bounds


def main(log_dir, config_name, trial):
# log_dir = "/home/sforesti/scm/Flowers/ICCM2016/src/test_1T/"
# config_log_name = "H-P-AMB-LCTC"
# config_name = "H-P-AMB"
#trial = 1
    
    config = configs[config_name]
    
    #config.env_cfg["env_conf"]["gui"]= True
    
    
    log = ExperimentLog(None, None, None)
    for key in ["motor", "sensori", "im_update_mod1", "im_update_mod2", "im_update_mod3", "im_update_mod4"]:
        try:
            filename = log_dir + config_name + '/log{}-'.format(trial) + key + '-{}.pickle'.format(0)
            with open(filename, 'r') as f:
                log_key = cPickle.load(f)
            log._logs[key] = log_key
        except:
            print "File not Found:", filename
        
        
        
    xp = ToolsExperiment(config, context_mode=config.context_mode)
    xp.ag.fast_forward(log, forward_im=True)
    
    
    
    s_space = "s_o"
    print "s_space", s_space
    
    
    
    def strategy_used(s):
        obj_end_pos_y = s[1] + s[-1]
        tool1_moved = (abs(s[-6] - s[-4]) > 0.0001)
        #tool2_moved = (abs(ms[-5] - ms[-3]) > 0.0001)
        tool1_touched_obj = tool1_moved and (abs(s[-4] - obj_end_pos_y) < 0.0001)
        #tool2_touched_obj = tool2_moved and (abs(ms[-3] - obj_end_pos_y) < 0.0001)
        obj_moved = abs(s[-1]) > 0.0001
        obj_moved_with_hand = obj_moved and (not tool1_touched_obj)# and (not tool2_touched_obj)
        
        if tool1_touched_obj or (tool1_moved and not obj_moved_with_hand):
            return "tool"
        else:
            return "hand"
    
    
    
    
    
    
    problems_2 = dict(
                  A=[-0.2, 0.7],
                  B=[0., 0.7],
                  C=[0.2, 0.7],
                  )
    
    results_niter_2 = dict(
                  A=-1,
                  B=-1,
                  C=-1,
                  )
    
    results_strategies_2 = dict(
                  A=[],
                  B=[],
                  C=[],
                  )
    
    
    problems_3 = dict(
                  A=[-0.2, 1.1],
                  B=[0., 1.2],
                  C=[0.2, 1.1],
                  )
    
    results_niter_3 = dict(
                  A=-1,
                  B=-1,
                  C=-1,
                  )
    
    results_strategies_3 = dict(
                  A=[],
                  B=[],
                  C=[],
                  )
    
    n_iter_max = 40
    
    
    # Reachable contexts, no learning
    # while True:
    #     print
    #     context = hand_reachable_context()
    #     sg = list(-np.array(context))
    #     xp.env.env.env.top_env.pos = context
    #     print "context", xp.env.get_current_context()
    #     #print "ds goal", sg
    #     m = xp.ag.inverse(s_space, sg, context=xp.env.get_current_context(), explore=False)[0]
    #     sr = xp.env.update(m, reset=False)
     
    # Hreachable contexts, learning
    for p2 in problems_2.keys():
        context = problems_2[p2]
        sg = [0] + list(-np.array(context))
        xp.env.env.env.top_env.pos = context
        print "context", xp.env.get_current_context()
        #print "ds goal", sg
        for i in range(n_iter_max):
            context = xp.env.get_current_context()
            m = xp.ag.inverse(s_space, sg, context=context, babbling=True, explore=None)[0]
            print "m", m
            sr = xp.env.update(m, reset=False)
            print "s", sr
            xp.ag.perceive([sr], context=context)
            results_niter_2[p2] = i
            results_strategies_2[p2].append(strategy_used(sr))
            if abs(sr[-1]) > 0.0001:
                break
    #         error = np.linalg.norm(np.array(sr[-2:]) - np.array(context))
    #         print "error", error
    #         if error < 0.05:
    #             break
        #print "reached ms:", ms
        
        
        
    # UnHreachable contexts, learning
    for p3 in problems_3.keys():
        context = problems_3[p3]
        sg = [0] + list(-np.array(context))
        xp.env.env.env.top_env.pos = context
        print "context", xp.env.get_current_context()
        #print "ds goal", sg
        for i in range(n_iter_max):
            context = xp.env.get_current_context()
            m = xp.ag.inverse(s_space, sg, context=context, babbling=True, explore=None)[0]
            print "m", m
            sr = xp.env.update(m, reset=False)
            print "s", sr
            xp.ag.perceive([sr], context=context)
            results_niter_3[p3] = i
            results_strategies_3[p3].append(strategy_used(sr))
            if abs(sr[-1]) > 0.0001:
                break
        
    print
    print "results_2", results_niter_2, results_strategies_2
    print "results_3", results_niter_3, results_strategies_3
    
    
if __name__ == "__main__":
    
    log_dir = sys.argv[1]
    config_name = sys.argv[2]
    trial = sys.argv[3]
    main(log_dir, config_name, trial)