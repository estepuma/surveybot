import requests
import json
import logging
import pymongo
from pymongo import MongoClient
from pymemcache.client.base import Client


def json_serializer(key, value):
     if type(value) == str:
         return value, 1
     return json.dumps(value), 2

def json_deserializer(key, value, flags):
    if flags == 1:
        return value
    if flags == 2:
        return json.loads(value)
    raise Exception("Unknown serialization format")

mem_cache_answer = Client(('localhost', 11211), serializer=json_serializer,
                deserializer=json_deserializer)

#Mongo connection
client = MongoClient('localhost', 27017)
db = client.survey
questions = db.questions

#cache_answers = dict()

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
    cache_answers = get_from_cache_answer(recipient_id)
    if cache_answers:
        logging.debug('In cache answer: %s', cache_answers)
        for question in cache_answers['questions']:
            logging.debug('In questions:%s', question)
            #Verify if question has an answer
            if 'answer' not in question or question['answer'] == None or question['answer'] == '' :
                logging.debug('No answer')
                if question['type'] == 'free_answer':
                    question_text = ''
                    image_msg = ''
                    logging.debug('**** Free question ****')
                    if 'url' in question['attachment']:
                        question_text = free_answer_template(recipient_id, question['question'])
                        show_question(recipient_id, question_text)
                        image_msg = free_answer_template(recipient_id, question['question'], True, question['attachment']['type'], question['attachment']['url'])
                        show_question(recipient_id, image_msg)
                    else:
                        question_text = free_answer_template(recipient_id, question['question'])
                        logging.debug('Question text: %s', question_text);
                        show_question(recipient_id, question_text)
                    break
                elif question['type'] == 'yes_no':
                    question_text = ''
                    image_msg = ''
                    logging.debug('**** yes/no question ****')
                    if 'url' in question['attachment']:
                        question_text = yes_no_template(recipient_id, question['question'])
                        show_question(recipient_id, question_text)
                        image_msg = yes_no_template(recipient_id, question['question'], True, question['attachment']['type'], question['attachment']['url'])
                        show_question(recipient_id, image_msg)
                    else:
                        question_text = yes_no_template(recipient_id, question['question'])
                        logging.debug('Question yes/no: %s', question_text);
                        show_question(recipient_id, question_text)
                    break
                    #return free_answer_template(reciepient_id, question['question'])

                elif question['type'] == 'satisfaction_level':
                    question_text = ''
                    image_msg = ''
                    logging.debug('**** satisfaction level ****')
                    if 'url' in question['attachment']:
                        question_text = satisfaction_level_template(recipient_id, question['question'], question['levels']['level'], question['levels']['best'])
                        show_question(recipient_id, question_text)
                        image_msg = satisfaction_level_template(recipient_id, question['question'], question['levels']['level'], question['levels']['best'], True, question['attachment']['type'], question['attachment']['url'])
                        show_question(recipient_id, image_msg)
                    else:
                        question_text = satisfaction_level_template(recipient_id, question['question'], question['levels']['level'], question['levels']['best'])
                        logging.debug('Question yes/no: %s', question_text);
                        show_question(recipient_id, question_text)
                    break


#Get the questions from DB and put in cache
def get_questions(recipient_id, survey_creator_id, survey_id):
    logging.debug('*********** get questions, recipient_id: %s, survey_creator_id:%s, survey_id:%s', recipient_id, survey_creator_id, survey_id)
    cache_answers = get_from_cache_answer(recipient_id)
    if cache_answers:
        logging.debug("** recipient_id in cache_answer")
        display_question(recipient_id)
    else:
        logging.debug("** creating recipient_id in cache_answer")
        logging.debug("cache_answer:%s", cache_answers)
        #cache_answers[str(recipient_id)] = dict()

        #Get user from database
        for doc in questions.find({'recipient_id':str(survey_creator_id), 'survey_id':survey_id }, projection={'_id': False, 'time':False}):
        #for doc in questions.find():
            print(doc)
            logging.debug('\n*** Questions ***')
            logging.debug('Survey:%s', doc)
            #Get all surveys

            #cache_answers[str(recipient_id)] = doc
            set_to_memcached_answer(recipient_id, doc)
            #for question in cache_answers[str(recipient_id)]['questions']:
                #logging.debug('** question: %s', question)

            display_question(recipient_id)

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

