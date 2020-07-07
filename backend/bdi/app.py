import agentspeak
import agentspeak.runtime
import agentspeak.stdlib

import os

import json
from flask import Flask
from flask import request, jsonify
from flask import Response
import logger


app = Flask(__name__)

actions = agentspeak.Actions(agentspeak.stdlib.actions)

api_url = "http://localhost:5000"

businessHours = [None]*7
businessHours[0] = {'start': '13:00', 'end': '19:00'}
businessHours[1] = {'start': '09:00', 'end': '19:00'}
businessHours[2] = {'start': '09:00', 'end': '19:00'}
businessHours[3] = {'start': '09:00', 'end': '19:00'}
businessHours[4] = {'start': '09:00', 'end': '21:00'}
businessHours[5] = {'start': '09:00', 'end': '22:00'}
businessHours[6] = {'start': None, 'end': None}

professional = {}
professional['hairstylist'] = ["David", "Diego", "Thiago"]
professional['manicure'] = ["Monica", "Juliana"]
professional['barber'] = ["William", "Guilherme"]
professional['epilator'] = ["Sara"]
professional['eyebrowstylist'] = ["Juliana", "Thais"]


@actions.add_function(".process_request", (str, ))
def process_request(request):
    return

@actions.add_function(".process_dialogflow_result", (str))
def process_dialogflow_result(response):
    return

@actions.add_function(".reply_to_bot", (str, ))
def reply_to_bot(message):
    return

@actions.add_function(".schedule_appointment", (str, str, str, str, ))
def schedule_appointment(customer_name, professional_name, service_name, date_time):
    return True


@actions.add_function(".check_agenda", (str, ))
def check_agenda(professional_name):
    return 


@actions.add_function(".check_business_hours", ( ))
def check_business_hours():
    return


@actions.add_function(".request_from_dialogflow", ( ))
def request_from_dialogflow():
    return


@actions.add_function(".request_to_dialogflow", ( ))
def request_to_dialogflow():
    return

@actions.add_function(".check_professionals_by_service", (str, ))
def check_professionals_by_service(service_name):
    result = ''
    if (service_name == 'cabelo' or service_name == 'progressiva'):
        for person in professional['hairstylist']:
            result +=person + "|"
    elif (service_name == 'mao' or service_name == 'pe'):
        for person in professional['manicure']:
            result += person + "|"
    elif (service_name == 'barba' or service_name == 'bigode'):
        for person in professional['barber']:
            result += person + "|"
    elif (service_name == 'depilar' or service_name == 'depilacao'):
        for person in professional['epilator']:
            result += person + "|"
    elif (service_name == 'sombrancelha' or service_name == 'sobrancelha'):
        for person in professional['eyebrowstylist']:
            result += person + "|"
    result = result[:-1]
    return result




# Sample action
@actions.add_function(".custom_action", (int, ))
def custom_action(x):
    return x ** 2

env = agentspeak.runtime.Environment()

with open(os.path.join(os.path.dirname(__file__), "jaycie.asl")) as source:
    agent = env.build_agent(source, actions)

if __name__ == "__main__":
    env.run_agent(agent)
    # Backend Flask app
    # app.run(host='0.0.0.0', port='5003', debug=True)
