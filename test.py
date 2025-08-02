#import requests

# competitor: https://www.listen411.com/?s=ep

##url = "https://feeds.simplecast.com/abc123"  # Example
#url = 'https://feeds.soundcloud.com/users/soundcloud:users:618306402/sounds.rss'
#response = requests.get(url)

#print("Status:", response.status_code)
#print("Content-Type:", response.headers.get("Content-Type"))
##print("First 500 characters:\n", response.text[:500])
#print(response.text)

# import feedparser

# url = "https://feeds.soundcloud.com/users/soundcloud:users:618306402/sounds.rss"
# feed = feedparser.parse(url)

# # Print basic feed info
# print("Feed title:", feed.feed.get("title", "N/A"))
# print("Feed link:", feed.feed.get("link", "N/A"))
# print()

# # Print first 5 entries
# for entry in feed.entries[:5]:
#     print("Episode Title:", entry.get("title"))
#     print("Published:", entry.get("published"))
#     print("Link:", entry.get("link"))

#     # Get audio enclosures (if available)
#     for enclosure in entry.get("enclosures", []):
#         print("Audio URL:", enclosure.get("href"))

#     print("-" * 40)

# import speech_recognition as sr
# from pydub import AudioSegment
# r = sr.Recognizer()


# # sound = AudioSegment.from_mp3("podcast.mp3")
# # sound.export("podcast.wav", format="wav")

# with sr.AudioFile("podcast.wav") as src:
#     audio = r.record(src)
# text = r.recognize_google(audio)
# print(text)

import whisper

model = whisper.load_model('base')

result = model.transcribe('podcast.wav')

with open("output2.txt", 'w') as f:
    print(result['text'], file=f)
