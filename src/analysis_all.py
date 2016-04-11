import cPickle
import numpy as np
from config import config_list
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scipy.stats
# import brewer2mpl
#     
#     
#     
# bmap = brewer2mpl.get_map('Dark2', 'qualitative', 6)
# colors = bmap.mpl_colors



########################################################
################### PARAMS #############################
########################################################
d = "2016-04-11_15-04-42-ICDL-xp1"
trials = range(1,101)
problems = ["A", "B", "C"]
ages = [1000, 2000, 5000, 10000]
########################################################
########################################################
########################################################



if os.environ.has_key("AVAKAS") and os.environ["AVAKAS"]:
    pref = ""
else:
    pref = "/home/seb/avakas"
    
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
        
            try:
        
                with open(log_dir + config_name + "/results-{}.pickle".format(trial), 'r') as f:
                    results[config_name][trial] = cPickle.load(f)
                    f.close()
                
            except:
                print "File not found", config_name, trial
        
    with open(log_dir + 'results.pickle', 'wb') as f:
        cPickle.dump(results, f)
    
    
    
    
elif mode == "first":
    
    with open(log_dir + "results.pickle", 'r') as f:
        results = cPickle.load(f)
        f.close()
        
        
        
    #print results
        
        
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
                
                n_trials = 0
                for trial in trials: 
                    try:
                        #first_2[config_name][age][problem] += results[config_name][trial]["results_strategies_2"][age][problem][0] == "hand"
                        first_3[config_name][age][problem] += results[config_name][trial]["results_strategies_3"][age][problem][0] == "hand"
                        n_trials += 1
                    except:
                        print "data not found for ", config_name, trial 
                #first_2[config_name][age][problem] = first_2[config_name][age][problem] / n_trials if n_trials > 0 else 0.
                first_3[config_name][age][problem] = first_3[config_name][age][problem] / n_trials if n_trials > 0 else 0.
#         
#         fig2, ax2 = plt.subplots()
#         fig2.canvas.set_window_title("Phase 2: " + config_name)
#         for age in ages:
#             ax2.plot([first_2[config_name][age][problem] for problem in problems], "o-", label=str(age))
#         
#         plt.title("Frequency of hand strategy as first attempt accross agents")
#         plt.legend()
#         plt.xlim([-0.5,2.5])
#         plt.ylim([0,1])
#         plt.xlabel("Problem")
#         plt.ylabel("F hand")
#         plt.xticks([0,1,2],problems)
        
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
        
        
    #print first_2
    print first_3
        
    plt.show(block=True)
    
    
    
    
elif mode == "success":
    
    
    with open(log_dir + "results.pickle", 'r') as f:
        results = cPickle.load(f)
        f.close()
        
        
        
    #print results
        
        
    # Analysis of first attempt: percentage of hand strategy on first attempt of phases 2 and 3, depending on cdt, problem, age, averaged accross trials
    success_2 = {}
    success_3 = {}
    
    for config_name in config_list["xp1"]:
        print config_name
        success_2[config_name] = {}
        success_3[config_name] = {}
    
        
        
        for age in ages:
            
            success_2[config_name][age] = {}
            success_3[config_name][age] = {}
            
            
            for problem in problems:
                
                success_2[config_name][age][problem] = 0.
                success_3[config_name][age][problem] = 0.
                
                n_trials = 0
                for trial in trials: 
                    try:
                        #success_2[config_name][age][problem] += results[config_name][trial]["results_niter_2"][age][problem] >= 0
                        success_3[config_name][age][problem] += results[config_name][trial]["results_niter_3"][age][problem] >= 0
                        n_trials += 1
                    except:
                        print "data not found for ", config_name, trial 
                #success_2[config_name][age][problem] = success_2[config_name][age][problem] / n_trials if n_trials > 0 else 0.
                success_3[config_name][age][problem] = success_3[config_name][age][problem] / n_trials if n_trials > 0 else 0.
        
