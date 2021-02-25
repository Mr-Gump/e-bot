from flask import Flask,request
from funcs import *
app = Flask(__name__)

@app.route('/user_exists')
def user_exists():
    qid = request.args.get('qid')
    if qid in Account.current_account:
        return '检测到用户!'
    else:
        return '未检测到用户'


@app.route('/get_info')
def get_info():
    return get_available_seats()

@app.route('/login')
def login():
    qid = request.args.get('qid')
    username = request.args.get("username")
    password = request.args.get('password')
    try:
        user = Account(qid, username, password)
        return user.show_my_info()
    except:
        return '登陆失败!密码错误!'

@app.route('/cancel')
def cancel():
    qid = request.args.get('qid')
    user = Account.current_account[qid]
    user.get_my_status
    user.cancel_seat()
    return '取消成功'

@app.route('/grab')
def grab():
    qid = request.args.get('qid')
    user = Account.current_account[qid]
    return user.grab_seat()

@app.route('/show')
def show():
    qid = request.args.get('qid')
    user = Account.current_account[qid]
    return user.show_my_info()

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=12345,threaded=True,debug=False)
