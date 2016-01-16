import requests
import json
import random
import hashlib
import os
import imghdr
from urllib.parse import quote

from chunsabot.botlogic import brain, Botlogic
from chunsabot.messages import ResultMessage, ContentType
from chunsabot.database import Database

API_KEY = Database.load_config("google_api_key")

GOOGLE_Y_SEARCH_RESULT = "GoogleYouTube"
GOOGLE_Y_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=8&type=video&q={0}&key={1}"
GOOGLE_IMG_SEARCH_RESULT = "GoogleImage"
GOOGLE_IMG_SEARCH_URL = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&rsz=8&q={0}&imgsz=small|medium|large&key={1}"

exhausted = {}

def _hash(url):
    return "{0}".format(hashlib.sha256(url.encode('utf-8')).hexdigest()[:16])

def _send_photos_from_url(url):
    path = os.path.join(Botlogic.__temppath__, _hash(url))

    if not os.path.exists(path):
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
                f.flush()
        else:
            return False

    real_path = "{0}.{1}".format(path, imghdr.what(path))
    os.rename(path, real_path)
    return ResultMessage(real_path, content_type=ContentType.Image)

def _get_data(cache_name, search_url, msg):
    if not cache_name in brain.cache:
        brain.cache[cache_name] = {}

    cache = brain.cache[cache_name]
    if msg in cache:
        return cache[msg]
    else:
        data = requests.get(search_url)

        if data.status_code != 200:
            return ResultMessage("검색 오류 ({0})".format(data.status_code))
        else:
            cache[msg] = data.text
            return data.text

def random_image_info():
    return """[짤]
랜덤한 구글 이미지 검색 결과를 제공하여 줍니다.
<경고 : 수위가 높은 이미지가 반환될 수 있습니다.>
"""

def random_youtube_info():
    return """[유튜브]
랜덤한 유튜브 URL을 업로드합니다.
"""


def random_image(msg, extras):
    if not msg:
        return random_image_info()


    exhausted[msg] = []

    data = _get_data(GOOGLE_IMG_SEARCH_RESULT, GOOGLE_IMG_SEARCH_URL.format(quote(msg), API_KEY), msg)

    if isinstance(data, ResultMessage):
        return data

    data = json.loads(data)
    results = data["responseData"]["results"]
    success = None
    while True:
        if len(exhausted[msg]) >= len(results):
            # TODO We've used all of data. should fetch new.
            exhausted[msg] = []
            print("ImageFetcher : Used all of images.")
            break

        result = results[random.randint(0, len(results) - 1)]
        if result not in exhausted[msg]:
            success = _send_photos_from_url(result["url"])
            if success:
                break
            else:
                exhausted[msg].append(result)
                print("ImageFetcher : Failsafe activated.")

    if success:
        return success
    else:
        return ResultMessage("이미지 다운로드 오류.")

@brain.startswith("유튜브")
def random_youtube(msg, extras):
    if not msg:
        return random_youtube_info()

    data = _get_data(GOOGLE_Y_SEARCH_RESULT, GOOGLE_Y_SEARCH_URL.format(quote(msg), API_KEY), msg)

    if isinstance(data, ResultMessage):
        return data

    data = json.loads(data)

    results = data["items"]
    result = results[random.randint(0, len(results) - 1)]

    return "http://youtu.be/{0}".format(result["id"]["videoId"])
