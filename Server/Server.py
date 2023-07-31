#!/usr/bin/env python3

# Import Necessary libraries
import socket # Provides interface for connections
from termcolor import colored # Terminal Colors for inform
import threading # Allows input polling while listening to port
import json # Handle JSON parsing
import os # File paths
import sys # System Operations
import time # Time management
import stopperService # Ping server to prevent server.tick() from clogging up stop operation

# Define data structures
info = []

# Start Server Startup Timer
starttime = time.time()

# Find path of commands.json
script_dir = os.path.dirname(os.path.abspath(__file__))
commands_path = os.path.join(script_dir, "commands.json")

# Server Class
class Server():
    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind(("0.0.0.0", port))
        except:
            exit()
        self.warntypes = [('red', '[CRITICAL] '), ('white', '[INFO] '), ('yellow', '[WARN] ')]
        self.running = True
        self.finishedStartup = False

    def inform(self, type, message):
        print(colored('\r' + self.warntypes[type][1] + message, self.warntypes[type][0]))

    def tick(self):
        while self.running:
            data, addr = self.server_socket.recvfrom(2048)
            received_data = data.decode()

            # Parse the received packet as JSON
            try:
                received_packet = json.loads(received_data)
            except json.JSONDecodeError:
                self.inform(2, "Invalid JSON packet from {}:{}".format(addr[0], addr[1]))

            # Check if the packet is present in packets.json
            with open('packets.json', 'r') as packets_file:
                packets_data = json.load(packets_file)

            if not received_packet['type'] == 'noreply':
                for packet in packets_data['packets']:
                    if packet['type'] == received_packet['type']:
                        response_packet = packet['response']
                        break
                else:
                    self.inform(2, "Invalid packet type from {}:{}".format(addr[0], addr[1]))
                    response_packet = packet["response"]

                # Send back the response packet
                self.server_socket.sendto(json.dumps(response_packet).encode(), addr)
            
    def parse(self, command):
        args = command.split()
        for cmd in data['commands']:
            if cmd['name'] == args[0]:
                args.pop(0)
                for line in cmd['script']:
                    exec(line)
                return

        # Command not found
        print("Command not found.")

    def get_command(self):
        while self.running:
            command = input()
            self.parse(command)
    
    def stop(self):
        self.inform(1, "Stopping Server...")
        self.running = False
        stopperService.stop()

# Init sequence
SERVER_PORT = 40624
SERVER_IP = socket.gethostbyname(socket.gethostname())
server = Server(SERVER_PORT)
server.inform(1, 'Server successfully launched on ' + str(SERVER_IP) + ':' + str(SERVER_PORT))

# Open commands.json
commandlist = open(commands_path, 'r')
data = json.load(commandlist)
commandlist.close()

# Threads
packetlistener_thread = threading.Thread(target=server.tick)
command_thread = threading.Thread(target=server.get_command)
packetlistener_thread.start()
command_thread.start()

# Complete startup sequence
server.finishedStartup = True
server.inform(1, "Complete! Elapsed Time: " + str(round(time.time()-starttime, 3)) + " seconds. For help, type \"/help\"")

# Main loop
#while server.running: