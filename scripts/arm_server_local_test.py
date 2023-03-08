import rospy

from actionlib import *
from actionlib_msgs.msg import *

from custom_msgs.msg import MoveCubesAction, ScanPlatformCubesAction, ScanPlatformCubesActionResult, ScanPlatformCubesResult

class MoveCubesServer:

    def __init__(self,name):
        self._sas = SimpleActionServer(name,
                MoveCubesAction, auto_start= False,
                execute_cb=self.execute_cb)
        self._sas.start()

    def execute_cb(self, msg):
        
        i = 0
        while i < 3: 
            if msg.fromSlotId[i] != "n":
                #The implementation of moving a cube from the arm group needs to be called here!
                rospy.loginfo("Moving Cube from : "+ msg.fromSlotId[i]+ " to: "+msg.toSlotId[i])
            i += 1
            

        #When Moving all cubes was sucsessfully call:
        self._sas.set_succeeded()

        #If an error occured call:
        #self._sas.set_aborted()
    

class ScanPlatformCubesServer:
    _result = ScanPlatformCubesResult()

    def __init__(self,name):
        self._sas = SimpleActionServer(name,
                ScanPlatformCubesAction, auto_start= False,
                execute_cb=self.execute_cb)
        self._sas.start()

    def execute_cb(self, msg):
        
        #The implementation of scanning the cubes on the platorm from the arm group need to be called here!
        rospy.loginfo("Locating the platform and scanning cubes")

        #The Result needs to be set like this example, but which the real cube Ids. 0 meaning the slot is empty.


        
        #When scannig all slots was sucsessfully call:
        self._sas.set_succeeded()

        #If an error occured call:
        #self._sas.set_aborted()

def main():

    rospy.init_node('arm_server_node')

    server = MoveCubesServer('MoveCubes_action_server')
    server = ScanPlatformCubesServer('ScanPlatformCubes_action_server')
 
if __name__ == '__main__':
    main()