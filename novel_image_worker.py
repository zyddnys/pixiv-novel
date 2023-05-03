

import asyncio
import aiohttp

async def get_pximg_image(url, session: aiohttp.ClientSession, dst) :
	try_count = 10
	headers = {
        'authority': 'i.pximg.net',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,image/jpeg,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        #'if-modified-since': 'Thu, 18 Feb 2021 21:27:06 GMT',
        'referer': 'https://www.pixiv.net/',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
	while try_count > 0 :
		try :
			with open(dst, 'wb') as fp :
				async with session.get(url = url, headers = headers) as response :
					if response.status // 100 == 2 :
						while True:
							chunk = await response.content.read(1024 * 1024 * 4) # 4MB
							if not chunk:
								break
							fp.write(chunk)
					else :
						raise Exception('response.status_code=%d' % response.status)
			break
		except Exception as ex :
			try_count -= 1
			print('[!] Retrying %s, remaining count %d' % (dst, try_count))
			continue

async def main() :
	async with aiohttp.ClientSession() as session :
		await get_pximg_image('https://i.pximg.net/novel-cover-original/img/2021/02/19/06/27/06/tei522686848835_0dc582f77d783a046ef4c86700d0fdb2.png', session, '3.png')
		
if __name__ == '__main__' :
	loop = asyncio.new_event_loop()
	loop.run_until_complete(main())

