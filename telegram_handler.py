import aiohttp.client_exceptions
import ujson
import aiohttp
import time
import config
from random import randint
import asyncio
import logging
import os



# this class gets updates from telegram api and sorts the data. most of the methods are self-explanatory. most of them
# needs an object of get_all() (mostly called 'data') in order to return the value


class Bot(object):

    def __init__(self, token):
        self.token = token
        self.link = f'https://api.telegram.org/bot{self.token}'
        self.session = aiohttp.ClientSession()
        self.watchlist = {}

    async def get_all(self):
        async with self.session.get(f'{self.link}/getUpdates') as response:
            return await response.json()
        
# defining the function that would look up for updates and put it in a queue. every message that bot receives gets
# logged. when this function receives a message - it checks for spamming. if spam returns true - it will start up a
# process that would handle the message.
        
    async def loop_void(self, queue, data_resolver):
        while True:
            try:
                data = await self.get_all()
                offset = self.get_id(data) + 1
                await self.log_saver(str(self.get_name(data)), str(self.get_from_id(data)), str(self.get_message(data)),
                                    self.get_chat_type(data), self.get_chat_id(data), self.get_username_or_first_name(data))
                # if spam.checker(bot.get_chat_id(data)):
                await queue.put(data)
                await self.session.get(self.link + '/getUpdates?offset=' + str(offset))
                await data_resolver(queue, admin=True)
                # elif not spam.checker(bot.get_chat_id(data)):
                #     requests.get(bot.link + '/getUpdates?offset=' + str(offset))
            except (IndexError, KeyError, TypeError):
                pass
            except (aiohttp.client_exceptions.ClientOSError, aiohttp.client_exceptions.ServerDisconnectedError) as e:
                await asyncio.sleep(3 + randint(0, 9))
    
    async def dummy_data(self, data):
        return {"ok":True,"result":
               [{"update_id":893056107,
                "message":
                    {"message_id":3597,
                     "from":
                     {"id":data,
                      "is_bot":False,
                      "first_name":"decaf",
                      "username":"omegapoggers",
                      "language_code":"en"},
                      "chat":
                      {"id":data,
                       "first_name":"decaf",
                       "username":"omegapoggers",
                       "type":"private"},
                       "date":1745357411,
                       "text":"/alert",
                       "entities":
                       [{"offset":0,
                         "length":6,
                         "type":"bot_command"}
                         ]
                    }
                }
            ]
            }

    # Logging method
    @staticmethod
    async def log_saver(name, uid, message, ctype, cid, uname):
        if os.path.exists('./logs/general.log'):
            pass
        else:
            os.mkdir('./logs')
            logging.basicConfig(filename=f'{os.path.dirname(os.path.abspath(__file__))}/../logs/general.log', level=logging.INFO,
                                format='%(asctime)s:%(message)s')
            logging.info('TYPE {}-{} BY @{}-{}, ID {} : {}'.format(ctype, cid, uname, name, uid, message))

    # Spam protection method
    def checker(self, uid):
        if uid in self.watchlist:
            if int(time.time())-int(self.watchlist[uid]) < 3:
                self.watchlist.update({uid: int(time.time())})
                return False
            elif int(time.time())-int(self.watchlist[uid]) >= 3:
                self.watchlist.update({uid: int(time.time())})
                return True
        elif uid not in self.watchlist:
            self.watchlist.update({uid: int(time.time())})
            return True

    @staticmethod
    def get_id(data):
        return int(data['result'][0]['update_id'])

    async def offset(self, data):
        offset = self.get_id(data) + 1
        self.session.get(self.link + '/getUpdates?offset=' + str(offset))

    @staticmethod
    def get_chat_id(data):
        if 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['chat']['id']
        elif 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['message']['chat']['id']
        else:
            return data['result'][0]['message']['chat']['id']

    @staticmethod
    def get_from_id(data):
        if 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['from']['id']
        elif 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['from']['id']
        else:
            return data['result'][0]['message']['from']['id']

    @staticmethod
    def get_sender_id(data):
        if type(data).__name__ == 'int':
            return data
        if 'edited_message' in data['result'][0]:
            if 'type' in data['result'][0]['edited_message']['chat'] == 'group':
                return data['result'][0]['edited_message']['from']['id']
            elif 'type' in data['result'][0]['edited_message']['chat'] == 'private':
                return data['result'][0]['edited_message']['from']['id']
        else:
            if 'type' in data['result'][0]['message']['chat'] == 'group':
                return data['result'][0]['message']['from']['id']
            elif 'type' in data['result'][0]['message']['chat'] == 'private':
                return data['result'][0]['message']['from']['id']

    @staticmethod
    def get_chat_type(data):
        if 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['chat']['type']
        elif 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['message']['chat']['type']
        else:
            return data['result'][0]['message']['chat']['type']

    def get_message(self, data):
        if self.is_callback(data):
            return self.get_callback_data(data)
        if 'message' in data['result'][0]:
            if 'chat' in data['result'][0]['message']:
                if data['result'][0]['message']['chat']['type'] == 'private':
                    if 'text' in data['result'][0]['message']:
                        return data['result'][0]['message']['text']
                elif data['result'][0]['message']['chat']['type'] == 'group':
                    if 'text' in data['result'][0]['message']:
                        return data['result'][0]['message']['text']
                    if 'new_chat_participant' in data['result'][0]['message']:
                        return False
                    elif 'left_chat_participant' in data['result'][0]['message']:
                        return False
                    elif 'pinned_message' in data['result'][0]['message']:
                        return False
        elif 'message' in data['result'][0]['edited_message']:
            if 'chat' in data['result'][0]['edited_message']:
                if data['result'][0]['edited_message']['chat']['type'] == 'private':
                    if 'text' in data['result'][0]['edited_message']:
                        return data['result'][0]['edited_message']['text']
                elif data['result'][0]['edited_message']['chat']['type'] == 'group':
                    if 'text' in data['result'][0]['edited_message']:
                        return data['result'][0]['edited_message']['text']
                    if 'new_chat_participant' in data['result'][0]['edited_message']:
                        return False
                    elif 'left_chat_participant' in data['result'][0]['edited_message']:
                        return False
                    elif 'pinned_message' in data['result'][0]['edited_message']:
                        return False
        else:
            return False

    @staticmethod
    def get_message_id(data):
        if 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['message_id']
        else:
            return data['result'][0]['message']['message_id']

    # this method creates a set of buttons for the message
    @staticmethod
    def make_keyboard(my_list=None):
        if my_list is None:
            my_list = []
        arr = []
        for i in my_list:
            res = ('{"text":"%s"}' % i)
            arr.append(res)
        keys = ('{"keyboard":[%s]}' % arr)
        return str(keys.replace('\'', ''))

    @staticmethod
    def make_inline(buttons, callback=None):
        button_set = {'inline_keyboard': []}
        if not buttons:
            prep = [{'text': 'Sorry, nothing here.', 'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}]
            button_set['inline_keyboard'].append(prep)
            return button_set
        elif buttons:
            if callback is not None:
                if type(callback) is list:
                    for item, call in zip(buttons, callback):
                        prep = [{'text': item, 'callback_data': call}]
                        button_set['inline_keyboard'].append(prep)
                elif type(callback) is str:
                    for item in buttons:
                        prep = [{'text': item, 'callback_data': callback}]
                        button_set['inline_keyboard'].append(prep)
            elif callback is None:
                for item in buttons:
                    prep = [{'text': item, 'url': f'https://telegra.ph/{item}'}]
                    button_set['inline_keyboard'].append(prep)
            elif callback == 'empty':
                num = 0
                for item in buttons:
                    prep = [{'text': item, 'callback_data': f'callback_data{num}'}]
                    button_set['inline_keyboard'].append(prep)
                    num += 1
        return button_set

    # this method creates a dictionary that can be used for post requests. this one is used for regular text messages
    def make_payload(self, ide, text, markup=None, inline=None, callback=None):
        if inline is not None:
            if callback is None:
                payload = {
                    'chat_id': ide,
                    'text': text,
                    'reply_markup': ujson.dumps(self.make_inline(inline))
                }
                return payload
            elif callback is not None:
                payload = {
                    'chat_id': ide,
                    'text': text,
                    'reply_markup': ujson.dumps(self.make_inline(inline, callback=callback))
                }
                return payload
        elif markup is not None:
            payload = {
                'chat_id': ide,
                'text': text,
                'reply_keyboard': self.make_keyboard(list(markup[0]))
            }
            return payload
        else:
            payload = {
                'chat_id': ide,
                'text': text,
            }
            return payload

    @staticmethod
    def make_charge(callback_id, text):
        charge = {
            'callback_query_id': callback_id,
            'text': text,
            'show_alert': False
        }
        return charge

    @staticmethod
    def prepare_message(text):
        if len(text) > 4096:
            return [text[i:i + 4096] for i in range(0, len(text), 4096)]
        else:
            return [text]

    # this method creates sendMessage requests that may contain inline keyboard, use get_chat_id or use clean data
    async def send_message(self, data, message, pure=None, inline=None, callback=None, chat_id=None):
        address = f'{self.link}/sendMessage'
        if inline is not None:
            await self.session.post(address,
                                    data=self.make_payload(ide=self.get_chat_id(data), text=message,
                                                           inline=inline))
        elif inline and callback is not None:
            await self.session.post(address,
                                    data=self.make_payload(ide=self.get_chat_id(data), text=message,
                                                           inline=inline,
                                                           callback=callback))
        elif pure is not None:
            await self.session.post(address, data=self.make_payload(data, message))
        elif chat_id is not None:
            await self.session.post(address, data=self.make_payload(chat_id, message))
        else:
            msg = self.prepare_message(message)
            for i in msg:
                await self.session.post(address, data=self.make_payload(self.get_chat_id(data), i))
            #
            # await self.session.post(address,
            #                         data=self.make_payload(ide=self.get_chat_id(data), text=message,
            #                                                    inline=inline))
            # await self.session.post(address,
            #                         data=self.make_payload(ide=self.get_chat_id(data), text=message,
            #                                                inline=inline,
            #                                                callback=callback))
            #     await self.session.post(address, data=self.make_payload(self.get_from_id(data), message))
            #     msg = self.prepare_message(message)
            #     for i in msg:
            #         await self.session.post(address, data=self.make_payload(self.get_chat_id(data), i))
            #   # pure
            #     await self.session.post(address, data=self.make_payload(data, message))
            # # chat_id
            #     await self.session.post(address, data=self.make_payload(chat_id, message))

    @staticmethod
    def get_name(data):
        if 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['from']['first_name']
        elif 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['from']['first_name']
        elif 'message' in data['result'][0]:
            return data['result'][0]['message']['from']['first_name']
        else:
            return False

    @staticmethod
    def is_username(data):
        if 'message' in data['result'][0]:
            if 'username' in data['result'][0]['message']['from']:
                return True
            elif 'edited_message' in data['result'][0]:
                if 'username' in data['result'][0]['edited_message']['from']:
                    return True
            elif 'callback_query' in data['result'][0]:
                if 'username' in data['result'][0]['callback_query']['from']:
                    return True
        else:
            return False

    @staticmethod
    def get_username(data):
        if 'message' in data['result'][0]:
            return data['result'][0]['message']['from']['username']
        elif 'edited_message' in data['result'][0]:
            return data['result'][0]['edited_message']['from']['username']
        elif 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['from']['username']
        else:
            return False

    @staticmethod
    def get_username_or_first_name(data):
        if 'message' in data['result'][0]:
            if 'username' in data['result'][0]['message']['from']:
                return data['result'][0]['message']['from']['username']
            else:
                return data['result'][0]['message']['from']['first_name']

        elif 'edited_message' in data['result'][0]:
            if 'username' in data['result'][0]['edited_message']['from']:
                return data['result'][0]['edited_message']['from']['username']
            else:
                return data['result'][0]['edited_message']['from']['first_name']

        elif 'callback_query' in data['result'][0]:
            if 'username' in data['result'][0]['callback_query']['from']:
                return data['result'][0]['callback_query']['from']['username']
            else:
                return data['result'][0]['callback_query']['from']['firstname']
        else:
            return False

    # same as make_payload(), creates a dictionary for delete_message() method that deletes messages. should rewrite it
    @staticmethod
    def make_remove(chat, message):
        payload = {
            'chat_id': chat,
            'message_id': message
        }
        return payload

    # this method deletes a message
    async def delete_message(self, data):
        url = f'{self.link}/deleteMessage'
        await self.session.post(url, data=self.make_remove(self.get_chat_id(data), self.get_message_id(data)))

    def print_debug(self):
        print(self.link)

    @staticmethod
    def is_callback(data):
        if 'callback_query' in data['result'][0]:
            return True
        else:
            return False

    @staticmethod
    def get_callback_id(data):
        if 'callback_query' in data['result'][0]:
            return data['result'][0]['callback_query']['id']
        else:
            pass

    async def callback_response(self, data, text):
        callback = f'{self.link}/answerCallbackQuery'
        await self.session.post(callback, data=self.make_charge(self.get_callback_id(data), text))

    @staticmethod
    def get_callback_data(data):
        data1 = [data]
        if 'callback_query' in data1[0]['result'][0]:
            return data1[0]['result'][0]['callback_query']['data']

    async def direct_message(self, chat_id, message):
        address = f'{self.link}/sendMessage'
        await self.session.post(address,
                                data=self.make_payload(ide=chat_id, text=message))

    async def get_uptime(self, start, data):
        if self.get_chat_id(data) == 237892260:
            past = start
            vremechko = time.asctime(time.gmtime(time.time() - past))
            await self.direct_message(chat_id='237892260', message=f'{vremechko[7:-5]}')
        else:
            await self.send_message(data, 'Only Gargoyle can do that!')

    @staticmethod
    def get_reply_to(data):
        if 'message' in data['result'][0]:
            if 'reply_to_message' in data['result'][0]['message']:
                if 'username' in data['result'][0]['message']['reply_to_message']['from']:
                    return data['result'][0]['message']['reply_to_message']['from']['username']
                else:
                    return data['result'][0]['message']['reply_to_message']['from']['first_name']

    @staticmethod
    def is_reply(data):
        if 'message' in data['result'][0]:
            if 'reply_to_message' in data['result'][0]['message']:
                return True
        else:
            return False

    @staticmethod
    def make_photo(chat_id, photo, caption=None,):
        if caption is None:
            payload = {
                'chat_id': chat_id,
                'photo': photo
            }
            return payload
        elif caption is not None:
            payload = {
                'chat_id': chat_id,
                'photo': photo,
                'caption': caption
            }
            return payload

    async def send_photo(self, data, link):
        address = f'{self.link}/sendPhoto'
        await self.session.post(address, data=self.make_photo(self.get_chat_id(data), link))

    def strict(self, data):
        return self.get_from_id(data) == config.ADMIN
    
    async def alert(self, data):
        for i in config.ADMINS:
            await self.send_message(await self.dummy_data(i), data)
