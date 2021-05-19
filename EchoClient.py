#!/usr/bin/env python3

import socket
from argparse import ArgumentParser

BUFSIZE = 4096

class EchoClient:
  def __init__(self, host, port):
    print('Client')
    print('connecting to port {}'.format(port))
    self.host = host
    self.port = port

    self.setup_socket()

    self.talk()
    
    
    data = self.sock.recv(BUFSIZE)
    print('connection closed.')
    self.sock.shutdown(1)
    self.sock.close()
    

  def setup_socket(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((self.host, self.port))
    #self.sock.setblocking(False)
    self.sock.send(bytes("CONN", 'utf-8'))
    data = self.sock.recv(BUFSIZE)
    print(data.decode('utf-8'))
  
  def talk(self):
    msg = input('')
    self.sock.send(bytes(msg, 'utf-8'))
    data = self.sock.recv(BUFSIZE)
    while True:
      print(data.decode('utf-8'))
      msg = input('')
      if msg == "": 
        self.sock.send(bytes("next", 'utf-8'))
      else:
        self.sock.send(bytes(msg, 'utf-8'))  
      data = self.sock.recv(BUFSIZE)
     
      if data == "DISC_ACK": 
        self.sock.send(bytes("DISC", 'utf-8'))
        break
      
           
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
  EchoClient(host, port)

