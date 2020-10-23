from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.dbmini1


@app.route('/')
def homework():
    return render_template('index.html')


@app.route('/memory', methods=['POST'])
def make_memory():
    title_receive = request.form['title_give']
    image_receive = request.form['image_give']
    comment_receive = request.form['comment_give']

    doc = {
        'title': title_receive,
        'image': image_receive,
        'comment': comment_receive
    }

    db.memories.insert_one(doc)

    return jsonify({'result': 'success'})



@app.route('/memory', methods=['GET'])
def view_memory():
    memories = list(db.memories.find({},{'_id':0}))
    return jsonify({'result': 'success', 'memories': memories})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
