Name: Riley Frieburg
Student ID: 5452034
Email: frieb240@umn.edu

To build and run the program navigate to the directory they are in. “python3 EchoServer.py” in one terminal, “python3 EchoClient.py” in another terminal. From there it should run as expected, all commands are the same as in the programming project document and must be capitalized. 
EX: 
SUB <TOPIC> 
PUB <TOPIC> RETAIN <INFO>
DISC
UNSUBSCRIBE <TOPIC> 
LIST

In order to handle the commands all the work is done within EchoServer. It receives the message from the client and then checks for commands in the message. If none are found an “INVALID COMMAND” is sent through the socket to the client. After finding a topic it then moves through a series of conditional statements in order to find the correct command. It is relatively simple for unsubscribe and list. Unsubscribe removes the specified topic from an array that contains the users subscriptions. For LIST it checks if users subscriptions array is empty, if not it returns the length of the list as well as the contents. If it is empty it sends an error message through the socket to the client. For PUB, it checks if there is a “/” in the command. If there is, it splits the topic and publishes each. If there is no “/” it simply publishes the request. For SUB it checks for “/’ once again. If there are “/”, a series of conditionals checks for “+” and “#”. When the user enters DISC it waits for the response of DISC_ACK to fully disconnect. When connecting, CONN and CONN_AKC are exchanged between client and server. 

