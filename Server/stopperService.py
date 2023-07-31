#!/usr/bin/env python3

# Import Necessary Modules
import socket # Communicate with server

# Create stopper function
def stop():
    fsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("localhost", 40624)
    packet_data = "{\"type\": \"noreply\", \"src\": \"stopperService\"}"
    fsocket.sendto(packet_data.encode(), server_address)
    fsocket.close()