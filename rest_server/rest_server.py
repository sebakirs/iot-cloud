#!/usr/bin/python
# Import required libarys
from flask import Flask, jsonify, abort, request, make_response, url_for, json

# Import GPIO libary
import RPi.GPIO as GPIO

# set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)

# Declare name of programmed app for function handling
app = Flask(__name__, static_url_path = "")

# Error handling in case of bad or wrong requests
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/vehicle/modes', methods = ['GET'])
def get_modes():
    return jsonify( { 'modes': modes} )

#-------------------------------------------------------------------------------
@app.route('/vehicle/modes/<int:mode_id>', methods = ['GET'])
def get_mode(mode_id):
    # Read file
    jsonFile = open('/home/pi/database/database.json', "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    # Read data
    #mode = filter(lambda t: t['id'] == mode_id, modes)
    #if len(mode) == 0:
        #abort(404)e
    return jsonify(data) #data[{ 'mode': mode[0] }]

#-------------------------------------------------------------------------------
@app.route('/vehicle/modes/<int:mode_id>', methods = ['PUT'])
def update_mode(mode_id):
    jsonFile = open("/home/pi/database/database.json", "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    # Read mode with mode_id from loaded data
    mode = filter(lambda t: t['id'] == mode_id, data)
    # Modify desired mode with data from "PUT"
    mode[0]['status'] = request.json.get('status', mode[0]['status'])

    ## Save our changes to JSON file
    jsonFile = open("/home/pi/database/database.json", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

    # Response "PUT" with the updated data
    return jsonify( { 'task': mode[0] } )


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port='5000')

#if mode[1]['status'] == 'False':
GPIO.output(18,HIGH)
