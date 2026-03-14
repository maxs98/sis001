import aiohttp
import asyncio
import re
import logging
import time
import socket
from bs4 import BeautifulSoup

class Sis001:
    def __init__(self):
        self.session = None  # Don't create session in __init__
        self.browse_headers = {"User-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"}
        self.forumurl = 'http://38.103.161.185'

    async def init_session(self):
        """Initialize session and login - call this instead of __init__ doing it"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self.login()

    async def getHash(self):
        timeout = aiohttp.ClientTimeout(total=10)
        async with self.session.get(
            'http://38.103.161.185/forum/logging.php?action=login',
            headers=self.browse_headers,
            timeout=timeout
        ) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            hidden_input = soup.find(type="hidden")
            if hidden_input:
                return hidden_input.get('value')
            return None

    async def login(self):
        hash_value = await self.getHash()
        if not hash_value:
            print('Failed to get hash value!')
            return False
            
        login_info = {
            "formhash": hash_value,
            "referer": f"{self.forumurl}/forum/index.php",
            "loginfield": "username",
            "62838ebfea47071969cead9d87a2f1f7": "volstad",
            "c95b1308bda0a3589f68f75d23b15938": "194105",
            "questionid": "4",
            "answer": "徐丽华",  # Decoded from GBK - verify this is correct
            "cookietime": "2592000",
            "loginmode": "",
            "styleid": "",
            "loginsubmit": "true"
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with self.session.post(
                f"{self.forumurl}/forum/logging.php?action=login&loginsubmit=true",
                data=login_info,
                headers=self.browse_headers,
                timeout=timeout
            ) as response:
                content = await response.text()
                login_success_pattern = re.compile(r'volstad')
                login_success_info = login_success_pattern.search(content)
                if login_success_info:
                    print('Login success!!')
                    return True
                else:
                    print('Login fail!!')
                    return False
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"Login error: {e}")
            return False

    async def savePic(self, imageurl):
        try:
            # Use asyncio.sleep instead of time.sleep
            await asyncio.sleep(2)
            
            filename = re.split(r'/', imageurl)
            fName = 'd:\\img\\' + filename[-1]  # Use [-1] instead of pop()

            proxy = "http://58.248.81.11:9999"
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with self.session.get(
                imageurl,
                headers=self.browse_headers,
                timeout=timeout,
                proxy=proxy
            ) as response:
                content = await response.read()
                # Use context manager to properly close file
                with open(fName, "wb") as f:
                    f.write(content)
                print(f"Saved: {fName}")
                    
        except (aiohttp.ClientError, asyncio.TimeoutError, socket.error, OSError) as e:
            logging.error(f"Save pic error for {imageurl}: {e}")

    async def close(self):
        if self.session:
            await self.session.close()


class Sis001Crawler:
    def __init__(self, sis001):
        self.sis001 = sis001

    async def generate_tids(self, forumurl, fid, pages):
        timeout = aiohttp.ClientTimeout(total=30)
        for page in pages:
            url = f"{forumurl}/forum/forum-{fid}-{page}.html"
            try:
                async with self.sis001.session.get(
                    url,
                    headers=self.sis001.browse_headers,
                    timeout=timeout
                ) as response:
                    content = await response.text()
                    tid_pattern = re.compile(r'<tbody id="normalthread_(\d+)"')
                    tids = tid_pattern.findall(content)
                    for tid in tids:
                        yield tid, page
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.error(f"Error fetching page {page}: {e}")

    async def generate_pics(self, forumurl, tid, page):
        timeout = aiohttp.ClientTimeout(total=30)
        url = f"{forumurl}/forum/thread-{tid}-1-{page}.html"
        try:
            async with self.sis001.session.get(
                url,
                headers=self.sis001.browse_headers,
                timeout=timeout
            ) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                img = soup.find_all('img')
                for myimg in img:
                    link = myimg.get('src')
                    if not link:
                        continue
                    attachments = re.split('/', link)
                    if attachments[0] == "attachments":
                        # Return string, not bytes
                        yield forumurl + "/forum/" + link
                    else:
                        extension = re.split(r'\.', link)
                        if extension[-1].lower() == "jpg":
                            yield link  # Return string, not bytes
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"Error fetching pics for tid {tid}: {e}")

    async def get_tids(self, forumurl, fid, pages):
        async for tid, page in self.generate_tids(forumurl, fid, pages):
            print(f"page is:{page}   tid is:{tid}")
            await self.get_pics(forumurl, tid, page)

    async def get_pics(self, forumurl, tid, page):
        async for imageurl in self.generate_pics(forumurl, tid, page):
            await self.sis001.savePic(imageurl)


async def main():
    start = time.time()
    
    sis001 = Sis001()
    await sis001.init_session()  # Initialize session and login
    
    sis001_crawler = Sis001Crawler(sis001)
    fids = {"DC": 242}  # Need to collect to forum {"DC": 411, "SF": 242, "ZP": 62}
    pages = range(1, 10)  # Number of pages to collect
    tasks = []

    for fid in fids.values():
        tasks.append(sis001_crawler.get_tids(sis001.forumurl, fid, pages))

    await asyncio.gather(*tasks)
    await sis001.close()
    print(f"Elapsed Time: {time.time() - start:.2f}s")


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
