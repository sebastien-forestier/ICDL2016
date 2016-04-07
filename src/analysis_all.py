import cPickle
import numpy as np
from config import config_list
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.stats
import brewer2mpl
    
    
    
bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
colors = bmap.mpl_colors



########################################################
################### PARAMS #############################
########################################################
d = "2016-04-07_17-18-36-ICCM-xp1"
trials = range(1,101)
problems = ["A", "B", "C"]
ages = [10000, 20000, 30000, 40000, 50000]
########################################################
########################################################
########################################################



if os.environ.has_key("AVAKAS") and os.environ["AVAKAS"]:
    pref = ""
else:
    pref = "/home/sforesti/avakas"
    
log_dir = pref + '/scratch/sforestier001/logs/' + d + '/'
    

mode = sys.argv[1]

if mode == "retrieve":

    
    
    results = {}
    
    
    
    n_logs = 1
    
    
    
    for config_name in config_list["xp1"]:
        print config_name
        results[config_name] = {}
    
        for trial in trials: 
            print trial
            results[config_name][trial] = {}
        
    
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
            
                     
            results[config_name][trial]["results_niter_2"] = results_niter_2
            results[config_name][trial]["results_niter_3"] = results_niter_3
            results[config_name][trial]["results_strategies_2"] = results_strategies_2
            results[config_name][trial]["results_strategies_3"] = results_strategies_3
            
    
        
    with open(log_dir + 'results.pickle', 'wb') as f:
        cPickle.dump(results, f)
    
    
    
    
elif mode == "first":
    
    with open(log_dir + "results.pickle", 'r') as f:
        results = cPickle.load(f)
        f.close()
        
        
        
    print results
        
        
    # Analysis of first attempt: percentage of hand strategy on first attempt of phases 2 and 3, depending on cdt, problem, age, averaged accross trials
    first_2 = {}
    first_3 = {}
    
    for config_name in config_list["xp1"]:
        print config_name
        first_2[config_name] = {}
        first_3[config_name] = {}
    
        
        
        for age in ages:
            
            first_2[config_name][age] = {}
            first_3[config_name][age] = {}
            
            
            for problem in problems:
                
                first_2[config_name][age][problem] = 0.
                first_3[config_name][age][problem] = 0.
                
                for trial in trials: 
                    first_2[config_name][age][problem] += results[config_name][trial]["results_strategies_2"][age][problem][0] == "hand"
                    first_3[config_name][age][problem] += results[config_name][trial]["results_strategies_3"][age][problem][0] == "hand"
                
                first_2[config_name][age][problem] = first_2[config_name][age][problem] / len(trials)
                first_3[config_name][age][problem] = first_3[config_name][age][problem] / len(trials)
        
        fig2, ax2 = plt.subplots()
        fig2.canvas.set_window_title("Phase 2: " + config_name)
        for age in ages:
            ax2.plot([first_2[config_name][age][problem] for problem in problems], "o-", label=str(age))
        
        plt.title("Frequency of hand strategy as first attempt accross agents")
        plt.legend()
        plt.xlim([-0.5,2.5])
        plt.ylim([0,1])
        plt.xlabel("Problem")
        plt.ylabel("F hand")
        plt.xticks([0,1,2],problems)
        
        fig3, ax3 = plt.subplots()
        fig3.canvas.set_window_title("Phase 3: " + config_name)
        for age in ages:
            ax3.plot([first_3[config_name][age][problem] for problem in problems], "o-", label=str(age))
        
        plt.title("Frequency of hand strategy as first attempt accross agents")
        plt.legend()
        plt.xlim([-0.5,2.5])
        plt.ylim([0,1])
        plt.xlabel("Problem")
        plt.ylabel("F hand")
        plt.xticks([0,1,2],problems)
        
        
    print first_2
    print first_3
        
    plt.show(block=True)