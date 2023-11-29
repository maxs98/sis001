#!/usr/bin/python
#coding=utf-8

import requests
import re
import logging
import time
import threading
import os

# 使用常量定义
LOG_FILENAME = "d:\\sis001\\log.txt"
FORUM_URL = 'http://38.103.161.185'
DOWNLOAD_FOLDER = 'av'

class Sis001:
    def __init__(self): 
        self.s = requests.Session()
        self.browse_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
        logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.forumurl = FORUM_URL
        self.login()

    def get_hash(self):
        hash_html = requests.get(f'{self.forumurl}/forum/logging.php?action=login', headers=self.browse_headers)
        hash_value = re.findall(b'<input type="hidden" name="formhash" value="(.*?)" />', hash_html.content).pop()
        return hash_value

    def login(self):
        hash_value = self.get_hash()
        login_info = {
            "formhash": f"{hash_value}",
            "referer": f"{self.forumurl}/forum/index.php",
            "loginfield": "username",
            "62838ebfea47071969cead9d87a2f1f7": "volstad",
            "c95b1308bda0a3589f68f75d23b15938": "194105",
            "questionid": "4",
            "answer": b"\xd0\xec\xc0\xf6\xbb\xaa",
            "cookietime": "2592000",
            "loginmode": "",
            "styleid": "",
            "loginsubmit": "true"
        }

        try:
            login_html = self.s.post(f"{self.forumurl}/forum/logging.php?action=login&loginsubmit=true", data=login_info, headers=self.browse_headers, timeout=10)
            login_success_info = re.findall(b'volstad', login_html.content, re.M | re.S)
            if len(login_success_info) >= 1:
                print('OK, logging success!!')
            else:
                print('Login failed!!')
        except requests.exceptions.RequestException as e:
            logging.error(e)

# 更改类名为大写驼峰命名规范
class ThreadGetTids(threading.Thread):
    Sis001.forumurl = fid = page = None
    
    def __init__(self, forumurl, fid, page):
        threading.Thread.__init__(self)
        self.forumurl = forumurl
        self.fid = fid
        self.page = page
        
    def run(self):
        url = f"{self.forumurl}/forum/forum-{self.fid}-{self.page}.html"
        page_html = Sis001.s.get(url, headers=Sis001.browse_headers, timeout=30)

        if not page_html.content:
            return

        attempts = 0
        while attempts < 3:
            topics_html = re.findall(b'<tbody.*?normalthread.*?>.*?</tbody>', page_html.content, re.M | re.S)
            if not topics_html:
                attempts += 1
            else:
                break

        topics = dict()
        p = b'<span id=\".*?\"><a href=\"(?P<url>.*?)\".*?>(?P<title>.*?)</a>.*?</tbody>'
        
        try:
            for h in topics_html:
                gd = re.search(p, h, re.M | re.S).groupdict()
                topics[gd['title']] = gd
        except Exception as e:
            logging.error(e)
        
        for i in topics:
            down_link_imgs_torrents(topics[i])
        return topics

def down_link_imgs_torrents(topic):
    print(f'GET:{topic["url"]}---{topic["title"].decode("gbk")}')
    dirname = get_valid_filename(topic['title'].decode('gbk'))

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    topic_url = f"{Sis001.forumurl}/forum/{topic['url'].decode('gbk')}"
    base_url = f"{Sis001.forumurl}/forum/"
    img_html = Sis001.s.get(topic_url, headers=Sis001.browse_headers, timeout=30)
    imgs = set(re.findall(b'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?\.jpg)\"', img_html.content, re.M | re.S))
    torrents = set(re.findall(b'a href=\"(?P<url>attach[=0-9a-zA-Z\.\?]+).*?>(?P<title>[^<>\"]*?torrent)', img_html.content, re.M | re.S))
    
    for img in imgs:
        img = img.decode('gbk')
        down_link(img, f'{dirname}/{get_valid_filename(os.path.basename(img))}')

    for t in torrents:
        t0 = t[0].decode('gbk')
        t1 = t[1].decode('gbk')
        down_link(f"{base_url}{t0}", f"{dirname}/{get_valid_filename(t1)}")
    return

def down_link(url, filename, is_torrent=0):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        return

    logging.info(url)
    if url.find('attachments/month') >= 0:
        url = f"{Sis001.forumurl}/forum/{url}"
    elif url.find('attachments/day') >= 0:
        url = f"{Sis001.forumurl}/forum/{url}"

    attempts = 0
    while attempts < 10:
        try:
            req = requests.Session()
            save_html = req.get(url, headers=Sis001.browse_headers, timeout=30)
            if not save_html.content:
                return
            open(filename, "wb").write(save_html.content)
            break
        except Exception as e:
            attempts += 1
            logging.error(e)            
    
    logging.info(f"{filename}||{url}")
    return

def get_valid_filename(filename):
    keepcharacters = (' ', '.', '_')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

if __name__ == '__main__':
    start = time.time()
    sis001 = Sis001()
    t = dict()
    fids = {"版面代码": 229}
    pages = range(1, 11)
    
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    os.chdir(DOWNLOAD_FOLDER)
    
    for fid in fids.values():
        for page in pages:
            t[fid, page] = ThreadGetTids(Sis001.forumurl, fid, page)
            t[fid, page].start()
    
    for fid in fids.values():
        for page in pages:
            t[fid, page].join()

    print("Elapsed Time:", (time.time() - start))
