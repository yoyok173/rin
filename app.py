# -*- coding: cp1252 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import errno, os, sys, tempfile, urllib, json
import urllib.request
import requests

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get variables from your environment variable
channel_secret = os.getenv('8a8f9217823f873b65d23809c0f7b049', None)
channel_access_token = os.getenv('hy9nfmiUlxEdDvxSCFK+3OBfxiCIqPzzj0QPdj/5kQd5/2Fv3SsbrL8TWlfJG5pAIWOPg/jSaRvyekXU3gsLRs5BLHgCZEw1sHcTZoEy8yPrHBNwwe6J3GuM4Hl7JOWSZtrIvR7VC7a+GwP/k2sikAdB04t89/1O/w1cDnyilFU=', None)
owmapi = os.getenv('e172c2f3a3c620591582ab5242e0e6c4', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if owmapi is None:
    print('Specify OWEATHER_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

def jokes():
    jokesurl = 'http://api.icndb.com/jokes/random'
    req = urllib.request.urlopen(jokesurl)
    jokes = json.loads(req.read())
    content = jokes['value']['joke']
    return content

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == '/bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token, TextMessage(text="Bot can't leave from 1:1 chat"))
    if '/joke' and '/j' in text:
        content = jokes()
        line_bot_api.reply_message(
            event.reply_token, TextMessage(text=content))
    
    if '/ping' and '/p' in text:
        line_bot_api.reply_message(
            event.reply_token, TextMessage(text='pong!'))
    if '/help' and '/h' in text:
        content = 'Available commands:\n/joke - Get Chuck Norris jokes.\n/weather - Gets the current weather in a given location.\n/ping - Send ping command.'
        line_bot_api.reply_message(
            event.reply_token, TextMessage(text=content))
    if '/weather' and '/w' in text:
        try :
            location = text.split(' ')[1]
            weatherurl = 'http://api.openweathermap.org/data/2.5/weather?q=' + location + '&APPID=' + owmapi
            req = requests.get(weatherurl)
            cuacaraw = json.loads(req.text)
            cuacajson = json.dumps(cuacaraw)
            cuaca = json.loads(cuacajson)
            a = cuaca['weather'][0]['description']
            d = cuaca['name']
            e = cuaca['sys']['country']
            f = cuaca['main']['temp']
            g = f - 273
            h = "%.2f" % g + 'ºC'
            i = cuaca['main']['humidity']
            j = str(i)
            content = 'Weather in ' + d + ', ' + e + '\n' + a + ', ' + h + '\nHumidity ' + j + '%'
        except IndexError:
            content = 'Usage: /weather <location>'
        line_bot_api.reply_message(
            event.reply_token, TextMessage(text=content))

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Thank you for inviting me to this ' + event.source.type))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
