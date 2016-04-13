import cPickle
import numpy as np
import sys

from experiment import ToolsExperiment
from explauto.experiment.log import ExperimentLog
from config import configs
from explauto.utils import rand_bounds
import matplotlib.pyplot as plt

    
    

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
        
        
        
    iterations = [1000, 10000, 50000]
    
    results = {}
    
    for iteration in iterations:
        print iteration
        results[iteration] = {}
        
        xp = ToolsExperiment(config, context_mode=config.context_mode)
        
        log_i = ExperimentLog(None, None, None)
        log_i._logs["motor"] = log._logs["motor"][:iteration]
        log_i._logs["sensori"] = log._logs["sensori"][:iteration]
        
        xp.ag.fast_forward(log_i, forward_im=False)
        
        s_space = xp.ag.config.s_spaces["s_o"]
        
        
        n_test_point = 100
        n_trial_per_point = 100
        
        x_points = np.linspace(-1.5, 1.5, n_test_point)
        y_points = np.linspace(-1.5, 1.5, n_test_point)
         
        results[iteration] = np.zeros((n_test_point, n_test_point))
        
        for ix in range(len(x_points)):
            for iy in range(len(y_points)):
                probas = xp.ag.choose_space_child(s_space, [x_points[ix], y_points[iy]], mode=xp.ag.choose_children_mode, local=xp.ag.ccm_local, k=n_trial_per_point)
                results[iteration][ix][iy] = probas[0]
                
                
        # Plot 
        
        fig, ax = plt.subplots()
        fig.canvas.set_window_title("Age " + str(iteration))
        
        pcol = plt.pcolormesh(x_points, y_points, results[iteration], vmin=0, vmax=1, linewidth=0, cmap="magma")  
        pcol.set_rasterized(True)      
        pcol.set_edgecolor('face')
        
        cb = plt.colorbar()
        cb.ax.set_yticklabels(["Tool", "", "", "", "", "", "", "", "", "", "Hand"], fontsize = 30)
        cb.solids.set_rasterized(True)
        cb.solids.set_edgecolor("face")

#         plt.xlabel("X", fontsize = 30)
#         plt.ylabel("Y", fontsize = 30)
        plt.xticks([-1., 0, 1.], fontsize = 26)
        plt.yticks([-1., 0, 1.], fontsize = 26)
        
        plt.savefig(log_dir + "img/" + config_name + '-map-{}.pdf'.format(iteration), format='pdf', bbox_inches='tight', rasterized=True)
        #plt.savefig(log_dir + "img/" + config_name + '-map-{}.png'.format(iteration), format='png', bbox_inches='tight', rasterized=True)
        
        
                     
    print results
    
    with open(log_dir + config_name + '/results-map-{}.pickle'.format(trial), 'wb') as f:
        cPickle.dump(results, f)
     

    #plt.show(block=True)
     
    
if __name__ == "__main__":
    
    log_dir = sys.argv[1]
    config_name = sys.argv[2]
    trial = sys.argv[3]
    main(log_dir, config_name, trial)