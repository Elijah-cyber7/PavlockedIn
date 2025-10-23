#PavlockedIn 

This project is built around openCV and mediaPipe. The current push-up detection algorithm goes based on the angle of the arm 
and has some tolorance zones. There are currently two modes that you can run this scrip in, endurance (go until failure) and timed (do x amount in the specified time window)


#The way it works:

OpenCV detects push-ups, if the failure criteria is met (not recovering from the down position within 2.5 seconds) then it sends a command via web socket to an ESP32 with a relay and boost converter. Once the ESP32 recieves the command it switches the relay to a HIGH state for .25 of a second. This then activates the taser (boost converter) and gives the user some encourgement to recover from the down position. 
