#!/bin/bash

# This script is used to extract the xml files out of the .7z files
url=$1

echo $url

echo "Unzipping the 7z file"
file_name=$(echo $url | rev | cut -d '/' -f 1 | rev)
just_file_name=$(echo $file_name | rev | cut -d '.' -f2- | rev)

echo $file_name
7za e $file_name
echo "Unzipping complete"
echo "rename xml files"
links_file="links$just_file_name.xml"
posts_file="posts$just_file_name.xml"
badges_file="badges$just_file_name.xml"
comments_file="comments$just_file_name.xml"
post_history_file="phist$just_file_name.xml"
tags_file="tags$just_file_name.xml"
users_file="users$just_file_name.xml"
votes_file="votes$just_file_name.xml"

mv PostLinks.xml $links_file
mv Posts.xml $posts_file
mv Comments.xml $comments_file
mv Badges.xml $badges_file
mv Tags.xml $tags_file
mv PostHistory.xml $post_history_file
mv Votes.xml $votes_file
mv Users.xml $users_file

echo "rename complete"

echo "Delete the files"

rm -r *.7z
