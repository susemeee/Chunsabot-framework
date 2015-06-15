# -*- coding: utf-8 -*-
from multiprocessing.pool import ThreadPool
import requests
import re
# from lib.botlogic import brain

class VerifyUrl:
    """
        verify_url.py
        This script was not updated to the new logic.
    """
    cURL_VERIFY_URL = u"http://api.yangslab.com/url_data.php?url={0}"
    #true if it is a valid url
    url_only_re = re.compile('(http://)?[가-힣\x00-\xff]+\.\
(MUSEUM|TRAVEL|AERO|ARPA|ASIA|EDU|GOV|MIL|MOBI|COOP|INFO|NAME|BIZ|CAT|COM|INT|JOBS|NET|ORG|PRO|TEL|\
A[CDEFGILMNOQRSTUWXZ]|B[ABDEFGHIJLMNORSTVWYZ]|C[ACDFGHIKLMNORUVXYZ]|D[EJKMOZ]|E[CEGHRSTU]\
|F[IJKMOR]|G[ABDEFGHILMNPQRSTUWY]|H[KMNRTU]|I[DELMNOQRST]|J[EMOP]|K[EGHIMNPRWYZ]\
|L[ABCIKRSTUVY]|M[ACDEFGHKLMNOPQRSTUVWXYZ]|N[ACEFGILOPRUZ]|OM|P[AEFGHKLMNRSTWY]\
|QA|R[EOSUW]|S[ABCDEGHIJKLMNORTUVYZ]|T[CDFGHJKLMNOPRTVWZ]|U[AGKMSYZ]|V[ACEGINU]\
|W[FS]|Y[ETU]|Z[AMW])+')
    
    @staticmethod    
    def async_verify_url(Sockets, url, room_id):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(VerifyUrl.verify_url, (Sockets, url, room_id))

    @staticmethod
    def verify_url(Sockets, url, room_id):
        try:
            res = requests.get(VerifyUrl.cURL_VERIFY_URL.format(url), headers=\
                {'User-Agent' : 'yangslab.com'}).json()
            
            if res['status'] == u"Success":
                res = u"URL 검증 : {0}\r\nPowered by NTMA".format(res['message'])
            else:
                raise Exception(res['message'])
        except Exception as e:
            #API Error
            print("SmishingError : "+str(e))
            res = u"URL 검증 : 스미싱 DB 서버 오류입니다."

        Sockets.write(room_id, res)

    @staticmethod
    def info():
        return u"URL 검증 시스템 : \r\n방에 URL 주소를 올릴 경우, 주소가 안전한지 아닌지를 검사해 줍니다.\r\nURL 주소에 대한 DB는 스미싱몬을 개발한 NTMA 연구소에서 제공합니다."
