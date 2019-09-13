import boto3
import subprocess
import csv
#python script to download the .7z files from s3 and convert them to xml files
if __name__ == "__main__":
  bucket_name = "dataignition-tech"
  destination_bucket_name = "dataignition-tech-xml"
  file_path='/home/ubuntu/dataignition-tech/src/s3/urls_list.txt'
  urls_list = []
  with open(file_path, "r") as ins:
      for line in ins:
        urls_list.append(line.rstrip('\n'))
  for urls in urls_list:
    #retrieve the filename from the stackexchange website url:
      url_name= urls
      file_name= url_name.split("/")[-1]
      #download the file name from the s3 bucket

      print('Stage 1: Pull data from S3 bucket')
      s3 = boto3.client('s3')
      s3.download_file(bucket_name,file_name,file_name)
      print('Stage 2: Shell Script to extract the xml files from the .7z files')
      #shell script to convert the .7z file to .gz files
      if "stackoverflow.com-" in file_name:
         if "Badges" in file_name:
            xml_file_name_so = "badgesstackoverflow.com.xml"
         elif "Posts" in file_name:
            xml_file_name_so = "postsstackoverflow.com.xml"
         elif "Links" in file_name:
            xml_file_name_so = "linksstackoverflow.com.xml"
         elif "Tags" in file_name:
            xml_file_name_so = "tagsstackoverflow.com.xml"
         elif "Votes" in file_name:
            xml_file_name = "votesstackoverflow.com.xml"
         elif "Comments" in file_name:
            xml_file_name_so = "commentsstackoverflow.com.xml"
         elif "Users" in file_name:
            xml_file_name_so = "usersstackoverflow.com.xml"
         else:
            xml_file_name_so = "phiststackoverflow.com.xml"
         command = "/home/ubuntu/dataignition-tech/src/s3/xml_extract_so.sh " + urls
         process_output = subprocess.call([command],shell=True)

      else:
         #generate the corresponding xml file names
         xml_file_name_posts = "posts" + file_name[:-2] + "xml"
         xml_file_name_links = "links" + file_name[:-2] + "xml"
         xml_file_name_badges = "badges" + file_name[:-2] + "xml"
         xml_file_name_tags = "tags" + file_name[:-2] + "xml"
         xml_file_name_votes = "votes" + file_name[:-2] + "xml"
         xml_file_name_phist = "phist" + file_name[:-2] + "xml"
         xml_file_name_comments = "comments" + file_name[:-2] + "xml"
         command = "/home/ubuntu/dataignition-tech/src/s3/xml_extract_se.sh " + urls
         process_output = subprocess.call([command],shell=True)


      #upload the xml to the amazon s3 bucket
      print('Stage 3: Data Load to s3 stage')
      ds3 = boto3.resource('s3')
      if "stackoverflow.com-" in file_name:
         print('Loading to bucket ' + xml_file_name_so)
         ds3.meta.client.upload_file(xml_file_name_so, destination_bucket_name, xml_file_name_so)
      else:
         print('Loading to bucket ' + xml_file_name_posts)
         ds3.meta.client.upload_file(xml_file_name_posts, destination_bucket_name, xml_file_name_posts)
         print('Loading to bucket ' + xml_file_name_links)
         ds3.meta.client.upload_file(xml_file_name_links, destination_bucket_name, xml_file_name_links)
         print('Loading to bucket ' + xml_file_name_badges)
         ds3.meta.client.upload_file(xml_file_name_badges, destination_bucket_name, xml_file_name_badges)
         print('Loading to bucket ' + xml_file_name_tags)
         ds3.meta.client.upload_file(xml_file_name_tags, destination_bucket_name, xml_file_name_tags)
         print('Loading to bucket ' + xml_file_name_votes)
         ds3.meta.client.upload_file(xml_file_name_votes, destination_bucket_name, xml_file_name_votes)
         print('Loading to bucket ' + xml_file_name_badges)
        ds3.meta.client.upload_file(xml_file_name_badges, destination_bucket_name, xml_file_name_badges)
         print('Loading to bucket ' + xml_file_name_phist)
         ds3.meta.client.upload_file(xml_file_name_phist, destination_bucket_name, xml_file_name_phist)
         print('Loading to bucket ' + xml_file_name_comments)
         ds3.meta.client.upload_file(xml_file_name_comments, destination_bucket_name, xml_file_name_comments)

      print('Delete the xml files post upload')
      command = "rm *.xml"
  #process_output2 = subprocess.call([command],shell=True)
