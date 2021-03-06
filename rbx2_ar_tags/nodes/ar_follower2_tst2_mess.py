#!/usr/bin/env python

"""
    ar_follower.py - Version 1.0 2013-08-25
    
    Follow an AR tag published on the /ar_pose_marker topic.  The /ar_pose_marker topic
    is published by the ar_track_alvar package
    
    Created for the Pi Robot Project: http://www.pirobot.org
    Copyright (c) 2013 Patrick Goebel.  All rights reserved.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details at:
    
    http://www.gnu.org/licenses/gpl.html
"""
import rospy
from std_msgs.msg import String
from ar_track_alvar_msgs.msg import AlvarMarkers
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped
#from move_base_msgs.msg import MoveBaseActionFeedback
from actionlib_msgs.msg import GoalStatusArray
#from move_base_msgs.msg import GoalStatus
from math import copysign
import time
import tf
from math import e

class ARFollower():
    #global counter
	def __init__(self):
		rospy.init_node("ar_follower")

		# Set the shutdown function (stop the robot)
		rospy.on_shutdown(self.shutdown)

		# How often should we update the robot's motion?
		self.rate = rospy.get_param("~rate", 15)
		r = rospy.Rate(self.rate) 

		# The maximum rotation speed in radians per second
		self.max_angular_speed = rospy.get_param("~max_angular_speed", 0.5)

		# The minimum rotation speed in radians per second
		self.min_angular_speed = rospy.get_param("~min_angular_speed", 0.1)

		# The maximum distance a target can be from the robot for us to track
		self.max_x = rospy.get_param("~max_x", 20.0)

		# The goal distance (in meters) to keep between the robot and the marker
		self.goal_x = rospy.get_param("~goal_x", 0.0001)

		# How far away from the goal distance (in meters) before the robot reacts
		self.x_threshold = rospy.get_param("~x_threshold", 0.01)

		# How far away from being centered (y displacement) on the AR marker
		# before the robot reacts (units are meters)
		self.y_threshold = rospy.get_param("~y_threshold", 0.05) #0.05 0.2

		# How much do we weight the goal distance (x) when making a movement
		self.x_scale = rospy.get_param("~x_scale", 0.5)

		# How much do we weight y-displacement when making a movement
		self.y_scale = rospy.get_param("~y_scale", 0.9)

		# The max linear speed in meters per second
		self.max_linear_speed = rospy.get_param("~max_linear_speed", 0.3)

		# The minimum linear speed in meters per second
		self.min_linear_speed = rospy.get_param("~min_linear_speed", 0.1)

		#intialize frame counter
		self.TargetFlag = rospy.get_param("~TargetFlag", False)
		self.MappingFlag = rospy.get_param("~MappingFlag",False)
		self.marker_id = rospy.get_param("~marker_id", 0)
		self.marker_id2 = rospy.get_param("~marker_id2", 0)
		# Publisher to control the robot's movement
		self.cmd_vel_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=5)

		# Intialize the movement command
		self.move_cmd = Twist()


		# Set flag to indicate when the AR marker is visible
		self.target_visible = False
		self.TargetFlag	 = False
		self.MappingFlag = False
		self.marker_id = 0
		self.marker_id2 = 0
		# Wait for the ar_pose_marker topic to become available
		rospy.loginfo("Waiting for ar_pose_marker topic...(notHassan)")
		#rospy.wait_for_message('move_base', String)
		#rospy.Subscriber('move_base', String, self.set_cmd_vel)
		rospy.wait_for_message('ar_pose_marker', AlvarMarkers)
		#rospy.loginfo("waiting for move_base")	
		#rospy.wait_for_message('move_base/status', GoalStatusArray)
		#rospy.loginfo("move_base message recieved")
		# Subscribe to the ar_pose_marker topic to get the image width and height
		rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.set_cmd_vel)
		#rospy.Subscriber('move_base', GoalStatusArray, self.set_cmd_vel)

		rospy.loginfo("Marker messages detected. Starting follower...")
        
        # Begin the cmd_vel publishing loop
		while not rospy.is_shutdown():
            # Send the Twist command to the robot
			self.cmd_vel_pub.publish(self.move_cmd)
            
            # Sleep for 1/self.rate seconds
			r.sleep()
	#def initial_spin(self, msg):
    # TAG OF THE PREVIOUS TEAM
        # Pick off the first marker (in case there is more than one)
        #if (( self.target_visible == False) and (MappingFlag==True)):
        #self.move_cmd.angular.z = 1.1
        #if(self.target_visible == True)
        # self.move_cmd.angular.z =0
        #break\
	def set_cmd_vel(self,msg):
		global TargetFlag
		global MappingFlag
		global marker_id
		#counter = 0
		#status = msg.status
		#rospy.loginfo("STATUS HERE:%s",status)
		try:
			
			marker = msg.markers[0]
			self.marker_id = msg.markers[0].id
			self.marker_id2 = msg.markers[1].id
			rospy.loginfo("ZERO MARKER ZERO is:%i\n",self.marker_id)
			rospy.loginfo("ONE MARKER ONE is:%i\n",self.marker_id2)
		        #rospy.loginfo("The MARKER ID is:%i\n",marker_id)
		   
		    # rospy.loginfo("the Roll is: %d",roll)
		    # rospy.loginfo("the Pitch is: %d",pitch)
		    # rospy.loginfo("the Roll is: %d",yaw)
			if ((not self.target_visible) and (self.marker_id==5)):

				rospy.loginfo("FOLLOWER is Tracking Target!")
		        
				self.move_cmd.angular.z = 0.0
				self.target_visible = True
		except:
			# If target is lost, stop the robot by slowing it incrementally
			self.move_cmd.linear.x /= 1.4 #1.9
			if ((self.TargetFlag is not True) or (self.marker_id !=5)):
				self.move_cmd.angular.z = 0.6 #1.08  , 0.9
			else:
				self.move_cmd.linear.y = 0.0
				self.move_cmd.linear.z = 0.0
				self.move_cmd.linear.x = 0.0
				self.move_cmd.angular.z= 0.0
		    
			if self.target_visible:
				rospy.loginfo("FOLLOWER LOST Target!")
				self.target_visible = False
				rospy.loginfo("----LOST ZERO LOST:%i\n",self.marker_id)
				rospy.loginfo("----LOST ONE LOST:%i\n",self.marker_id2)
		        #counter+=1
			return
                    
        
        #rospy.loginfo("the frame count is : %f", counter)
		
		
		quaternion = (
						marker.pose.pose.orientation.x,
						marker.pose.pose.orientation.y,
						marker.pose.pose.orientation.z,
						marker.pose.pose.orientation.w)
		euler = tf.transformations.euler_from_quaternion(quaternion)
		#roll = euler[0]
		#pitch = euler[1]
		yaw = euler[2]
		
		#if(msg.markers[1] is not None): 
			#quaternion = (
							#msg.markers[1].pose.pose.orientation.x,
							#msg.markers[1].pose.pose.orientation.y,
							#msg.markers[1].pose.pose.orientation.z,
							#msg.markers[1].pose.pose.orientation.w)
			#euler = tf.transformations.euler_from_quaternion(quaternion)
			#roll1 = euler[0]
			#pitch1 = euler[1]
			#yaw1 = euler[2]

		#rospy.loginfo("the Roll is: %f",roll)
		#rospy.loginfo("the Pitch is: %f",pitch)
		rospy.loginfo("the yaw is: %f",yaw)
		#rospy.loginfo("the yaw is: %f",yaw1)



		# Get the displacement of the marker relative to the base
		target_offset_y = marker.pose.pose.position.y

		# Get the distance of the marker from the base
		target_offset_x = marker.pose.pose.position.x
		#target_offset_x1 = msg.markers[1].pose.pose.position.x

		# Get the distance of the marker from the base
		target_offset_z = marker.pose.pose.position.z

		rospy.loginfo("zero target_offset_x is: %f",target_offset_x)

		#rospy.loginfo("one target_offset_x is: %f",target_offset_x1)
		#rospy.loginfo("the target_offset_y is: %f",target_offset_y)
		#rospy.loginfo("the target_offset_z is: %f",target_offset_z)
		rospy.loginfo("out ZERO MARKER ZERO is:%i\n",self.marker_id)
		rospy.loginfo("out ONE MARKER ONE is:%i\n",self.marker_id2)
		if (self.marker_id==5):
			self.TargetFlag = True
			# Rotate the robot only if the displacement of the target exceeds the threshold
			if ((abs(target_offset_y) > (self.y_threshold)) ):  #and (self.TargetFlag is not True)
			    # Set the rotation speed proportional to the displacement of the target
				speed = (target_offset_y * self.y_scale)
				self.move_cmd.angular.z = copysign(max(self.min_angular_speed,
				                        min(self.max_angular_speed, abs(speed))), speed)
			else:
				self.move_cmd.angular.z = 0.0
			    #self.counter = 121;

			# Now get the linear speed
			if (target_offset_x - self.goal_x) > self.x_threshold:
				speed =  abs((self.goal_x - (target_offset_x + 0.2))) * self.x_scale
				if speed > 0:
					speed += 0.1#1.5
				self.move_cmd.linear.x = copysign(min(self.max_linear_speed, max(self.min_linear_speed, abs(speed))), speed)
			else:
				self.move_cmd.linear.x /= 1.6 #1.9
				cspeed =  self.move_cmd.linear.x
				rospy.loginfo("the current speed is : %f",cspeed)
				if((target_offset_x <= 0.8 ) and (target_offset_x >= 0.30) and (cspeed <= 0.1)):#0.8 0.05 0.1, respectively
					self.move_cmd.linear.x = cspeed*e**(0.1)-cspeed*e**(cspeed) # 0.4 worked cspeed*0.1+0.16  ,,,cspeed*e**(0.43)-cspeed*e**(cspeed)+0.08
					rospy.loginfo("increasing Speed \n")
					rospy.loginfo("Incr ZERO MARKER ZERO is:%i\n",self.marker_id)
					rospy.loginfo("Incr ONE MARKER ONE is:%i\n",self.marker_id2)		
				else:
					self.move_cmd.linear.x /= 1.1
				# self.move_cmd.linear.y = 0.0
				# self.move_cmd.linear.z = 0.0
					rospy.loginfo("Targ ZERO MARKER ZERO is:%i\n",self.marker_id)
					rospy.loginfo("Targ ONE MARKER ONE is:%i\n",self.marker_id2)
					rospy.loginfo("arrived to destination : %r", self.TargetFlag)
					rospy.loginfo("target achieved\n")
     					#if yaw > 1.5 and yaw < 3:
                 			#	self.move_cmd.angular.z = 0.2
														
                 			#	self.move_cmd.linear.x = -0.01
                 			#	rospy.loginfo("Parking\n")

		elif((self.TargetFlag is not True) and ((self.marker_id != 5 ) or (self.marker_id2!= 5 ))  and ((self.marker_id2 != 12) or (self.marker_id != 12))):
			self.move_cmd.angular.z = 0.6 #1.08
            
                
                	

	def shutdown(self):
		rospy.loginfo("Stopping the robot...")
		self.cmd_vel_pub.publish(Twist())
		rospy.sleep(1)     

if __name__ == '__main__':
    
	try:

		ARFollower()
		rospy.spin()
	except rospy.ROSInterruptException:
		rospy.loginfo("AR follower node terminated.")
