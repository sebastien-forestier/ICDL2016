# ICDL2016
Repository aiming at reproducibility of experiments and analysis of results provided in ICDL2016 conference paper. 

We provide source code of the experiments (Licence GPLv3), and data analysis. 

We do not provide data as it is too large, but we explain how to re-generate it.

## Paper
Here is the ICDL [paper](http://sforestier.com/sites/default/files/Forestier2016Overlapping.pdf).
## Video 
Here is a [video](https://www.youtube.com/watch?v=o5ARhTA8cfg) of the setup. 

## Tutorial on Active Model Babbling
Here is a Jupyter Notebook explaining the Active Model Babbling algorithm with comparisons to other algorithms: [notebook](http://nbviewer.jupyter.org/github/sebastien-forestier/ExplorationAlgorithms/blob/master/main.ipynb).

## Experiments ##
* [notebook](http://nbviewer.jupyter.org/github/sebastien-forestier/ICDL2016/blob/master/notebook/experiments.ipynb) describing how to run the experiments

## Analysis ##
* [notebook](http://nbviewer.jupyter.org/github/sebastien-forestier/ICDL2016/blob/master/notebook/analysis.ipynb) describing how to analyze the data.

## Code Dependencies ##
* [Explauto](https://github.com/flowersteam/explauto) on branch random_goal_babbling, [this](https://github.com/flowersteam/explauto/commit/11307b75730f4ca933a918d782aca09cbe357298) commit
* [pydmps](https://github.com/sebastien-forestier/pydmps) on branch master, [this](https://github.com/sebastien-forestier/pydmps/commit/464450d99ec8be962d54270164861a56eb94993c) commit
* Run with Numpy version '1.10.1', and scipy version '0.15.1'.
