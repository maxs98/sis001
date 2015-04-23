#!/usr/bin/python
#coding=utf-8

import requests
import re
import logging
import time
import threading
import os

try:
    import urllib.request
    #import urllib.parse
except ImportError:
    import urllib
    urllib.request = __import__('urllib2')
    urllib.parse = __import__('urlparse')
 
urlopen = urllib.request.urlopen
request = urllib.request.Request
#1234
class sis001:
	def __init__(self): 
		self.s = requests.Session()
		self.browse_headers ={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
		LOG_FILENAME="d:\\sis001\\log.txt"
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
		hash = re.findall(b'<input type="hidden" name="formhash" value="(.*?)" />',html.content)
		hash = hash.pop()
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
		"answer":b"\xd0\xec\xc0\xf6\xbb\xaa",#"answer":"\xd0\xec\xc0\xf6\xbb\xaa",
		"cookietime":"2592000",
		"loginmode":"",
		"styleid":"",
		"loginsubmit":"true"}
		
		try:
			html = self.s.post("%s/forum/logging.php?action=login&loginsubmit=true"%self.forumurl, data=login_info,headers=self.browse_headers,timeout=10)
			login_success_info = re.findall(b'volstad',html.content,re.M|re.S)
			if len(login_success_info) >= 1:
				print('ok logging success!!')
			else:
				print('login fail!!')
		except requests.exceptions.ConnectionError as e:
			logging.info(e)
		except requests.exceptions.HTTPError as e:
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
			topics_html = re.findall(b'<tbody.*?normalthread.*?>.*?</tbody>', html.content, re.M | re.S) #粗过滤，先过滤每个帖子的所有内容返回top_html只包含所有帖子的内容
			if topics_html == '':
				attempts += 1 # need retry download
			else:
				break
		topics = dict()
		p = b'<span id=\".*?\"><a href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*?</tbody>' 
		#细过滤，以下代码解析每个帖子的标题和url
		try:
			for h in topics_html:
				gd = re.search(p, h, re.M | re.S).groupdict()
				topics[gd['title']] = gd
				#print gd['title']
				#logging.info(gd)
		except Exception as e:
			logging.info(e)
		
		for i in topics:
			down_link_imgs_torrents(topics[i])
		return topics
	
def down_link_imgs_torrents(topic):
	print('GET:%s---%s'%(topic['url'],topic['title'].decode('gbk')))
	dirname = get_valid_filename(topic['title'].decode('gbk')) #由于windows默认是gbk编码，建立文件夹时必须解码成gbk字符
	#print dirname
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	topic_url = "%s/forum/%s"%(sis001.forumurl,topic['url'].decode('gbk'))
	base_url = "%s/forum/"%(sis001.forumurl)
	html = sis001.s.get(topic_url,headers=sis001.browse_headers,timeout=30)
	imgs = re.findall(b'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?\.jpg)\"', html.content, re.M | re.S) #匹配这个页面所有的图片链接
	torrents = re.findall(b'a href=\"(?P<url>attach[=0-9a-zA-Z\.\?]+).*?>(?P<title>[^<>\"]*?torrent)', html.content, re.M | re.S) #匹配这个页面所有的种子链接
    
	imgs = set(imgs)
	st = set(torrents) 
	#print(imgs, st)
	#logging.info(imgs,st)
	for img in imgs:
		img = img.decode('gbk')
		down_link(img, dirname + '/' + get_valid_filename(os.path.basename(img)))
	for t in st:
		t0 = t[0].decode('gbk')
		t1 = t[1].decode('gbk')
		down_link(base_url + t0, dirname + '/' + get_valid_filename(t1))
	return

def down_link(url, filename, istorrent = 0):
	if os.path.exists(filename) and os.path.getsize(filename) > 0: #TODO MD5
		return
	#print url #这里可以写一个把链接保存为文件的功能
	logging.info(url)
	if url.find('attachments/month')>=0: #如果是本论坛的图片则补全地址
		url = sis001.forumurl + "/forum/" + url
	elif url.find('attachments/day')>=0: #如果是本论坛的图片则补全地址
		url = sis001.forumurl + "/forum/" + url
	print(url)
	req = request(url, headers = sis001.browse_headers)
	try:
		data = get_data_from_req(req)
		if data is '':
			return
		f = open(filename, 'wb')
		f.write(data)
		f.close
	except Exception as e:
		#print(e)
		logging.info(e)
	return
	
def get_data_from_req(req):
	attempts = 0
	binary = ''
	while attempts < 10:
		try:
			binary = urlopen(req).read()
			break
		except Exception as e:
			attempts += 1
			#print(e)
			logging.info(e)
	return binary

def get_valid_filename(filename): #如果文件名有数字字母和特殊字符，按顺序连接起来去除右边空格，（连接c）
    keepcharacters = (' ','.','_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


	
if __name__ == '__main__':
	start = time.time()
	sis001 = sis001()
	t = dict()	
	fids = {"版面代码":62} #需要采集的版面{"典藏":411,"熟妇":242,"自拍":62,"若兰居":495,"亚洲无码":25}
	pages = range(1,10) #采集的页数
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