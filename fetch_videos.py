import csv
import yt_dlp

VIEW_THRESHOLD = 80000

# Channel URLs to scrape
CHANNELS = [
    {"name": "Colaws", "url": "https://www.youtube.com/@Colaws/videos"},
    {"name": "Kanerr", "url": "https://www.youtube.com/@Amerikanerr/videos"}
]

def fetch_channel_videos(channel_info, threshold):
    """Fetches video metadata directly via yt-dlp without an API key."""
    name = channel_info["name"]
    url = channel_info["url"]
    
    print(f"Fetching videos for {name} ({url})...")
    
    # extract_flat=True pulls playlist/channel video entries quickly without downloading streams
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
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                
                qualified.append({
                    "channel": name,
                    "title": entry.get('title', 'Unknown Title'),
                    "views": views,
                    "url": video_url,
                    "id": video_id
                })
                
    return qualified

def main():
    all_videos = []
    
    for ch in CHANNELS:
        try:
            matched = fetch_channel_videos(ch, VIEW_THRESHOLD)
            print(f"Found {len(matched)} videos with >= {VIEW_THRESHOLD:,} views for {ch['name']}.")
            all_videos.extend(matched)
        except Exception as e:
            print(f"Error fetching {ch['name']}: {e}")

    # Sort descending by view count
    all_videos.sort(key=lambda x: x["views"], reverse=True)

    # Export to CSV
    output_filename = "kanerr_colaws_80k.csv"
    fieldnames = ["channel", "views", "title", "url", "id"]
    
    with open(output_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_videos)

    print(f"\nDone! Saved {len(all_videos)} qualifying videos to '{output_filename}'.")

if __name__ == "__main__":
    main()