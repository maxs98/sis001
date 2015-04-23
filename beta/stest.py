#!/usr/bin/python
#coding=utf-8

import requests
import re
import logging
import time
import threading
import socket
import os
import urllib2
from bs4 import BeautifulSoup


#1234
class sis001:
	def __init__(self): 
		self.s = requests.Session()
		self.browse_headers ={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
		LOG_FILENAME="d:\\sis001\log.txt"
		logging.basicConfig(filename=LOG_FILENAME,format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
		self.forumurl = 'http://38.103.161.185'
		'''
		http://38.103.161.185--good!
		http://38.103.161.156
		http://38.103.161.167--good!
		http://38.103.161.140
		http://68.168.16.150
		http://162.252.9.8
		http://38.103.161.142
		http://162.252.9.7
		'''
		self.login()
		
	def getHash(self):
		html = requests.get('http://38.103.161.185/forum/logging.php?action=login',headers=self.browse_headers)
		soup = BeautifulSoup(html.content)
		#hash = soup.find(type ="hidden")
		hash = re.findall('<input type="hidden" name="formhash" value="(.*?)" />',html.content)
		#hash = hash.get('value')
		return hash
		
	def login(self):
		hash = self.getHash()
		login_info = {
		"formhash":"%s"%hash,
		"referer":"%s/forum/index.php"%self.forumurl,
		"loginfield":"username",
		"62838ebfea47071969cead9d87a2f1f7":"volstad",
		"c95b1308bda0a3589f68f75d23b15938":"194105",
		"questionid":"4",
		"answer":"\xd0\xec\xc0\xf6\xbb\xaa",
		"cookietime":"2592000",
		"loginmode":"",
		"styleid":"",
		"loginsubmit":"true"}
		try:
			html = self.s.post("%s/forum/logging.php?action=login&loginsubmit=true"%self.forumurl, data=login_info,headers=self.browse_headers,timeout=10)
			login_success_pattern = re.compile(r'volstad')
			login_success_info = login_success_pattern.search(html.content)
			if login_success_info:
				print 'login success!!'
			else:
				print 'login fail!!'
		except requests.exceptions.ConnectionError,e:
			logging.info(e)
		except requests.exceptions.HTTPError,e:
			logging.info(e)
			
	def savePic(self,imageurl,title):
		try:
			#用帖子id或者标题，做文件夹名。将一个帖子的放在一个文件夹下。
			time.sleep(2)
			#logging.info(imageurl)
			filename = re.split(r'/',imageurl)
			fName =  "d://sis001//av//" + title +"//" + filename.pop()
			#print fName
			proxies = {
			    "http1":"http://58.248.81.11:9999",
			    "http2":"http://220.199.6.54:8080",
			    "http3":"http://122.224.97.84:80",
			    "http4":"http://60.28.31.194:80",
			    "http5":"http://222.240.141.4:8080",
			}
			#imageurl = self.s.get(imageurl,headers=self.browse_headers,timeout=10,proxies=proxies)
			#f = open(fName, "wb")
			#f.write(imageurl.content)
			#f.close
		except requests.exceptions.ConnectionError,e:
			logging.info(e)	
		except requests.exceptions.HTTPError,e:
			logging.info(e)
		except requests.exceptions.Timeout,e:
			logging.info(e)
			pass
		except socket.error,e: 
			logging.info(e)
			pass
			
	def GetPics(self,tid,page):
		try:
			imageurls =  []
			#sis001.forumurl = tid = title = page = None
			url = "%s/forum/thread-%s-1-%s.html"%(sis001.forumurl,tid,page)
			html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
			#soup = BeautifulSoup(html.content)
			#img = soup.find_all('img')
			#if not os.path.exists(title):
			#	dirname = ".\\av\\" + title
			#	os.makedirs(dirname)
			for myimg in img:
				link = myimg.get('src')
				attachments = re.split('/', link)
				if attachments[0] == "attachments":
					imageurls.append(sis001.forumurl+"/forum/"+link.encode('utf-8'))
				else:
					extension = re.split(r'\.', link)
					if extension.pop() == "jpg":
						imageurls.append(link.encode('utf-8'))
						#print link.encode('utf-8')
			#imageurl_pattern = re.compile(r'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?.jpg)\"')
			#imageurls = imageurl_pattern.findall(html.content)
			imageurls = list(set(imageurls))
			#logging.info(imageurls)
			#for imageurl in imageurls:
				#sis001.savePic(imageurl,title)
			#return imageurls
		except requests.exceptions.ConnectionError,e:
			logging.info(e)
		except requests.exceptions.HTTPError,e:
			logging.info(e)

class ThreadGetTids(threading.Thread):
	sis001.forumurl = fid = page = None
	def __init__(self, forumurl,fid, page):
		threading.Thread.__init__(self)
		self.forumurl = forumurl
		self.fid = fid
		self.page = page
		
	def run(self):
		#t = dict()
		url = "%s/forum/forum-%s-%s.html"%(self.forumurl,self.fid,self.page)
		#print url
		html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
		#tid_pattern = re.compile(r'<tbody id="normalthread_(\d+)\"') #返回两个东西，一个tid，一个标题
		#tid_pattern = re.compile(r'<a href="thread-(\d+)-1-1.html" style=".*?">(.*?)</a>')
		#tids = tid_pattern.findall(html.content)
		if html.content == '':
			return
		attempts = 0
		while attempts < 3:
			topics_html = re.findall('<tbody.*?normalthread.*?>.*?</tbody>', html.content, re.M | re.S)
			if topics_html == '':
				attempts += 1 # need retry download
			else:
				break
		topics = dict()
		p = '<span id=\".*?\"><a href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*?</tbody>'
		# p = '<span id.*?<a href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*?<img.*?<td.*?author.*?img.*?>.*?(?P<star>\d+).*?</cite>.*?<td.*?nums\">.*?(?P<comment>\d+).*?<em>(?P<view>\d+).*?lastpost.*?<a href.*?>(?P<time>.*?)</a>'
		try:
			for h in topics_html:
				#print h
				gd = re.search(p, h, re.M | re.S).groupdict()
				#gd['url'] = sis001.forumurl + gd['url']
				topics[gd['title']] = gd
				#print(topics[gd['title']])
				print gd['title']
		except Exception as e:
			print(e)
		
		for i in topics:
			down_link_imgs_torrents(topics[i])
		return topics
		#print topics_html		
		# for tid in tids:
			# #tid = topic[0]
			# #title = topic[1]
			# print "page is:%s   tid is:%s"%(self.page,tid)
			# sis001.GetPics(tid,self.page)  #然后把标题当参数传给getpic类
	
def down_link_imgs_torrents(topic):
	print('GET:', topic['url'])
	dirname = topic['title'].rstrip()
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	topic_url = "%s/forum/%s"%(sis001.forumurl,topic['url'])
	html = sis001.s.get(topic_url,headers=sis001.browse_headers,timeout=30)
    #content = get_content_from_url(topic['url'])
	#imgs = re.findall('<img src=\"attachments/.*?\.jpg\">', html.content, re.M | re.S)
	imgs = re.findall('\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?.jpg)\"', html.content, re.M | re.S)
    #imgs = re.findall('img src=\"(http[^\"]+)\"', content, re.M | re.S)
	torrents = re.findall('a href=\"(?P<url>attach[=0-9a-zA-Z\.\?]+).*?>(?P<title>[^<>\"]*?torrent)', html.content, re.M | re.S)
    
	imgs = set(imgs)
	st = set(torrents)
    #t = re.findall('a href=\"attach.*?torrent', content, re.M | re.S)
    #t = re.findall('a href=\"(?P<torrent>attach[=0-9a-zA-Z\.\?]+).*?>(.*?torrent)', content, re.M | re.S)
     
	#print(imgs, st)
	for img in imgs:
		down_link(img, dirname + '/' + os.path.basename(img))
    # for t in st:
        # down_link(base_url + t[0], dirname + '/' + t[1])
	return

def down_link(url, filename, thresold = 0):
	if os.path.exists(filename) and os.path.getsize(filename) > 0: #TODO MD5
		return
	url = sis001.forumurl + "/forum/" + url
	html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
	try:
		if html.content is '':
			return
		print filename
		open(filename, "wb").write(html.content)
	except Exception as e:
		print(e)
	return
	
def get_valid_filename(filename):
	keepcharacters = (' ','.','_')
	return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


	
if __name__ == '__main__':
	start = time.time()
	sis001 = sis001()
	t = dict()	
	fids = {"若兰居":495} #需要采集的版面{"典藏":411,"熟妇":242,"自拍":62,"若兰居":495}
	pages = range(1,2) #采集的页数
	for fid in fids.values():
		for page in pages:
			t[fid,page] = ThreadGetTids(sis001.forumurl,fid,page)
			t[fid,page].start()
	for fid in fids.values():
		for page in pages:
			t[fid,page].join()
	print("Elapsed Time:", (time.time() - start))