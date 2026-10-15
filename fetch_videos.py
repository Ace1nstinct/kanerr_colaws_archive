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
    """Generates an HTML page with direct YouTube App playlist links."""
    video_ids = [v["id"] for v in videos]
    
    # YouTube URL queues support batches of up to 45 IDs per link
    batch_size = 45
    playlist_buttons = []
    for i in range(0, len(video_ids), batch_size):
        chunk = video_ids[i:i + batch_size]
        part_num = (i // batch_size) + 1
        yt_queue_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(chunk)}"
        playlist_buttons.append(
            f'<a class="yt-btn" href="{yt_queue_url}" target="_blank">▶ Open Part {part_num} in YouTube App ({len(chunk)} Videos)</a>'
        )

    buttons_html = "\n".join(playlist_buttons)

    video_items_html = "\n".join([
        f'<li><a href="{v["url"]}" target="_blank"><b>[{v["channel"]}]</b> {v["title"]}</a> ({v["views"]:,} views)</li>'
        for v in videos
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kanerr & Colaws Archive</title>
  <style>
    body {{
      margin: 0;
      background: #0f0f0f;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .container {{
      max-width: 650px;
      width: 100%;
    }}
    h1 {{
      font-size: 1.4rem;
      margin-bottom: 8px;
    }}
    p {{
      color: #aaa;
      font-size: 0.95rem;
    }}
    .button-group {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin: 20px 0;
    }}
    .yt-btn {{
      display: block;
      text-align: center;
      background: #cc0000;
      color: #ffffff;
      text-decoration: none;
      padding: 14px 18px;
      font-size: 1rem;
      font-weight: bold;
      border-radius: 8px;
    }}
    .yt-btn:hover {{
      background: #e60000;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin-top: 20px;
    }}
    li {{
      padding: 10px 0;
      border-bottom: 1px solid #222;
      font-size: 0.9rem;
    }}
    li a {{
      color: #3ea6ff;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Kanerr & Colaws Archive (&ge; 80k Views)</h1>
    <p>Tap a button below to launch these videos directly into the <b>YouTube App</b> with your account/ad-blocker active and continuous autoplay enabled.</p>
    
    <div class="button-group">
      {buttons_html}
    </div>

    <h3>All Archived Videos ({len(videos)})</h3>
    <ul>
      {video_items_html}
    </ul>
  </div>
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
    print("Updated CSV and regenerated YouTube player launcher.")

if __name__ == "__main__":
    main()
