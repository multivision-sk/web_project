# 돌리기 전에 kakao api 와 client id / secret 추가하기 !!!!

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import requests
# from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.dbhairhere

SECRET_KEY = 'apple'

import jwt

import datetime

import hashlib


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_shop')
def get_shop():
    return render_template('index_shop.html')


@app.route('/get_style')
def get_style():
    return render_template('index_style.html')


@app.route('/get_review')
def get_review():
    return render_template('index_review.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/shop', methods=['POST'])
def post_shop():
    searching = request.form['search_input']
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {

        "Authorization": "KakaoAK 55e7f20c7f8ea3c682fa473fc5d52869"  # 돌리기 전에 api key 추가하기 !!

    }
    places = requests.get(url, headers=headers).json()['documents']

    db.shops.drop()

    for shop in places:
        shop_name = shop['place_name']
        shop_url = shop['place_url']

        doc = {
            'shop_name': shop_name,
            'shop_url': shop_url
        }

        db.shops.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/shop', methods=['GET'])
def read_shop():
    shops = list(db.shops.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'shops': shops})


@app.route('/style', methods=['POST'])
def post_style():
    searching = request.form['search_input']

    db.styles.drop()

    # 돌리기 전에 secret key에서 client id 와 client secret 추가하기 !!!
    client_id = '3cM33RVzsCGd7lI0ZmCU'
    client_secret = 'KoezOPz8XR'

    url = "https://openapi.naver.com/v1/search/image?query={}&display=30".format(searching)
    headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
    contents = requests.get(url, headers=headers).json()['items']

    for style in contents:
        style_url = style['thumbnail']
        img_url = style['link']

        doc = {

            'style_url': style_url,
            'img_url': img_url

        }

        db.styles.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/style', methods=['GET'])
def read_style():
    styles = list(db.styles.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'styles': styles})


@app.route('/review', methods=['POST'])
def write_review():
    hair_shop = request.form['shop']
    hair_style = request.form['style']
    hair_date = request.form['date']
    hair_comment = request.form['comment']
    token_receive = request.form['token_give']

    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(payload)

    userinfo = db.reguser.find_one({'id': payload['id']}, {'_id': 0})

    doc = {
        'shop': hair_shop,
        'style': hair_style,
        'date': hair_date,
        'comment': hair_comment,
        'like': 0,
        'hate': 0,
        'user': userinfo['nick']

    }

    db.all.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/review', methods=['GET'])
def read_review():
    all_memo = list(db.all.find({}, {'_id': False}).sort('date', 1))

    return jsonify({'result': 'success', 'comments': all_memo})


@app.route('/api/like', methods=['POST'])
def like_post():
    shop_receive = request.form['shop_give']
    style_receive = request.form['style_give']
    date_receive = request.form['date_give']
    user_receive = request.form['user_give']

    shop_like = db.all.find_one({'shop': shop_receive,'style': style_receive,'date': date_receive,'user': user_receive})
    new_like = shop_like['like'] + 1
    db.all.update_one({'shop': shop_receive,'style': style_receive,'date': date_receive,'user': user_receive}, {'$set': {'like': new_like}})

    return jsonify({'result': 'success'})


@app.route('/api/hate', methods=['POST'])
def hate_post():
    shop_receive = request.form['shop_give']
    style_receive = request.form['style_give']
    date_receive = request.form['date_give']
    user_receive = request.form['user_give']

    shop_hate = db.all.find_one({'shop': shop_receive,'style': style_receive,'date': date_receive,'user': user_receive})
    new_hate = shop_hate['hate'] + 1
    db.all.update_one({'shop': shop_receive,'style': style_receive,'date': date_receive,'user': user_receive}, {'$set': {'hate': new_hate}})

    return jsonify({'result': 'success'})


@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    doc = {
        'id': id_receive,
        'pw': pw_hash,
        'nick': nickname_receive
    }

    db.reguser.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.reguser.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=3)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.headers['token_give']
    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db.reguser.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
