import cPickle
import numpy as np

from experiment import ToolsExperiment
from explauto.experiment.log import ExperimentLog
from config import configs
from explauto.utils import rand_bounds

log_dir = "/home/sforesti/scm/Flowers/ICCM2016/src/test/"
config_name = "H-P-AMB"
trial = 1

config = configs[config_name]

config.env_cfg["env_conf"]["gui"]= True


log = ExperimentLog(None, None, None)
for key in ["agentM", "agentS"]:
    try:
        filename = log_dir + config_name + '/log{}-'.format(trial) + key + '-{}.pickle'.format(0)
        with open(filename, 'r') as f:
            log_key = cPickle.load(f)
        log._logs[key] = log_key
    except:
        print "File not Found:", filename
    
    
    
xp = ToolsExperiment(config, context_mode=config.context_mode)
xp.ag.fast_forward(log, forward_im=False)



s_space = config.s_spaces["s_o"]
print "s_space", s_space

context = [0.18, -0.028]
xp.env.env.env.top_env.pos = context
print "current_context", xp.env.get_current_context()

sg = [0.2, 0.046]
print "sg", sg

#mid = xp.ag.choose_space_child(s_space, context + s)
#print "chosen module:", mid

# for mid in ["mod4", "mod5", 'mod6']:
#     dists, idxs = xp.ag.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.nn_y(np.array(context + sg), k=1)
#     print mid, xp.ag.modules[mid].sensorimotor_model.model.imodel.fmodel.dataset.get_xy(idxs[0])
# 
# print "chosen m", m

# dists, idxs = xp.ag.modules["mod1"].sensorimotor_model.model.imodel.fmodel.dataset.nn_x(np.array(m))
# xy = xp.ag.modules["mod1"].sensorimotor_model.model.imodel.fmodel.dataset.get_xy(idxs[0])
# print "corresponding NN mod1", xy
# dists, idxs = xp.ag.modules["mod2"].sensorimotor_model.model.imodel.fmodel.dataset.nn_x(np.array(xy[1]))
# xy = xp.ag.modules["mod2"].sensorimotor_model.model.imodel.fmodel.dataset.get_xy(idxs[0])
# print "corresponding NN mod2", xy 


# for it in range(len(log._logs["agentM"])):
#     if list(m) == list(log._logs["agentM"][it]):
#         print it, "s=", log._logs["agentS"][it]


while True:
    print
    context = list(rand_bounds(np.array([[-0.5, -0.5], [0.5, 0.5]]))[0])
    sg = list(rand_bounds(np.array([[-0.5, -0.5], [0.5, 0.5]]))[0])
    xp.env.env.env.top_env.pos = context
    print "current_context", xp.env.get_current_context()
    print "ds goal", sg
    mid = xp.ag.choose_space_child(s_space, context + sg)
    print "chosen module:", mid
    m = xp.ag.inverse(s_space, sg, context=context, explore=False)
    sr = xp.env.update(m, reset=False)
    ms = np.hstack((m, sr))
    #print "reached ms:", ms
    
    