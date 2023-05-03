
import os
import asyncio
import aiohttp
from lxml import etree
import json
import re

from novel_image_worker import get_pximg_image

IMAGE_EXTRACTER = re.compile(r'\[pixivimage:(\d+)\]')

async def get_novel(session: aiohttp.ClientSession, nid: int = 14700041, php_sessid = '') :
    url = f"https://www.pixiv.net/novel/show.php?id={nid}"

    headers = {
        'authority': 'www.pixiv.net',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'cookie': f'PHPSESSID={php_sessid}',
        'pragma': 'no-cache',
        'referer': 'https://www.pixiv.net/',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }

    async with session.get(url = url, headers = headers) as response :
        txt = await response.text()
    dom = etree.HTML(txt)
    preload_data = json.loads(dom.xpath('//*[@id="meta-preload-data"]/@content')[0])
    content = preload_data['novel'][f'{nid}']
    cover_url = preload_data['novel'][f'{nid}']['coverUrl']
    img_urls = {}
    if 'textEmbeddedImages' in preload_data['novel'][f'{nid}'] and preload_data['novel'][f'{nid}']['textEmbeddedImages'] :
        embd_images = list(preload_data['novel'][f'{nid}']['textEmbeddedImages'].keys())
    else :
        novel_content = content['content']
        for m in IMAGE_EXTRACTER.findall(novel_content) :
            img_id = m
            img_urls[img_id] = f'https://www.pixiv.net/en/artworks/{img_id}'
        embd_images = []
    for imgid in embd_images :
        img_urls[imgid] = preload_data['novel'][f'{nid}']['textEmbeddedImages'][imgid]['urls']['original']
    return content, img_urls, cover_url

async def scrape_novel(root, session, nid, php_sessid) :
    try :
        dst = os.path.join(root, f'{nid}.json')
        if os.path.exists(dst) :
            return
        content, img_urls, cover_url = await get_novel(session = session, nid = nid, php_sessid = php_sessid)
        for k, v in img_urls.items() :
            if 'https://i.pximg.net/' in v :
                ext = v.split('.')[-1]
                dst = os.path.join(root, f'{nid}-{k}.{ext}')
                await get_pximg_image(v, session, dst)
        ext = cover_url.split('.')[-1]
        dst_novel = os.path.join(root, f'{nid}-cover.{ext}')
        await get_pximg_image(cover_url, session, dst_novel)
        dst = os.path.join(root, f'{nid}.json')
        with open(dst, 'w', encoding = 'utf-8') as fp :
            json.dump(content, fp, ensure_ascii = False)
    except Exception as e :
        pass

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def scrape_range(root, session, start, end, php_sessid) :
    all_nid = list(range(start, end + 1))
    for chunk in chunks(all_nid, 10) :
        print('Downloading', chunk)
        tasks = [scrape_novel(root, session, nid, php_sessid) for nid in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)

async def main() :
    import sys
    save_dir = sys.argv[1]
    php_sessid = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])
    print('Range', start, 'to', end)
    async with aiohttp.ClientSession() as session :
        await scrape_range(save_dir, session, start, end, php_sessid)

if __name__ == '__main__' :
	loop = asyncio.new_event_loop()
	loop.run_until_complete(main())




