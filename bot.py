#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 susemine*.

Author: Suho Lee (susemeee@gmail.com)

Chunsabot is following MIT License. (check LICENSE)

"""

import sys
import asyncio
import telepot
import telepot.async
from datetime import datetime

from chunsabot.chunsa import Chunsa
from chunsabot.database import Database
from chunsabot.messages import Message, ContentType
API_KEY = Database.load_config('telegram_api_key')

ch = Chunsa(sync=True)
loop = asyncio.get_event_loop()

class ChunsabotEndPoint(telepot.async.Bot):
    debug = Database.load_config('debug_mode')

    def process_attachment(self, msg):
        if msg.get('photo', None):
            # Photo
            return msg['photo'][-1]['file_id']
        else:
            # TODO
            return None

    def make_message(self, msg):
        chat = msg.get('chat', None)
        rid = chat['id'] if chat else msg['from']['id']
        # msg['new_chat_participant']
        # msg['left_chat_participant']
        return Message(room_id=rid,
            user_id=msg['from']['id'],
            user_name="{} {}".format(
                msg['from'].get('first_name', ''),
                msg['from']('last_name', '')
            ),
            text=msg.get('text', ''),
            datetime=datetime.fromtimestamp(int(msg['date'])),
            attachment=self.process_attachment(msg)
        )

    @asyncio.coroutine
    def handle(self, msg):
        """
        {'chat': {'first_name': 'Bot',
                  'id': ########,
                  'last_name': 'Chunsa',
                  'type': 'private',
                  'username': 'chunsabot_old'},
         'date': 1450889343,
         'from': {'first_name': 'Bot',
                  'id': ########,
                  'last_name': 'Chunsa',
                  'username': 'chunsabot_old'},
         'message_id': 10,
         'text': 'ping'}
        """
        try:
            if self.debug:
                from pprint import pprint
                pprint(msg)

            p_msg = self.make_message(msg)
            r = ch.process_msg(p_msg)
        except:
            import traceback
            traceback.print_exc()
            r = None

        if r:
            if r.content_type == ContentType.Image:
                file_id = yield from self.sendPhoto(
                    r.peer,
                    open(r.content, 'rb'),
                    caption=p_msg.text
                )
                ch.register_file_id(file_id)
            elif r.content_type == ContentType.ImageId:
                yield from self.sendPhoto(
                    r.peer,
                    r.content,
                    caption='"{}"'.format(p_msg.text.lstrip('..'))
                )
            elif r.content_type == ContentType.Text:
                yield from self.sendMessage(
                    r.peer,
                    r.content,
                    reply_to_message_id=r.reply
                )

bot = ChunsabotEndPoint(API_KEY)
loop.create_task(bot.messageLoop())
print('Starting receive event loop.')

try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Interrupted.')
    sys.exit(0)
except:
    print('Unhandled exception has occurred.')
    import traceback
    traceback.print_exc()
    sys.exit(-1)
