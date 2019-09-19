from pyspark.sql.session import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import functions as f

from pyspark import SparkContext, SparkConf
import re, html
import boto3

"""spark script to read the posts .xml files of different stack exchange communities and convert them to parquet. """


def read_tags_raw(tags_string):  # converts <tag1><tag2> to ['tag1', 'tag2']
    return html.unescape(tags_string).strip('>').strip('<').split('><') if tags_string else []


def main():
    print("printing spark conf")
    print(SparkConf())
    sc = SparkContext(conf=SparkConf().setAppName("se"))
    spark = SparkSession.builder.appName("se").getOrCreate()
    pattern = re.compile(' ([A-Za-z]+)="([^"]*)"')
    parse_line = lambda line: {key: value for key, value in pattern.findall(line)}
    unescape = udf(lambda escaped: html.unescape(escaped) if escaped else None)

    read_tags = udf(read_tags_raw, ArrayType(StringType()))

    s3_client = boto3.client('s3')
    bucket = 'dataignition-tech-xml'

    response = s3_client.list_objects(Bucket=bucket)
    posts_xml = []
    for file in response['Contents']:
        name = file['Key']
        if "posts" in name.lower():
            posts_xml.append(name)

    xml_files = ["s3a://dataignition-tech-xml/" + post_xml for post_xml in posts_xml]

    posts_udf = spark.read.text(xml_files).where(col('value').like('%<row Id%')) \
        .select(udf(parse_line, MapType(StringType(), StringType()))('value').alias('value')) \
        .select(col('value.Id').cast('integer'),
                col('value.ParentId').cast('integer'),
                col('value.PostTypeId').cast('integer'),
                col('value.CreationDate').cast('timestamp'),
                col('value.Score').cast('integer'),
                col('value.ViewCount').cast('integer'),
                unescape('value.Body').alias('Body'),
                col('value.OwnerUserId').cast('integer'),
                col('value.LastActivityDate').cast('timestamp'),
                unescape('value.Title').alias('Title'),
                read_tags('value.Tags').alias('Tags'),
                col('value.CommentCount').cast('integer'),
                col('value.AnswerCount').cast('integer'),
                col('value.LastEditDate').cast('timestamp'),
                col('value.LastEditorUserId').cast('integer'),
                col('value.AcceptedAnswerId').cast('integer'),
                col('value.FavoriteCount').cast('integer'),
                col('value.OwnerDisplayName'),
                col('value.ClosedDate').cast('timestamp'),
                col('value.LastEditorDisplayName'),
                col('value.CommunityOwnedDate').cast('timestamp')
                )
    # file_name_df = spark.read.text(xml_files).where(col('value').like('%<row Id%')).select(input_file_name())
    # community_name_df = file_name_df.withColumn('Community',
    #                                             regexp_extract(col('input_file_name()'), './(posts)([\w\.]+).xml', 2))
    # clean_name_df_subset = community_name_df.select("Community")

    posts_udf_id = posts_udf.withColumn("iid", monotonically_increasing_id())
    posts_udf_id.limit(100)
    # clean_name_df_subset_id = clean_name_df_subset.withColumn("iid", monotonically_increasing_id())
    #
    # community_posts = posts_udf_id.join(clean_name_df_subset_id, posts_udf_id.iid == clean_name_df_subset_id.iid).drop(
    #     "iid")
    posts_udf_id.write.parquet("s3a://dataignition-tech-xml-parq/posts.parquet")
    spark.catalog.clearCache()


if __name__ == "__main__":
    main()
