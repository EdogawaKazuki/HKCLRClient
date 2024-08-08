# Introduction
- The HKCLRROSClient.py is a client to connect the ROS that runs on the HKCLR robot. The client is written in Python and uses the ROS Python API to communicate with the ROS master. 
- The HKCLRUDPServer.py is a UDP server that allows clients to send and receive data from the HKCLR robot.
- The RobotUDPClient.cs can be used in unity as a client to the UDP server.

# How to use
1. Run the desired ROS nodes on the robot
   1. Open a terminal and run "roslaunch ~/Desktop/robot_2d.launch"
   2. Open another terminal and run "source_carto"
   3. At the same terminal in ii. run "roslaunch cartographer_ros service_robot.launch"
2. Run the rosbridge websocket server on the robot
   1. Open a terminal and run "rosrun rosbridge_server rosbridge_websocket"
3. Run the HKCLRUDPServer.py on any machine
4. Run another client to connect to the UDP server

# Something about the MOVEYAW
Just input what you need yaw to set_yaw(yaw)
