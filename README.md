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
./pipeline.py -a 2025-07-01 -b 2025-08-01 -f timber.json
```

##### If it works then:

```
./api.py &
curl http://localhost:8870/api/reports/timber.json?after=2025-07-01&before=2025-08-01
```

