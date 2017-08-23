import requests
import json
import logging
from pymongo import MongoClient
from datetime import datetime
from hashids import Hashids

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
cache = dict()

client = MongoClient('localhost', 27017)
db = client.survey
users = db.users

def add_attachment_to_question(recipient_id, fb_data):
    logging.debug("*** Cache: %s ***", str(cache))

    if str(recipient_id) in cache:
        if fb_data['type'] == 'image':
            return attachment_file(recipient_id, fb_data, 'image')

        elif fb_data['type'] == 'audio':
            return attachment_file(recipient_id, fb_data, 'audio')

        elif fb_data['type'] == 'video':
            return attachment_file(recipient_id, fb_data, 'video')

        elif fb_data['type'] == 'file':
            return attachment_file(recipient_id, fb_data, 'file')

        elif fb_data['type'] == 'location':
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "location"
            cache[recipient_id][str(size_cache)]["attachment"]["coordinates"] = {"lat": fb_data['payload']['coordinates']['lat'], "long":fb_data['payload']['coordinates']['long']}
            message = 'Add another question or finish the survey'
            return add_finish(recipient_id, message)

    logging.debug("*** Cache: %s ***", str(cache))

def attachment_file(recipient_id, fb_data, type_of_file):
    size_cache = len(cache[str(recipient_id)])
    cache[recipient_id][str(size_cache)]["attachment"]["type"] = type_of_file
    cache[recipient_id][str(size_cache)]["attachment"]["url"] = fb_data['payload']['url']
    message = 'Add another question or finish the survey'
    return add_finish(recipient_id, message)

def send_message(recipient_id, message_string):

    params = {
        "access_token": "EAAMqqmvE4FYBAGNVfR53ZAZC0QZAfSLeTXQIUMDGreTbIv61IcfB10fjvJkSkcT75E44vZBpkLVmoFAlwESEHFjC7lYk41a4MwzqZAMHqZAKqKGCuXhZAIgZC0sBFKh0wOX5NXpswZB1XJaIbJmzvzuDwcWmrHKZCBVfgE8CaC6mZBxEAZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response_data = json.loads(message_string)
    data = json.dumps(response_data)
    logging.debug("*** Cache: %s ***", str(cache))

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        logging.debug("response status code: %s", r.status_code)
        logging.debug("response message: %s", r.text)


def type_of_message(recipient_id, fb_data):
    message = ''

    if 'text' in fb_data['message']:
        message = fb_data['message']['text']
    if message.lower() == 'hi' or message.lower() == 'hello' or message.lower() == 'hola':
        message = "Hi, lets to create the new survey!! Click the button below to start";
        return start(recipient_id, message)
    elif 'quick_reply' in fb_data["message"]:

        #Init creating the first question
        if 'init_questions' == fb_data['message']['quick_reply']['payload']: #Initialize the first question
            message = 'Write your question #1 and send ...'
            #Init cache of recipient_id
            cache[recipient_id] = {"1":dict()}

            #insert_data(cache)
            return normal_message(recipient_id, message)

        elif 'free_answer' == fb_data['message']['quick_reply']['payload']: #Config a free answer question
            return set_question_type(recipient_id, 'free_answer')

        elif 'yes_no' == fb_data['message']['quick_reply']['payload']:
            return set_question_type(recipient_id, 'yes_no')

        elif 'satisfaction_levels' == fb_data['message']['quick_reply']['payload']:
            return set_question_type(recipient_id, 'satisfaction_level')
            # return set_satisfaction_leves(recipient_id)

        elif 'another_question' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                size_cache = len(cache[recipient_id])
                cache[recipient_id][str(size_cache + 1)] = {"question":"none", "type":"none", "attachment":{"type":"none"}}
                message = 'Write your question #' +  str(size_cache + 1)  + ' and send ...'
                return normal_message(recipient_id, message)

        elif 'level_5' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 5)

        elif 'level_6' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 6)

        elif 'level_7' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 7)

        elif 'level_8' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 8)

        elif 'level_9' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 9)


        elif 'level_10' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                return set_level(recipient_id, 10)

        elif 'less_value' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                size_cache = len(cache[str(recipient_id)])
                cache[recipient_id][str(size_cache)]["levels"]["best"] = 1
                message = 'Add image/video/audio to the question or select one option below'
                return add_finish(recipient_id, message)

        elif 'best_value' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                size_cache = len(cache[str(recipient_id)])
                cache[recipient_id][str(size_cache)]["levels"]["best"] = cache[recipient_id][str(size_cache)]["levels"]["level"]
                message = 'Add image/video/audio to the question or select one option below'
                return add_finish(recipient_id, message)

        elif 'finish' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                insert_data(recipient_id, cache[recipient_id])
                eliminates_user_from_cache(recipient_id)  #Eliminates cache
                return finish_webview(recipient_id)


    elif 'attachments' in fb_data["message"]:
        if fb_data["message"]['attachments'][0]['type'] == 'location':
            response_data['message']['text'] = 'Your location: lat ' + str(fb_data["message"]['attachments'][0]['payload']['coordinates']['lat']) + ' and long ' + str(fb_data["message"]['attachments'][0]['payload']['coordinates']['long'])
    elif cache.get(recipient_id):
        message = fb_data['message']['text']
        size_cache = len(cache[recipient_id])
        cache[recipient_id][str(size_cache)] = {"question":message, "type":"none", "attachment":{"type":"none"}}
        #normal_message(recipient_id, message)

        return next_question(recipient_id, "What type of response you expect?")
    else:
        message = "I don't understand you";
        return normal_message(recipient_id, message)


