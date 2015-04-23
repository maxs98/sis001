#!/usr/bin/python
#coding=utf-8

import requests
import re
import logging

def getHash():
	html = requests.get('http://38.103.161.185/forum/logging.php?action=login',headers=browse_headers)
	hash = re.findall(b'<input type="hidden" name="formhash" value="(.*?)" />',html.content)
	hash = hash.pop().decode('gbk')
	print(hash)
	return hash

s = requests.Session()
browse_headers ={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
LOG_FILENAME="d:\\sis001\log.txt"
logging.basicConfig(filename=LOG_FILENAME,format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
forumurl = 'http://38.103.161.185'

#hash = getHash()
login_info = {
"formhash":"21301523",
"referer":"index.php",
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
	html = s.post("%s/forum/logging.php?action=login&loginsubmit=true"%forumurl, data=login_info,headers=browse_headers,timeout=10)
	logging.info(html.content.decode('gbk'))
	login_success_info = re.findall(b'volstad',html.content,re.M|re.S)
	#print(html.text)
	print(html.status_code)
	print(html.encoding)
	#print(login_success_info)
	if len(login_success_info) >= 1:
		print('login success!!')
	else:
		print('login fail!!')
except requests.exceptions.ConnectionError as e:
	logging.info(e)
except requests.exceptions.HTTPError as e:
	logging.info(e)
			
