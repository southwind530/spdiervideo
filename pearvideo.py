import os
import requests
from lxml import etree
import random
from multiprocessing.dummy import Pool

urls = []
headers = {
    'User-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

down_urls = []


def get_content(url):
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(e)


def parse_content(html):
    tree = etree.HTML(html)
    a_list = tree.xpath('//div[@id="vervideoTlist"]//a[@class="vervideo-lilink actplay"]')
    for a in a_list:
        #获取视频地址
        url = "https://www.pearvideo.com/" + a.xpath('./@href')[0]
        urls.append(url)


def get_detail(li):
    try:
        for i in li:
            contId = str(i.split('_')[-1])
            params = {
                "contId": contId,
                "mrd": str(random.random())
            }

            headers = {
                'User-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                "Referer": "https://www.pearvideo.com/video_" + contId
            }

            url = "https://www.pearvideo.com/videoStatus.jsp"
            rep = requests.get(url=url, headers=headers, params=params)
            rep.raise_for_status()
            json = rep.json()
            if 'videoInfo' in json.keys():
                srcUrl = json['videoInfo']['videos']['srcUrl']
                title = '/'.join(srcUrl.split('/')[0:-1])
                body = "/cont-" + contId + '-'
                footer = '-'.join(srcUrl.split('-')[1:])
                file_root = title + body + footer
                down_urls.append(file_root)
    except Exception as e:
        print(e)


def down_file(file):
    try:
        filename = file.split('/')[-1]
        print('正在下载', filename, '....')
        video = requests.get(url=file, headers=headers).content
        boot = './video'
        if not os.path.exists(boot):
            os.mkdir(boot)
        file_root = os.path.join(boot, filename)
        if not os.path.exists(file_root):
            with open(file_root, 'wb') as f:
                f.write(video)
            print(filename, '下载完成!')
        else:
            print('文件已经存在')
    except Exception as e:
        print(e)


def main():
    url = "https://www.pearvideo.com/"
    html = get_content(url=url)
    parse_content(html=html)
    get_detail(urls)
    pool = Pool(1)
    pool.map(down_file, down_urls)

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()