#         fig2, ax2 = plt.subplots()
#         fig2.canvas.set_window_title("Phase 2: " + config_name)
#         for age in ages:
#             ax2.plot([success_2[config_name][age][problem] for problem in problems], "o-", label=str(age))
#         
#         plt.title("Success rate to catch object, averaged accross agents")
#         plt.legend()
#         plt.xlim([-0.5,2.5])
#         plt.ylim([0,1])
#         plt.xlabel("Problem")
#         plt.ylabel("F hand")
#         plt.xticks([0,1,2],problems)
#         
        fig3, ax3 = plt.subplots()
        fig3.canvas.set_window_title("Phase 3: " + config_name)
        for age in ages:
            ax3.plot([success_3[config_name][age][problem] for problem in problems], "o-", label=str(age))
        
        plt.title("Success rate to catch object, averaged accross agents")
        plt.legend()
        plt.xlim([-0.5,2.5])
        plt.ylim([0,1])
        plt.xlabel("Problem")
        plt.ylabel("Success")
        plt.xticks([0,1,2],problems)
        
        
    print success_2
    print success_3
        
    plt.show(block=True)
    

    
    
elif mode == "all":
    
    
    with open(log_dir + "results.pickle", 'r') as f:
        results = cPickle.load(f)
        f.close()
        
        
        
    #print results
        
        
    # Analysis of first attempt: percentage of hand strategy on first attempt of phases 2 and 3, depending on cdt, problem, age, averaged accross trials
    all_2 = {}
    all_3 = {}
    
    for config_name in config_list["xp1"]:
        print config_name
        all_2[config_name] = {}
        all_3[config_name] = {}
    
        
        
        for age in ages:
            
            all_2[config_name][age] = {}
            all_3[config_name][age] = {}
            
            
            for problem in problems:
                
                all_2[config_name][age][problem] = 0.
                all_3[config_name][age][problem] = 0.
                
                n_trials = 0
                for trial in trials: 
                    try:
                        all_2[config_name][age][problem] += len([strat for strat in results[config_name][trial]["results_strategies_2"][age][problem] if strat == "hand"]) / float(len(results[config_name][trial]["results_strategies_2"][age][problem]))
                        all_3[config_name][age][problem] += len([strat for strat in results[config_name][trial]["results_strategies_3"][age][problem] if strat == "hand"]) / float(len(results[config_name][trial]["results_strategies_3"][age][problem]))
                        n_trials += 1
                    except:
                        print "data not found for ", config_name, trial 
                all_2[config_name][age][problem] = all_2[config_name][age][problem] / n_trials if n_trials > 0 else 0.
                all_3[config_name][age][problem] = all_3[config_name][age][problem] / n_trials if n_trials > 0 else 0.
        
#         fig2, ax2 = plt.subplots()
#         fig2.canvas.set_window_title("Phase 2: " + config_name)
#         for age in ages:
#             ax2.plot([success_2[config_name][age][problem] for problem in problems], "o-", label=str(age))
#         
#         plt.title("Success rate to catch object, averaged accross agents")
#         plt.legend()
#         plt.xlim([-0.5,2.5])
#         plt.ylim([0,1])
#         plt.xlabel("Problem")
#         plt.ylabel("F hand")
#         plt.xticks([0,1,2],problems)
#         
        fig3, ax3 = plt.subplots()
        fig3.canvas.set_window_title("Phase 3: " + config_name)
        for age in ages:
            ax3.plot([all_3[config_name][age][problem] for problem in problems], "o-", label=str(age))
        
        plt.title("Frequency of hand strategy accross agents")
        plt.legend()
        plt.xlim([-0.5,2.5])
        plt.ylim([0,1])
        plt.xlabel("Problem")
        plt.ylabel("F hand")
        plt.xticks([0,1,2],problems)
        
        
    print all_2
    print all_3
        
    plt.show(block=True)
    

    
