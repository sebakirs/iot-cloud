#!/usr/bin/python

#-------------------------------------------------------------------------------
# Import required libarys
from threading import Lock
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, Namespace, emit, disconnect
import datetime
from time import gmtime, strftime
import json

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

# Create falsk app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Create socket
socketio = SocketIO(app, async_mode=async_mode)

#------------------------------------------------------------------------------
# Init variables for datastream background task
datastream_thread = None
datastream_thread_lock = Lock()
datastream_update_rate = .1

# Init variables for server-time background task
global time_thread
time_thread = None
time_thread_lock = Lock()

#-------------------------------------------------------------------------------
# Background task to update server-time
def server_time():
    while True:
        server_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        socketio.sleep(1)
        return(server_time)

# Start background task for server-time
with time_thread_lock:
        if time_thread is None:
            time_thread = socketio.start_background_task(target=server_time)

#-------------------------------------------------------------------------------
# Background task to stream data to ccu
def datastream():
    while True:
        # Read data from database.json
        database_json = open('/home/pi/database/database.json', "r") # Open the JSON file for reading
        database = json.load(database_json) # Read the JSON into the buffer
        database_json.close() # Close the JSON file

        # Send data from IoT Cloud to ccu
        socketio.emit('response', database, namespace='/data')

        # Wait for some time
        socketio.sleep(datastream_update_rate)

#-------------------------------------------------------------------------------
# Tell console about start of server
print server_time(), "- IoTCloud: Starting Websocket-Server..."

connected_js = {
'time': server_time(),
'text': "IoTCloud: Connection accomplished"
}

datastream_js = {
'time': server_time(),
'text': "IoTCloud: Datastream activated"
}

#-------------------------------------------------------------------------------
@app.route('/')
def handle_request():
    return 'This is the Websocket-Server of the IoTCloud'

#-------------------------------------------------------------------------------
# Event if ccu connected to namespace '/data'
@socketio.on('connect', namespace='/status')
def handle_connect():
    emit('connect', connected_js)
    #print('IoTCloud: CCU connected', request.sid)

# Event if ccu connected to namespace '/data'
@socketio.on('connect', namespace='/data')
def handle_connect():
    emit('connect', datastream_js)
    global datastream_thread
    with datastream_thread_lock:
        if datastream_thread is None:
            datastream_thread = socketio.start_background_task(target=datastream)

# Event if ccu connected to namespace '/data'
@socketio.on('message')
def handle_message(message):
    emit('message', '- IoTCloud: Message received')
    emit('message', 'namespace test', namespace='/data')
    print server_time(), message['text']

# Event for case that client disconnected from server
@socketio.on('disconnect')
def handle_disconnect():
    print server_time(), '- IoTCloud: CCU disconnected'#, request.sid)

#------------------------------------------------------------------------------
# Start application server
# '0.0.0.0': listen to external requests
# 5000: listen to port 5000
# ebug: activate console debugging

if __name__ == '__main__':
    socketio.run(app, '0.0.0.0', 8000)#, debug=True)
