from nonebot import on_command , CommandSession
import requests
from nonebot.permission import *

__plugin_name__ = '图书馆抢座'
__plugin_usage__ = r"""
图书馆抢座

1.状态查询
作用:显示当前图书馆各自习室人数
格式：状态查询

以下功能需要先私聊机器人,发送:图书馆
1.我的当前状态
作用：显示你的图书馆预约最新状态
格式：预约状态 
2.抢座
作用:自动抢座(如果检测到有座位直接抢)
格式:抢座
3.取消预约
作用:取消当前预约的座位
格式：取消预约

"""
base_url = 'http://cloud.mrgump.org:9999/'

login_url = base_url + 'login?qid={}&username={}&password={}'
user_status_url = base_url + 'show?qid={}'
user_exists_url = base_url + 'user_exists?qid={}'
querry_url = base_url+'get_info'
cancel_url = base_url + 'cancel?qid={}'
grab_url = base_url + 'grab?qid={}'

@on_command('my_status',aliases=['预约状态'],permission=PRIVATE)
async def my_status(session=CommandSession):
    qid = session.event["user_id"]
    await session.send(requests.get(user_status_url.format(qid)).text)

@on_command('get_info',aliases=['状态查询'],only_to_me=False)
async def get_info(session=CommandSession):
    res = requests.get(querry_url).text
    await session.send(res)

@on_command('login',aliases=['图书馆'],permission=PRIVATE)
async def login(session=CommandSession):
    return

@login.args_parser
async def _(session=CommandSession):
    qid = session.event["user_id"]
    if session.is_first_run:
        if requests.get(user_exists_url.format(qid)).text == '检测到用户!':
            await session.send('已检测到您的账户!')
            await session.send(requests.get(user_status_url.format(qid)).text)
            return
        else:
            session.pause('请按照:用户名 密码 的格式发送进行登录:\n例如:2199999999 123456')
    else:
        args = session.current_arg_text.strip().split(' ')
        if len(args) == 2:
            user_name = args[0]
            password = args[1]
            res = requests.get(login_url.format(qid , user_name , password)).text
            if res != '登陆失败!密码错误!':
                await session.send('登陆成功!')
                await session.send(res)
            else:
                await session.send('用户名或密码错误,登陆失败!')
        else:
            await session.finish('格式错误,终止会话!')

@on_command('cancel',aliases='取消预约',permission=PRIVATE)
async def cancel(session = CommandSession):
    qid = session.event["user_id"]
    requests.get(cancel_url.format(qid))
    await session.send('取消成功')
    await session.send(requests.get(user_status_url.format(qid)).text)

@on_command('grab',aliases='抢座',permission=PRIVATE)
async def grab(session = CommandSession):
    await session.send('正在抢座,可能需要一些时间~')
    qid = session.event["user_id"]
    res = requests.get(grab_url.format(qid))
    if res.status_code == 200:
        await session.send('抢座成功')
        await session.send(res.text)
    else:
        await session.send('抢座失败,请重新尝试!')

