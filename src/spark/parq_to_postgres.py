from pyspark import SparkConf, SparkContext
from pyspark.sql.session import SparkSession

from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as f
import re,html
from pyspark.sql.functions import broadcast

"""
This pyspark script performs the joins between the questions which has the response times and the pagerank dataframe of
the post(question) links which is then pushed to the postgresql database
"""
def main():
  sc = SparkContext(conf=SparkConf().setAppName("se"))
  spark = SparkSession.builder.appName("se").getOrCreate()
  #read in the links parquet file
  # links = spark.read.load("s3a://dataignition-tech-xml-parq/pr_se_links.parquet")
  #read in the posts parquet file
  posts = spark.read.parquet("s3a://dataignition-tech-xml-parq/posts.parquet/_temporary")
  #filter the questions:
  questions = posts.filter((f.col('PostTypeId')==1)).filter((f.col('AcceptedAnswerId').isNotNull()))
  questions_subset = questions.select('Id','AcceptedAnswerId','Tags','CreationDate', 'Community')
  #filter the answers in another dataframe
  answers = df3.filter((f.col('PostTypeId')==2))
  #rename the answer dataframe columns
  answers_subset = answers.select("Id","CreationDate","Community")
  new_names = ['AnsId', 'AnsCreationDate','AnsCommunity']
  answers_subset = answers_subset.toDF(*new_names)
  #perform a join on the questions df and the answer df based on the common answer id
  qa_deets = questions_subset.join(answers_subset,(answers_subset.AnsCommunity == all_questions.Community) & (questions_subset.AcceptedAnswerId == answers_subset.AnsId))

  timeFmt = "yyyy-MM-dd' 'HH:mm:ss.SSS"
  timeDiff = (f.unix_timestamp('AnsCreationDate', format=timeFmt)
            - f.unix_timestamp('CreationDate', format=timeFmt))
  #divide duration by seconds to convert it to milli- minutes
  qa_deets = qa_deets.withColumn("Duration", timeDiff/60)

  qa_deets_subset = qa_deets.select("Id",  "Tags","CreationDate","Community", "Duration")
  #filter off questions which have no answers
  questions_null = df3.filter((f.col('PostTypeId')==1)).filter((f.col('AcceptedAnswerId').isNull()))
  questions_null_subset = questions_null.select('Id','Tags','CreationDate','Community')
  questions_null_duration = questions_null_subset.withColumn('Duration', lit(None).cast(DoubleType()))
  #combine all questions; questions with answers and question with no answers
  all_questions = qa_deets_subset.union(questions_null_duration)
  all_questions = all_questions.withColumn('post_create_date',all_questions['CreationDate'].cast('date'))
  all_questions = all_questions.withColumnRenamed('id','COMMUNITY_QUESTION_ID')
  all_questions_subset = all_questions.select('COMMUNITY_QUESTION_ID','Community','Tags', 'post_create_date')
  all_questions_subset.show()

  # links  = links.withColumnRenamed("community","lcommunity")
  # """ perform a join based on community and the question id to combine the pagerank score and
  #     response time duration in one dataframe
  # """
  # cred_tags = all_questions.join(broadcast(links), (links.id == all_questions.COMMUNITY_QUESTION_ID) & (all_questions_subset.Community == links.lcommunity), "left_outer")
  # #rename columns as per postgresql schema, round off values and write to the database:
  # total_df = cred_tags.select("COMMUNITY_QUESTION_ID","Community","post_create_date","Tags","Duration","cred_score")
  # total_df  = total_df.withColumn("duration",f.round(total_df["Duration"],2))
  # total_df  = total_df.withColumn("pr_score",f.round(total_df["cred_score"],3))
  # total_df  = total_df.withColumnRenamed("COMMUNITY_QUESTION_ID","qid")
  # total_df  = total_df.withColumnRenamed("Community","community")
  # total_df  =  total_df.withColumnRenamed("Tags","tags")
  # total_df  = total_df.withColumnRenamed("post_create_date","create_date")
  # total_df_reqd = total_df.select("qid","tags","community","duration","create_date","pr_score")
  # total_df_reqd.write.format("jdbc").mode("append") .option("url", "jdbc:postgresql://hostname/ls?user=xxx&password=xxx").option("dbtable", "questions").option("user", "postgres").option("password", "xxx").save()
  spark.catalog.clearCache()

if __name__ == "__main__":
  main()
