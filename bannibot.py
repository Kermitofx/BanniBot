import json
import requests
import time
import urllib.parse
import datetime
import os
import random

TOKEN = os.environ.get('956323132:AAHJXDVL3jMmZrsYvcEG_wlxoJ2Fxz1C8tw')
APPNAME = os.environ.get('heradrobot')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        url = self.api_url + "getUpdates"
        url += "?timeout={}".format(timeout)
        if offset:
            url += "&offset={}".format(offset)
        #print(url)
        # get url
        resp = requests.get(url)
        # get json from url
        content = resp.content.decode("utf8")
        js = json.loads(content)
        # res = resp.json()["result"]
        return js

    def send_message(self, text, chat_id):
        #params = {'chat_id': chat_id, 'text': text}
        #method = 'sendMessage'
        #resp = requests.post(self.api_url + method, params)
        text = urllib.parse.quote_plus(text)
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        resp = requests.post(url)
        return resp
   
    def send_sticker(self, sticker_id, chat_id):
        url = self.api_url + 'sendSticker'
        url += '?chat_id={}'.format(chat_id)
        url += '&sticker={}'.format(sticker_id)
        resp = requests.post(url)
        return resp  

    def get_last_update(self):
        get_result = self.get_updates()        
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]
        return last_update

    def get_name(self, update):
        if update["message"]["chat"]["type"]=="group":
            name = update["message"]['from']['first_name']
            # NB 'language_code' and 'last_name' are also sometimes
            # arguments under ['from'] but not always
        else:
            name = update["message"]["chat"]['first_name']
        return name
        
    def is_fedro(self, update):
        res = False        
        if update['message']['chat']['type']=='group':
            if update['message']['chat']['title']=='Il mito di Fedro':
                res = True
        return res
   
    def is_sticker(self, update):
        res = True
        try:
            temp = update['message']['sticker']
        except KeyError as err:
            res = False
        return res

    def send_image(self, image_name, chat_id, caption=None):
         url = self.api_url + 'sendPhoto' 
         url += '?chat_id={}'.format(chat_id)
         if caption is not None:
             url += ('&caption=' + caption) 
         files = {'photo': open('./media/images/'+image_name, 'rb')}
         #data = {'chat_id' : chat_id}
         r = requests.post(url, files=files)
         print(r.status_code, r.reason, r.content)
    
def get_next_update_id(updates):
    num = len(updates['result'])
    if num == 0:
        next_up = None
    else: 
        next_up = int(updates["result"][num-1]["update_id"]) + 1
#    update_ids = []
#    for update in updates["result"]:
#        update_ids.append(int(update["update_id"]))
#    if len(update_ids)==0:
#        last = 0
#    else:
#        last = max(update_ids)
    return next_up

# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------

def main():
    group_perm = True # permissive to send message to groups

    # some settings and initialization
    greetings = ('hello', 'hi', 'greetings', 'ciao')
    wished = []
    launch_min = datetime.datetime.now().minute
    next_update_id = None
    f = open('./media/dante_comedia.txt')
    comedia_lines = f.readlines()

    # create the bot
    banni = Bot(TOKEN)

    #reset updates received while not online
    updates = banni.get_updates(next_update_id)
    next_update_id = get_next_update_id(updates)

    while True:
        now = datetime.datetime.now()
        today = now.day
        hour = now.hour
        updates = banni.get_updates(next_update_id)

        if len(updates["result"]) > 0:
            next_update_id = get_next_update_id(updates)
            flag_greet = 0

            for update in updates["result"]:

                chat = update["message"]["chat"]["id"]
                name = banni.get_name(update)
             
                # action based on the calendar day only ------------------------------------------------
                if now.day == 1 and now.month == 1:
                    if not (name in wished):
                        wished.append(name)
                        send_text = 'Un anno più vicini eh?'
                        banni.send_message(send_text, chat)
                        # waving death
                        banni.send_sticker('CAADAgADuwUAAvoLtggGKjKfVlb_hAI', chat)
                        continue
                elif now.day == 25 and now.month == 12:
                    if not (name in wished):
                        wished.append(name)
                        send_text = 'Felice Natale ' + name + '!'
                        banni.send_message(send_text, chat)
                        if not (chat in wished):
                            wished.append(chat)
                            send_text_2 = 'https://www.youtube.com/watch?v=3nx7_G5R0oA'
                            banni.send_message(send_text_2, chat)
                        # Merkel drinking
                        banni.send_sticker('CAADAgAD0QUAAvoLtgjYyEx1T51U2wI', chat)
                        # do this only and do it once
                        continue
                elif now.day == 31 and now.month == 12:
                    if not (name in wished):
                        wished.append(name)
                        send_text = 'Buona fine e miglior inizio ' + name + '!'
                        wished.append(chat)
                        banni.send_message(send_text, chat)
                        # Merkel cheering with beer
                        banni.send_sticker('CAADAgADgwADOQ-GA9ZTbnrjNkZDAg', chat)
                        continue
                else:
                    # if it's any other day cancel the 'wished' list
                    wished = []
                
                # if the message wasn't a sticker ------------------------------------------------------
                if not banni.is_sticker(update):
                    text = update['message']['text']
                    if any([greet in text.lower() for greet in greetings]):
                        if today == now.day and 6 <= hour < 9:
                            send_text = '{} il buongiorno si vede dal mattino'.format(name)
                            flag_greet = 1
                        elif today == now.day and 12 <= hour < 17:
                            send_text = 'Buon pomeriggio bello'.format(name)
                            flag_greet = 1
                        elif today == now.day and 18 <= hour < 23:
                            send_text = 'Buonasera caro {}'.format(name)
                            flag_greet = 1
                        # else:
                            # echo last message
                            # send_text = text
                        if flag_greet:
                            if (not update["message"]["chat"]["type"]=="group") or group_perm:
                                banni.send_message(send_text, chat)
                    
                    if 'birra' in text.lower():
                        banni.send_message('Chi invita Angelona?', chat)
                        banni.send_sticker('CAADAgADhQADOQ-GAyBWCYCoan7eAg', chat)

                    if 'marx' in text.lower():
                        banni.send_sticker('CAADBAADMgADyIsGAAGw4osRBXRB3AI', chat)
                    
                    if 'general' in text.lower() and 'electric' in text.lower() or 'GE' in text:
                        banni.send_image('GE_Red.png', chat, 'I love that company!')
                 
                    poetry = ('poem','poetry','poesia')
                    if any([x in text.lower() for x in poetry]):
                        i = random.randint(1, 19688)
                        while comedia_lines[i]=='\n' or comedia_lines[i+1]=='\n' or comedia_lines[i+2]=='\n':
                            i += 1
                        banni.send_message('Learn, this is real poetry...', chat)
                        banni.send_message(comedia_lines[i], chat)
                        banni.send_message(comedia_lines[i+1], chat)
                        banni.send_message(comedia_lines[i+2], chat)

        # before looking for the next update
        # time.sleep(0.5)
        # every 15 min wake up the app (otherwise heroku puts it to sleep)
        now_min = datetime.datetime.now().minute
        if (now_min-launch_min)%10==0:
            print("Pinging")
            requests.get('https://'+APPNAME+'.herokuapp.com')

if __name__ == '__main__':
    main()
