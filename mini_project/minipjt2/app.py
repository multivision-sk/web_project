from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbmini1


@app.route('/')
def homework():
    return render_template('index.html')


@app.route('/paper', methods=['POST'])
def post_paper():
    url_receive = request.form['url_give']
    date_receive = request.form['date_give']
    comment_receive = request.form['comment_give']


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[property="og:description"]')

    title = og_title['content']
    abstract = og_description['content']

    doc = {
        'title': title,
        'date': date_receive,
        'comment': comment_receive,
        'abstract' : abstract
    }

    db.papers.insert_one(doc)

    return jsonify({'result': 'success'})


@app.route('/paper', methods=['GET'])
def view_paper():
    results = list(db.papers.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'papers': results})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
