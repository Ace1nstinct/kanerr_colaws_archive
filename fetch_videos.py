import csv
import json
import yt_dlp

VIEW_THRESHOLD = 80000

CHANNELS = [
    {"name": "Colaws", "url": "https://www.youtube.com/@Colaws/videos"},
    {"name": "Kanerr", "url": "https://www.youtube.com/@Amerikanerr/videos"}
]

def fetch_channel_videos(channel_info, threshold):
    url = channel_info["url"]
    name = channel_info["name"]
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
        'ignoreerrors': True,
    }
    
    qualified = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        entries = result.get('entries', []) if result else []
        
        for entry in entries:
            if not entry:
                continue
            views = entry.get('view_count') or 0
            if views >= threshold:
                video_id = entry.get('id')
                qualified.append({
                    "channel": name,
                    "title": entry.get('title', 'Unknown Title'),
                    "views": views,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "id": video_id
                })
    return qualified

def generate_player_html(videos):
    """Creates a self-contained auto-advancing YouTube player."""
    video_ids = [v["id"] for v in videos]
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kanerr & Colaws Autoplay</title>
  <style>
    body {{
      margin: 0;
      background: #0f0f0f;
      color: #fff;
      font-family: sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
    }}
    #player {{
      width: 100%;
      max-width: 900px;
      aspect-ratio: 16 / 9;
      border: none;
      border-radius: 8px;
    }}
    .controls {{
      margin-top: 15px;
      display: flex;
      gap: 12px;
    }}
    button {{
      background: #cc0000;
      color: #fff;
      border: none;
      padding: 10px 18px;
      font-size: 16px;
      border-radius: 6px;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <h2>Kanerr / Colaws (&ge; 80k Views) Archive</h2>
  <div id="player"></div>
  <div class="controls">
    <button onclick="prevVideo()">Previous</button>
    <button onclick="nextVideo()">Next</button>
  </div>

  <script src="https://www.youtube.com/iframe_api"></script>
  <script>
    const videoIds = {json.dumps(video_ids)};
    let currentIndex = 0;
    let player;

    function onYouTubeIframeAPIReady() {{
      player = new YT.Player('player', {{
        videoId: videoIds[0],
        playerVars: {{ 'autoplay': 1, 'playsinline': 1 }},
        events: {{
          'onReady': (e) => e.target.playVideo(),
          'onStateChange': onPlayerStateChange
        }}
      }});
    }}

    function onPlayerStateChange(event) {{
      // YT.PlayerState.ENDED is 0: advances immediately to next video
      if (event.data === 0) {{
        nextVideo();
      }}
    }}

    function nextVideo() {{
      currentIndex = (currentIndex + 1) % videoIds.length;
      player.loadVideoById(videoIds[currentIndex]);
    }}

    function prevVideo() {{
      currentIndex = (currentIndex - 1 + videoIds.length) % videoIds.length;
      player.loadVideoById(videoIds[currentIndex]);
    }}
  </script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    all_videos = []
    for ch in CHANNELS:
        try:
            matched = fetch_channel_videos(ch, VIEW_THRESHOLD)
            all_videos.extend(matched)
        except Exception as e:
            print(f"Error: {e}")

    all_videos.sort(key=lambda x: x["views"], reverse=True)

    with open("kanerr_colaws_80k.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["channel", "views", "title", "url", "id"])
        writer.writeheader()
        writer.writerows(all_videos)

    generate_player_html(all_videos)
    print("Done! Updated CSV and created index.html autoplay player.")

if __name__ == "__main__":
    main()
