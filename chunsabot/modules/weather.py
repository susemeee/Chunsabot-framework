# -*- coding: utf-8 -*-
from chunsabot.botlogic import brain
from chunsabot.database import Database, Cache

from bs4 import BeautifulSoup as Soup
import requests
#from threading import Thread
from multiprocessing.pool import ThreadPool

class Weather:
    cWEATHER_GET_URL = Database.load_config("weather_url_all")
    pool = ThreadPool(processes=1)
    no_such_region = u"해당 지역의 정보가 존재하지 않습니다."
    province_map = {}

    @staticmethod
    def parse_all():
        xml = requests.get(Weather.cWEATHER_GET_URL).text
        result = {}
        weather = Soup(xml)
        #channel
        weather = weather.find('channel')
        #<pubDate>2014년 02월 21일 (금)요일 18:00</pubDate>
        published_date = weather.find('pubdate').text

        #header->item->desc
        weather = weather.find('item').find('description')
        #<wf><![CDATA[기압골의 영향으로 26~27....]]></wf>
        whole_description = weather.find('header').find('wf').text
        all_locations = weather.find('body').findAll('location')

        result[None] = whole_description.replace('<br  />', '\r\n').replace('<br />', '\r\n')
        result[u'전국'] = result[None]

        for loca in all_locations:
            # mapping province text to city
            Weather.province_map[loca.find('province').text] = loca.find('city').text

            region = loca.find('city').text
            data = loca.findAll('data')
            res = []

            weather_location_header = u"{0} 지역의 날씨 정보입니다.\r\n({1} 발표)".format(region, published_date)
            weather_location_footer = u"data by 기상청 RSS 서비스"

            res.append(weather_location_header)
            i = 2
            for d in data:
                res.append(Weather.prettify(i, d))
                i += 1
                if i > 6: break
            res.append(weather_location_footer)
            res = "\r\n".join(res)

            result[region] = res

        return result

    @staticmethod
    def prettify(i, data):
        apm = [u'오전', u'오후']
        day = u"[{0}일 후 {1}예보]".format(i/2, apm[i%2])

        tmx = data.find('tmx').text
        tmn = data.find('tmn').text
        wf = data.find('wf').text
        text = u"{0}, 기온 {1}°C ~ {2}°C".format(wf, tmn, tmx)

        return u"{0}\r\n{1}".format(day, text)


@brain.route(u"날씨")
def async_view(msg, extras):
    def info():
        return u"날씨 : 전국 날씨에 관한 간략한 설명 또는 지역별 날씨를 볼 수 있습니다. \r\n예) .날씨 전국 .날씨 경기도"

    if not msg:
        return info()
    else:
        region = msg

    #using SQLite from another thread causes a program to crash
    #should use other DataModel (ex. Mamcached) later
    info_all = Cache.load(Weather.cWEATHER_GET_URL)

    if not info_all:
        info_all = Weather.pool.apply_async(Weather.parse_all, ()).get(timeout=300)
        new_cache = True
    else:
        new_cache = False

    #new_cache returns parsed info
    if new_cache:
        Cache.save(Weather.cWEATHER_GET_URL, info_all)

    try:
        # Inaccurate
        for tu in Weather.province_map.items():
            if region in tu[0]:
                region = tu[1]

        info = info_all[region]
        return info
        # Sockets.write(room_id, info)
    except KeyError:
        return Weather.no_such_region
        # Sockets.write(room_id, Weather.no_such_region)
