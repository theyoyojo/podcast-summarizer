# podcast summarizer

## Setup:

### Linux

```
python3 -m venv .
source bin/activate
pip install -r requirements.txt
./db.py
```

# M-series MacOS

```
python3.12 -m venv .
source bin/activate
pip install -r requirements.txt
pip install mlx-whisper
./db.py
```

Get ffmpeg

Set your `OPENAI_API_KEY` in the environment

## Example usage:

```
# example invocation: ./pipeline.py -a 2025-07-01 -b 2025-08-01 -f timber.json
```

##### If it works then:

```
cat 2025-07-01_2025-08-01/general.summary.txt
```

