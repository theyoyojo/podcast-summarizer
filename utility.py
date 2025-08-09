import requests
import argparse
from datetime import datetime


def date_type(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
              f'Bad date argument: {datestr} (Excepted YYYY-MM-DD)')


def parse_abf(prog):
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('-a',
                        '--after',
                        type=date_type,
                        required=True,
                        help='select content published after this date')
    parser.add_argument('-b',
                        '--before',
                        type=date_type,
                        required=True,
                        help='select content published before this date')
    parser.add_argument('-f',
                        '--feeds',
                        type=str,
                        required=True,
                        help='select json tile with rss feed list')
    return parser.parse_args()


def download_file(url, local_filename=None, return_data=False):
    if local_filename is None and not return_data:
        local_filename = url.split('/')[-1]

    headers = {
        'User-Agent': '''
                    Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/58.0.3029.110 Safari/537.3'
                    '''.strip()
    }

    try:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
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
