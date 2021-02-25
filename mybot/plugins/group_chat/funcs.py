import requests

async def get_reply_async(msg):
    url = f'http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}'
    reply = requests.get(url).json()['content']
    return reply