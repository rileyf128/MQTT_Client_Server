#!/usr/bin/env python3
# See https://docs.python.org/3.2/library/socket.html
# for a decscription of python socket and its parameters
import socket

from dataclasses import dataclass
from threading import Thread
from argparse import ArgumentParser

BUFSIZE = 4096 

class Subjects ():  
  def __init__(self, name: str, msg: str, childTopics: list, savedMsg: str, changed: int):
    self.name = name
    self.msg = msg
    self.childTopics = childTopics
    self.savedMsg = savedMsg
    self.changed = changed


WEATHER = Subjects("WEATHER", "", [], "", 0)
NEWS = Subjects("NEWS", "", [], "", 0)
HEALTH = Subjects("HEALTH", "", [], "", 0)
SECURITY = Subjects("SECURITY", "", [], "", 0)
  
Topics = [
  WEATHER,
  NEWS,
  HEALTH,
  SECURITY
]

def client_talk(client_sock, client_addr):
    print('talking to {}'.format(client_addr))
    data = client_sock.recv(BUFSIZE)
    client_sock.send(bytes("CONN_ACK", 'utf-8'))
    userSubs = []					#topics user is subscribed to
    subMsgs = dict()
    
    while data: 
      retVal = ""
      data = client_sock.recv(BUFSIZE)
      msg = data.decode('utf-8')
      print(msg) 
      
      if msg == "DISC":
        break
      
      command = msg.split(' ', 1)[0]
      if command == "SUB":
        topic = msg.split(' ', 2)[1]
        if "/" in topic:  
          subCat = topic.split('/')[1:]
          parent = topic.split('/', 1)[0]
          #print("topic: " + topic + "subCat: " + str(subCat) + "parent: " + parent)
          for i in range(topic.count("/")):
            newTopic = subCat[i]
            if "#" in newTopic: 			#SUB for use in #
              #print()
              if i == topic.count("/") - 1 and newTopic[0] == "#": #Error detection for  	
                subbed = []					#SUB for use in #
                for i in Topics:    	         
                  if i.name == parent:
                    parentTop = i
                  for k in i.childTopics: 
                    if k.name not in subbed:
                      subbed.insert(0, k.name)
                      listedSub(k.name, userSubs, subMsgs)
                      if subMsgs.get(k) != None:
                        retVal += subMsgs[k]
       
              else:
                retVal = "ERROR: INCORRECT USE OF #" 
                break            
            
            elif "+" in newTopic: 			#SUB for use in + 
               if "+" == subCat[0]: 
                 listedSub(parent, userSubs, subMsgs)
                  
               else: 
                 newSub = parent
                 for i in range(topic.count("/") - 1): 
                   newSub += "/" + subCat[i]
                 listedSub(newSub, userSubs, subMsgs)

            for i in subMsgs:   
              if subMsgs.get(i) != None:  
                retVal += subMsgs[i] 
            else: 							#SUB if / exists w/o # or +
              subscribe(topic, userSubs, subMsgs)
              if subMsgs.get(topic) != None:
                retVal = subMsgs[topic]
             
        else: 						#Sub for when no /, +, or # 
          topic = msg.split(' ', 1)[1]
          subscribe(topic, userSubs, subMsgs)
          if subMsgs.get(topic) != None:
            retVal = subMsgs[topic]
        retVal += "SUCCESS"
      elif command == "PUB":
        retain = 0
        topic = msg.split(' ', 2)[1]
        if "RETAIN" in msg:
          retain = 1
          info = str(msg.split(' ', 3)[3:])
        else: 
          info = str(msg.split(' ', 2)[2:])
        
        if "/" in topic: 
          new = 0
          parent = topic.split('/', 1)[0]
          childTop = (parent)
          for i in Topics:    		#For loop to find topic in topicList 
            if i.name == parent:
              parentTop = i
              new = 1
          if new != 1: 
            parentTop = publish(parent, "", 0)    
          subCat = topic.split('/')
          for i in range(topic.count("/")): #Iterates through input based on # of /'s
            childTop += "/" + str(subCat[i + 1])
            print("Child top is: " + childTop)
            if i == topic.count("/") - 1:
              cat = publish(childTop, info , retain)
             
            else:  
              cat = publish(childTop, "" , retain)
            parentTop.childTopics.insert(0, cat)
            parentTop = cat
          
        else:                                   #If no / in
          val = publish(topic, info, retain) 
        
        retVal = "SUCCESS"
        
      elif command == "UNSUBSCRIBE": #maybe need to account for user 
        topic = msg.split(' ', 1)[1]
        userSubs.remove(topic)
        del subMsgs[topic]
        retVal = "SUCCESS"
      
      elif command == "LIST":
        if userSubs is None: 
           retVal = "ERROR"
        
        else: 
          length = str(len(userSubs))
          for i in userSubs:
            length = length + ", " + str(i) 
          retVal = length
    
      else: 
        retVal = "COMMAND NOT RECOGNIZED"
      
      
      print(str(retVal))
      #subTopics = subMsgs.keys()
      #msgs = subMsgs.values()
      
      for key in subMsgs:    		#For loop to find topic in topicList 
        #print(" topic is: " + subTopic + " msg is: " + msg )
        for i in Topics:
          if i.name == key: 
            if subMsgs.get(i.name) != i.savedMsg and i.savedMsg != None:
              if subMsgs.get(i.name) != i.savedMsg:
                subMsgs[key] = i.savedMsg
                retVal += "\nUPDATE: " + key + " topic has been updated: " + i.savedMsg
         
      client_sock.send(bytes(retVal, 'utf-8'))
        
    # clean up
    client_sock.send(bytes("DISC_ACK", 'utf-8'))
    client_sock.shutdown(1)
    client_sock.close()
    print('connection closed.')

