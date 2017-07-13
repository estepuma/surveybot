import os
import sys

from bottle import route, run, request, response
from message_type import send_message, add_attachment_to_question, type_of_message

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

@route('/webhook', method='GET')
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    logging.debug(request.GET.get("hub.verify_token"))
    logging.debug(request.GET.get("hub.challenge"))
    if request.GET.get("hub.mode") == "subscribe" and request.GET.get("hub.challenge"):
        if not request.GET.get("hub.verify_token") == "myToken123":
            response.status = 403
            return "Verification token mismatch"

        response.status = 200
        return request.GET.get("hub.challenge")

    return "Hello world", 200


@route('/webhook', method='POST')
def webhook():

    # endpoint for processing incoming messaging events

    data = request.json
    logging.debug(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    if messaging_event["message"].get("attachments"):
                        for messaging_attachment in messaging_event["message"].get("attachments"):
                            logging.debug("*** JSON attachment: %s ***", str(messaging_attachment))
                            message_string = add_attachment_to_question(sender_id, messaging_attachment)
                            if (message_string and message_string != ''):
                                send_message(sender_id, message_string)
                    else:
                        message_string = type_of_message(sender_id, messaging_event)
                        if (message_string and message_string != ''):
                            send_message(sender_id, message_string)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

                if messaging_event.get("referral") and messaging_event["referral"]["source"] == "MESSENGER_CODE":
                    data = messaging_event["referral"]["ref"]
                    sender_id = messaging_event["sender"]["id"]

                    send_message(sender_id, "you has sent a messenger code with data: " + data)

    response.status = 200
    return



run(host='localhost', port=8089)