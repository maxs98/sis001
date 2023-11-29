#!/usr/bin/python
# coding=utf-8

import aiohttp
import asyncio
import os
import re
import requests
import logging
import time

LOG_FILENAME = "d:\\sis001\\log.txt"
FORUM_URL = 'http://38.103.161.185'
DOWNLOAD_FOLDER = 'av'

class Sis001:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.browse_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:22.0) Gecko/20100101 Firefox/22.0'}
        logging.basicConfig(filename=LOG_FILENAME, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.forumurl = FORUM_URL
        self.login()

    async def close(self):
        await self.session.close()

    async def get_hash(self):
        hash_html = await self.session.get(f'{self.forumurl}/forum/logging.php?action=login', headers=self.browse_headers)
        hash_value = re.findall(b'<input type="hidden" name="formhash" value="(.*?)" />', await hash_html.read()).pop()
        return hash_value

    async def login(self):
        hash_value = await self.get_hash()
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
            login_html = await self.session.post(f"{self.forumurl}/forum/logging.php?action=login&loginsubmit=true", data=login_info, headers=self.browse_headers, timeout=10)
            login_success_info = re.findall(b'volstad', await login_html.read(), re.M | re.S)
            if len(login_success_info) >= 1:
                print('OK, logging success!!')
            else:
                print('Login failed!!')
        except requests.exceptions.RequestException as e:
            logging.error(e)

async def down_link_imgs_torrents(topic, session):
    print(f'GET:{topic["url"]}---{topic["title"].decode("gbk")}')
    dirname = get_valid_filename(topic['title'].decode('gbk'))

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    topic_url = f"{Sis001.forumurl}/forum/{topic['url'].decode('gbk')}"
    base_url = f"{Sis001.forumurl}/forum/"
    
    async with session.get(topic_url, headers=Sis001.browse_headers, timeout=30) as img_html:
        imgs = set(re.findall(b'\<img src\=\"(http\:\/\/.*?\.jpg|attachments\/.*?\.jpg)\"', await img_html.read(), re.M | re.S))
        torrents = set(re.findall(b'a href=\"(?P<url>attach[=0-9a-zA-Z\.\?]+).*?>(?P<title>[^<>\"]*?torrent)', await img_html.read(), re.M | re.S))
        
        for img in imgs:
            img = img.decode('gbk')
            await down_link(img, f'{dirname}/{get_valid_filename(os.path.basename(img))}', session)

        for t in torrents:
            t0 = t[0].decode('gbk')
            t1 = t[1].decode('gbk')
            await down_link(f"{base_url}{t0}", f"{dirname}/{get_valid_filename(t1)}", session)
    return

async def down_link(url, filename, session, is_torrent=0):
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
            async with session.get(url, headers=Sis001.browse_headers, timeout=30) as save_html:
                if not save_html.content:
                    return
                open(filename, "wb").write(await save_html.read())
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
    
    async def main():
        sis001 = Sis001()
        fids = {"版面代码": 229}
        pages = range(1, 11)
        
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)
        os.chdir(DOWNLOAD_FOLDER)
        
        for fid in fids.values():
            for page in pages:
                url = f"{Sis001.forumurl}/forum/forum-{fid}-{page}.html"
                async with sis001.session.get(url, headers=Sis001.browse_headers, timeout=30) as page_html:
                    if not page_html.content:
                        continue

                    attempts = 0
                    while attempts < 3:
                        topics_html = re.findall(b'<tbody.*?normalthread.*?>.*?</tbody>', await page_html.read(), re.M | re.S)
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
                        await down_link_imgs_torrents(topics[i], sis001.session)
    
    asyncio.run(main())
    await sis001.close()
    
    print("Elapsed Time:", (time.time() - start))
