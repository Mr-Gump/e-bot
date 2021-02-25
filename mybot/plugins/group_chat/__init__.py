import random
import re
from .funcs import get_reply_async
import nonebot
from nonebot import on_command, CommandSession, permission, NLPSession, on_natural_language

__plugin_name__ = '群聊增强'
__plugin_usage__ = r"""
群聊功能

1.禁言群成员
格式：禁言 【@xxx】 【x分钟】/【随机时间】
例如：禁言 @洪博晖 30分钟
2.解除禁言
格式：解除禁言 【@xxx】 
例如：解除禁言 @洪博晖 
3.自动回复问候语
例如：早上好
4.智能聊天
需要先开启聊天模式
开启命令：启动聊天模式
关闭命令：关闭聊天模式
"""

enable_chat = False
bot = nonebot.get_bot()


@on_command('ban_mem', aliases=['禁言'], only_to_me=False)
async def ban_mem(session=CommandSession):
    print(str(session.state))
    await bot.set_group_ban(group_id=session.event['group_id'], user_id=session.state['target_mem'],
                            duration=session.state['dura'] * 60)
    await session.send(f'遵命[CQ:face,id=282][CQ:at,qq={session.event["user_id"]}]')


@ban_mem.args_parser
async def _(session=CommandSession):
    splited_args = session.current_arg
    target_mem = re.search('\\d{9,11}', splited_args).group()
    session.state['target_mem'] = target_mem
    if '随机时间' in splited_args:
        session.state['dura'] = random.randint(1, 60)
    else:
        session.state['dura'] = int(re.search('(\\d+)分钟', splited_args).group(1))


@on_command('undo_ban_mem', aliases=['解除禁言'], only_to_me=False)
async def undo_ban_mem(session=CommandSession):
    print(str(session.state))
    await bot.set_group_ban(group_id=session.event['group_id'], user_id=session.state['target_mem'],
                            duration=session.state['dura'])
    await session.send(f'遵命[CQ:face,id=282][CQ:at,qq={session.event["user_id"]}]')
    await session.send(f'暂且放你一条生路[CQ:face,id=271][CQ:at,qq={session.state["target_mem"]}]')


@on_command('say_hello', patterns=['(早|中|午|上|下|晚).{0,2}(好|安)'],aliases=['拜拜','再见'], only_to_me=False, permission=nonebot.permission.GROUP_MEMBER)
async def say_hello(session=CommandSession):
    await session.send(re.sub('\[CQ:at.*?\]', '', session.event['raw_message']) + f'[CQ:face,id=74][CQ:at,qq={session.event["user_id"]}]')


@undo_ban_mem.args_parser
async def _(session=CommandSession):
    splited_args = session.current_arg
    target_mem = re.search('\\d{9,11}', splited_args).group()
    session.state['target_mem'] = target_mem
    session.state['dura'] = 0


@on_natural_language(only_to_me=False)
async def chat(session=NLPSession):
    if not enable_chat:
        return
    reply = await get_reply_async(re.sub('\[CQ:at.*?\]', '', session.event['raw_message']))
    await session.send(reply.replace('{br}','\n')+f'[CQ:at,qq={session.event["user_id"]}]')

@on_command('关闭聊天模式',only_to_me=False)
async def shut_up(session=CommandSession):
    global enable_chat
    enable_chat = False
    await session.finish('已关闭聊天[CQ:face,id=111]')

@on_command('启动聊天模式',only_to_me=False)
async def start_chat(session=CommandSession):
    global enable_chat
    enable_chat = True
    await session.finish('已开启聊天[CQ:face,id=175]')



