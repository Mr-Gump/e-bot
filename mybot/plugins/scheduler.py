from datetime import datetime
from os import path
import cn2an
import os
import shutil
import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot import on_command, CommandSession

__plugin_name__ = '整点报时'
__plugin_usage__ = r"""
整点报时

1.开启整点报时
格式：启动整点报时
2.关闭整点报时
格式：关闭整点报时
"""

bot = nonebot.get_bot()
group_id = bot.config.GROUP_ID
enable_clock = False

@nonebot.scheduler.scheduled_job('cron' , hour='*')
async def _():
    if not enable_clock:
        return
    now = datetime.now()
    try:
        await bot.send_group_msg(group_id=group_id ,
                                 message=f'现在{cn2an.an2cn(now.hour)}点整啦!')
        await bot.send_group_msg(group_id=group_id ,
                                 message='[CQ:image,file=c88e98e18b77b4951d5bede4a186f4ae.image,url=http://c2cpicdw.qpic.cn/offpic_new/2424659013//2424659013-2207874604-C88E98E18B77B4951D5BEDE4A186F4AE/0?term=3]')
    except CQHttpError:
        print('------遇到错误------')
        pass


@nonebot.scheduler.scheduled_job('cron' , hour="4")
async def _():
    img_cache_dir = path.join(path.dirname(__file__) , 'borrow_and_return' , 'img_cache')
    shutil.rmtree(img_cache_dir)
    os.mkdir(img_cache_dir)
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=group_id ,
                             message=f'Duang!图片缓存已清理!')

@on_command('关闭整点报时',only_to_me=False)
async def stop_clock(session=CommandSession):
    global enable_clock
    enable_clock= False
    await session.finish('已关闭整点报时[CQ:face,id=111]')

@on_command('启动整点报时',only_to_me=False)
async def start_clock(session=CommandSession):
    global enable_clock
    enable_clock = True
    await session.finish('已开启整点报时[CQ:face,id=175]')