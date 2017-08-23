import requests
import json
import logging
import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.survey
users = db.users

cache_answers = dict()

def show_survey(recipient_id):
    params = {
        "access_token": "EAAMqqmvE4FYBAJTZBJVZCVkwWCEMybOzEuVQtLwbP2PxYLP6v3XUFi1ZAgEHx6vr2fwmQZAL7YZBrXTZCrPkdeoGA8ub9JhZBh0SHG3cIg6vZChpRzMSo3cyrsvLpE72uDIS9sMnza4rT3pIG6wCmGMEns4ObFRnt5PnCZA1ZA4B3oqAZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response_data = json.loads(normal_message_test(recipient_id, 'This is a test'))
    data = json.dumps(response_data)

    logging.debug("**** Displaying survey")

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        logging.debug(r.status_code)
        logging.debug(r.text)

def get_questions(recipient_id, survey_id):
    logging.debug('*********** get questions')
    for doc in users.find({'recipient_id':recipient_id, 'surveys':{"$elemMatch":{'survey_id':survey_id}}}):
        logging.debug('\n*** Questions ***')
        logging.debug('Survey:%s', doc)
        for survey in doc['surveys']:
            if survey['survey_id'] == survey_id:
                for question in survey['questions']:
                    print('** question: ', question)

def normal_message_test(recipient_id, text):
    greet = """{
    	"recipient": {
    		"id": %s
    	},
        "message": {
    		"text": "%s"
    	}
    }"""
    return greet % (recipient_id, text)


get_questions(str(1182512435167240), 'XBvMbZBzXmAqm')
