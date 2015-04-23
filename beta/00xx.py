#!/usr/bin/python
#coding=utf-8

from bs4 import BeautifulSoup
import re
import os

av_dir = "avdir"
html = open('123.html', 'r')
#print html.read()
#soup = BeautifulSoup(html)
#img = soup.find_all('a')
#<a href="thread-9352065-1-1.html" style="font-weight: bold;color: blue">(¥¢¥¸¥¢Ìì¹ú)(0486)ÃØÃÜ¤Î¤ªÊËÊÂ¡«¥Ù¥Ó©`¥·¥Ã¥¿©`¤ªÊËÖÃ¤­¡«ARIEL ROSE</a>
#tid_pattern = re.compile(r'<a href="thread-(\d+)-1-1.html" style=".*?">(.*?)</a>')
topics_html = re.findall('<tbody.*?normalthread.*?>.*?</tbody>', html.read(), re.M | re.S)
#tids = tid_pattern.findall(html.read())
topics = dict()
p = '<span id.*?<a href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*?<img.*?<td.*?author.*?img.*?>.*?(?P<star>\d+).*?</cite>.*?<td.*?nums\">.*?(?P<comment>\d+).*?<em>(?P<view>\d+).*?lastpost.*?<a href.*?>(?P<time>.*?)</a>'
 
try:
	for h in topics_html:
		gd = re.search(p, h, re.M | re.S).groupdict()
		#print gd
        gd['url'] = "sis001" + gd['url']
        topics[gd['title']] = gd
        #print(topics[gd['title']])
	print topics
except Exception as e:
	print(e)

def get_valid_filename(filename):
    keepcharacters = (' ','.','_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

# if not os.path.exists(av_dir):
    # os.makedirs(av_dir)
    # os.chdir(av_dir)
# for tid in tids:
	# print tid[0]

for myimg in img:
	#print myimg
	link = myimg.get('href')
	title = myimg.get_text()
	m = re.match("thread-\d*-1-1.html",str(link))
	if m:
		if title == "1" or title == "":
			pass
		else:
			dirname = get_valid_filename(title)
			print dirname
			if not os.path.exists(dirname):
				os.makedirs(dirname)