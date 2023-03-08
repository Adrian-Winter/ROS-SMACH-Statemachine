import rospy
import smach
import smach_ros

import tkinter as tk
from tkinter import ttk

from array import *

from actionlib import *
from actionlib_msgs.msg import *

from custom_msgs.msg import MovePlatformAction, MovePlatformGoal, InitialMappingAction, MoveCubesAction, MoveCubesGoal, ScanPlatformCubesAction

from smach_ros import SimpleActionState

from custom_msgs.srv import Lager_get, Lager_set, find_empty_slot,find_cubes
from custom_msgs.srv import Lager_get, Lager_getResponse



class UserInputState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['request','store',"aborted"],
                        output_keys=['requestedCubes',"direction","station"],input_keys=[
                            "requestedCubes","direction","station"])
    
    def execute(self, userdata):
        # User Input GUI

        root = tk.Tk()
        root.title('User input')
        #Outcome Klasse
        class outcome:
            def __init__(self):
                self.outcome = 'abort'
            def set_store_S1(self):
                self.outcome = 'store'
                userdata.direction = "s"
                userdata.station = "S1"
                root.destroy()
            def set_request_S1(self):
                self.outcome = 'request'
                userdata.direction = "r"
                userdata.station = "S1"
                root.destroy()
            def set_store_S2(self):
                self.outcome = 'store'
                userdata.direction = "s"
                userdata.station = "S2"
                root.destroy()

            def set_request_S2(self):
                self.outcome = 'request'
                userdata.direction = "r"
                userdata.station = "S2"
                root.destroy()

            def set_abort(self):
                self.outcome = "aborted"
                root.destroy()

        outcome = outcome()

        ttk.Label(root, text="Select what you would like to do:", compound="top",font='Helvetica 12').grid(row=0, column=0, padx='5', pady='5', sticky = tk.S,columnspan=2)
        button_s_s1 = ttk.Button(root, text='Store from Station 1', compound='top', command=outcome.set_store_S1).grid(row=2, column=0, padx='5', pady='5', sticky='ew')
        button_s_s2 = ttk.Button(root, text='Store from Station 2', compound='top', command=outcome.set_store_S2).grid(row=3, column=0, padx='5', pady='5', sticky='ew')
        button_r_s1 = ttk.Button(root, text='Request to Station 1', compound='top', command=outcome.set_request_S1).grid(row=2, column=1, padx='5', pady='5', sticky='ew')
        button_r_s2 = ttk.Button(root, text='Request to Station 2', compound='top', command=outcome.set_request_S2).grid(row=3, column=1, padx='5', pady='5', sticky='ew')
        abbort_button = ttk.Button(root, text='Abort', compound='top', command=outcome.set_abort).grid(row=5, column=0, padx='5', pady='5', sticky = tk.S,columnspan=2)

        root.mainloop()  
        if outcome.outcome == 'store':
            rospy.loginfo("Request to store Cubes from Station"+str(userdata.station))

    # Abfrage der Würfel
        elif outcome.outcome == 'request':
            root = tk.Tk()
            root.title('Requested cubes input')
            ttk.Label(root, text="Select the cubes you want to request:", compound="top", font='Helvetica 12').grid(row=0, column=0,padx='5',pady='5',sticky=tk.S,columnspan=2)
            ttk.Label(root, text="(for less than three cubes, leave the input box empty)", compound="top",font='Helvetica 10').grid(row=1, column=0, padx='5', pady='5', sticky=tk.S, columnspan=3)
            
            # Abfragen des Lagerinhaltes
            rospy.wait_for_service('Lager_get')
            Lager_get_srv = rospy.ServiceProxy('Lager_get', Lager_get)
            Lager_inhalt = Lager_get_srv()
            

            ttk.Label(root, text="The warehouse currently contains following cubes: \n"+str(Lager_inhalt.slot_inhalt), compound="top",font='Helvetica 10').grid(row=1, column=0, padx='5', pady='5', sticky=tk.S, columnspan=3)

            def get_entries(Entrys):
                #Würfel_Verfuegbar=True #Hier Abrage bei Lagermangement einfügen
                for i in range(3):
                    input=Entrys[i].get()
                    if input=="":
                        userdata.requestedCubes[i]="n"
                    else:
                        userdata.requestedCubes[i]=input
                rospy.wait_for_service('find_cubes')
                find_cubes_srv=rospy.ServiceProxy('find_cubes', find_cubes)
                cube_slots=find_cubes_srv(userdata.requestedCubes)
                Würfel_Verfuegbar = cube_slots.cubes_available
                rospy.loginfo("Sind die gesuchten Würfel im Lager vorhanden: "+str(cube_slots.cubes_available))

                if Würfel_Verfuegbar:
                    root.destroy()
                    rospy.loginfo("Verfügbar")
                else:
                    ttk.Label(root, text="Cubes not available, pelese cnage your request ", compound="top",font='Helvetica 12').grid(row=7, column=0, padx='5', pady='5', sticky=tk.S, columnspan=3)

            Entrys = []
            for i in range(3):
                entry = ttk.Entry(root)
                entry.grid(row=3, column=i, padx='5', pady='5', sticky='ew')
                Entrys.append(entry)
            finished_button = ttk.Button(root, text='Request Cubes', compound='top', command=lambda:get_entries(Entrys)).grid(row=5, column=0, padx='5', pady='5', sticky = tk.S,columnspan=3)
            abbort_button = ttk.Button(root, text='Abort', compound='top', command=outcome.set_abort).grid(row=6, column=0,padx='5', pady='5',sticky=tk.S,columnspan=3)

            root.mainloop()
        if outcome.outcome == 'request':
            rospy.loginfo("Cubes "+str(userdata.requestedCubes)+"have been requested to Station"+str(userdata.station))

        return outcome.outcome

