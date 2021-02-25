import requests
from tabulate import tabulate


async def get_weather_of_city(city: str) -> str:
    url = 'http://apis.juhe.cn/simpleWeather/query'
    params = {
        'key': '01f7912c9d8fc92d7f29e9ad0b7cf1eb' ,
        'city': city
    }
    data = requests.get(url , params=params).json()
    if data["reason"] != "暂不支持该城市":
        data = data['result']
        real_time = [['城市' , data['city']] , ['温度' , data['realtime']['temperature'] + '℃'] ,
                     ['湿度' , data['realtime']['humidity'] + '%'] , ['天气' , data['realtime']['info']] ,
                     ['风向' , data['realtime']['direct']] , ['风力' , data['realtime']['power']] ,
                     ['空气指数' , data['realtime']['aqi']]]
        data = data['future'][1]
        tommorrow = [['日期' , data['date']] , ['温度' , data['temperature'] + '℃'] , ['天气' , data['weather']] ,
                     ['风向' , data['direct']]]
        return f'''
-----当前天气-----
{tabulate(real_time)}
-----明天天气-----
{tabulate(tommorrow)}'''
    else:
        return '查询的城市不存在8[CQ:face,id=32]'


async def get_weather_life(city):
    url = 'http://apis.juhe.cn/simpleWeather/life'
    params = {
        'key': '01f7912c9d8fc92d7f29e9ad0b7cf1eb' ,
        'city': city
    }
    try:
        datas = requests.get(url , params=params).json()['result']['life']
    except:
        return '[CQ:image,file=5060fb53c5311f660d29f42f62d354e8.image,url=http://c2cpicdw.qpic.cn/offpic_new/2424659013//2424659013-1036848333-5060FB53C5311F660D29F42F62D354E8/0?term=3]'
    pinyin_dict = {
        'kongtiao': '空调' ,
        'guomin': '过敏' ,
        'shushidu': '舒适度' ,
        'ganmao': '感冒' ,
        'ziwaixian': '紫外线' ,
        'yundong': '运动' ,
        'daisan': '带伞' ,
        'chuanyi': '穿衣建议'
    }
    report = [['城市',city]]
    for key in pinyin_dict:
        if key == 'chuanyi':
            report.append([pinyin_dict[key] , datas[key]['des']])
        else:
            report.append([pinyin_dict[key] , datas[key]['v']])
    return tabulate(report)


if __name__ == "__main__":
    print(get_weather_of_city('鹤岗'))
