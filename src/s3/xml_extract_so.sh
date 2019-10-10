#!/bin/bash
url=$1
#shell script to extract stackoverflow xml files
echo $url

echo "Unzipping the 7z file"
file_name=$(echo $url | rev | cut -d '/' -f 1 | rev)
#just_file_name=$(echo $file_name | rev | cut -d '.' -f2- | cut -d '-' -f2- | rev)
file_type=$(echo $file_name | rev | cut -d '-' -f-1 | rev)

echo $file_type
echo $file_name
7za e $file_name

echo "Unzipping complete"
echo "rename xml files"

if [ "$file_type" == "Votes.7z" ]
then
    mv Votes.xml "votesstackoverflow.com.xml"
fi

if [ "$file_type" == "Badges.7z" ]
then
    mv Badges.xml "badgesstackoverflow.com.xml"
fi

if [ "$file_type" == "Tags.7z" ]
then
    mv Tags.xml "tagsstackoverflow.com.xml"
fi

if [ "$file_type" == "Users.7z" ]
then
    mv Users.xml "usersstackoverflow.com.xml"
fi

if [ "$file_type" == "Posts.7z" ]
then
    mv Posts.xml "postsstackoverflow.com.xml"
fi

if [ "$file_type" == "PostLinks.7z" ]
then
    mv PostLinks.xml "linksstackoverflow.com.xml"
fi

if [ "$file_type" == "PostHistory.7z" ]
then
    mv PostHistory.xml "phiststackoverflow.com.xml"
fi

if [ "$file_type" == "Comments.7z" ]
then
    mv Comments.xml "commentsstackoverflow.com.xml"
fi

echo "rename complete"

echo "Delete the files"

rm -r *.7z