class DebuggingState(smach.State): 
    def __init__(self):
        smach.State.__init__(self, outcomes=["Initial_mapping",'User_input','Plan_cube_transfer','Platform_moves_to_the_warehouse to_collect_cubes','Platform_moves_to_the_warehouse to_store_cubes','Platform_moves_to_the_station_to_deliver_cubes','Platform_moves_to_the_station_to_collect_cubes','Waiting_for_user','Arm_loads_platform','Arm_unloads_platform','Scan_platform_cubes',]
        ,output_keys=['requestedCubes',"cubesOnPlatform",'fromSlotId',"toSlotId","direction","station"]
        ,input_keys=['requestedCubes',"cubesOnPlatform",'fromSlotId',"toSlotId","direction","station"])

    def execute(self, userdata):

        rospy.loginfo("Currently in DebuggingState")

        #Start der Debug GUI
        ########################################

        #Definieren der GUI
        root = tk.Tk()
        root.title("Debugging State")
        #root.geometry("800x800")

        #Liste mit den möglichen outcomes/States
        States=['Initial_mapping','User_input','Plan_cube_transfer','Platform_moves_to_the_warehouse to_collect_cubes','Platform_moves_to_the_warehouse to_store_cubes','Platform_moves_to_the_station_to_deliver_cubes','Platform_moves_to_the_station_to_collect_cubes','Waiting_for_user','Arm_loads_platform','Arm_unloads_platform','Scan_platform_cubes']
        # Atribute der userdata die in der GUI verwendet werden sollen. 
        Userdata_to_display=["requestedCubes","cubesOnPlatform","fromSlotId","toSlotId","direction","station"] 
        # Anzeigenname der Atribute der userdata für die GUI. 
        Userdata_name_to_display=["requestedCubes","cubesOnPlatform","fromSlotId","toSlotId","direction","station"]

        #Liste aller akzeptierter Werte für die Eingaben der GUI. Bei ["all_values"] werden alle Eingaben akzeptiert.
        Userdata_accepted_values=[["all_values"],["all_values"],["L1","L2","L3","L4","L5","L6","L7","L8","L9","P1","P2","P3","n"],["L1","L2","L3","L4","L5","L6","L7","L8","L9","P1","P2","P3","n"],["r","s"],["S1","S2"]]


        #Funktion um den outcome zu wählen und den nächsten State zu starten
        def call_state(Sate_Name):
            #setzen des outcomes
            State_Button.outcome = Sate_Name
            rospy.loginfo("Starte State: " + str(State_Button.outcome))
            #beenden der GUI und des Debugstates
            root.destroy()
            

        #Eine Klasse um Buttos in der GUI für jeden State zu erstellen
        class State_Button:
            alle_Buttons = []
            outcome="n"

            def __init__(self, State_Name, row, column):
                ttk.Button(root, text=State_Name,compound='top', command=lambda:call_state(State_Name)).grid(row=row, column=column, padx='5', pady='5', sticky='ew')
                State_Button.alle_Buttons.append(self)


        #Funktion um die Werte der Userdata zu ändern
        def change_Userdata(Entrys,Data,name, ud_attribute,accepted_values):
            if isinstance(Data, list):
                Data_new=["" for j in range(length(Data))]
                for i in range(length(Data)):
                    Data_new[i]=Entrys[i].get()
                    if accepted_values.count(Data_new[i])>0 or accepted_values==["all_values"]:
                        Data[i]=Data_new[i]
                        
                    else:
                        rospy.loginfo("Userdata nicht geändert, ungültige Eingabe")
                    Entrys[i].delete('0', tk.END)
                    Entrys[i].insert(0, str(Data[i]))

                setattr(userdata, ud_attribute,Data)
                rospy.loginfo("Userdata "+name+ " ist: " + str(getattr(userdata, ud_attribute)))                
                
            elif isinstance(Data, str):
                Data_new = Entrys[0].get()
                if accepted_values.count(Data_new)>0 or accepted_values=="all_values":
                    Data=Data_new
                    setattr(userdata, ud_attribute,Data)
                    rospy.loginfo("Userdata "+name+ " geändert zu: " + str(getattr(userdata, ud_attribute)))
                else:
                    rospy.loginfo("Userdata nicht geändert, ungültige Eingabe")
                Entrys[0].delete('0', tk.END)
                Entrys[0].insert(0, str(Data))
            

            

        #Funktion die die Länge einer Liste zurück gibt und bei einem einzelenen String 1 (ähnlich zu len())
        def length(obj):
            if isinstance(obj, list):
                return len(obj)
            else: return 1

        class Userdata_Edit:
            Amount_of_Entrys = 1
            def __init__(self, name, ud_attribute,accepted_values, row, column):
                Data=getattr(userdata, ud_attribute)
                ttk.Label(root, text=name, compound="top").grid(row=row, column=column, padx='5', pady='5', sticky='ew')
                Entrys = []

                #Speichern der größten Anzahl an einträgen pro Zeile (nicht gut Programmiert, geht nur wenn die längste Zeile die erste ist)
                if len(Data) > Userdata_Edit.Amount_of_Entrys:
                    Userdata_Edit.Amount_of_Entrys = length(Data)

                for i in range(length(Data)):
                    self.entry = ttk.Entry(root)
                    self.entry.grid(row=row, column=column+1+i, padx='5', pady='5', sticky='ew')
                    if isinstance(Data, list):
                        self.entry.insert(0, str(Data[i]))
                    else:
                        self.entry.insert(0, str(Data))
                    Entrys.append(self.entry)

                ttk.Button(root, text="Change", compound="top",command=lambda:change_Userdata(Entrys,Data,name, ud_attribute,accepted_values)).grid(row=row, column=Userdata_Edit.Amount_of_Entrys+1, padx='5', pady='5', sticky='ew')


        # Befüllen der GUI

        ttk.Label(root, text="Debugging", compound="top",font='Helvetica 18 bold').grid(row=0, column=0, padx='5', pady='5', sticky = tk.S,columnspan=5)

        ttk.Label(root, text="An error occured! Manual interaction or data manipulation might be necessary.", compound="top",font='Helvetica 12 ').grid(row=1, column=0, padx='5', pady='5', sticky = tk.S,columnspan=5)

        #Erstellen der Buttons
        ttk.Label(root, text="Chose a State to start:", compound="top",font='Helvetica 16 bold').grid(row=2, column=0, padx='5', pady='5', sticky='ew')

        for i in range(len(States)):
            State_Button(States[i],i+4,0)

        #Erstellen der Userdata Entries in der GUI
        ttk.Label(root, text="Userdata:", compound="top",font='Helvetica 16 bold').grid(row=len(State_Button.alle_Buttons)+3, column=0, padx='5', pady='5', sticky='ew')

        Zeilenversatz=5

        # Erstellen der Zeilen mit Eingabefeldern für jede Userdata in der Liste "Userdata_to_display"

        for i in range(len(Userdata_to_display)):
            Userdata_Edit(Userdata_name_to_display[i], Userdata_to_display[i],Userdata_accepted_values[i][:], len(State_Button.alle_Buttons)+1+i+Zeilenversatz, 0)
            

        root.mainloop()
        


        # Ende der Debug GUI
        ##################################################

        # Zurückgeben des Outcomes um in den entsprechnden State zu wechseln
        return State_Button.outcome

        
