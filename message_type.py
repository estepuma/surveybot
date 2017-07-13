import requests
import json
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
cache = dict()

def add_attachment_to_question(recipient_id, fb_data):
    logging.debug("*** Cache: %s ***", str(cache))

    if str(recipient_id) in cache:
        if fb_data['type'] == 'image':
            size_cache = len(cache[recipient_id])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "image"
            cache[recipient_id][str(size_cache)]["attachment"]["url"] = fb_data['payload']['url']

            next_question = size_cache + 1
            cache[recipient_id][str(next_question)] = {"question":"none", "type":"none", "attachment":{"type":"none"}}
            message = 'Write your question #' +  str(next_question)  + ' and send ...'
            return normal_message(recipient_id, message)
        elif fb_data['type'] == 'audio':
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "audio"
            cache[recipient_id][str(size_cache)]["attachment"]["url"] = fb_data['payload']['url']
        elif fb_data['type'] == 'video':
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "video"
            cache[recipient_id][str(size_cache)]["attachment"]["url"] = fb_data['payload']['url']
        elif fb_data['type'] == 'file':
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "file"
            cache[recipient_id][str(size_cache)]["attachment"]["url"] = fb_data['payload']['url']
        elif fb_data['type'] == 'location':
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["attachment"]["type"] = "location"
            cache[recipient_id][str(size_cache)]["attachment"]["coordinates"]["lat"] = fb_data['payload']['coordinates']['lat']
            cache[recipient_id][str(size_cache)]["attachment"]["coordinates"]["long"] = fb_data['payload']['coordinates']['long']

    logging.debug("*** Cache: %s ***", str(cache))


def send_message(recipient_id, message_string):

    params = {
        "access_token": "EAAMqqmvE4FYBAJTZBJVZCVkwWCEMybOzEuVQtLwbP2PxYLP6v3XUFi1ZAgEHx6vr2fwmQZAL7YZBrXTZCrPkdeoGA8ub9JhZBh0SHG3cIg6vZChpRzMSo3cyrsvLpE72uDIS9sMnza4rT3pIG6wCmGMEns4ObFRnt5PnCZA1ZA4B3oqAZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response_data = json.loads(message_string)
    data = json.dumps(response_data)

    logging.debug("*** Cache: %s ***", str(cache))

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        logging.debug(r.status_code)
        logging.debug(r.text)


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
            return normal_message(recipient_id, message)

        elif 'free_answer' == fb_data['message']['quick_reply']['payload']: #Config a free answer question
            size_cache = len(cache[str(recipient_id)])
            cache[recipient_id][str(size_cache)]["type"] = "free_answer"
            #cache[recipient_id][str(size_cache + 1)] = {"question":"none", "type":"none", "attachment":"none"}
            message = 'Add image or video or tap -No- button to continue'
            return add_files(recipient_id, message)
            # return add_type_question(recipient_id, message, "free_answer", size_cache)

        elif 'yes_no' == fb_data['message']['quick_reply']['payload']:
            # size_cache = len(cache[str(recipient_id)])
            # logging.debug("cache size ++++++++ %s", str(size_cache));
            # cache[recipient_id][str(size_cache)]["type"] = "yes_no"
            # cache[recipient_id][str(size_cache + 1)] = {"question":"none", "type":"none"}
            message = 'Add an image/video or tap No if you want to continue'
            return normal_message(recipient_id, message)
            # return add_type_question(recipient_id, message, "yes_no", size_cache)

        elif 'satisfaction_levels' == fb_data['message']['quick_reply']['payload']:
            message = 'satisfaction level'
            return normal_message(recipient_id, message)

        elif 'no_attachments' == fb_data['message']['quick_reply']['payload']:
            if str(recipient_id) in cache:
                size_cache = len(cache[recipient_id])
                cache[recipient_id][str(size_cache + 1)] = {"question":"none", "type":"none", "attachment":{"type":"none"}}
                message = 'Write your question #' +  str(size_cache + 1)  + ' and send ...'
                return normal_message(recipient_id, message)


    elif 'attachments' in fb_data["message"]:
        if fb_data["message"]['attachments'][0]['type'] == 'location':
            response_data['message']['text'] = 'Your location: lat ' + str(fb_data["message"]['attachments'][0]['payload']['coordinates']['lat']) + ' and long ' + str(fb_data["message"]['attachments'][0]['payload']['coordinates']['long'])
    elif cache.get(recipient_id):
        message = fb_data['message']['text']
        size_cache = len(cache[recipient_id])
        logging.debug("cache size +++++++ %s", str(size_cache))
        cache[recipient_id][str(size_cache)] = {"question":message, "type":"none", "attachment":{"type":"none"}}
        #normal_message(recipient_id, message)

        return next_question(recipient_id, "What type of response you expect?")
    else:
        message = "I don't understand you";
        return normal_message(recipient_id, message)




def add_type_question(recipient_id, message, type_question, size_cache):
    logging.debug("cache size ++++++++ %s", str(size_cache));
    cache[recipient_id][str(size_cache)]["type"] = type_question
    #cache[recipient_id][str(size_cache + 1)] = {"question":"none", "type":"none"}
    #return normal_message(recipient_id, message)
    return add_files(recipient_id, message)

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

def add_files(recipient_id, text):
    add_files = """{
      "recipient":{
        "id":"%s"
      },
      "message":{
        "text":"%s",
        "quick_replies":[
            {
              "content_type":"text",
              "title":"No",
              "payload":"no_attachments"
            }]
      }
    }"""
    return add_files % (recipient_id, text)
