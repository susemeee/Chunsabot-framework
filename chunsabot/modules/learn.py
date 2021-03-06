# -*- coding: utf-8 -*-
from threading import Thread, Lock
from chunsabot.database import Database
import os
import time

class Imagewait:
    image_ext = (u'jpg', u'jpeg', u'png', u'bmp', u'gif', u'svg', u'tif', u'tga')
    multiple_cnt = 10

    def __init__(self, r, u, k, multiple=False):
        self.room_id = r
        self.user_id = u
        self.key = k
        self.multiple = multiple
        self.count = 0

    @property
    def max(self):
        return self.multiple_cnt if self.multiple else 1

initialized_once = False

class Learnlogic:
    """
        This class is designed to bind text/image databases and bot logic.
    """
    __namepath__ = ".\\data\\name_saved" if "windows" in os.name.lower() else "./data/name_saved"
    __overload__ = u"이 방에서 너무 많은 짤을 부르고 있습니다!"

    def __init__(self, _sockets):
        global initialized_once
        assert(not initialized_once)

        self.sockets = _sockets
        self.curse_map = Database.load_config('curse_map')

        #adding name_map later
        # self.name_map = Database.load_object(Learnlogic.__namepath__, 'name') or []

        # combining name_map and sensitive_map (pre-compiling)
        # we should not save name_map and won't to that.
        self.name_map = Database.load_config('sensitive_map')

        self.image_map = Database('image_map', room_specific=True)
        self.msg_map = Database('msg_map', room_specific=True)
        self.emotion_map = Database('emotion_map')

        self.image_wait = []

        self.l = Lock()
        self.user_hot = {}
        self.t = Thread(target=self.async_release_user_hot, args=(self.l,))
        self.t.start()

        initialized_once = True

    def is_image_waiting(self, room_id, user_id, delete=False):
        for i in self.image_wait:
            if i.room_id == room_id and i.user_id == user_id:
                if i.count + 1 >= i.max or delete:
                    self.image_wait.remove(i)

                i.count += 1
                return i

        return Imagewait(None, None, None)

    def add_curse(self, msg):
        self.curse_map.append(msg)
        Database.save_config('curse_map', self.curse_map)

    def get_msg(self, msg, room_id):
        # weak sensitive_map filtering
        strict = msg in self.name_map

        return self.msg_map.load(msg, room_id, strict)

    def get_image(self, msg, room_id):
        if self.engage_user_hot(room_id):
            return Learnlogic.__overload__
        else:
            return self.image_map.load(msg, room_id, strict=True)

    def async_release_user_hot(self, l):
        while not self.sockets.shutdown:
            l.acquire()
            self.user_hot = { k : v - 1 for k, v in self.user_hot.items() if v > 1 }
            l.release()
            time.sleep(3)

    def engage_user_hot(self, user_id):
        try:
            self.user_hot[user_id] += 1
        except KeyError:
            self.user_hot[user_id] = 1

        if self.user_hot[user_id] > 5:
            return True
        else:
            return False

    def list_image(self, room_id):
        return self.image_map.list_all(room_id)

    def delete_image(self, key):
        self.image_map.delete(key)

    def save_image(self, image_url, extras):
        # Image id or image path
        room_id = extras.room_id
        user_id = extras.user_id

        iw = self.is_image_waiting(room_id, user_id)

        if iw.key:
            if iw.count > Imagewait.multiple_cnt:
                return None
            else:
                if iw.multiple or iw.count < Imagewait.multiple_cnt:
                    self.image_map.save(iw.key, image_url, room_id)

                    s = " ({} / {})".format(
                                iw.count,
                                Imagewait.multiple_cnt
                            ) if iw.multiple else ""
                    return u"이미지가 등록되었습니다!{}".format(s)
        else:
            return None