class PlanCubeTransferState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['store','request',"aborted"],
                        output_keys=['fromSlotId',"toSlotId"],input_keys=[
                            "requestedCubes","direction","cubesOnPlatform",'fromSlotId',"toSlotId"])
    
    def execute(self, userdata):

        rospy.loginfo("The Warehouse service gets called, and returns the fromSlotId and toSlotId arrays")
    
        #The Warehouse Service gets the userdata.requestedCubes, userdata.cubesOnPlatform and userdata.direction as input and needs to return the from and to slots to plan the cube transfer. 
        #The return from the service need to replace the hard coded arrays:

        #requesed cubes are n if nothing is requested 
        #userdata.cubesOnPlatform ist bekannt durch vorherigen scan 
        rospy.loginfo("Current CubesOnPlatform: "+str(userdata.cubesOnPlatform))
        
        #userdata.fromSlotId = ["L1","L2","L3"]
        #userdata.toSlotId =["P1","P2","P3"]

        #Calculating the fromSlotId array for storing & requesting the toSlotId form the service
        if userdata.direction == "s":
            i=0
            j=0
            while i < 3:
                if userdata.cubesOnPlatform[i] != "n":
                    slot = "P"+str(i+1)
                    userdata.fromSlotId[i] = slot 
                    j+=1
                else:
                    userdata.fromSlotId[i] = "n"
                i+=1

            rospy.wait_for_service('find_empty_slot')
            empty_slot_srv=rospy.ServiceProxy('find_empty_slot', find_empty_slot)
            empty_slot=empty_slot_srv(j)
            while len(empty_slot.empty_slot_name) < 3:
                empty_slot.empty_slot_name.append("n")
            
            userdata.toSlotId =empty_slot.empty_slot_name
            rospy.loginfo("Empty slots in Warehouse available: "+str(empty_slot.empty_slot_available))
            if not empty_slot.empty_slot_available:
                
                rospy.loginfo("Not enough enmpty slots in the warehouse")
                return "aborted"

            rospy.loginfo("FromSlotID is: "+str(userdata.fromSlotId))
            rospy.loginfo("ToSlotID is: "+str(userdata.toSlotId))
            return "store"

        #Assuming the Platform is Empty & Requesting FromSlotID from service. 
        if userdata.direction == "r":

            rospy.wait_for_service('find_cubes')
            find_cubes_srv=rospy.ServiceProxy('find_cubes', find_cubes)
            cube_slots=find_cubes_srv(userdata.requestedCubes)
            userdata.toSlotId = ["n","n","n"]
            rospy.loginfo("Service answer for find Cubes: "+str(cube_slots.cube_slot_name))
            while len(cube_slots.cube_slot_name) < 3:
                cube_slots.cube_slot_name.append("n")
            i=0
            while i < 3:
                if cube_slots.cube_slot_name[i] != "n":
                    slot = "P"+str(i+1)
                    userdata.toSlotId[i] = slot 
                i+=1
        
            userdata.fromSlotId = cube_slots.cube_slot_name

            rospy.loginfo("FromSlotID is: "+str(userdata.fromSlotId))
            rospy.loginfo("ToSlotID is: "+str(userdata.toSlotId))
            return "request"
        else:
            rospy.loginfo("No direction was set!")
            return "aborted"

