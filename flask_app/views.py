from flask import render_template, request
from flask_app import app
# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
# import pandas as pd
# import psycopg2
import requests
import redis
# from bs4 import BeautifulSoup

# user = 'postgres' #add your username here (same as previous postgreSQL)
# host = db_config.host
# port = db_config.port
# dbname = db_config.dbname
# password = db_config.password
# con = None
id_map_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2)
# con = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2)

@app.route('/')
@app.route('/index')
def index():
    id = request.args.get('id')
    if not id:
        for id in id_map_redis.scan_iter('id:*'):
            id = id
            id = id.decode('UTF-8')
            break
    if "stackoverflow.com" in id:
        split_url = id.split("/")
        questions_idx = split_url.index("questions")
        id = split_url[questions_idx+1]
    limit = request.args.get('limit')
    if not limit:
        limit = 5
    limit = int(limit)

    scores = []
    unanswered_question = {}
    id = id.split(":")[-1]
    linked_ids = id_map_redis.smembers('id:{}'.format(id))
    unanswered_question['id'] = id
    unanswered_question['url'] = "https://stackoverflow.com/questions/{}".format(id)
    for id in linked_ids:
        id = id.decode('UTF-8')
        score = id.split("_")[1]
        id = id.split("_")[0]
        score_dict = {}

        score_dict['url'] = "https://stackoverflow.com/questions/{}".format(id)
        score_dict['id'] = id
        score_dict['score'] = score
        scores.append(score_dict)
    scores = sorted(scores, key=lambda k: k['score'], reverse=True)[:limit]
    return render_template('index.html', scores=scores, unanswered_question=unanswered_question)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guide')
def guide():
    return render_template('api_guide.html')
