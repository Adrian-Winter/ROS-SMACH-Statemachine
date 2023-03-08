import rospy

from actionlib import *
from actionlib_msgs.msg import *

from custom_msgs.msg import MovePlatformAction, InitialMappingAction


class MovePlatformServer:

    def __init__(self,name):
        self._sas = SimpleActionServer(name,
                MovePlatformAction, auto_start= False,
                execute_cb=self.execute_cb)
        self._sas.start()

    def execute_cb(self, msg):
        
        #The implementaion of the platform group for moving needs to go here! The goal position can be "WL","KS1","KS2"
        rospy.loginfo("Platform moving to : "+ msg.position)
       
        #When moving to the goal position was succsesfully call:
        self._sas.set_succeeded()

        #If an error occured call:
        #self._sas.set_aborted()

class InitialMappingServer:

    def __init__(self,name):
        self._sas = SimpleActionServer(name,
                InitialMappingAction, auto_start= False,
                execute_cb=self.execute_cb)
        self._sas.start()
  
    def execute_cb(self, msg):
        
        #Mapping is manual, user needs to confirm that the stations and WH have been found
        rospy.loginfo("mapping the room...")
        

        #When mapping the room and all stations and the Warehouse have been found call:
        self._sas.set_succeeded()

        #If an error occured call:
        #self._sas.set_aborted()

def main():

    rospy.init_node('platform_server_node')

    server = MovePlatformServer('MovePlatform_action_server')
    server = InitialMappingServer('InitialMapping_action_server')

if __name__ == '__main__':
    main()