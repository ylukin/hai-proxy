#!/usr/bin/python3

import subprocess, re

def send_to_hai(cmd):
        """ send command to HAI panel, return stdout as file """

        cmd_output = subprocess.check_output([cmd], shell=True)
        return cmd_output.decode('utf-8').strip("\n")

def unit(unit_id, **kwargs):
	'''
	HAI unit command implementation:

	Format:	unit <unit> <command> <parms>

	Send command to unit. Command is on/off/dim/brighten/level/ramp
        unit <unit> <on|off|> [<time>]
        unit <unit> <dim|brighten> <step> [<time>]
        unit <unit> level <level> [<time>]
        unit <unit> ramp <level> [<time>]
	Step is 1 to 9. Level is 0 to 100. ALC ramp is to <level> over <time>.
        Time is #h, #m, or #s. (ex: 20m = 20 minutes)
        Time can be a duration user-setting (ex: unit 10 on user 7).
	'''

	if "on" in kwargs:
		cmd_output = send_to_hai("hai unit " + str(unit_id) + " on")
		return {"unit_id": unit_id, "is_on": True}
	elif "off" in kwargs:
		cmd_output = send_to_hai("hai unit " + str(unit_id) + " off")
		return {"unit_id": unit_id, "is_on": False}
	elif "level" in kwargs:
		if (int(kwargs["level"]) >= 0) and (int(kwargs["level"]) <= 100):
			cmd_output = send_to_hai("hai unit " + str(unit_id) + " level " + kwargs["level"])
			if int(kwargs["level"]) == 0:
				return {"unit_id": unit_id, "is_on": False, "brightness_level": kwargs["level"]}
			else:
				return {"unit_id": unit_id, "is_on": True, "brightness_level": kwargs["level"]}
		else:
			return {"error":"Valid brightness level is 0:100"}


def units(unit_id):
	'''
	HAI units command implementation:

	Format:	units [<start unit>] [<end unit>]

	Displays the status of a set of units.
	Default is all named. Specify 'all' to include unnamed.
	'''

	cmd_output = send_to_hai("hai units " + str(unit_id) + " " + str(unit_id))
	match = re.search('^\s*(\d+) :\s+([a-zA-Z0-9 ]+) : (\d\d\d).*', cmd_output)
	if match:
		if int(match.group(3)) == 000:
			return {"unit_id":int(match.group(1)), "name":match.group(2), "brightness_level":int(match.group(3)), "is_on": False}
		else:
			return {"unit_id":int(match.group(1)), "name":match.group(2), "brightness_level":int(match.group(3)), "is_on": True}
	return {"error": "Not Found"}

def zones(zone_id):
	'''
	HAI zones command implementation:

	Format:	zones [<start zone>] [<end zone>]

	Displays the status of a set of zones.
	Default is all named. Specify 'all' to include unnamed.
	'''

	cmd_output = send_to_hai("hai zones " + str(zone_id) + " " + str(zone_id))
	# match groups: [1: zone id, 2: zone name, 3: zone status, 4: latch status, 5: zone arm status]
	match = re.search('^\s*(\d+) :\s+([a-zA-Z0-9 ]+) : \d\d\d,\s+([a-zA-Z ]+),\s+([a-zA-Z ]+),\s+([a-zA-Z]+).*', cmd_output)
	if int(match.group(1)) == int(zone_id):
		return {"zone_id": int(match.group(1)), "name": match.group(2), "zone_status": match.group(3), "zone_latch_status": match.group(4), "zone_arm_status": match.group(5)}
	else:
		return {"error": "Not Found"}


def get_active_entities(type):
	'''
	Gets a list of all currently configured entities on the HAI system.
 	Supported entity types: units, zones
	'''

	active_entities = []
	cmd_dict = {'units': 'hai units', 'zones': 'hai zones'}

	if type not in cmd_dict:
		return active_entities

	cmd_output = send_to_hai(cmd_dict[type])
	for line in cmd_output.splitlines():
		match = re.search('^\s*(\d+).*', line, re.MULTILINE)
		active_entities.append(int(match.group(1)))
	return active_entities
