import requests
import json
import logging
import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.survey
questions = db.questions

cache_answers = dict()

def show_question(recipient_id, response_data_text):
    params = {
        "access_token": "EAAMqqmvE4FYBAJTZBJVZCVkwWCEMybOzEuVQtLwbP2PxYLP6v3XUFi1ZAgEHx6vr2fwmQZAL7YZBrXTZCrPkdeoGA8ub9JhZBh0SHG3cIg6vZChpRzMSo3cyrsvLpE72uDIS9sMnza4rT3pIG6wCmGMEns4ObFRnt5PnCZA1ZA4B3oqAZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response_data = json.loads(response_data_text)
    data = json.dumps(response_data)

    logging.debug("**** Displaying survey")

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        logging.debug(r.status_code)
        logging.debug(r.text)


def display_question(recipient_id):
    logging.debug("********* Entra a display question, con recipient_id:%s", recipient_id)
    if str(recipient_id) in cache_answers:
        logging.debug('In cache answer')
        for question in cache_answers[recipient_id]['questions']:
            logging.debug('In questions')
            #Verify if question has an answer
            if 'answer' not in question or question['answer'] == None or question['answer'] == '' :
                logging.debug('No answer')
                if question['type'] == 'free_answer':
                    question_text = ''
                    image_msg = ''
                    logging.debug('**** Free question ****')
                    if question['attachment']['url'] or question['attachment']['url'] != None:
                        question_text = free_answer_template(recipient_id, question['question'])
                        show_question(recipient_id, question_text)
                        image_msg = free_answer_template(recipient_id, question['question'], True, question['attachment']['type'], question['attachment']['url'])
                        show_question(recipient_id, image_msg)
                    else:
                        question_text = free_answer_template(recipient_id, question['question'])
                    logging.debug('Question text: %s', question_text);
                    #show_question(recipient_id, question_text)
                    break
                    #return free_answer_template(reciepient_id, question['question'])

#Returns the questions and the attachment
def free_answer_template(recipient_id, question, has_attachment = False, type_attachment = None, url = None):
    question = question + ' (type your answer and send)'
    free_question = """ """

    if has_attachment:
        logging.debug('With attachment')
        free_question = """{
        	"recipient": {
        		"id": %s
        	},
            "message": {
                "attachment":{
                    "type":"%s",
                    "payload":{
                    "url":"%s"
                    }
                }
        	}
        }"""
        free_question = free_question % (recipient_id, type_attachment, url)
    else:
        logging.debug('Without attachment')
        free_question = """{
        	"recipient": {
        		"id": %s
        	},
            "message": {
        		"text": "%s"
        	}
        }"""
        free_question = free_question % (recipient_id, question)

    return free_question

#Get the questions from DB and put in cache
def get_questions(recipient_id, survey_creator_id, survey_id):
    logging.debug('*********** get questions, recipient_id_creator:%s', recipient_id_creator)

    if str(recipient_id) in cache_answers:
        logging.debug("** recipient_id in cache_answer")
        display_question(recipient_id)
    else:
        logging.debug("** creating recipient_id in cache_answer")
        cache_answers[str(recipient_id)] = {survey_id: None}

        #Get user from database
        for doc in questions.find_one({'recipient_id':survey_creator_id, 'survey_creator_id':survey_creator_id, 'survey_id':survey_id }):
            logging.debug('\n*** Questions ***')
            logging.debug('Survey:%s', doc)
            #Get all surveys
            cache_answers[recipient_id]['questions'] = quests
            for question in cache_answers[recipient_id]['questions']:
                logging.debug('** question: %s', question)

            display_question(recipient_id)


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


#get_questions(str(1182512435167240), 'XBvMbZBzXmAqm')
