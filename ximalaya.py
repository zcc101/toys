import sys
import re
import json
from pathlib import Path
import requests
from pyquery import PyQuery as pq


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'
    }


def usage(args):
    prompt = f'python {args[0]} https://www.ximalaya.com/[album, sound]/xxxx'
    print(prompt)


def parse_url(url):
    """
    解析url是音频详情页还是专辑页
    """
    res = re.findall(r'(album)|(sound)', url)
    parse_res = {}
    if not res:
        parse_res['tag'] = res[0][0]
        parse_res['id'] = re.findall(r'\d+', url)[0][0]
        parse_res['url'] = url
    return parse_res


def download_sound(sound_id):
    parse_res = parse_sound_page(sound_id)
    r = requests.get(parse_res['src'], stream=True, headers=headers)
    suffix = '.' + parse_res['src'].split('.')[-1]
    save_path = Path(__file__).parent.joinpath('data', parse_res['album_title'])
    file_path = save_path.joinpath(f'{parse_res["title"]}{suffix}')
    save_path.mkdir(exist_ok=True, parents=True)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)


def download_sound_list(album_id):
    ids = parse_album_page(album_id)
    for i in ids:
        download_sound(i)


def parse_sound_page(sound_id):
    r = requests.get(f'https://www.ximalaya.com/sound/{sound_id}', headers=headers)
    res = {}
    doc = pq(r.text)
    res['title'] = doc('h1.title-wrapper').text()
    r = requests.get(f'https://www.ximalaya.com/revision/play/v1/audio?id={sound_id}&ptype=1', headers=headers)
    res['id'] = sound_id
    res['src'] = json.loads(r.text)['src']
    res['album_title'] = doc('a.albumTitle').text()
    return res


def parse_album_page(album_id):
    r = requests.get(
        f'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum=1&sort=0',headers=headers)
    d = json.loads(r.text)
    return list(map(lambda x: x['trackId'], d['data']['tracks']))


def main():
    args = sys.argv[:]
    if len(args) != 2:
        usage(args)
        sys.exit(-1)
    url = args[1]
    parse_url_res = parse_url(url)
    if len(parse_url_res):
        usage(args)
        sys.exit(-1)
    else:
        if parse_url_res['tag'] == 'album':
            download_sound_list(parse_url_res['id'])
        else:
            download_sound(parse_url_res['id'])
