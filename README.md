### What is the SMACH library?🧐

SMACH is a Python library for creating and managing state machines in the Robot Operating System (ROS) environment. It allows you to define a state machine that represents the behavior of your robot, ensuring the robot performs the desired actions in the correct sequence. SMACH is useful for creating complex robot behaviors and controlling robots in dynamic environments. 

### Why did I upload this project? 
I participated in a university project which goal it was to have a robot to drive autonomously to a warehouse, then receive items from a loader robot and drive back to the commissioning station. My job was to orchestrate the whole process and enable the communication between the different robots and find solutions with the other teams that implemented the functions for the robots. My teammate and I decided quite early that we would love to use SMACH to work with ActionStates.  It was our first time working with ROS and SMACH, and the documentation on the official http://wiki.ros.org/smach was sometimes hard to follow. That is why I uploaded this project, in hope it will help others in understating the mechanisms and syntax of SMACH faster that we did.😄  

You can go ahead and directly dive into the code: https://github.com/Adrian-Winter/ROS-SMACH-Statemachine/tree/main/scripts
or have a look at our german documentation for this project: 


**Global State Machine Doku**

Die globale Statemachine ist dafür zuständig, die von dem Arm und der Platform zur verfügung gestellten Fuktionen in der richtigen Reinfolge aufzurufen, die Schnittstellen zu definieren und die User Schnittstelle bereit zu stellen. Für die implementierung wurde mit der SMACH Library realisiert. SMACH ist eine Statemachine Library die für ROS optimiert ist. 

Sobald die Statemachine initialisiert wurde, wird userdata erstellt welche genutzt werden kann um Daten zwischen den States zu übertragen und zwischenzuspeichern. Damit ein State auf die userdata zugreifen kann, muss diese als "input_key" deklariet werden um diese zu lesene, bzw. als "output_key" um diese zu modifizieren. Es ist sinnvoll, dass jeder State nur die Variablen lesen und ändern kann die auch wirklich gebraucht werden um möglichlich Fehler zu vermeiden. 

Wenn ein State fertig ist sendet er ein "outcome" welches darüber entscheidet welcher State als nächstes aufgerufen werden soll. Die Outcomes können frei gewählt werden. Die SMACH Library bietet einen Action-State, welcher dafür optimiert ist Actions in ROS zu verwalten. Diese Action-States haben die festgesetzten outcomes "succeeded", "aborted" und "preemted". ROS Actions Server können goals als input akzeptieren und result als outputs liefern welche genutzt werden können um Daten mit dem Client, in diesem Falle die Statemachine auszutauschen. 

Das folgende Diagramm visualisiert wie die Statemachine userdata benutzt und die übergänge der States festgelegt sind je nach outcome. Die Action States kommunizieren mit den Action Servern, hier als Roter Kasten dargestellt. Nur das "succeded" outcome wird im Diagramm dargestellt. Wenn das outcome "aborted" ist, fällt die Statemachine in einen eigens implementierten Debugging State von dem aus userdata geändert werden kann und neue States gestartet werden können. 

![](https://)![](https://writemd.rz.tuhh.de/uploads/86a4e3b4-7e4a-40ef-8298-e16585d6c8fd.png)

Eine vereinfachte Visualisung der Statemachine ist im folgendem Diagramm dargestellt. Hier wird einem übersichtlich zusammengefasst, welche States welche funktion erfüllen ohne zu sehr ins Detail einzugehen. 


![](https://writemd.rz.tuhh.de/uploads/d085fce7-c8b4-4bee-beee-99bcb72a9ff2.png)




**Lagermanagement**

Das lager_magement Package dient dazu die Position und Art von Würfeln im Lager dauerhaft zu speichern und für andere Packages die notwendigen Interaktionsmöglichkeiten bereit zu stellen. Dazu zählt das Abrufen und Speichern von Daten, aber auch das suchen nach leeren Lager Slots, sowie das Finden von eingelagerten Würfeln. 
Die Interaktion ist über vier Services mit eigenen Nachrichtformaten realisiert, da diese so lange „Blocken“, bis die Informationen verfügbar sind. Dies ist notwendig, da die Client Nodes auf die Verfügbarkeit der Daten angewiesen sind. 
Die Services sind in dem Package custom_messages definiert, um diese zentral verwalten zu können. 
Die im Lager_mangement gespeichert daten sind in folgender Tabelle aufgelistet:

![](https://writemd.rz.tuhh.de/uploads/e3fdeb19-5f8b-43e2-96d8-a30170d185ec.png)

Die bereitgestellten Services sind folgende:

•	find_cubes

•	find_empty_slots

•	Lager_set

•	Lager_get



Lager GUI

Weiterhin befindet sich ein Skript im Paket lager_management, welches manuell gestartet werden kann und ein Userinterface bereitstellt, mit dem sich jegliche gespeicherten Daten manuell ändern lassen. Dies ermöglich bei der Inbetriebnahme einfach Änderungen vorzunehmen oder auch ein Lager mit bestimmten Inhalten zu Initialisieren, falls dieses vor dem Start bereits Würfel beinhaltet. 



**Custom Messages**


Für eine sinnvolle Nutzung von Services und Actions, werden Definitionen von eigenen Nachrichtformaten benötigt. 
Das Package custom_messages hat keine eigene Funktionalität bzw. ausführbaren Code. Es beinhaltet die speziell definierten Service und Action Nachrichten. So können die Nachrichten zentral verwaltet werden und sind unabhängig von den Paket in denen sie benutzt werden. 

## Feedback 
* Please feel free to let me know if you have trouble getting the results you are looking for. 
* Also what features could be added? 

### Hope this little device made your project a little bit easier! ☺️
