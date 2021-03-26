# Multi agent Path Planning
This code contains my 6-month work as a Machine Learning intern at France's National Research Institute in Computer Science @Inria.

The main idea of my work is to develope a machine learning model powered by Graph Neural Networks and merged with Deep Reinforcement Learning algorithms 
to build a multi-agent path planning algorithm that generalizes to different network topologies, while mainting fast communication and efficient convergence.

We use CoppeliaSim as our simulator to see the performance of our algorithms on mobile robots.

All code is written in Python3, and we use Ros2-Interface to communicate with CoppeliaSim.

 
## Pre-requisites 
Please make sure to have the following installed before using the main.py code:
* NumPy 
* Pandas
* ROS2 
* CoppeliaSim 
* ROS2-Interface


## Simulation in CoppeliaSim 
We test our algorithms on two bubblerob's from CoppeliaSim, however our work applies to all kinds of mobile robots that just need some initial parameter tuning.
We first run a vanilla consensus algorithm, and start collecting data of relative poses for robot i w.r.t robot j and it's corresponding local input.'