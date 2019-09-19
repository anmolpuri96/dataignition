# !/bin/bash

export PYSPARK_PYTHON=python3;
/usr/local/spark/bin/spark-submit \
   --master spark://ec2-3-228-180-18.compute-1.amazonaws.com:7077 \
   --executor-memory 6G \
   /home/ubuntu/dataignition-tech/src/spark/posts_xml_to_parq.py
