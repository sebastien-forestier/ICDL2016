import cPickle
from experiment import ToolsExperiment
from explauto.experiment.log import ExperimentLog
from config import configs

log_dir = "/home/sforesti/scm/Flowers/ICCM2016/src/test/"
config_name = "H-P-AMB"
trial = 1

config = configs[config_name]

config.gui = True


log = ExperimentLog(None, None, None)
for key in ["agentM", "agentS"]:
    filename = log_dir + config_name + '/log{}-'.format(trial) + key + '-{}.pickle'.format(0)
    with open(filename, 'r') as f:
        log_key = cPickle.load(f)
    log._logs[key] = log_key
                    
    
    
    
xp = ToolsExperiment(config, context_mode=config.context_mode)
xp.ag.fast_forward(log)



s_space = config.s_spaces["s_o"]
print "s_space", s_space

context = [0., 0.8]
xp.env.env.env.top_env.pos = context
print "current_context", xp.env.get_current_context()

s = [0., 0., 0., 0.5, 0.25, 0.]
print "s", s

print xp.ag.choose_space_child(s_space, context + s)