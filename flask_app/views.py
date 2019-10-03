from flask import render_template, request
from flask_app import app
# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
# import pandas as pd
# import psycopg2
import requests
import redis
from bs4 import BeautifulSoup

# user = 'postgres' #add your username here (same as previous postgreSQL)
# host = db_config.host
# port = db_config.port
# dbname = db_config.dbname
# password = db_config.password
# con = None
id_map_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2, health_check_interval=30)
# con = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2)

@app.route('/')
@app.route('/index')
def index():
    def add_html_body(page, question_dict):
        soup = BeautifulSoup(page.content, 'html.parser')

        # body
        body = soup.select_one('body')

        question_links = body.select("h1 a.question-hyperlink")
        questions = [i.text for i in question_links]
        question_dict['title'] = questions[:2][0]

        summary_divs = body.select("div.post-text")
        summaries = [i.text.strip() for i in summary_divs]
        question_dict['body'] = summaries[0]

    id = request.args.get('id')
    if not id:
        # for id in id_map_redis.scan_iter('id:*'):
        #     id = id
        #     id = id.decode('UTF-8')
        #     break
        return render_template('intial_home.html', id=id)
    if "stackoverflow.com" in id:
        split_url = id.split("/")
        questions_idx = split_url.index("questions")
        id = split_url[questions_idx+1]
    limit = request.args.get('limit')
    if not limit:
        limit = 5
    try:
        limit = int(limit)
    except:
        return render_template('no_posts_found.html', id=id)

    scores = []
    unanswered_question = {}
    id = id.split(":")[-1]
    linked_ids = id_map_redis.smembers('id:{}'.format(id))
    if not linked_ids:
        return render_template('no_posts_found.html', id=id)
    unanswered_question['id'] = id
    unanswered_question['url'] = "https://stackoverflow.com/questions/{}".format(id)

    page = requests.get(unanswered_question['url'])
    add_html_body(page, unanswered_question)

    for id in linked_ids:
        id = id.decode('UTF-8')
        score = id.split("_")[1]
        id = id.split("_")[0]
        score_dict = {}

        score_dict['url'] = "https://stackoverflow.com/questions/{}".format(id)
        score_dict['id'] = id
        score_dict['score'] = "{0:.2f}".format(float(score)-0.1)
        scores.append(score_dict)
    scores = sorted(scores, key=lambda k: k['score'], reverse=True)[:limit]
    for score in scores:
        page = requests.get(score['url'])
        add_html_body(page, score)
    return render_template('index.html', scores=scores, unanswered_question=unanswered_question)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guide')
def guide():
    return render_template('api_guide.html')
