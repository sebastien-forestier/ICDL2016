import cPickle
import numpy as np
import sys

from experiment import ToolsExperiment
from explauto.experiment.log import ExperimentLog
from config import configs
from explauto.utils import rand_bounds


def strategy_used(s):
    obj_end_pos_y = s[1] + s[-1]
    tool1_moved = (abs(s[-6] - s[-4]) > 0.0001)
    #tool2_moved = (abs(ms[-5] - ms[-3]) > 0.0001)
    tool1_touched_obj = tool1_moved and (abs(s[-4] - obj_end_pos_y) < 0.0001)
    #tool2_touched_obj = tool2_moved and (abs(ms[-3] - obj_end_pos_y) < 0.0001)
    obj_moved = abs(s[-1]) > 0.0001
    obj_moved_with_hand = obj_moved and (not tool1_touched_obj)# and (not tool2_touched_obj)
    
    if tool1_touched_obj or (tool1_moved and not obj_moved_with_hand):
        print "tool moved"
        return "tool"
    else:
        print "no tool moved"
        return "hand"
    
    
    

def main(log_dir, config_name, trial):
    
    config = configs[config_name]
    
    #config.env_cfg["env_conf"]["gui"]= True
    
    
    log = ExperimentLog(None, None, None)
    for key in ["motor", "sensori"]:
        try:
            filename = log_dir + config_name + '/log{}-'.format(trial) + key + '-{}.pickle'.format(0)
            with open(filename, 'r') as f:
                log_key = cPickle.load(f)
            log._logs[key] = log_key
        except:
            print "File not Found:", filename
        
        
        
    iterations = [1000, 2000, 5000, 10000, 20000]
    
    results_niter_2 = {}
    results_niter_3 = {}
    results_strategies_2 = {}
    results_strategies_3 = {}
    
    for iteration in iterations:
        print iteration
        
        xp = ToolsExperiment(config, context_mode=config.context_mode)
        
        log_i = ExperimentLog(None, None, None)
        log_i._logs["motor"] = log._logs["motor"][:iteration]
        log_i._logs["sensori"] = log._logs["sensori"][:iteration]
        
        xp.ag.fast_forward(log_i, forward_im=False)
        
        s_space = "s_o"
        
        
        
        
        
        
        
        
        problems_2 = dict(
                      A=[-0.2, 0.7],
                      B=[0., 0.7],
                      C=[0.2, 0.7],
                      )
        
        results_niter_2_i = dict(
                      A=-1,
                      B=-1,
                      C=-1,
                      )
        
        results_strategies_2_i = dict(
                      A=[],
                      B=[],
                      C=[],
                      )
        
        
        problems_3 = dict(
                      A=[-0.1, 1.2],
                      B=[0., 1.25],
                      C=[0.1, 1.2],
                      )
        
        results_niter_3_i = dict(
                      A=-1,
                      B=-1,
                      C=-1,
                      )
        
        results_strategies_3_i = dict(
                      A=[],
                      B=[],
                      C=[],
                      )
        
        n_iter_max = 50
        
        
        # Reachable contexts, learning
    #     while True:
    #         print
    #         context =  [0, 1.2]
    #         #context = rand_bounds(np.array([[-0.5, -0.5], [0.5, 0.5]]))[0]
    #         sg = [0] + list(-np.array(context))
    #         xp.env.env.env.top_env.pos = context
    #         print "context", xp.env.get_current_context()
    #         #print "ds goal", sg
    #         m = xp.ag.inverse(s_space, sg, context=xp.env.get_current_context(), babbling=True, explore=None)[0]
    #         sr = xp.env.update(m, reset=False)
    #         xp.ag.perceive([sr], context=context)
         
         
        print "----- Phase 2"
        # Hreachable contexts, learning
        for p2 in sorted(problems_2.keys()):
            context = problems_2[p2]
            sg = [0] + list(-np.array(context))
            xp.env.env.env.top_env.pos = context
            print "\n-------------- new context", xp.env.get_current_context()
            #print "ds goal", sg
            for i in range(n_iter_max):
                context = xp.env.get_current_context()
                m = xp.ag.inverse(s_space, sg, context=context, babbling=True, explore=None)[0]
                print "m", m
                sr = xp.env.update(m, reset=False)
                print "s", sr
                xp.ag.perceive([sr], context=context)
                results_strategies_2_i[p2].append(strategy_used(sr))
                if abs(sr[-1]) > 0.0001:
                    results_niter_2_i[p2] = i
                    break
            
            
            
        print "----- Phase 3"
        # UnHreachable contexts, learning
        for p3 in sorted(problems_3.keys()):
            context = problems_3[p3]
            sg = [0] + list(-np.array(context))
            xp.env.env.env.top_env.pos = context
            print "\n-------------- new context", xp.env.get_current_context()
            #print "ds goal", sg
            for i in range(n_iter_max):
                context = xp.env.get_current_context()
                m = xp.ag.inverse(s_space, sg, context=context, babbling=True, explore=None)[0]
                print "m", m
                sr = xp.env.update(m, reset=False)
                print "s", sr
                xp.ag.perceive([sr], context=context)
                results_strategies_3_i[p3].append(strategy_used(sr))
                if abs(sr[-1]) > 0.0001:
                    results_niter_3_i[p3] = i
                    break
            
        results_niter_2[iteration] = results_niter_2_i
        results_niter_3[iteration] = results_niter_3_i
        results_strategies_2[iteration] = results_strategies_2_i
        results_strategies_3[iteration] = results_strategies_3_i
        
    
    with open(log_dir + config_name + '/results_niter_2-{}.pickle'.format(trial), 'wb') as f:
        cPickle.dump(results_niter_2, f)
     
    with open(log_dir + config_name + '/results_niter_3-{}.pickle'.format(trial), 'wb') as f:
        cPickle.dump(results_niter_3, f)
        
    with open(log_dir + config_name + '/results_strategies_2-{}.pickle'.format(trial), 'wb') as f:
        cPickle.dump(results_strategies_2, f)
     
    with open(log_dir + config_name + '/results_strategies_3-{}.pickle'.format(trial), 'wb') as f:
        cPickle.dump(results_strategies_3, f)
     
    print "results_niter_2", results_niter_2
    print "results_niter_3", results_niter_3
    print "results_strategies_2", results_strategies_2
    print "results_strategies_3", results_strategies_3
    
if __name__ == "__main__":
    
    log_dir = sys.argv[1]
    config_name = sys.argv[2]
    trial = sys.argv[3]
    main(log_dir, config_name, trial)