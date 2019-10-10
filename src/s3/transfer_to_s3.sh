#!/bin/bash

# This script is used to redirect the archives in the urls of the txt file to the amazon s3 bucket

input=$HOME'/urls_list.txt'
echo $input
while read url
do

    the_url=""${url}""
    echo $the_url
    echo "Transferring to S3"
    file_name=$(echo $url | rev | cut -d '/' -f 1 | rev)
    echo $file_name
    wget -qO- $the_url | aws s3 cp - s3://dataignition-tech/$file_name

    #echo "Transfer Complete"
done < "$input"
