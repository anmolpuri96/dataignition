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
from pyspark.sql import SQLContext
from pyspark.sql.types import StructType, StructField, StringType
import pyspark.sql.functions as F

from pyspark.sql.types import IntegerType, FloatType, ArrayType

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config")
# import config

def compare_text(overlap_threshold=0.9):
    """
    Overview: read in MinHash Values for articles, group by category, and find overlaps in MinHash values

    Input: optional threshold for overlap scores. If two articles are above this threshold, they are written to the Postgres database (default 0.9)
    Output: none
    """
    # cf = configparser.ConfigParser()
    # cf.read('../config/db_properties.ini')
    #
    # # Set up postgres connection for writing similarity scores
    # connection = psycopg2.connect(host=cf['postgres']['url_results'], database='similarity_scores', user=cf['postgres']['user'], password=cf['postgres']['password'])
    # cursor = connection.cursor()

    # Set up redis connection
    unanswered_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=1)

    # For each category, go through each unanswered post and output the answered ones with a high enough minhash overlap to redis

    #Need to distribute this using spark somehow (maybe spark-redis?)
    categories = []
    for category in unanswered_redis.scan_iter('cat:*'):
        categories.append(category)
    dist_categories = sc.parallelize(categories)

    def calculate_overhead_for_category(category_partition):
        # Set up redis connections
        answered_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=0)
        unanswered_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=1)
        id_map_redis = redis.StrictRedis(host="ec2-52-73-233-196.compute-1.amazonaws.com", port=6379, db=2)
        for category in category_partition:
            answered_members = answered_redis.smembers(category)
            if answered_members:
                answered_ids = eval(list(answered_members)[0])
                unanswered_ids = eval(list(unanswered_redis.smembers(category))[0])
                temp = list(itertools.product(unanswered_ids, answered_ids))
                id_pairs = []
                for elem in temp:
                    if elem[0]!= elem[1]:
                        id_pairs.append(elem)
                print(category)

                for ids in id_pairs:
                    minhash1 = unanswered_redis.smembers('id:{}'.format(ids[0]))
                    if minhash1:
                        # print("minhash1")
                        minhash1 = ast.literal_eval(list(minhash1)[0].decode('utf-8'))
                        minhash2 = answered_redis.smembers('id:{}'.format(ids[1]))
                        if minhash2:
                            # print("minhash2")
                            minhash2 = ast.literal_eval(list(minhash2)[0].decode('utf-8'))
                            overlap = 1.0 * len(set(minhash1).intersection(set(minhash2)))/len(minhash1)
                            # print(overlap)
                            if overlap >= overlap_threshold:
                                print(overlap)
                                # print("overlap_threshold")
                                id_map_redis.sadd('id:{}'.format(ids[0]), "{0}_{1}".format(ids[1], overlap))
    dist_categories.foreachPartition(calculate_overhead_for_category)

def main():
    spark_conf = SparkConf().setAppName("Spark Custom MinHashLSH").set("spark.cores.max", "30")

    global sc
    global sql_context

    sc = SparkContext(conf=spark_conf)
    sc.setLogLevel("ERROR")
    sql_context = SQLContext(sc)
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
