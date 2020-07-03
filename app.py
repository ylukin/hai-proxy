from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, make_response, abort, request
from time import strftime

import hai_api
import logging
import traceback

app = Flask(__name__)

units = []
zones = []

@app.route('/api/light/<int:id>', methods=['GET'])
def light_get_status(id):
	# check if light is in the list of currently active units
	if id not in units:
		abort(404)
	# return light status
	response = hai_api.units(id)
	return make_response(response, 202)

@app.route('/api/light/<int:id>', methods=['PUT'])
def light_update_state(id):
	# check if light is in the list of currently active units
	if id not in units:
		abort(404)

	response = ''
	req = request.get_json()

	# check for JSON request
	if not req:
		abort(400)

	# check if on/off command is present
	if 'is_on' in req and type(req['is_on']) is bool:
		if req['is_on']:
			# if on command and brightness, dim the light according to level specified
			if 'brightness_level' in req and type(req['brightness_level']) is int:
				response = hai_api.unit(id, level=str(req['brightness_level']))
				return make_response(response, 202)
			# else turn the light on to full level
			response = hai_api.unit(id, on='100')
			return make_response(response, 202)
		else:
			# turn the light off
			response = hai_api.unit(id, off='0')
			return make_response(response, 202)
	# dim the light to brightness level
	if 'brightness_level' in req and type(req['brightness_level']) is int:
		response = hai_api.unit(id, level=str(req['brightness_level']))
		return make_response(response, 202)

@app.route('/api/zone/<int:id>', methods=['GET'])
def zone_get_status(id):
	# check if zone is in the list of currently active zones
	if id not in zones:
		abort(404)
	# return zone status
	response = hai_api.zones(id)
	return make_response(response, 202)

# Error handling routines
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.after_request
def after_request(response):
	""" Logging after every request. """
	# This avoids the duplication of registry in the log,
	# since that 500 is already logged via @app.errorhandler.
	if response.status_code != 500:
		ts = strftime('[%Y-%b-%d %H:%M]')
		logger.error('%s %s %s %s %s %s',
			      ts,
			      request.remote_addr,
			      request.method,
			      request.scheme,
			      request.full_path,
			      response.status)
	return response

@app.errorhandler(Exception)
def exceptions(e):
	""" Logging after every Exception. """
	ts = strftime('[%Y-%b-%d %H:%M]')
	tb = traceback.format_exc()
	logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
		      ts,
		      request.remote_addr,
		      request.method,
		      request.scheme,
		      request.full_path,
		      tb)
	return "Internal Server Error", 500

if __name__ == '__main__':
	# setup logging
	handler = RotatingFileHandler('/var/log/hai-proxy/app.log', maxBytes=1000000, backupCount=10)
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.ERROR)
	logger.addHandler(handler)

	# get list of configured units and zones in the system
	units = hai_api.get_active_entities("units")
	zones = hai_api.get_active_entities("zones")

	# run the API
	app.run(host = '0.0.0.0', port = 7881, threaded=True)
