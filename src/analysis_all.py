import cPickle
import numpy as np
from config import config_list
import os
import sys


########################################################
################### PARAMS #############################
########################################################
d = "2016-04-06_17-47-28-ICCM-xp1"
trials = range(1,11)
########################################################
########################################################
########################################################





if os.environ.has_key("AVAKAS") and os.environ["AVAKAS"]:
    pref = ""
else:
    pref = "/home/sforesti/avakas"
    
log_dir = pref + '/scratch/sforestier001/logs/' + d + '/'





n_logs = 1



for trial in trials: 
    print trial

    for config_name in config_list["xp1"]:
    
        print config_name
    

        with open(log_dir + config_name + "/results_niter_2-{}.pickle".format(trial), 'r') as f:
            results_niter_2 = cPickle.load(f)
            f.close()
        
        with open(log_dir + config_name + "/results_niter_3-{}.pickle".format(trial), 'r') as f:
            results_niter_3 = cPickle.load(f)
            f.close()
        
        with open(log_dir + config_name + "/results_strategies_2-{}.pickle".format(trial), 'r') as f:
            results_strategies_2 = cPickle.load(f)
            f.close()
        
        with open(log_dir + config_name + "/results_strategies_3-{}.pickle".format(trial), 'r') as f:
            results_strategies_3 = cPickle.load(f)
            f.close()
        
                 
        print "results_niter_2", results_niter_2
        print "results_niter_3", results_niter_3
        print "results_strategies_2", results_strategies_2
        print "results_strategies_3", results_strategies_3
    
    