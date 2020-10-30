from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


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


@app.route('/shop', methods=['POST'])
def post_shop():

    searching = request.form['search_input']
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {
        "Authorization": "KakaoAK appkey"
    }
    places = requests.get(url, headers=headers).json()['documents']

    db.shops.drop()

    for shop in places:
        shop_name = shop['place_name']
        shop_url = shop['place_url']

        doc = {
            'shop_name': shop_name ,
            'shop_url' : shop_url
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
    url = 'https://dapi.kakao.com/v2/search/image.json?query={}'.format(searching)
    headers = {
        "Authorization": "KakaoAK appkey"
    }
    contents = requests.get(url, headers=headers).json()['documents']

    db.styles.drop()

    for style in contents:

        style_url = style['thumbnail_url']

        doc = {

            'style_url' : style_url
        }

        db.styles.insert_one(doc)


    return jsonify({'result': 'success'})



@app.route('/style', methods=['GET'])
def read_style():
    styles = list(db.styles.find({}, {'_id': False}))

    return jsonify({'result': 'success', 'styles': styles})




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
