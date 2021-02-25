import requests
import base64
import json
import time
import re
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from collections import Counter

pattern = re.compile(r'\d+')
status_pattern = re.compile(r'预约状态:\n(.*?)\n')
session_dict = {}

headers = {
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'http://org.xjtu.edu.cn',
    'Referer': 'http://org.xjtu.edu.cn/openplatform/login.html',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
}

class Account(object):
    current_account = {}

    def __init__(self,qid,username,password):
        self.qid = qid
        self.username = username
        self.password = password
        self.my_status = self.get_my_status
        self.session = self.login
        Account.current_account[qid] = self


    @staticmethod
    def _aes_cipher(key , aes_str):
        # 使用key,选择加密方式
        aes = AES.new(key.encode('utf-8') , AES.MODE_ECB)
        pad_pkcs7 = pad(aes_str.encode('utf-8') , AES.block_size ,
                        style='pkcs7')  # 选择pkcs7补全
        encrypt_aes = aes.encrypt(pad_pkcs7)
        # 加密结果
        encrypted_text = str(base64.encodebytes(
            encrypt_aes) , encoding='utf-8')  # 解码
        encrypted_text_str = encrypted_text.replace("\n" , "")

        return encrypted_text_str

    @staticmethod
    def _encrypt(username , password):
        """
        加密函数\n
        获取加密串\n
        @return dict
        """
        key = "0725@pwdorgopenp"
        params = {
            'loginType': 1 ,
            'username': username ,
            'pwd': Account._aes_cipher(key , password) ,
            'jcaptchaCode': ''
        }
        return params

    @property
    def login(self):
        param = Account._encrypt(self.username , self.password)
        s = requests.Session()
        s.get('http://202.117.24.3:8080/bxusr')
        s.post('http://org.xjtu.edu.cn/openplatform/g/admin/getJcaptchaCode' , headers=headers)
        res = s.post('http://org.xjtu.edu.cn/openplatform/g/admin/login' , data=json.dumps(param) ,
                     headers=headers).json()
        memberid = res['data']['orgInfo']['memberId']
        user_token = res['data']['tokenKey']
        s.cookies.set('open_Platform_User' , user_token)
        s.cookies.set('memberId' , str(memberid))
        t = "https://org.xjtu.edu.cn/openplatform/g/admin/getUserIdentity?memberId=" + \
            str(memberid) + \
            "&_=" + str(int(1000 * time.time()))
        t = s.get(url=t)
        number = t.json()['data'][0]['personNo']
        t = "https://org.xjtu.edu.cn/openplatform/oauth/auth/getRedirectUrl?userType=1&personNo=" + \
            str(number) + "&_=" + str(int(time.time() * 1000))
        res = s.get(url=t)
        url = res.json()['data']
        s.get(url)
        return s

    def show_my_info(self):
        self.my_status = self.get_my_status
        return self.my_status+self.info

    @property
    def get_my_status(self):
        self.session = self.login
        my_url = "http://rg.lib.xjtu.edu.cn:8086/my/"
        html = self.session.get(my_url , headers=headers).text
        soup = BeautifulSoup(html , 'html.parser')
        items = soup.find_all(class_="bs-calltoaction")
        for item in items[:1]:
            status = item.find(class_="cta-button")
            info = item.find(class_='cta-contents')
            code = status.find('a')
            code = re.search(pattern , code['onclick']).group()
            self.code = code
            self.info = info.text.replace('	','').replace('\n\n','\n').replace('\n\n','')
            return re.search(status_pattern,status.text).group(1)

    def cancel_seat(self):
        self.session = self.login
        self.session.get("http://rg.lib.xjtu.edu.cn:8086/my/?cancel=1&ri=" + self.code, headers=headers)

    def choose_seat(self,room,seat):
        self.session = self.login
        choose_url = "http://rg.lib.xjtu.edu.cn:8086/seat/?kid=" + seat + "&sp=" + room
        res = self.session.get(choose_url , headers=headers)
        soup = BeautifulSoup(res.text , 'html.parser')
        return (soup.find(class_='alert').text)

    def grab_seat(self):
        flag = 0
        while True:
            if flag == 0:
                available_seats_list = get_available_seats(need_list=True)
                if len(available_seats_list) > 0:
                    index = 1
                    msg = self.choose_seat(available_seats_list[index - 1][0] , available_seats_list[index - 1][1])
                    if msg[3:].strip() == '抱歉，该座位已被预约' :
                        continue
                    else:
                        self.my_status = self.get_my_status
                        return self.my_status+self.info
                else:
                    time.sleep(0.5)
                    continue

def get_seat(room,available_seats,s):
    room_url = "http://rg.lib.xjtu.edu.cn:8086/qseat?sp=" + room
    message = s.get(room_url,headers=headers).json()
    seats = message['seat']
    seats.pop('')
    for seat in seats:
        if seats[seat] == 0:
            available_seats.append((room,seat))


def get_available_seats(need_list = False):
    s = Account(2424659013,'2182310012','000803').session
    url = "http://rg.lib.xjtu.edu.cn:8086/qseat?sp=north2east"
    available_seats = []
    try:
        message = s.get(url , headers=headers).json()
        rooms = message['scount']
        rooms.pop('')

        for room in rooms:
            name = room
            status = rooms[room][1]
            if status > 0:
                get_seat(name , available_seats,s)

    except:
        pass
    counter = dict(Counter([i for i,j in available_seats]))
    if not need_list:
        return '\n'.join([f'{room}:{counter[room]}个空位'  for room in counter])
    else:
        return available_seats

if __name__ == "__main__":
    # print(get_available_seats())
    default_account = Account(2424659013,'gan2000','000803')
    print(default_account.grab_seat())












