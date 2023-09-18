import requests
import json
import datetime
import time
import yaml

from datetime import datetime
from configparser import ConfigParser

print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')

try:
	config = ConfigParser()
	config.read('config.ini')

	nasa_api_key = config.get('nasa', 'api_key')
	nasa_api_url = config.get('nasa', 'api_url')
except:
	print('ERROR')
print('DONE')

# Getting todays date and formating it into a suitable format
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))

# Requesting the data from NASA using the API key and URL for today
print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

# Printing descriptive info about request
print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

# Only contining if the status code response is successful
if r.status_code == 200:

	# Parsing the request data as JSON
	json_data = json.loads(r.text)

	# Defining lists for safe and hazardous asteroids
	ast_safe = []
	ast_hazardous = []

	# Checking if the JSON data contains the 'element_count' key and getting the total count of asteroids
	if 'element_count' in json_data:
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))

		# Checking if the asteroid count today is more than 0
		if ast_count > 0:

			# Iterating through the JSON data to find all near Earth objects today
			for val in json_data['near_earth_objects'][request_date]:

				# Checking if the data about an asteroid contains the necessary information
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:

					# Creating temporary variables for the asteroid name and NASA JPL URL
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']

					# Checking if the estimated diameter is expressed in kilometers
					if 'kilometers' in val['estimated_diameter']:

						# Checking if the data about an asteroid has an minimum and maximum estimated diameter
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:

							# Creating temporary variables for the min and max diameter and rounds the values to 3 decimal places
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)

						# If the check of the asteroid minimum and maximum failed, assigns the temporary diameter values -2
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2

					# If the check if the asteroid diameter is in kilometeres failed, assigns the temporary diameter values -1
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1

					# Creating a temporary variable for the flag of a hazardous asteroid
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']

					# Checking if there is any data about a close approach from the asteroid 
					if len(val['close_approach_data']) > 0:

						# Checking if the data about a close approach from the asteroid contains the necessary information
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:

							# Creating temporary variables for the date and time of the close aproach
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')

							# Checking if the relative velocity of the asteroid is in km/h
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:

								# Creating temporary variable for the asteroid velocity
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))

							# If the check if the velocity is in km/h failed, assigning temporary velocity variable value -1
							else:
								tmp_ast_speed = -1

							# Checking if the miss distance is in kilometers
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:

								# Creating temporary variable for the miss distance
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)

							# If the check if the miss distance is in kilometers failed, assigning temporary miss distance variable value -1
							else:
								tmp_ast_miss_dist = -1

						# If the check if the data about a close approach from the asteroid contains the necessary information failed, assigning temporary date and time variables values -1
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"

					# If the check if there is any data about a close approach from the asteroid failed, assigning temporary variables error values
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1

					# Prints the data about each asteroid
					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")

					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])

		# If the check if the asteroid count today is more than 0 failed, prints out appropriate message
		else:
			print("No asteroids are going to hit earth today")

	# Printing the amounts of hazardous and safe asteroids
	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))

	# Checking if there were any hazardous asteroids
	if len(ast_hazardous) > 0:

		# Sorts the hazardous asteroids by their time of closest approach
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)

		# Prints all asteroid approaches and their respective times today in the sorted order
		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))

		# Sorts the hazardous asteroids by their closest passing distance
		ast_hazardous.sort(key = lambda x: x[8], reverse=False)

		# Prints the closest passing  asteroid and it's approach time
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))

	# If the check if there were any hazardous asteroids failed, prints appropriate message
	else:
		print("No asteroids close passing earth today")

# If the response from API was not successful, prints error message
else:
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
