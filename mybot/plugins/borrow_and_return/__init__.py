import os
import re
import shutil
import time
from math import ceil
from os import path
import pytab as pt
import matplotlib.pyplot as plt
import pandas as pd
import uuid
from nonebot import on_command, CommandSession
from nonebot.permission import *

__plugin_name__ = '设备借还登记'
__plugin_usage__ = r"""
设备、物品借还

1.添加设备（仅限管理员）
格式：添加 【设备】 x【数量】
例如：添加 王岳龙 x1
2.删除设备（仅限管理员）
格式：删除 【设备】 x【数量】
例如：删除 王岳龙 x1
3.查看设备
格式：查看设备列表
4.查看日志（所有操作记录）
格式：查看日志
5.借出设备
格式：借出 【设备】 x【数量】
例如：借出 王岳龙 x1
6.归还设备
格式：还回 【设备】 x【数量】
例如：还回 王岳龙 x1
7.查看我的清单（借还记录）
格式：查看我的清单
8.查看群成员清单（仅限管理员）
格式：查看清单 【@xxx】
例如：查看清单 @洪博晖
9.清空所有记录（仅限超级用户）
格式:清空所有记录
"""

plt.rcParams['font.sans-serif'] = ['simhei']

devs_path = path.join(path.dirname(__file__), 'devs.csv')
logs_path = path.join(path.dirname(__file__), 'logs.csv')
notes_dir_path = path.join(path.dirname(__file__), 'notes')
img_cache_path = path.join(path.dirname(__file__), 'img_cache')


