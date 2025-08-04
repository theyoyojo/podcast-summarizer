import json
import os
import pathlib
from datetime import datetime

def date_type(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f'Bad date argument: {datestr} (Excepted YYYY-MM-DD)')


def load_cache(cachedir):
    if not os.path.exists(cachedir):
        pathlib.Path(cachedir).mkdir()
    cachefile  = f'{cachedir}/cache.json'
    if os.path.exists(cachefile):
        try:
            with open(cachefile, 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            print(f"Error: The file '{cachefile}' was not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{cachefile}'. The file may be invalid.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    return {
            'dir': cachedir,
            'count': 0,
            'ranges': [],
            'timestamp': datetime.now().isoformat(),
            'podcasts': []
        }

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
