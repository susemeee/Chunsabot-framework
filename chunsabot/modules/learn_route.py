# -*- coding: utf-8 -*-
from chunsabot.botlogic import brain
from chunsabot.modules.verify_url import VerifyUrl
from chunsabot.modules.learn import Imagewait
from chunsabot.logger import Logger
import re
import random

learn = brain.learn
logger = Logger.mainLogger()
learn_re = re.compile(' 라고 말?하면 너는 \w+ 라고 말?하면 돼~?')
phone_re = re.compile('(010|o1o|O1O|0ㅣ0|공일공|ㅇㅣㅇ)?(-|\s)?[0-9]{3,4}(-|\s)?[0-9]{4}')
hangeul = u"ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
emotions = [u'좋아요',u'싫어요',u'슬퍼요',u'기뻐요',u'힘내요',u'사랑스러워요',u'짜증나요',u'미워요',u'갖고싶어요',u'무서워요',u'안쓰러워요', u'부끄러워요', u'재밌어요', u'민망해요', u'엄청나요', u'궁금해요']
emoticon_map = [u'(미소)', u'(눈물)', u'(눈물)', u'(방긋)', u'(브이)', u'(반함)', u'(버럭)', u'(으으)', u'(부끄)', u'(당황)', u'(눈물)', u'(부끄)', u'(행복)', u'(당황)', u'(궁금)', u'(궁금)']
emotion_reply_map = [u'저도 [WORD] [EMOTION]! [EMOTICON]', u'[WORD][EMOTICON]', u'[EMOTICON][EMOTION]~~', u'완전 [EMOTION]!']


@brain.startswith(u"지우기", disable_when_silence=True)
def delete_msg(msg, extras=None):
    if not msg:
        return info_delete()

    if extras:
        room_id = extras['room_id']
    else:
        room_id = None
        
    row_match = learn.msg_map.delete(msg, room_id)
    if row_match > 0:
        return u"[지우기]\r\n{0}개의 단어를 삭제하였습니다!".format(row_match)
    else:
        return u"[지우기]\r\n이 방에서 그런 단어는 배우지 않았습니다!"

@brain.route(u"짤리스트")
def image_list(msg, extras):
    room = extras['room']
    if room.is_personal():
        return u"[짤리스트]\r\n이 기능은 개인 대화에서 작동하지 않습니다."

    return u"[짤리스트]\r\n{0}".format(learn.list_image(extras['room_id']))


@brain.startswith(u"짤지우기", disable_when_silence=True)
def image_list(msg, extras):
    if not msg:
        return info_delete_image()

    room = extras['room']
    if room.is_personal():
        return u"[짤지우기]\r\n이 기능은 개인 대화에서 작동하지 않습니다."

    if msg:
        room_id = extras['room_id']
        row_match = learn.image_map.delete(msg, room_id)
        if row_match > 0:
            return u"[짤지우기]\r\n{0}개의 단어를 삭제하였습니다!".format(row_match)
        else:
            return u"[짤지우기]\r\n이 방에서 그런 단어는 배우지 않았습니다!"


@brain.startswith(u"짤배우기", disable_when_silence=True)
def process_image(msg, extras):
    if extras['room'].is_personal():
        return u"[짤배우기]\r\n이 기능은 개인 대화에서 작동하지 않습니다."

    if msg:
        room_id = extras['room_id']
        user_id = extras['user_id']

        if msg == u"취소":
            # Delete logic
            o_key = learn.is_image_waiting(room_id, user_id, delete=True)
            if o_key:
                return u"[짤배우기]\r\n[NAME]님의 대기중인 키워드 \"{0}\"이(가) 삭제되었습니다.".format(o_key)
            else:
                return u"[짤배우기]\r\n[NAME]님의 대기중인 키워드가 없습니다."
        
        key = learn.is_image_waiting(room_id, user_id)
        if key:
            return u"[짤배우기]\r\n현재 [NAME]님은 이 방에서 이미지 대기 중입니다. (키워드 {0})".format(key)
        else:
            key = msg
            learn.image_wait.append(Imagewait(room_id, user_id, key))
            return u"[짤배우기]\r\n[NAME]님이 처음으로 올린 이미지가 적용됩니다!"
    else:
        return info_image()

