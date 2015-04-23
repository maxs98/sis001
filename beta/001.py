#/usr/bin/python
#coding utf-8

import re

url = 'attachments/month_070610/IMG_1635_xDxaUI6xax8M.jpg'
if url.find('attachments/month')>= 0:
	print "finded month"

if url.find('attachments/day')>= 0:
	print "finde day"