def publish (topic, msg, retain):
  newTop = 0 
  for i in Topics:
    if i.name == topic: 
      i.msg += str(msg)
      newTop = 1
      if retain == 1: 
        i.savedMsg = str(msg)
        i.changed = 1
      return i
     
  if newTop != 1:
    newTopic = Subjects(topic, str(msg), [], "", 0)
    Topics.insert(0, newTopic)
    
    if retain == 1: 
      newTopic.savedMsg = str(msg)
      
  return newTopic
  
def subscribe (topic, userSubs, subMsgs):		
  for i in Topics:
    if i.name == topic:
      if topic not in userSubs:
        userSubs.insert(0, topic)
      if subMsgs.get(i.name) == None:
        subMsgs[i.name] = i.savedMsg
        #print("New is :" + str(new))
      return "SUCCESS"
            
def listedSub (parent, userSubs, subMsgs): 	#Helper function for SUB +/#
  for i in Topics:
    if i.name == parent:  
      for j in i.childTopics: 
        if j.childTopics != None: 
          subscribe(j.name, userSubs, subMsgs)
        else: 
          subscribe(j.name, userSubs, subMsgs)
  return 


   
class EchoServer:
  def __init__(self, host, port):
    print("Server")
    print('listening on port {}'.format(port))
    self.host = host
    self.port = port

    self.setup_socket()

    self.accept()

    self.sock.shutdown()
    self.sock.close()

  def setup_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.bind((self.host, self.port))
    self.sock.listen(128)

  def accept(self):
    while True:
      (client, address) = self.sock.accept()
      th = Thread(target=client_talk, args=(client, address))
      th.start()
      
def parse_args():
  parser = ArgumentParser()
  parser.add_argument('--host', type=str, default='localhost',
                      help='specify a host to operate on (default: localhost)')
  parser.add_argument('-p', '--port', type=int, default=9001,
                      help='specify a port to operate on (default: 9001)')
  args = parser.parse_args()
  return (args.host, args.port)


if __name__ == '__main__':
  (host, port) = parse_args()
  EchoServer(host, port)

