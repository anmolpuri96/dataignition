# !/bin/bash

export PYSPARK_PYTHON=python3;
spark-submit \
  --master spark://10.0.0.7:7077 \
  /home/ubuntu/dataignition-tech/src/spark/posts_xml_to_parq.py \
  1000