class WaitForUserState(smach.State): 
    def __init__(self):
        smach.State.__init__(self, outcomes=['finishedUnloading',"finishedLoading",'aborted'],input_keys=["direction","cubesOnPlatform"],output_keys=["cubesOnPlatform"]
                        )
    
    def execute(self, userdata):

        # GUI: wait for user

        root = tk.Tk()
        root.title('Wait for User')

        class outcome:
            def __init__(self):
                self.outcome = ''
            def set_aborted(self):
                self.outcome = 'aborted'
                root.destroy()
            def set_success(self):
                self.outcome = 'success'
                root.destroy()

        outcome = outcome()

        ttk.Label(root, text="Please load or unload the Platform and click finished when you are done. \n In case something goes wrong click abort to enter debugging mode.", compound="top",font='Helvetica 12').pack(side='top')
        finished_button = ttk.Button(root, text='Finished', compound='top', command=outcome.set_success).pack(side='top')
        abbort_button = ttk.Button(root, text='Abort', compound='top', command=outcome.set_aborted).pack(side='top')

        root.mainloop()

        #set outcomes
        if userdata.direction == "s" and outcome.outcome=='success':
            return "finishedLoading"
        if userdata.direction == "r"and outcome.outcome=='success':
            userdata.cubesOnPlatform = ["n","n","n"]
            rospy.wait_for_service('Lager_set')
            rospy.wait_for_service('Lager_get')
            Lager_set_srv = rospy.ServiceProxy('Lager_set', Lager_set)
            Lager_get_srv = rospy.ServiceProxy('Lager_get', Lager_get)
            Lager_inhalt = Lager_get_srv()
            Lager_inhalt.slot_inhalt[9]="n"
            Lager_inhalt.slot_inhalt[10]="n"
            Lager_inhalt.slot_inhalt[11]="n"
            Lager_set_srv(Lager_inhalt.slot_name,Lager_inhalt.slot_inhalt,Lager_inhalt.slot_pos_x,Lager_inhalt.slot_pos_y,Lager_inhalt.slot_pos_z,Lager_inhalt.slot_pos_w)
            return "finishedUnloading"
        else:
            return 'aborted'