#배우기 나, 너
#나, 너
#눈은->우유는
@brain.startswith(u"배우기", disable_when_silence=True)
def process(msg, extras, detect_curse=True):

    def learn_new(msg, room_id):
        if u"->" in msg:
            content = msg.split('->', 1)
            recursive = True
        else:
            content = msg.split(',', 1)
            recursive = False
        
        if len(content) == 2:
            get = content[0]
            response = content[1].lstrip()
        else:
            return info()

        if len(response) > 400 or get.replace(u'.', u'') == u'':
            return u"[배우기]\r\n단어가 너무 길거나 단어가 없습니다!"            
        # experimental data
        elif extras['room'].is_personal() and get in learn.name_map:
            return u"[배우기]\r\n개인 대화에서 사람 이름을 가르칠 수 없습니다."

        if recursive:
            try:
                learn.msg_map.save(get, learn.msg_map[response], room_id)
            except KeyError:
                return u"(당황) 그런 단어는 몰라요 ㅠㅠ"        
        else:
            learn.msg_map.save(get, response, room_id)   
        return u"(윙크) 알겠어요!!"

    room_id = extras['room_id']
    user_id = extras['user_id']
    
    if msg:
        if learn.engage_user_hot(user_id):
            return u"[NAME]님은 지금 너무 많이 가르치고 있습니다!"
        else:
            #sample words for detecting curse
            msg_sample = msg.replace(' ', '')
            if detect_curse:
                detected = False
                for curse in learn.curse_map:
                    #enhanced curse map
                    #unicode!
                    for i in range(32,128):
                        nc = curse[:1]+chr(i)+curse[1:]
                        if nc in msg_sample or curse in msg_sample:
                            detected = True

                    if not detected:
                        for s in hangeul:
                            nc = curse[:1]+s+curse[1:]
                            if nc in msg_sample or curse in msg_sample:
                                detected = True

                    if detected:
                        logger.info("Curse detected : {0}".format(str(user_id)))
                        #return u"욕은 안돼요~(당황)\r\n* 주의: 계속 부적절한 단어를 입력 시 배우기가 차단됩니다."
                        return None

            if phone_re.search(msg):
                return u"대체 폰번호는 왜 가르치는거에요?"
            elif VerifyUrl.url_only_re.search(msg.upper()):
                return u"대체 URL 주소는 왜 가르치는거에요?"

        return learn_new(msg, room_id)
    else:
        return info()

#종아요 고려대
@brain.route(emotions)
def learn_emotion(emotion, word, extras):

    def emotion_reply(word, emotion):
        if emotion == u"힘내요":
            return u"힘내요 (눈물) (브이)"
        rand = int((random.random()*1000))%len(emotion_reply_map)
        res = emotion_reply_map[rand]

        res = res\
        .replace(u"[WORD]", word)\
        .replace(u"[EMOTICON]", emoticon_map[emotions.index(emotion)])\
        .replace(u"[EMOTION]", emotion)
        return res

    if not emotion in emotions:
        return info()
        
    learn.emotion_map[word] = emotion
    return emotion_reply(word, emotion)



@brain.route(u"유의사항", no_params=True)
def pm():
    return u"""[배우기에 관하여]
수호천사의 .배우기 기능은 플랫폼으로써 개발자는 컨텐츠를 제공하지 않습니다.
즉, .배우기 내용을 통해 습득된 데이터 베이스는 유저 여러분들이 만들어 가는 것이고,
개발자는 특정 의도를 가지고 추가 및 수정하지 않음을 공지합니다.

.배우기 관련 내용에 대하여 불쾌하거나 불만사항이 있으신 경우, 메일을 통하여 알려주시면 감사하겠습니다."""

@brain.route(u"감정", no_params=True)
def info_emotion():
    return u"""[감정]
로봇에게 감정을 가르칠 수 있습니다! 
예) .좋아요 고려대
{0}
감정에 대한 정보는 추후 업데이트에서 사용될 수 있습니다.""".format(u" ".join(emotions))

# @brain.route(u"짤배우기")
def info_image():
    return u"""[짤배우기]
이제 봇이 사진을 배울 수 있습니다! 
**주의 : 천사와의 개인톡에서는 이 기능이 작동하지 않습니다! 
1. .배우기 명령어 대신 .짤배우기가 사용됩니다. 
2. .짤배우기 명령어 후 가장 먼저 올린 사진이 적용됩니다.
3. 사진은 점을 두 개 찍어야 불러올 수 있습니다.
예) .짤배우기 계획대로 ->
..계획대로
.짤배우기로 배운 사진은 방 내에서만 적용됩니다."""

#@brain.route(u"지우기")
def info_delete():
    return u"""[지우기]
같은 방에서 배운 단어에 한해 배우기한 단어를    지울 수 있습니다. 
예) 친구가 내 이름에 병신이라고 등록해놨을 때 : 
.지우기 내이름"""

def info_delete_image():
    return u"""[짤지우기]
해당 방에서 배운 이미지를 삭제합니다.
"""

#@brain.route(u"배우기")
def info():
    return u"""[배우기]
1차원적인 단어를 학습할 수 있습니다.
**.유의사항 키워드를 통하여 .배우기 키워드의 유의사항을 확인할 수 있습니다.
예) .배우기 안녕, 안녕하세요~
배우기를 통해 학습한 단어는 앞에 .을 붙여야 인식할 수 있습니다.
똑같은 단어로 링크할 수도 있습니다. 
예) 우유는?, 하얗다가 이미 있을 때 : .눈은?->우유는? 
눈은?, 하얗다
*** 주의 *** 
배우기한 단어는 모든 방에서 적용됩니다!!!"""