@on_command('add_dev', aliases=['添加', '增加'], only_to_me=False, permission=GROUP_ADMIN)
async def add_device(session=CommandSession):
    item_to_add = session.state['item']
    num = session.state["num"]
    now = session.state['time']
    items = await get_list()
    flag = False
    for item in items[1:]:
        if item[0] == item_to_add:
            item[1] = str(int(item[1]) + num)
            flag = True
    if not flag:
        items.append([item_to_add, str(num), now])
    await write_csv(items)
    await session.send(f'⭕{num}个{item_to_add}已加入成功! \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await take_to_log(','.join([str(session.event['user_id']), '添加', item_to_add, str(num), now]))
    await session.send(f'已计入日志!\n[ {time.strftime("%Y %m %d %X" , time.localtime())}]')
    await show_devices(session)


@add_device.args_parser
async def _(session=CommandSession):
    args = session.current_arg.strip().split(' ')
    if len(args) != 2 or args[1][0] != 'x':
        await session.send('请重新输入,例如:\n添加 王岳龙 x1')
        session.finish()
    else:
        session.state['item'] = args[0]
        session.state["num"] = int(args[1][1:])
        session.state['time'] = time.strftime("%Y.%m.%d", time.localtime())


@on_command('del_dev', aliases=['删除','移除'], only_to_me=False, permission=GROUP_ADMIN)
async def del_device(session=CommandSession):
    item_to_add = session.state['item']
    num = session.state["num"]
    now = session.state["time"]
    items = await get_list()
    flag = False
    for item in items[1:]:
        if item[0] == item_to_add:
            if int(item[1]) - num > 0:
                item[1] = str(int(item[1]) - num)
                item[2] = now
                flag = True
            elif int(item[1]) - num == 0:
                items.pop(items.index(item))
                flag = True
            else:
                await session.send('没这么多你删个🔨,重删!')
                await session.finish()
    if not flag:
        await session.send('没有这个东西你删个🔨')
        await session.finish()
    await write_csv(items)
    await session.send(f'⭕{num}个{item_to_add}已删除成功! \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await take_to_log(','.join([str(session.event['user_id']), '删除', item_to_add, str(num), now]))
    await session.send(f'已计入日志! \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await show_devices(session)


@on_command('show_dev', aliases=['查看设备列表', '打印设备列表'], only_to_me=False, permission=GROUP_MEMBER)
async def show_devices(session=CommandSession):
    img_path = await gen_img(devs_path, '设备清单')
    msg = ''.join([f'[CQ:image,file={img}]' for img in img_path])
    await session.send(msg)


@del_device.args_parser
async def _(session=CommandSession):
    args = session.current_arg.strip().split(' ')
    session.state['time'] = time.strftime("%Y.%m.%d", time.localtime())
    if len(args) != 2 or args[1][0] != 'x':
        await session.send('格式错误,请重新输入,例如:\n删除 王岳龙 x1')
        await session.finish()
    else:
        session.state['item'] = args[0]
        try:
            session.state["num"] = int(args[1][1:])
        except BaseException:
            await session.send('可以整一个人能看懂的数🐴')
            await session.finish()


async def get_list():
    with open(devs_path, 'r', encoding='utf-8') as File:
        lines = File.readlines()
    data = [[line.split(',')[0], line.split(',')[1], line.split(',')[2].strip('\n')] for line in lines]
    return data


async def write_csv(items):
    with open(devs_path, 'w', encoding="utf-8") as File:
        for item in items:
            File.write(','.join(item) + '\n')


@on_command('borrow', aliases=['借出', '借'], only_to_me=False, permission=GROUP_MEMBER)
async def borrow_device(session=CommandSession):
    item_to_add = session.state['item']
    num = session.state["num"]
    now = session.state["time"]
    items = await get_list()
    flag = False
    for item in items[1:]:
        if item[0] == item_to_add:
            if int(item[1]) - num > 0:
                item[1] = str(int(item[1]) - num)
                item[2] = now
                flag = True
            elif int(item[1]) - num == 0:
                item[1] = '0'
                flag = True
            else:
                await session.send('没这么多你借个🔨,重删!')
                await session.finish()
    if not flag:
        await session.send('没有这个东西你借个🔨')
        await session.finish()
    await write_csv(items)
    await session.send(f'⭕{num}个{item_to_add}已借出成功! \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await write_to_my_note(session.event['user_id'], ','.join(['借', item_to_add, str(num), now]))
    await take_to_log(','.join([str(session.event['user_id']), '借出', item_to_add, str(num), now]))
    await session.send(f'已计入日志!记得归还哦[CQ:face,id=224] \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await show_devices(session)


@borrow_device.args_parser
async def _(session=CommandSession):
    args = session.current_arg.strip().split(' ')
    session.state['time'] = time.strftime("%Y.%m.%d", time.localtime())
    if len(args) != 2 or args[1][0] != 'x':
        await session.send('格式错误,请重新输入,例如:\n借出 王岳龙 x1')
        await session.finish()
    else:
        session.state['item'] = args[0]
        try:
            session.state["num"] = int(args[1][1:])
        except BaseException:
            await session.send('可以整一个人能看懂的数🐴')
            await session.finish()


async def take_to_log(log):
    with open(logs_path, 'a', encoding="utf-8") as File:
        File.writelines(log + '\n')


@on_command('show_logs', aliases=['查看日志','打印日志'], only_to_me=False, permission=GROUP_MEMBER)
async def show_logs(session=CommandSession):
    img_path = await gen_img(logs_path, '日志')
    msg = ''.join([f'[CQ:image,file={img}]' for img in img_path])
    await session.send(msg)


@on_command('give_back', aliases=['还回', '归还', '还'], only_to_me=False, permission=GROUP_MEMBER)
async def give_back_device(session=CommandSession):
    item_to_add = session.state['item']
    num = session.state["num"]
    now = session.state['time']
    items = await get_list()
    flag = False
    for item in items[1:]:
        if item[0] == item_to_add:
            item[1] = str(int(item[1]) + num)
            flag = True
    if not flag:
        await session.send('❌这个东西还没添加到设备列表,联系管理员添加后再归还吧!')
        await session.finish()
    await check_ligal(session, session.event['user_id'], item_to_add, num)
    await write_csv(items)
    await session.send(f'⭕{num}个{item_to_add}已归还成功! \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await take_to_log(','.join([str(session.event['user_id']), '归还', item_to_add, str(num), now]))
    await write_to_my_note(session.event['user_id'], ','.join(['还', item_to_add, str(num), now]))
    await session.send(f'已计入日志和你的清单!欢迎下次再借[CQ:face,id=227] \n[{time.strftime("%Y %m %d %X" , time.localtime())}]')
    await show_devices(session)


@give_back_device.args_parser
async def _(session=CommandSession):
    args = session.current_arg.strip().split(' ')
    if len(args) != 2 or args[1][0] != 'x':
        await session.send('请重新输入,例如:\n还回 王岳龙 x1')
        session.finish()
    else:
        session.state['item'] = args[0]
        session.state["num"] = int(args[1][1:])
        session.state['time'] = time.strftime("%Y.%m.%d", time.localtime())


async def write_to_my_note(qid, log):
    my_note_path = path.join(notes_dir_path, f'{qid}.csv')
    if path.exists(my_note_path):
        with open(my_note_path, "a", encoding="utf-8") as f:
            f.writelines(log + '\n')
    else:
        with open(my_note_path, "a", encoding="utf-8") as f:
            f.writelines('类型,设备\\物品,数量,时间\n')
            f.writelines(log + '\n')


@on_command('show_note', aliases=['查看我的清单', '打印我的清单'], only_to_me=False, permission=GROUP_MEMBER)
async def show_note(session=CommandSession):
    qid = session.event['user_id']
    my_note_path = path.join(notes_dir_path, f'{qid}.csv')
    if path.exists(my_note_path):
        img_path = await gen_img(my_note_path, f"{qid}的借还清单")
        await session.send(''.join([f'[CQ:image,file={img}]' for img in img_path]))

    else:
        with open(my_note_path, "w", encoding="utf-8") as f:
            f.write('类型,设备\\物品,数量,时间\n')
        await session.send('文件不存在,已为您新建清单~')


async def get_sumary(qid):
    my_note_path = path.join(notes_dir_path, f'{qid}.csv')
    sumary = {}

    with open(my_note_path, "r") as f:
        lines = f.readlines()
        if len(lines) > 1:
            for line in lines[1:]:
                line = line.strip('\n').split(',')
                if line[0] == '借':
                    if line[1] in sumary:
                        sumary[line[1]] += int(line[2])
                    else:
                        sumary[line[1]] = int(line[2])
                else:
                    sumary[line[1]] -= int(line[2])

    return sumary


async def check_ligal(session, qid, item, num):
    sumary = await get_sumary(qid)
    if item not in sumary:
        await session.send(f'{item}是你变出来的🐴')
        await session.finish()

    if sumary[item] < num:
        await session.send(f'你一共只有{sumary[item]}个{item},以为我不知道🐴')
        await session.finish()


@on_command('refresh', aliases=['清空所有记录','清空全部记录'], only_to_me=False, permission=SUPERUSER)
async def refresh(session=CommandSession):
    dir_path = path.dirname(__file__)
    with open(devs_path, "w") as f:
        f.write('设备/物品,数量,变更时间\n')
    with open(logs_path, "w") as f:
        f.write('发起人,类型,设备/物品,数量,录入时间\n')
    shutil.rmtree(notes_dir_path)
    os.mkdir(path.join(dir_path, 'notes'))
    await session.send('Bang！记录已全部清空！')


@refresh.args_parser
async def _(session=CommandSession):
    if session.is_first_run:
        await session.pause('确定请回复:我确定')

    if '我确定' in session.current_arg_text:
        pass
    else:
        await session.finish('删除失败!')


@on_command('show_user_note', aliases=['查看记录','打印记录'], only_to_me=False, permission=GROUP_MEMBER)
async def show_user_note(session=CommandSession):
    qid = session.state['qid']
    my_note_path = path.join(notes_dir_path, f'{qid}.csv')
    if path.exists(my_note_path):
        await session.send(f'[CQ:image,file={await gen_img(my_note_path,f"{qid}的借还清单")}]')

    else:
        with open(my_note_path, "w", encoding="utf-8") as f:
            f.write('类型,设备\\物品,数量,时间\n')
        await session.send('文件不存在,已为您新建清单~')


@show_user_note.args_parser
async def _(session=CommandSession):
    splited_args = session.current_arg
    try:
        qid = re.search('\\d{9,11}', splited_args).group()
    except BaseException:
        if session.is_first_run:
            session.pause('请@你要查询的群成员~')
        else:
            session.finish()
    session.state['qid'] = qid


async def gen_img(file_path, title):
    Data = pd.read_csv(file_path)
    base_url = 'http://8.135.14.64:5000/'
    lines = Data.shape[0]
    size = 5
    pages = ceil(lines / size)
    img_urls = []

    for page in range(pages):
        if page != pages - 1:
            data = {column: list(Data[column])[page * 5:5 * (page + 1)] for column in Data.columns}
        else:
            data = {column: list(Data[column])[page * 5:] for column in Data.columns}
        uid = str(uuid.uuid4())
        img_path = os.path.join(img_cache_path, f'{uid}.png')

        for column in data:
            if not len(data[column]):
                data[column] = ['...']

        pt.table(
            data=data,
            th_type='dark',
            table_type='striped'
        )

        plt.title(title+'_'+str(page+1))
        pt.save(img_path,dpi=300)
        img_url = base_url + f"{uid}.png"
        img_urls.append(img_url)

    return img_urls


