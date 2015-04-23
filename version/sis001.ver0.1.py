#!/usr/bin/python
# -*- coding: cp936 -*-
#coding utf-8


import urllib
import urllib2
import re
import cookielib
import Queue
import threading
import socket
import time
import sys
import random

def log(message):
    log = open("log.txt","a")
    log.write(time.ctime()+" "+message+"\n")
    log.close()

def getPic():
	i = q.get()
	if re.match("http",i):
		#print "%s downloading..."%i
		filename = re.split(r'/',i)
		try:
			req = urllib2.Request(i,None,self.browse_headers)
			res = opener.open(req).read()
			savefile = '.\\img\\'+filename[-1]+ str(int(random.random()*100000000))+'.jpg'
			open(savefile,'wb').write(res)
		except:
			etype, value, tb = sys.exc_info()
			errormsg = i + "||"+str(etype) +"||"+ str(value)
			log(errormsg)
			pass
	else:
		img_url = "http://38.103.161.185/forum/%s"%i
		filename = re.split(r'/',img_url)
		#print "%s"%img_url
		try:
			req = urllib2.Request(img_url,None,self.browse_headers)
			res = opener.open(req).read()
			savefile = '.\\img\\'+filename[-1]+ str(int(random.random()*100000000))+'.jpg'
			open(savefile,'wb').write(res)
		except:
			etype, value, tb = sys.exc_info()
			errormsg = i + "||"+str(etype) +"||"+ str(value)
			log(errormsg)
		pass


def downPic(tiezi_url,q):
    req = urllib2.Request(tiezi_url,None,headers)
    tiezi_html = opener.open(req).read()
    #print tiezi_html
    re_img = re.compile(r'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?.jpg)\"')
    img_list = re_img.findall(tiezi_html)
    img_list = list(set(img_list))
    #print img_list
    for i in img_list:
        q.put(i)
    while True:
        if q.qsize()>0:
            th = threading.Thread(target=getPic)
            th.start()
            #print "Queue %s"%q.qsize()
        else:
            break


headers ={"User-agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1"}
socket.setdefaulttimeout(30)
cj = cookielib.CookieJar()
#proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#urllib2.install_opener(opener)
data =  {
    "formhash":"3fec4925",
    "referer":"index.php",
    "loginfield":"username",
    "240aa46b3893fb57c436c0a3785b61e7":"xxx",
    "ea32b1cadbde4b66ca614e0bb593d1c9":"xxx",
    "questionid":"0",
    "answer":"",
    "cookietime":"2592000",
    "loginmode":"",
    "styleid":"",
    "loginsubmit":"true"}
post_data = urllib.urlencode(data)
req = urllib2.Request("http://38.103.161.185/forum/logging.php?action=login&",post_data,headers)
content=opener.open(req)
#print content.read()
req2 = urllib2.Request("http://38.103.161.185/forum/forum-62-1.html",None,headers)
board_html = opener.open(req2).read()
#print board_html
re_link = re.compile(r'\<a href\=\"(thread-\d{7}-1-\d{1}.html)')
title_list = re_link.findall(board_html)
title_list = list(set(title_list)) #去除list中的重复项
#http://38.103.161.185/forum/thread-(4917300)-1-(1).html
#http://38.103.161.185/forum/forum-62-(2).html
#[\u4e00-\u9fa5]
#print title_list

for i in title_list:
    tiezi_url = "http://38.103.161.185/forum/%s"%i
    print tiezi_url
    q = Queue.Queue(0)
    downPic(tiezi_url,q)

print 'All threads terminate!'