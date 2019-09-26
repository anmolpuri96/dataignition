import os
import sys
import time
# import configparser
import numpy as np
import mmh3
import itertools
import pickle
import redis
import ast
# import psycopg2
from termcolor import colored

from pyspark.conf import SparkConf
from pyspark.context import SparkContext
# from pyspark.sql import SQLContext
from pyspark.sql.functions import udf, col

from pyspark.sql.types import IntegerType, FloatType, ArrayType

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config")
# import config

def compare_text(overlap_threshold=0.6):
    """
    Overview: read in MinHash Values for articles, group by category, and find overlaps in MinHash values

    Input: optional threshold for overlap scores. If two articles are above this threshold, they are written to the Postgres database (default 0.6)
    Output: none
    """
    # cf = configparser.ConfigParser()
    # cf.read('../config/db_properties.ini')
    #
    # # Set up postgres connection for writing similarity scores
    # connection = psycopg2.connect(host=cf['postgres']['url_results'], database='similarity_scores', user=cf['postgres']['user'], password=cf['postgres']['password'])
    # cursor = connection.cursor()

    # Set up redis connection for reading in minhash values
    rdb0 = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=0)
    rdb1 = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=1)
    rdb2 = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2)

    # For each category, go through each pair of articles and write the ones with a high enough minhash overlap to a database
    for category in rdb1.scan_iter('cat:*'):
        answered_members = rdb0.smembers(category)
        if answered_members:
            print("answered_members")
            answered_ids = eval(list(answered_members)[0])
            unanswered_ids = eval(list(rdb1.smembers(category))[0])
            for ua_id in unanswered_ids:
                print(ua_id)
                minhash1 = rdb1.smembers('id:{}'.format(ua_id))
                if minhash1:
                    print("minhash1")
                    minhash1 = ast.literal_eval(list(minhash1)[0].decode('utf-8'))
                    for a_id in answered_ids:
                        minhash2 = rdb0.smembers('id:{}'.format(a_id))
                        if minhash2:
                            print("minhash2")
                            minhash2 = ast.literal_eval(list(minhash2)[0].decode('utf-8'))
                            overlap = 1.0 * len(set(minhash1).intersection(set(minhash2)))/len(minhash1)
                            print(overlap)
                            if overlap > overlap_threshold:
                                print("overlap_threshold")
                                rdb2.sadd('id:{}'.format(ua_id), a_id)


    # URL_HEADER = 'https://stackoverflow.com/questions/'
    # for category in rdb.scan_iter('cat:*'):
    #     pairs = list(itertools.combinations(eval(list(rdb.smembers(category))[0]), 2))
    #     print("Evaluating potential for {} pairs in category {}".format(len(pairs), category))
    #     for pair in pairs:
    #        minhash1 = rdb.smembers('id:{}'.format(pair[0]))
    #        minhash2 = rdb.smembers('id:{}'.format(pair[1]))
    #        if minhash1 and minhash2:
    #            minhash1 = ast.literal_eval(list(minhash1)[0].decode('utf-8'))
    #            minhash2 = ast.literal_eval(list(minhash2)[0].decode('utf-8'))
    #            overlap = 1.0 * len(set(minhash1).intersection(set(minhash2)))/len(minhash1)
    #            if overlap > overlap_threshold:
    #                url1 = URL_HEADER + pair[0]
    #                url2 = URL_HEADER + pair[1]
                   #print(category, url1, url2, overlap)
                   # cursor.execute('''INSERT INTO scores (id1, id2, score, category) VALUES (%s, %s, %s, %s)''', (url1, url2, overlap, str(category)))
                   # connection.commit()

def main():
    spark_conf = SparkConf().setAppName("Spark Custom MinHashLSH").set("spark.cores.max", "30")

    global sc
    # global sql_context

    sc = SparkContext(conf=spark_conf)
    sc.setLogLevel("ERROR")
    # sql_context = SQLContext(sc)
    # sc.addFile(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/lib/util.py")
    # sc.addFile(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.py")


    start_time = time.time()
    similarity_scores_df = compare_text(0.9)

    # config = configparser.ConfigParser()
    # config.read('../config/db_properties.ini')
    # similarity_scores_df.write.jdbc(config['postgres']['url'], config['postgres']['table'], mode='overwrite', properties={'user': config['postgres']['user'], 'password': config['postgres']['password']})

    end_time = time.time()
    print(colored("Spark MinHash run time (seconds): {0} seconds".format(end_time - start_time), "magenta"))


if(__name__ == "__main__"):
    main()
