수호천사 (Chunsabot)
==================

***This readme.md is not yet completed.***

Bot framework for messenger just for playing :)

This framework can be attached to many different bot implementation.

Official facebook page : http://fb.com/chunsab

Chunsabot is written in Python. 

(Tested in Python 3, I recently migrated it from Python 2 to Python 3, so I don't guarantee that Python 2 will work).

2015 susemeee.


How to use (Normal user - Korean)
--------

수호천사는 봇 구현체가 아닌 하나의 프레임워크입니다. 하지만, 테스트와 재미를 위해서 텔레그램을 위한 봇 구현체가 구현되어 있습니다. 일반 사용자를 이를 이용해서 텔레그램에서 봇을 운영할 수 있습니다.

* telegram-cli는 비동기 메시지 전송을 지원하지 않습니다. 따라서, 메시지가 오면 그 메시지에 대한 처리를 하는 동기 방식을 사용하고 있습니다. 이는 많은 메시지가 동시에 올 경우 봇을 불안정하게 만들 수 있습니다.


How to use (Normal user)
--------

Despite Chunsabot is not a bot implementation but a framework, I made a bot implementation which works in Telegram.
In other words, a user can run a bot via Telegram.

* telegram-cli does not support async message sending, so I wrote it using synchronous procedure. This behavior would make bot unstable when a lot of messages are arriving at the same time.

How to do:

1. Install Python 3. (I tested it using Python 3.4.3 and OS X 10.10)
2. Install dependencies by running command.
```
pip install -r pip.dependencies
```
3. Run following command to make initial config.
```
python3 /path/to/your/framework/bot.py --make-initial-config
```
4. Run telegram-cli with bot script by using following command.
```
./telegram-cli -Z /path/to/your/framework/bot.py
```

You can learn how to play with bot by typing "." command. :)

How to use (Bot Developer)
--------------------

Chunsabot supports both synchronous and asynchronous logic.

You can make a bot implementation via modifying bot.py. Doing this, you can make a bot implementation using LINE, Facebook Messenger or even KakaoTalk. (up to you)

- How to make bot implementation

1. Delete bot.py
2. Write "Your" bot.py by following these rules.

```
TBA
```
3. 

Adding new modules (Bot Developer)
--------------------------------------------

Chunsabot's Botlogic uses routing system to process different modules.

You can create new python file to `modules` directory and write the bot logic script. 

Below is an example code.

```python

from chunsabot.botlogic import brain
from chunsabot.messages import ResultMessage
import random
import re

@brain.route('Hello')
def hello(msg, extras):
    resp = u"Hello {0}!".format(extras['user_name'])
    return ResultMessage(resp)

@brain.startswith('테스트')
def test(msg, extras):
    return "{0}\n\n{1}".format(msg.__repr__(), extras.__repr__())

@brain.startswith('선택')
def choice(msg, extras):
    msg = msg.split(',')

    if len(msg) == 1:
        return ResultMessage(".선택 사과, 딸기, 포도")

    for m in msg:
        m = m.strip()

    choiced = msg[random.randint(0, len(msg) - 1)]

    return ResultMessage("{0}님이 제시한 것들 중 {1}을(를) 골랐습니다.".format(extras['user_name'], choiced))

@brain.route(['나', '너', '우리'])
def youandi(cmd, msg, extras):
    return ResultMessage("[나, 너, 우리]\n{0}".format(cmd))

@brain.route(re.compile('^\d+$'))
def number(cmd, msg, extras):
    return ResultMessage("숫자입니다.")

```

* The decorator, brain.route or brain.startswith, can accept a type : list, str, regex type.

* you can pass a parameter below to the decorator.

|        kwargs        |                   description                              |
|----------------------|------------------------------------------------------------|
|       no_params      |          don't provide a parameter to the function.        |
| disable_when_silence | the function won't work when the bot is in "Silence Mode". |  


Remark
------
- All strings are processed as unicode. Though there are a logic that converts type(str) to type(unicode), all responses should be given as unicode. <- Don't need to do it since Chunsabot now uses Python 3.

- *Mafiagame (mafia.py) and SharedScheduler (schedule.py) is not yet fully implemented and tested.*

- Some modules are not yet tested after the migration. (such as weather.py)

- ~~verify_url.py is a module which verifies a given URL is whether spam or not. Since the API is now broken (Note, Chunsabot is originally deployed 1 year ago), it won't work.~~
it is now deprecated.


####Editing config.yaml file

*We don't have to create config.py but configmaker does it for you.*

|   keys for config   | type |   description                                                        |
----------------------|------|----------------------------------------------------------------------| 
|      curse_map      | list |  Collection of words which should be filtered.                       |
|  debug_allowed_room | list |  Collection of rooms which should accept messages during debug mode. |
|  debug_mode         | bool |  Switch for "debug mode".                                            |
|  debug_users        | list |  Collection of users allowing "debug command". (starts with @)       |
|  leave              | str  |  Keyword for force bot to leave the room. (Telegram unsupported)     | 
|  sensitive_map      | list |  Collection of words which should be applied only in the room where executed the learn command. |
|  weather_url_all    | str  |  KMA Weather API URL                                                 |
|  google_api_key     | str  |  Google API Key for searching images and YouTube.                    |

####Extras (passed to botlogic with msg)

|    key     |  type   | description |
|------------|---------|-------------|
|  room_id   | long    | Unique identifier of room.        |
|  user_id   | int     | Unique identifier of person.      |
| user_name  | str     | User's current profile name.      |
|    room    | dict    | Current room for current message. |
|    peer    | object  | representing "peer" for Telegram messenger. |


Support
-------

Send me a Telegram message (@susemeee) if you need any support.

If you think you have found a bug, have an idea or suggestion, please open a issue here.


Changelog
---------
this changelog has been written before the git commit.

    20140223 (internal version 0.9)

    20140225 first release(version 1.0)

    20140226 update(version 1.2)

    20140227 update(version 1.3)
    1. chaged upanddown logic : 0~50 to 0~99

    20140228 update(version 2.0)
    1. restructured socket class (Queue)
    2. fixed upanddown bug (shared variable)

    20140302 update(version 2.2)

    20140305 update(version 2.3)
    1. def silence() and updated hello() and new()
    2. pickle-based persistent self.rooms storage
    3. chewing some response in learnlogic

    20140308 update(version 2.6)
    1. words learned from same room will be applied firstly
    2. added .지우기
    3. fixed silence mode bug

    20140310 update(version 2.7)
    1. fixed another silence bug
    2. selfheal script re-added
    3. attempts to fix process_msg stuck bug

    20140331 update(version 2.9)
    1. attempts to fix msg stuck bug #2
    1-1. ignoring messages longer than 200 words
    1-2. restructured Cache (DB->memory, nicer)

    20140403 will have to do:
    1. image crawler
    2. saving self.rooms objects (by pickle) before quitting

    20140415 update(version 3.1)
    1. dramatically increased weather performance

    20140421 update(version 3.2)
    1. Image learnlogic added
    2. filtering name logic

    20140502 update(version 3.3)
    (not changed much)
    1. new account
    2. added no-warning mode

    20140517 update(version 4.0)
    1. a lot of refactoring
	2. using argsparser in bot.py
    3. Readme.md added (and making the source public)

Licenses
--------

Chunsabot is following MIT License.

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
