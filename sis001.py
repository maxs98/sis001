#!/usr/bin/python
#coding=utf-8

import requests
import re
import logging
import time
import threading
import socket
from bs4 import BeautifulSoup

class sis001:
	def __init__(self): 
		self.s = requests.Session()
		self.browse_headers ={"User-agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1"}
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
		hash = soup.find(type ="hidden")		
		hash = hash.get('value')
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
			
	def savePic(self,imageurl):
		try:
			#用帖子id或者标题，做文件夹名。将一个帖子的放在一个文件夹下。
			time.sleep(2)
			#logging.info(imageurl)
			filename = re.split(r'/',imageurl)
			fName =  'd:\\img\\'+filename.pop()
			proxies = {
			    "http1":"http://58.248.81.11:9999",
			    "http2":"http://220.199.6.54:8080",
			    "http3":"http://122.224.97.84:80",
			    "http4":"http://60.28.31.194:80",
			    "http5":"http://222.240.141.4:8080",
			}
			imageurl = self.s.get(imageurl,headers=self.browse_headers,timeout=10,proxies=proxies)
			open(fName, "wb").write(imageurl.content)
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

class ThreadGetTids(threading.Thread):
	sis001.forumurl = fid = page = None
	def __init__(self, forumurl,fid, page):
		threading.Thread.__init__(self)
		self.forumurl = forumurl
		self.fid = fid
		self.page = page
		
	def run(self):
		t = dict()
		url = "%s/forum/forum-%s-%s.html"%(self.forumurl,self.fid,self.page)
		html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
		tid_pattern = re.compile(r'<tbody id="normalthread_(\d+)\"')
		tids = tid_pattern.findall(html.content)
		#logging.info(tids)			
		for tid in tids:
			print "page is:%s   tid is:%s"%(self.page,tid)
			t[tid,page] = ThreadGetPics(tid,self.page)
			t[tid,page].start()
			t[tid,page].join()	

class ThreadGetPics(threading.Thread):
	sis001.forumurl = tid = page = None
	def __init__(self, tid, page):
		threading.Thread.__init__(self)
		self.tid = tid
		self.page = page
	def run(self):
		try:
			imageurls =  []
			url = "%s/forum/thread-%s-1-%s.html"%(sis001.forumurl,self.tid,self.page)
			html = sis001.s.get(url,headers=sis001.browse_headers,timeout=30)
			soup = BeautifulSoup(html.content)
			img = soup.find_all('img')			
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
			for imageurl in imageurls:
				sis001.savePic(imageurl)			
			#return imageurls
		except requests.exceptions.ConnectionError,e:
			logging.info(e)
		except requests.exceptions.HTTPError,e:
			logging.info(e)		
	
if __name__ == '__main__':
	start = time.time()
	sis001 = sis001()
	t = dict()	
	fids = {"DC":242} #需要采集到版面{"DC":411,"SF":242,"ZP":62}
	pages = range(1,10) #采集的页数
	for fid in fids.values():
		for page in pages:
			t[fid,page] = ThreadGetTids(sis001.forumurl,fid,page)
			t[fid,page].start()
	for fid in fids.values():
		for page in pages:
			t[fid,page].join()
	print("Elapsed Time:", (time.time() - start))