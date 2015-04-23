#!/usr/bin/python
#coding=gbk

import requests
import re
import logging
import time
import threading
import socket
import os
import urllib2


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
		hash = re.findall('<input type="hidden" name="formhash" value="(.*?)" />',html.content)
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
			


class ThreadGetTids(threading.Thread):
	sis001.forumurl = fid = page = None
	def __init__(self, forumurl,fid, page):
		threading.Thread.__init__(self)
		self.forumurl = forumurl
		self.fid = fid
		self.page = page
		
	def run(self):
		url = "%s/forum/forum-%s-%s.html"%(self.forumurl,self.fid,self.page)
		html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
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
		
		try:
			for h in topics_html:
				gd = re.search(p, h, re.M | re.S).groupdict()
				topics[gd['title']] = gd
				#print gd['title']
		except Exception as e:
			logging.info(e)
		
		for i in topics:
			down_link_imgs_torrents(topics[i])
		return topics
	
def down_link_imgs_torrents(topic):
	#print('GET:', topic['url'])
	dirname = topic['title']
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	topic_url = "%s/forum/%s"%(sis001.forumurl,topic['url'])
	base_url = "%s/forum/"%(sis001.forumurl)
	html = sis001.s.get(topic_url,headers=sis001.browse_headers,timeout=30)
	imgs = re.findall('\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?.jpg)\"', html.content, re.M | re.S) 
	torrents = re.findall('a href=\"(?P<url>attach[=0-9a-zA-Z\.\?]+).*?>(?P<title>[^<>\"]*?torrent)', html.content, re.M | re.S) 
    
	imgs = set(imgs)
	st = set(torrents) 
	#print st
	#print(imgs, st)
	for img in imgs:
		down_link(img, dirname + '/' + os.path.basename(img))
	for t in st:
		down_link(base_url + t[0], dirname + '/' + t[1])
	return

def down_link(url, filename, thresold = 0):
	if os.path.exists(filename) and os.path.getsize(filename) > 0: #TODO MD5
		return
	if url.find('src=\"attachments/month')>= 0: 
		url = sis001.forumurl + "/forum/" + url
	print url
	attempts = 0
	while attempts < 10:
		try:
			html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
			break
		except Exception as e:
			attempts += 1
			print(e)
			logging.info(e)
	try:
		if html.content is '':
			return
		#print filename
		open(filename, "wb").write(html.content)
	except Exception as e:
		print(e)
		logging.info(e)
	return
	
def get_valid_filename(filename):
	keepcharacters = (' ','.','_')
	return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


	
if __name__ == '__main__':
	start = time.time()
	sis001 = sis001()
	t = dict()	
	fids = {"rlj":25} 
	pages = range(1,3) 
	if not os.path.exists('av'):
		os.makedirs('av')
		os.chdir('av')
	for fid in fids.values():
		for page in pages:
			t[fid,page] = ThreadGetTids(sis001.forumurl,fid,page)
			t[fid,page].start()
	for fid in fids.values():
		for page in pages:
			t[fid,page].join()
	print("Elapsed Time:", (time.time() - start))