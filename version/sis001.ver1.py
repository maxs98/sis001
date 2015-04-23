#!/usr/bin/python
#coding=utf-8

import requests
import re
import Queue
import threading
import logging
import time

class sis001:
	def __init__(self):
		self.q = Queue.Queue(maxsize=10) 
		self.s = requests.Session()
		self.browse_headers ={"User-agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1"}
		LOG_FILENAME="d:\\sis001\log.txt"
		logging.basicConfig(filename=LOG_FILENAME,format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)	
		self.login()
		
		
	def login(self):
		login_info = {
		"formhash":"962ee4d3",
		"referer":"http://38.103.161.185/forum/index.php",
		"loginfield":"username",
		"62838ebfea47071969cead9d87a2f1f7":"volstad",
		"c95b1308bda0a3589f68f75d23b15938":"194105",
		"questionid":"4",
		"answer":"\xd0\xec\xc0\xf6\xbb\xaa",
		"cookietime":"2592000",
		"loginmode":"",
		"styleid":"",
		"loginsubmit":"true"}
		html = self.s.post("http://162.252.9.3/forum/logging.php?action=login&loginsubmit=true", data=login_info,headers=self.browse_headers,timeout=10)
		login_success_pattern = re.compile(r'volstad')
		login_success_info = login_success_pattern.search(html.content)
		if login_success_info:
			print 'login success!!'
		else:
			print 'login fail!!'

	def getTids(self):
		page = 2
		url = "http://162.252.9.3/forum/forum-62-%s.html"%page
		html = self.s.get(url,headers=self.browse_headers,timeout=30)
		tid_pattern = re.compile(r'<tbody id="normalthread_(\d+)\"')
		tids = tid_pattern.findall(html.content)
		#print tids
		return tids

	def getPics(self,tid):
		url = "http://162.252.9.3/forum/thread-%s-1-1.html"%tid
		html = self.s.get(url,headers=self.browse_headers,timeout=30)
		image_pattern = re.compile(r'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?.jpg)\"')
		images = image_pattern.findall(html.content)
		images = list(set(images))
		if len(images)==0:
			print tid   #打不开的帖子
		else:
		#这里有问题，一直发送请求链接会造成HTTP连接池满而罢工。
		#如果队列为空再往队列里put链接，如果不为空就执行savepic（），如果为空就继续put链接进队列。
			for i in images:			
				while True:
					if self.q.qsize()<1:
						self.q.put(i) #得拿出去，不然一直在put进队列，先把队列弄满了。在用线程一个一个去执行。执行完一批检查队列？		
						print "Queue %s"%self.q.qsize()
					else:
						th = threading.Thread(target=sis001.savePic)
						th.start()
		#print images
		#return images
			
	def savePic(self):
		try:
			i = self.q.get()
			filename = re.split(r'/',i)
			fName =  '.\\img\\'+filename.pop()
			image = self.s.get(i,headers=self.browse_headers,timeout=30)
			open(fName, "wb").write(image.content)
			self.q.task_done()
		except requests.exceptions.ConnectionError,e:
			logging.info(e)
		except requests.exceptions.HTTPError:
			logging.info(e)

			
if __name__ == '__main__':
	sis001 = sis001()
	tids = sis001.getTids()
	for tid in tids:
		sis001.getPics(tid)