elif mode == "waves":
    
    
    with open(log_dir + "results.pickle", 'r') as f:
        results = cPickle.load(f)
        f.close()
        
        
        
    #print results
        
        
    # Analysis of first attempt: percentage of hand strategy on first attempt of phases 2 and 3, depending on cdt, problem, age, averaged accross trials
    waves_2 = {}
    waves_3 = {}
    
    for config_name in config_list["xp1"]:
        print config_name
        waves_2[config_name] = {}
        waves_3[config_name] = {}
    
        
        
        for age in ages:
            
            waves_2[config_name][age] = [[], []]
            waves_3[config_name][age] = [[], []]
            
            for trial in trials: 
            
#                 if results[config_name][trial]["results_niter_2"][age]["A"] >= 0:
#                     p_success = "A"
#                 elif results[config_name][trial]["results_niter_2"][age]["B"] >= 0:
#                     p_success = "B"
#                 elif results[config_name][trial]["results_niter_2"][age]["C"] >= 0:
#                     p_success = "C"
#                 else:
#                     p_success = "D"
#                     
#                 if p_success == "A":
#                     for problem in ["B", "C"]:
#                         waves_2[config_name][age][1] += results[config_name][trial]["results_strategies_2"][age][problem]
#                 elif p_success == "B":
#                     for problem in ["C"]:
#                         waves_2[config_name][age][1] += results[config_name][trial]["results_strategies_2"][age][problem]
#                     for problem in ["A"]:
#                         waves_2[config_name][age][0] += results[config_name][trial]["results_strategies_2"][age][problem]
#                 elif p_success == "C":
#                     for problem in ["A", "B"]:
#                         waves_2[config_name][age][0] += results[config_name][trial]["results_strategies_2"][age][problem]
#                 elif p_success == "D":
#                     for problem in ["A", "B", "C"]:
#                         waves_2[config_name][age][0] += results[config_name][trial]["results_strategies_2"][age][problem]
#                         
                        
                if results[config_name][trial]["results_niter_3"][age]["A"] >= 0:
                    p_success = "A"
                elif results[config_name][trial]["results_niter_3"][age]["B"] >= 0:
                    p_success = "B"
                elif results[config_name][trial]["results_niter_3"][age]["C"] >= 0:
                    p_success = "C"
                else:
                    p_success = "D"
                    
                if p_success == "A":
                    for problem in ["B", "C"]:
                        waves_3[config_name][age][1] += results[config_name][trial]["results_strategies_3"][age][problem]
                elif p_success == "B":
                    for problem in ["C"]:
                        waves_3[config_name][age][1] += results[config_name][trial]["results_strategies_3"][age][problem]
                    for problem in ["A"]:
                        waves_3[config_name][age][0] += results[config_name][trial]["results_strategies_3"][age][problem]
                elif p_success == "C":
                    for problem in ["A", "B"]:
                        waves_3[config_name][age][0] += results[config_name][trial]["results_strategies_3"][age][problem]
                elif p_success == "D":
                    for problem in ["A", "B", "C"]:
                        waves_3[config_name][age][0] += results[config_name][trial]["results_strategies_3"][age][problem]
                        

#             waves_2[config_name][age][0] = -1. if len(waves_2[config_name][age][0]) == 0 else len([strat for strat in waves_2[config_name][age][0] if strat == "hand"]) / float(len(waves_2[config_name][age][0]))
#             waves_2[config_name][age][1] = -1. if len(waves_2[config_name][age][1]) == 0 else len([strat for strat in waves_2[config_name][age][1] if strat == "hand"]) / float(len(waves_2[config_name][age][1]))
            waves_3[config_name][age][0] = -1. if len(waves_3[config_name][age][0]) == 0 else len([strat for strat in waves_3[config_name][age][0] if strat == "hand"]) / float(len(waves_3[config_name][age][0]))
            waves_3[config_name][age][1] = -1. if len(waves_3[config_name][age][1]) == 0 else len([strat for strat in waves_3[config_name][age][1] if strat == "hand"]) / float(len(waves_3[config_name][age][1]))
            
        
    #print waves_2
    print waves_3
        
    
