from bs4 import BeautifulSoup
import requests
from multiprocessing import Pool
import csv
import time
""" This script uses BeautifulSoup to parse the urls to the stackexchange file and store them in a text file """

if __name__ == '__main__':
 url = 'https://archive.org/download/stackexchange'
 response = requests.get(url)
 page_content = BeautifulSoup(response.text, "lxml")
 tabledatas = page_content.find_all("td")[1:]
 urls_list = []
 for tabledata in tabledatas:
   if len(tabledata.find_all("a"))>0 :
     if tabledata.find_all("a")[0]['href'][-3:] == '.7z':
       urls_list.append('https://archive.org/download/stackexchange/'  + tabledata.find_all("a")[0]['href'])
 with open('urls_list.txt', 'w') as f:
   for item in urls_list:
       f.write("%s\n" % item)
