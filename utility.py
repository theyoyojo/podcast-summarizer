import json
import os
import pathlib
from datetime import datetime
import requests

def date_type(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f'Bad date argument: {datestr} (Excepted YYYY-MM-DD)')


def download_file(url, local_filename=None, return_data=False):
    """
    Downloads a file from a URL and saves it to the current directory.

    Args:
        url (str): The URL of the file to download.
        local_filename (str, optional): The name to save the file as.
                                         If None, the function will try to
                                         determine the filename from the URL.
                                         Defaults to None.
    """
    if local_filename is None and not return_data:
        local_filename = url.split('/')[-1]

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }


    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            if return_data:
                return r.content
            else:
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")


def range_union(first, second):
    _0 = first[0]
    _1 = first[1]
    __0 = second[0]
    __1  = second[1]
    
    if _0 > __0:
        if _0 > __1:
            return [second, first]
        if _1 >= __1 >= _0:
            return [(__0, _1)]
        if __1 > _1:
            return [second]
    elif _1 >= __0 >= _0:
        if _1 >= __1 >= _0:
            return [first]
        if __1 > _1:
            return [(_0, __1)]
    else:
        return [first, second]


def cache_add_range(cache, after, before):
    if before < after:
        return
    merged=False
    for i in range(len(cache['ranges'])):
        _0 = cache['ranges'][i][0]
        _1 = cache['ranges'][i][1]
        if _0 > after:
            if _0 > before:
                cache['ranges'].insert(i, [after, before])
                merged = True
                break
            if _1 >= before >= _0:
                cache['ranges'][i] = (after, _1)
                merged = True
                break
            if before > _1:
                cache['ranges'][i] = (after, before)
                merged = True
                break
        elif _1 >= after >= _0:
            if _1 >= before >= _0:
                # merge has no effect
                merged = True
                break
            if before > _1:
                cache['ranges'][i] = (_0, before)
                merged = True
                break
    if not merged:
        cache['ranges'].append([after, before])

def range_interesection(first, second):
    for r in cache['ranges']:
        if before <= r[0] or r[1] <= after:
            if fetch:
                pass # TODO
            else:
                return False

def cache_query(cache, after, before):
    for r in cache['ranges']:
        if r[0] <= after.date().isoformat() and before.date().isoformat() <= r[1]:
            return True
    return False

def cache_write(cache, after, before):
    with open('cache.json', 'w') as f:
        cache['timestamp'] = datetime.now().isoformat()
        cache_add_range(cache, after.date().isoformat(), before.date().isoformat())
        print(json.dumps(cache), file=f)
