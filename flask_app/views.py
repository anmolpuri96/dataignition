from flask import render_template, request, redirect
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

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    if request.url.startswith('dataignition'):
        url = "https://"+request.url
        code = 301
        return redirect(url, code=code)

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
        scores = []
        count = 0
        # ids = ["3131957", "2274158", "", "", ""]
        for id in id_map_redis.scan_iter('id:*'):
            id = id
            id = id.decode('UTF-8')
            score_dict = {}
            id = id.split(":")[-1]
            score_dict['url'] = "https://stackoverflow.com/questions/{}".format(id)
            score_dict['url2'] = "http://dataignition.tech?id={}".format(id)
            score_dict['id'] = id
            scores.append(score_dict)
            if count == 4:
                break
            count += 1
        for score in scores:
            page = requests.get(score['url'])
            add_html_body(page, score)
        return render_template('intial_home.html', scores=scores)
    if "stackoverflow.com" in id:
        split_url = id.split("/")
        questions_idx = split_url.index("questions")
        id = split_url[questions_idx+1]
    limit = request.args.get('limit')
    if not limit:
        limit = 3
    try:
        limit = int(limit)
    except:
        message = '''Invalid input "{}" for limit'''.format(limit)
        return render_template('no_posts_found.html', message=message)

    scores = []
    unanswered_question = {}
    id = id.split(":")[-1]
    linked_ids = id_map_redis.smembers('id:{}'.format(id))
    if not linked_ids:
        message = '''No match found for id "{}"'''.format(id)
        return render_template('no_posts_found.html', message=message)
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
