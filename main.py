import json
from pathlib import Path
import feedparser
from youtube_transcript_api import YouTubeTranscriptApi

#OddAlerts
CHANNEL_ID = "UCIahRM8pCOxKZ2FmGgDHGyg"
STATE_FILE = Path("data/state.json")
TRANSCRIPTS_DIR = Path("data/transcripts")

def load_state():
    if not STATE_FILE.exists():
        return {"last_video_id": ""}
    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_state(video_id):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump({"last_video_id": video_id}, file, indent=4)

def get_latest_video():
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + CHANNEL_ID
    feed = feedparser.parse(url)
    if len(feed.entries) == 0:
        return None
    entry = feed.entries[0]
    video_id = getattr(entry, "yt_videoid", "")
    if video_id == "":
        video_id = entry.id.split(":")[-1]
    return {
        "video_id": video_id,
        "title": entry.title,
        "link": entry.link,
        "published": entry.get("published", "")
    }

def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=["en", "pl"])
    text = ""
    for line in transcript:
        text += line.text + "\n"
    return text

def save_transcript(video, transcript):
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = video["title"].replace("/", "_").replace("\\", "_").replace(":", "_")
    filename = video["published"][:10] + "_" + video["video_id"] + "_" + safe_title[:50] + ".txt"
    path = TRANSCRIPTS_DIR / filename
    with open(path, "w", encoding="utf-8") as file:
        file.write("TITLE: " + video["title"] + "\n")
        file.write("URL: " + video["link"] + "\n")
        file.write("VIDEO_ID: " + video["video_id"] + "\n\n")
        file.write(transcript)
    return path

def main():
    state = load_state()
    video = get_latest_video()
    if video is None:
        print("Nie znaleziono filmów.")
        return
    if video["video_id"] == state["last_video_id"]:
        print("Brak nowego filmu.")
        return
    print("Jest nowy film:")
    print(video["title"])
    print(video["link"])
    try:
        transcript = get_transcript(video["video_id"])
        path = save_transcript(video, transcript)
        print("Transkrypcja zapisana:")
        print(path)
    except Exception as error:
        print("Nie udało się pobrać transkrypcji.")
        print(error)
    save_state(video["video_id"])
main()