def yes_no_template(recipient_id, question, has_attachment = False, type_attachment = None, url = None):
    question = question + ' (Select one option)'
    yes_no_question = """ """

    if has_attachment:
        logging.debug('With attachment in yes/no')
        yes_no_question = """{
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
        yes_no_question = yes_no_question % (recipient_id, type_attachment, url)
    else:
        logging.debug('Without attachment in yes/no')
        yes_no_question = """{
          "recipient":{
            "id":"%s"
          },
          "message":{
            "text":"%s",
            "quick_replies":[
              {
                "content_type":"text",
                "title":"Yes",
                "payload":"yes_answer"
              },
              {
                "content_type":"text",
                "title":"No",
                "payload":"no_answer"
              }]
          }
        }"""
        yes_no_question = yes_no_question % (recipient_id, question)

    return yes_no_question

def satisfaction_level_template(recipient_id, question, level = 5, best = 1, has_attachment = False, type_attachment = None, url = None):
    question = question + ' (Select one option)'
    satisfaction_level_question = """ """

    if has_attachment:
        logging.debug('With attachment in yes/no')
        satisfaction_level_question = """{
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
        satisfaction_level_question = satisfaction_level_question % (recipient_id, type_attachment, url)
    else:
        logging.debug('Without attachment in yes/no')
        satisfaction_level_question = """{
          "recipient":{
            "id":"%s"
          },
          "message":{
            "text":"%s",
            "quick_replies":[%s]}}"""

        botton_level = ""
        happy = u'\U0001F642'
        sad = u'\U0001F61F'
        for i in range(1, level+1):
            if best == i:
                botton_level = botton_level + '{"content_type":"text","title":"' + str(i) + happy + '","payload":"level_' + str(i) + '"},'
            elif ((level - best) + 1) == i:
                botton_level = botton_level + '{"content_type":"text","title":"' + str(i) + sad + '","payload":"level_' + str(i) + '"},'
            else:
                botton_level = botton_level + '{"content_type":"text","title":"' + str(i) + '","payload":"level_' + str(i) + '"},'


        botton_level = botton_level[:-1]  # remove the last character
        satisfaction_level_question = satisfaction_level_question % (recipient_id, question, botton_level)

        # satisfaction_level_question = """{
        #   "recipient":{
        #     "id":"%s"
        #   },
        #   "message":{
        #     "text":"%s",
        #     "quick_replies":[
        #         {
        #           "content_type":"text",
        #           "title":"1",
        #           "payload":"level_1"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"2",
        #           "payload":"level_2"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"3",
        #           "payload":"level_3"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"4",
        #           "payload":"level_4"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"5",
        #           "payload":"level_5"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"6",
        #           "payload":"level_6"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"7",
        #           "payload":"level_7"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"8",
        #           "payload":"level_8"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"9",
        #           "payload":"level_9"
        #         },
        #         {
        #           "content_type":"text",
        #           "title":"10",
        #           "payload":"level_10"
        #         }]
        #   }
        # }"""
        # satisfaction_level_question = satisfaction_level_question % (recipient_id, question)

    print '** level question:', satisfaction_level_question

    return satisfaction_level_question

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

#Ge value from mem_cache with prefix survey_
def get_from_cache_answer (recipient_id):
    cache = mem_cache_answer.get('answer_' + recipient_id)

    return cache;

#Set value to memcached with prefix survey_
def set_to_memcached_answer (recipient_id, cache):
    mem_cache_answer.set('answer_' + recipient_id, cache, 172800)

#Eliminates user from local cache
def eliminates_user_from_cache_answer (recipient_id):
    mem_cache_answer.delete(recipient_id)

#get_questions(str(1182512435167240), 'XBvMbZBzXmAqm')
