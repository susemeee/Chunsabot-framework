from enum import Enum

class ContentType(Enum):
    Text = 100
    Image = 101
    Leave = 199
    Exit = 999

class Message:
    def __init__(self, room_id, user_id, user_name, text, datetime, peer=None, by=None, attachment=None):
        # used for Mafiagame
        if peer:
            self.peer = peer
        else:
            self.peer = room_id
        if by:
            self.by = by
        else:
            self.by = user_id

        self.room_id = room_id
        self.user_id = user_id
        self.user_name = user_name
        self.text = text
        self.datetime = datetime
        self.attachment = attachment


    def __repr__(self):
        return "<Message>\npeer : {0}\nroom_id : {1}\nuser_id : {2}\nuser_name : {3}\nmessage : {4}".format(self.peer, self.room_id, self.user_id, self.user_name, self.text)


class ResultMessage:
    def __init__(self, content, reply=False, content_type=ContentType.Text, peer=None):
        self.peer = peer
        self.content = content
        self.content_type = content_type
        self.reply = reply

    def __repr__(self):
        return "<ResultMessage>\npeer : {0}\ncontent : {1}\nreply : {2}".format(self.peer, self.content, self.reply)
