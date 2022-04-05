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
base_url = 'https://www.ximalaya.com/'
sound_url = base_url + 'sound/{}'
album_url = base_url + 'album/{}'


def usage():
    prompt = f'python {Path(__file__).name} {base_url}[album | sound]/[album_id | sound_id]'
    print(prompt)


def parse_url(url):
    """
    解析url是音频页还是专辑页
    """
    res = re.findall(r'(album)|(sound)', url)
    parse_res = {}
    if res:
        album, sound = res[0]
        if album:
            parse_res['tag'] = album
        else:
            parse_res['tag'] = sound
        parse_res['id'] = re.findall(r'\d+', url)[0]
        parse_res['url'] = url
    return parse_res


def download_sound(sound_id):
    """
    下载单个音频
    """
    print(f'>>>正在解析：{sound_url.format(sound_id)}')
    parse_res = parse_sound_page(sound_id)

    suffix = '.' + parse_res['src'].split('.')[-1]
    save_path = Path(__file__).parent.joinpath('data', parse_res['album_title'])
    file_path = save_path.joinpath(f'{parse_res["title"]}{suffix}')

    print(f'>>>正在下载：{parse_res["title"]}{suffix}')
    r = requests.get(parse_res['src'], stream=True, headers=headers)

    
    if not save_path.exists():
        save_path.mkdir(exist_ok=True, parents=True)

    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    print(f'>>>下载完成！\n')


def download_sound_list(album_id):
    """
    下载专辑列表
    """
    print(f'>>>正在解析：{album_url.format(album_id)}\n')
    ids = parse_album_page(album_id)
    for i in ids:
        download_sound(i)


def parse_sound_page(sound_id):
    """
    解析音频页面，获取音频真实地址
    """
    sound_url_ = sound_url.format(sound_id)
    r = requests.get(sound_url_, headers=headers)

    res = {}
    doc = pq(r.text)
    res['title'] = doc('h1.title-wrapper').text()

    # 获取音频的真实地址
    sound_api = f'{base_url}revision/play/v1/audio?id={sound_id}&ptype=1'
    r = requests.get(sound_api, headers=headers)

    res['id'] = sound_id
    res['src'] = json.loads(r.text)['data']['src']
    res['album_title'] = doc('a.albumTitle').text()

    return res


def parse_album_page(album_id):
    """
    解析专辑页面，获取第一页（专辑可能有多页）的音频url
    """
    album_api = f'{base_url}revision/album/v1/getTracksList?albumId={album_id}&pageNum=1&sort=0'
    r = requests.get(album_api, headers=headers)
    d = json.loads(r.text)
    return list(map(lambda x: x['trackId'], d['data']['tracks']))


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
        sys.exit(-1)
    url = args[0]
    parse_url_res = parse_url(url)
    if not len(parse_url_res):
        usage()
        sys.exit(-1)
    else:
        if parse_url_res['tag'] == 'album':
            download_sound_list(parse_url_res['id'])
        else:
            download_sound(parse_url_res['id'])


if __name__ == '__main__':
    main()
