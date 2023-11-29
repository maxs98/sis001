import aiohttp
import asyncio
import re
import logging
import time
import socket
from bs4 import BeautifulSoup

class Sis001:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.browse_headers = {"User-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"}
        self.forumurl = 'http://38.103.161.185'
        self.login()

    async def getHash(self):
        async with self.session.get('http://38.103.161.185/forum/logging.php?action=login',
                                    headers=self.browse_headers) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            hash_value = soup.find(type="hidden").get('value')
            return hash_value

    async def login(self):
        hash_value = await self.getHash()
        login_info = {
            "formhash": "%s" % hash_value,
            "referer": "%s/forum/index.php" % self.forumurl,
            "loginfield": "username",
            "62838ebfea47071969cead9d87a2f1f7": "volstad",
            "c95b1308bda0a3589f68f75d23b15938": "194105",
            "questionid": "4",
            "answer": "\xd0\xec\xc0\xf6\xbb\xaa",
            "cookietime": "2592000",
            "loginmode": "",
            "styleid": "",
            "loginsubmit": "true"
        }
        try:
            async with self.session.post(
                    "%s/forum/logging.php?action=login&loginsubmit=true" % self.forumurl,
                    data=login_info, headers=self.browse_headers, timeout=10) as response:
                content = await response.text()
                login_success_pattern = re.compile(r'volstad')
                login_success_info = login_success_pattern.search(content)
                if login_success_info:
                    print('Login success!!')
                else:
                    print('Login fail!!')
        except (aiohttp.ClientConnectionError, aiohttp.ClientHttpProxyError, aiohttp.ClientTimeoutError) as e:
            logging.info(e)

    async def savePic(self, imageurl):
        try:
            time.sleep(2)
            filename = re.split(r'/', imageurl)
            fName = 'd:\\img\\' + filename.pop()

            proxies = {
                "http1": "http://58.248.81.11:9999",
                "http2": "http://220.199.6.54:8080",
                "http3": "http://122.224.97.84:80",
                "http4": "http://60.28.31.194:80",
                "http5": "http://222.240.141.4:8080",
            }
            async with self.session.get(imageurl, headers=self.browse_headers, timeout=10,
                                       proxy=proxies.get("http1")) as response:
                content = await response.read()
                open(fName, "wb").write(content)
        except (aiohttp.ClientConnectionError, aiohttp.ClientHttpProxyError,
                aiohttp.ClientTimeoutError, socket.error) as e:
            logging.info(e)

    async def close(self):
        await self.session.close()

class Sis001Crawler:
    def __init__(self, sis001):
        self.sis001 = sis001

    async def generate_tids(self, forumurl, fid, pages):
        for page in pages:
            url = "%s/forum/forum-%s-%s.html" % (forumurl, fid, page)
            async with self.sis001.session.get(url, headers=self.sis001.browse_headers, timeout=30) as response:
                content = await response.text()
                tid_pattern = re.compile(r'<tbody id="normalthread_(\d+)\"')
                tids = tid_pattern.findall(content)
                for tid in tids:
                    yield tid, page

    async def generate_pics(self, forumurl, tid, page):
        url = "%s/forum/thread-%s-1-%s.html" % (forumurl, tid, page)
        async with self.sis001.session.get(url, headers=self.sis001.browse_headers, timeout=30) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            img = soup.find_all('img')
            for myimg in img:
                link = myimg.get('src')
                attachments = re.split('/', link)
                if attachments[0] == "attachments":
                    yield forumurl + "/forum/" + link.encode('utf-8')
                else:
                    extension = re.split(r'\.', link)
                    if extension.pop() == "jpg":
                        yield link.encode('utf-8')

    async def get_tids(self, forumurl, fid, pages):
        async for tid, page in self.generate_tids(forumurl, fid, pages):
            print("page is:%s   tid is:%s" % (page, tid))
            await self.get_pics(forumurl, tid, page)

    async def get_pics(self, forumurl, tid, page):
        async for imageurl in self.generate_pics(forumurl, tid, page):
            await self.sis001.savePic(imageurl)

async def main():
    start = time.time()
    sis001 = Sis001()
    sis001_crawler = Sis001Crawler(sis001)
    fids = {"DC": 242}  # Need to collect to forum {"DC": 411, "SF": 242, "ZP": 62}
    pages = range(1, 10)  # Number of pages to collect
    tasks = []

    for fid in fids.values():
        tasks.append(sis001_crawler.get_tids(sis001.forumurl, fid, pages))

    await asyncio.gather(*tasks)
    await sis001.close()
    print("Elapsed Time:", (time.time() - start))

if __name__ == '__main__':
    asyncio.run(main())