def main():

    rospy.init_node('statemachine_Node')
    
    

    # Create a SMACH state machine
    #The outcomes should only be called after the system shut down. Multiple requests can be executed without shutting the state machine down. 
    sm = smach.StateMachine(outcomes=['fertig','abgestürzt'])

    with sm:

        #Userdata that can be used and changed by all states. 

        #The Cube Ids are int64 scanned by the user/arm. 0 meaning the slot is empty.
        sm.userdata.requestedCubes = ["0","0","0"]
        sm.userdata.cubesOnPlatform = ["0","0","0"]

        #The direction can be either "r" for request, or "s" for storing
        sm.userdata.direction = "."

        #The Station names can be either "S1" or "S2"
        sm.userdata.station = "."

        #Slot Ids are "P1","P2","P3" for the Platform Slots and "L1"..."L9" for the Warehouse 
        sm.userdata.fromSlotId = ["n","n","n"] 
        sm.userdata.toSlotId = ["n","n","n"]
        
        #Sets the goal for the MoveCubesAction dynamicly depending on the current userdata
        def arm_goal_callback(userdata, default_goal):
            goal = MoveCubesGoal()
            goal.fromSlotId = userdata.fromSlotId
            goal.toSlotId = userdata.toSlotId
            return goal

        #Sets the goal for the MovePlatformGoal dynamicly depending on the current userdata
        def plattform_goal_callback(userdata, default_goal):
            goal = MovePlatformGoal()
            goal.position = userdata.station
            return goal

        def moveCube_result_cb(userdata, status, result):
            if status == GoalStatus.SUCCEEDED:
                rospy.loginfo("Moved successfully from: "+str(userdata.fromSlotId)+" to: "+str(userdata.toSlotId))

                rospy.wait_for_service('Lager_set')
                rospy.wait_for_service('Lager_get')
                Lager_set_srv = rospy.ServiceProxy('Lager_set', Lager_set)
                Lager_get_srv = rospy.ServiceProxy('Lager_get', Lager_get)
                Lager_inhalt = Lager_get_srv()

                if userdata.direction == "r":
                    i=0
                    while i <3:
                        if userdata.fromSlotId[i] != "n":

                            
                            indexOfLagerSlot = Lager_inhalt.slot_name.index(userdata.fromSlotId[i])

                            cubeId = Lager_inhalt.slot_inhalt[indexOfLagerSlot]

                            indexOfPlatformSlot = Lager_inhalt.slot_name.index(userdata.toSlotId[i])

                            #Updating cube ID on Platform 
                            userdata.cubesOnPlatform[indexOfPlatformSlot-9] = cubeId
                           
                            Lager_inhalt.slot_inhalt[indexOfPlatformSlot]= cubeId

                            #Removing cubeID from Warehouse
                            Lager_inhalt.slot_inhalt[indexOfLagerSlot]= "n"
                        i+=1

                if userdata.direction == "s":
                    i=0
                    while i <3:
                        if userdata.fromSlotId[i] != "n":
                            
                            indexOfPlatformSlot = Lager_inhalt.slot_name.index(userdata.fromSlotId[i])
                            
                            cubeId = Lager_inhalt.slot_inhalt[indexOfPlatformSlot]

                            indexOfLagerSlot = Lager_inhalt.slot_name.index(userdata.toSlotId[i])

                            #Updating cube ID in Lager 
                            Lager_inhalt.slot_inhalt[indexOfLagerSlot]= cubeId

                            #Removing cubeID from Platform
                            #indexOfPlatformSlot = Lager_inhalt.slot_name.index(userdata.fromSlotId[i])
                            
                            Lager_inhalt.slot_inhalt[indexOfPlatformSlot]= "n"
                            
                            
                        i+=1


                Lager_set_srv(Lager_inhalt.slot_name,Lager_inhalt.slot_inhalt,Lager_inhalt.slot_pos_x,Lager_inhalt.slot_pos_y,Lager_inhalt.slot_pos_z,Lager_inhalt.slot_pos_w)
                

        #Saves the scanned cubes to the userdata. 
        def scanPlatformCubes_result_cb(userdata, status, result):
            if status == GoalStatus.SUCCEEDED:
                rospy.wait_for_service('Lager_get')
                Lager_get_srv = rospy.ServiceProxy('Lager_get', Lager_get)
                
                Lager_inhalt = Lager_get_srv()
                i=0
                while i < 3:
                    userdata.cubesOnPlatform[i] = Lager_inhalt.slot_inhalt[i+9]
                    i+=1
                rospy.loginfo("Current cubesOnPlatform as scanned  "+ str(userdata.cubesOnPlatform))
                    
              

        smach.StateMachine.add('Initial_mapping',
                            SimpleActionState('InitialMapping_action_server',InitialMappingAction),
                            #transitions={'succeeded':'User_input','preempted':'abgestürzt','aborted':'Debugging_State'}) 
                            transitions={'succeeded':'User_input','preempted':'abgestürzt','aborted':'Debugging_State'}) 
                          
        smach.StateMachine.add('User_input',
                            UserInputState(), 
                            transitions={'request':'Plan_cube_transfer','store':'Platform_moves_to_the_station_to_collect_cubes','aborted':'Debugging_State'},)
                            #transitions={'request':'Debugging_State','store':'Debugging_State','aborted':'Debugging_State'},)

        smach.StateMachine.add('Plan_cube_transfer',
                            PlanCubeTransferState(), 
                            transitions={'request':'Platform_moves_to_the_warehouse to_collect_cubes','store':'Arm_unloads_platform','aborted':'Debugging_State'})

        smach.StateMachine.add('Platform_moves_to_the_warehouse to_collect_cubes',
                            SimpleActionState('MovePlatform_action_server',MovePlatformAction,goal = MovePlatformGoal(position = "WH")),
                            transitions={'succeeded':'Arm_loads_platform','preempted':'abgestürzt','aborted':'Debugging_State'})   
        
        smach.StateMachine.add('Platform_moves_to_the_warehouse to_store_cubes',
                            SimpleActionState('MovePlatform_action_server',MovePlatformAction,goal = MovePlatformGoal(position = "WH")),
                            transitions={'succeeded':'Scan_platform_cubes','preempted':'abgestürzt','aborted':'Debugging_State'}) 

        smach.StateMachine.add('Platform_moves_to_the_station_to_deliver_cubes',
                            SimpleActionState('MovePlatform_action_server',MovePlatformAction,goal_cb = plattform_goal_callback,input_keys=["station"]),
                            transitions={'succeeded':'Waiting_for_user','preempted':'abgestürzt','aborted':'Debugging_State'})  

        smach.StateMachine.add('Platform_moves_to_the_station_to_collect_cubes',
                            SimpleActionState('MovePlatform_action_server',MovePlatformAction,goal_cb = plattform_goal_callback,input_keys=["station"]),
                            transitions={'succeeded':'Waiting_for_user','preempted':'abgestürzt','aborted':'Debugging_State'})  

        smach.StateMachine.add('Waiting_for_user', 
                            WaitForUserState(), 
                            transitions={'finishedUnloading':'User_input',"finishedLoading": "Platform_moves_to_the_warehouse to_store_cubes",'aborted':'Debugging_State'})

        smach.StateMachine.add('Arm_loads_platform',
                            SimpleActionState('MoveCubes_action_server',MoveCubesAction, goal_cb = arm_goal_callback,result_cb=moveCube_result_cb, input_keys=["fromSlotId","toSlotId","direction","cubesOnPlatform"]),
                            transitions={'succeeded':'Platform_moves_to_the_station_to_deliver_cubes','preempted':'abgestürzt','aborted':'Debugging_State'})   

        smach.StateMachine.add('Arm_unloads_platform',
                            SimpleActionState('MoveCubes_action_server',MoveCubesAction, goal_cb = arm_goal_callback,result_cb=moveCube_result_cb, input_keys=["fromSlotId","toSlotId","direction","cubesOnPlatform"]),
                            transitions={'succeeded':'User_input','preempted':'abgestürzt','aborted':'Debugging_State'})   

        smach.StateMachine.add('Scan_platform_cubes',
                            SimpleActionState('ScanPlatformCubes_action_server',ScanPlatformCubesAction, result_cb=scanPlatformCubes_result_cb,output_keys=["cubesOnPlatform"],input_keys=["cubesOnPlatform"]),
                            transitions={'succeeded':'Plan_cube_transfer','preempted':'abgestürzt','aborted':'Debugging_State'})   

        smach.StateMachine.add('Debugging_State',
                            DebuggingState(), 
                            transitions={"Initial_mapping":"Initial_mapping",'User_input':'User_input','Plan_cube_transfer':'Plan_cube_transfer',
                            'Platform_moves_to_the_warehouse to_collect_cubes':'Platform_moves_to_the_warehouse to_collect_cubes','Platform_moves_to_the_warehouse to_store_cubes':'Platform_moves_to_the_warehouse to_store_cubes',
                            'Platform_moves_to_the_station_to_deliver_cubes':'Platform_moves_to_the_station_to_deliver_cubes',
                            'Platform_moves_to_the_station_to_collect_cubes':'Platform_moves_to_the_station_to_collect_cubes','Waiting_for_user':'Waiting_for_user','Arm_loads_platform':'Arm_loads_platform',
                            'Arm_unloads_platform':'Arm_unloads_platform',"Scan_platform_cubes":"Scan_platform_cubes"})

        #sis = smach_ros.IntrospectionServer('Introspection_server', sm, '/SM_ROOT')
        #sis.start()
        
        while not rospy.is_shutdown():
            outcome = sm.execute()
        
        rospy.signal_shutdown('All done.')
        #rospy.spin()
        #sis.stop()

if __name__ == '__main__':
    main()