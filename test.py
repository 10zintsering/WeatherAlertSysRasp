#Importing libraries
import requests
import json
import sys,traceback
import time
import RPi.GPIO as GPIO
import gc

#Set up Country ID 
CountryID = '102000000' #Hamburg

#Set up input/ output GPIO pins
GREEN = 20
RED = 16
BUTTON = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN, GPIO.OUT)  # Green LED
GPIO.setup(RED, GPIO.OUT)  # Red LED
GPIO.setup(BUTTON, GPIO.IN,  pull_up_down= GPIO.PUD_DOWN) #Button PIN

#Refresh interval : note that this program itself takes about 50 secs to run once, therefore for 10mins 
refresh = 0

#address of the server and dummy header
url = "https://www.dwd.de/DWD/warnungen/warnapp_landkreise/json/warnings.json"
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'}

#empty string for storing the warning message
description1= ''
description2= ''

#keeping the led off at the beginning 
GPIO.output(GREEN, GPIO.LOW)
GPIO.output(RED, GPIO.LOW)

def key_exists(foo, key): #Function for checking CountryID in warning dictionary
	"""
	foo -> dictionary
	key -> lookup key
	Return foo if key exists in foo. Otherwise, return None
	"""
	return 'yes' if key in foo else None

try:
	while(True):
    		response = requests.get(url, headers=header)

		response_json_string = response.text.split("(", 1)[1].strip(");") # conversion from jsonp to json

		response_json_python = json.loads(response_json_string)

   		if response_json_python['warnings']:	#if warning  exist for any states
        		if key_exists(response_json_python['warnings'],CountryID):  #if warning exist for CountryID
				print("There is warning for Hamburg: turn on red LED")
				description1 = response_json_python['warnings'][CountryID][0]['description']
				description2 = response_json_python['warnings'][CountryID][1]['description']
				GPIO.output(RED, GPIO.HIGH)
        		else:
            			print("There is no warning: Turn on green led") #when there are warnings among states  but not for CountryID
				GPIO.output(RED, GPIO.LOW)
				GPIO.output(GREEN, GPIO.HIGH)
    		else:
        		print("There is no warning: turn on green led")    #when warning doesn't exist 
			GPIO.output(RED, GPIO.LOW)
			GPIO.output(GREEN, GPIO.HIGH)
    
    		time.sleep(refresh)
except KeyboardInterrupt: 
	print("Shutdown requested...exiting")
	GPIO.cleanup()
	gc.collect() # clean the memory allocated for global variables
except Exception:
	traceback.print_exc(file=sys.stdout)
	sys.exit(0)
    