def set_question_type(recipient_id, question_type):
    size_cache = len(cache[str(recipient_id)])
    cache[recipient_id][str(size_cache)]["type"] = question_type
    if question_type == 'satisfaction_level':
        return satisfaction_levels(recipient_id, 'How many levels of satisfaction you want ?')
    else:
        message = 'Add one image/video/audio/location to the question or select one option below'
        return add_finish(recipient_id, message)


def set_level(recipient_id, level):
    size_cache = len(cache[str(recipient_id)])
    cache[recipient_id][str(size_cache)]["levels"] = {"level":level, "best":"none"}
    message = 'What is the best score?'
    return best_score(recipient_id, message, level)


def finish_webview(recipient_id, survey_id, questions):
    webview = """
        {
      "recipient":{
        "id":%s
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            "text":"What do you want to do next?",
            "buttons":[
              {
                "type":"element_share",
                "share_contents": {
                  "attachment": {
                    "type": "template",
                    "payload": {
                      "template_type": "generic",
                      "elements": [
                        {
                          "title": "I took Peter's 'Which Hat Are You?' Quiz",
                          "subtitle": "m.me functionality",
                          "image_url": "http://louisville.k12.ms.us/survey/Survey1.jpg",
                          "default_action": {
                            "type": "web_url",
                            "url": "https://m.me/witaidemo?ref=343434"
                          },
                          "buttons": [
                            {
                              "type": "web_url",
                              "url": "https://m.me/witaidemo?ref=343434",
                              "title": "Init"
                            }
                          ]
                        }
                      ]
                    }
                  }
                }
              }
            ]
          }
        }
      }
    }
    """
    return webview % (recipient_id)

def normal_message(recipient_id, text):
    greet = """{
    	"recipient": {
    		"id": %s
    	},
        "message": {
    		"text": "%s"
    	}
    }"""
    return greet % (recipient_id, text)

def start(recipient_id, text):
    start = """{
      "recipient":{
        "id":"%s"
      },
      "message":{
        "text":"%s",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Start",
            "payload":"init_questions"
          }]
      }
    }"""
    return start % (recipient_id, text)

def next_question(recipient_id, text):
    type_of_questions = """{
      "recipient":{
        "id":"%s"
      },
      "message":{
        "text":"%s",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Free Answer",
            "payload":"free_answer"
          },
          {
            "content_type":"text",
            "title":"Satisfaction levels",
            "payload":"satisfaction_levels"
          },
          {
            "content_type":"text",
            "title":"yes/no",
            "payload":"yes_no"
          }]
      }
    }"""
    return type_of_questions % (recipient_id, text)

def add_finish(recipient_id, text):
    add_finish = """{
      "recipient":{
        "id":"%s"
      },
      "message":{
        "text":"%s",
        "quick_replies":[
            {
              "content_type":"text",
              "title":"Add another Question",
              "payload":"another_question"
            },
            {
              "content_type":"text",
              "title":"Finish",
              "payload":"finish"
            }]
      }
    }"""
    return add_finish % (recipient_id, text)

def best_score(recipient_id, text, maximum):
    best_score = """{
        "recipient":{
          "id":"%s"
        },
        "message":{
          "text":"%s",
          "quick_replies":[
              {
                "content_type":"text",
                "title":"1",
                "payload":"less_value"
              },
              {
                "content_type":"text",
                "title":"%s",
                "payload":"best_value"
              }]
        }
    }"""

    return best_score % (recipient_id, text, maximum)

def satisfaction_levels(recipient_id, text):
    add_finish = """{
      "recipient":{
        "id":"%s"
      },
      "message":{
        "text":"%s",
        "quick_replies":[
            {
              "content_type":"text",
              "title":"5",
              "payload":"level_5"
            },
            {
              "content_type":"text",
              "title":"6",
              "payload":"level_6"
            },
            {
              "content_type":"text",
              "title":"7",
              "payload":"level_7"
            },
            {
              "content_type":"text",
              "title":"8",
              "payload":"level_8"
            },
            {
              "content_type":"text",
              "title":"9",
              "payload":"level_9"
            },
            {
              "content_type":"text",
              "title":"10",
              "payload":"level_10"
            }]
      }
    }"""
    return add_finish % (recipient_id, text)

#Eliminates user from local cache
def eliminates_user_from_cache(recipient_id):
    del cache[recipient_id]

#Insert data in mongo DB
def insert_data(recipient_id, dict_data):
    logging.debug("\n*** Insert data in DB ***")
    logging.debug("DATA: %s ", dict_data)
    logging.debug("Recipient_id: %s ", recipient_id)
    size_cache = len(dict_data)

    #Generating the id for the survey
    hashids = Hashids(salt = recipient_id)
    now = datetime.utcnow()
    hashid = hashids.encode(long(now.strftime('%Y%m%d%H%M%S%f')))
    survey = {'survey_id': hashid, 'time':now, 'questions':[]}

    # Pushing every question in the array
    for number in range(1, size_cache + 1):
        question = dict_data[str(number)]
        question['order'] = number
        survey['questions'].append(question)

    logging.debug("SURVEY: %s ***", survey)
    logging.debug("\n")

    users.find_one_and_update({'recipient_id': recipient_id}, {"$push": {'surveys':survey}}, upsert=True)
