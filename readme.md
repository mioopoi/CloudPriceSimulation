# Cloud Power Price Simulation

This is the source code of the simulation for the paper named 
*Approximation algorithms for minimizing time-variable electricity cost
in cloud system (accepted)*. The code is written in pure python.

To successfully run the simulation, first you need to install Anaconda2
and then install Gurobi to Anaconda.

Python version: 2.7.11 (Anaconda2)  
Gurobi version: 7.0.2

`simulation_online.py` is the main file for online algorithms and
`simulation_offline.py` is for offline algorithms.

Notice: The data file (`task_events_out.csv`) for real-trace simulation 
has not been uploaded, since it is too large. So others can only run the
simulation with random input, otherwise it will throw an exception. If
you want to ask for the data to run the simulation with real-trace input,
please contact me through e-mail.

Author: Huafan Li  
E-mail: huafan@seu.edu.cn

