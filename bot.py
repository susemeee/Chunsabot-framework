#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 susemine*.

Author: Suho Lee (susemeee@gmail.com)

Chunsabot is following MIT License. (check LICENSE)

"""


def main():
    print("Type bot.py -h to check extra arguments")
    res = parser.parse_args()

    if res.initial_config:
        from chunsabot.configmaker import make_initial_config
        make_initial_config()
    else:
        print("Usage : ./telegram-cli -Z bot.py")

    return True

if __name__ == "__main__":
    import argparse
    import base64
    import random

    parser = argparse.ArgumentParser(description='Chunsabot main framework')

    parser.add_argument('--make-initial-config', dest='initial_config', action='store_true', default=True,
                       help='Making initial config for Chunsabot')
    # parser.add_argument('--no-warning', dest='warn', action='store_false', default=True,
    #                    help='Turns off warning filter')
    # parser.add_argument('-s', dest='hello', action='store_false', default=True,
    #                    help='Slient mode (No initial response when entered new room)')
    # parser.add_argument('-p', dest='profile', action='store_true', default=False,
    #                    help='Profile mode')
    # parser.add_argument('--disable-logs', dest='logs', action='store_false', default=True,
    #                     help='Disables logging room when true')

    if main():
        exit(0)
else:
    import tgl
    import os
    from chunsabot.chunsa import Chunsa
    from chunsabot.messages import Message, ContentType
    
    real_path = os.path.realpath(__file__)
    real_path = real_path[:real_path.rfind("/")]

    ch = Chunsa(real_path=real_path, sync=True)

    our_id = 0
    binlog_done = False

    def _make_message(msg, peer, _by, attachment=None):
        return Message(room_id=peer.id, 
            user_id=_by.id, 
            user_name=_by.name.replace("_", " "), 
            text=msg.text, 
            datetime=msg.date,
            attachment=attachment,
            peer=peer)

    def _on_close():
        print("closing")
        tgl.safe_exit(0)

    ch.on_close = _on_close

    def empty_cb(success):
        pass

    def msg_cb(success, msg):
        pass


    def file_cb(success, file_path, peer=None, msg=None):
        r = ch.process_msg(_make_message(msg, peer, msg.src, attachment=file_path))
        peer.send_msg(r.content)

    def on_binlog_replay_end():
        binlog_done = True

    def on_get_difference_end():
        pass

    def on_our_id(id):
        global our_id
        our_id = id
        return "Set ID: " + str(our_id)

    def on_msg_receive(msg):
        global our_id

        try:
            if msg.out and not binlog_done:
                return

            _by = msg.src
            if msg.dest.id == our_id: 
                # direct message
                peer = msg.src
            else: 
                # chatroom
                peer = msg.dest

            if msg.media and msg.media['type'] == 'photo':
                if ch.image_ready(peer.id, _by.id):
                    msg.load_photo(lambda success, file_path: file_cb(success, file_path, peer=peer, msg=msg))
            else:            
                r = ch.process_msg(_make_message(msg, peer, _by))
                if r:
                    peer.mark_read(empty_cb)
                    if r.content_type == ContentType.Text:
                        peer.send_msg(r.content)
                    elif r.content_type == ContentType.Image:
                        peer.send_photo(r.content)


        except Exception as e:
            import traceback
            traceback.print_exc()

    def on_secret_chat_update(peer, types):
        return "on_secret_chat_update"

    def on_user_update(peer, what):
        pass

    def on_chat_update(peer, what):
        pass

    # Set callbacks
    tgl.set_on_binlog_replay_end(on_binlog_replay_end)
    tgl.set_on_get_difference_end(on_get_difference_end)
    tgl.set_on_our_id(on_our_id)
    tgl.set_on_msg_receive(on_msg_receive)
    tgl.set_on_secret_chat_update(on_secret_chat_update)
    tgl.set_on_user_update(on_user_update)
    tgl.set_on_chat_update(on_chat_update)
