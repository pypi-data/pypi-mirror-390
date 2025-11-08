# 🎥 YoutubeVideoCrawler

A **Python module for scalable YouTube data collection** using the YouTube Data API v3.  
It supports keyword-based crawling, comment extraction, intelligent rate limiting, and structured storage (JSON + CSV).

---

## 🚀 Features

- 🔍 Crawl YouTube videos by keywords
- 🧠 Supports **multi-keyword** and **incremental crawling**
- 💬 Optionally fetch video comments
- 🧾 Stores all video metadata in JSON + indexed CSV
- 🧰 Automatically skips duplicate videos
- 💤 Rate-limit friendly (`safe_sleep`)
- 📜 Flexible logger: print to console, file, or both

---

## 📦 Installation

```bash
pip install YoutubeVideoCrawler
````

*(If installing locally from source after modification:)*

```bash
pip install .
```

---

## 🔑 Requirements

Before running, you **must have a YouTube Data API key**:

1. Visit [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a project → Enable the **YouTube Data API v3**
3. Generate an **API key**

---

## 🧩 Basic Usage

```python
from YoutubeVideoCrawler.crawler import YouTubeCrawler

# Initialize the crawler
crawler = YouTubeCrawler(api_key="YOUR_YOUTUBE_API_KEY")

# Start crawling
crawler.run(
    keywords=["software engineering", "machine learning", "distributed systems"],
    fetch_comments=False,
    max_per_keyword=100
)
```

This will:

* Crawl up to 100 videos for each keyword
* Store video metadata in `videos.json`
* Maintain an index in `video_index.csv`

---

## 📂 Storage Output

After running, the module creates the following files:

| File              | Description                                            |
| ----------------- | ------------------------------------------------------ |
| `videos.json`     | Full JSON dump of all fetched video metadata           |
| `video_index.csv` | Lightweight index (videoId, title) for quick reference |
| `token.csv`       | Tracks how many videos have been fetched per keyword   |
| `app.log`         | Logger file recording crawl progress                   |

---

## ⚙️ Advanced Usage

### 🧠 Load keywords from file

Create a file `keywords.txt`:

```
software engineering
deep learning
data visualization
```

Then run:

```python
crawler.run(keyword_file="keywords.txt", max_per_keyword=50)
```

---

### 🪣 Multi-keyword mode

Search all keywords in a single query (logical OR):

```python
crawler.run(
    keywords=["AI", "ML", "DL"],
    search_mode="multi",
    max_per_keyword=200
)
```

---

### 💬 Fetch comments

Enable fetching comments for each video:

```python
crawler.run(
    keywords=["open source software"],
    fetch_comments=True,
    max_per_keyword=20
)
```

Comments are stored within the corresponding video entry in `videos.json`.

---

### 🕒 Resume partially completed crawl

The crawler automatically:

* Detects existing videos in `video_index.csv`
* Skips duplicates
* Continues from where it left off

---

## 🧱 Module Structure

```
YoutubeVideoCrawler/
│
├── crawler.py      # Core crawling logic using YouTube API
├── storage.py      # Persistent storage manager (JSON + CSV)
└── utils.py        # Logging, sleep, and helper functions
```

---

## 🧰 Utility Functions

### `get_logger(name="YouTubeCrawler", log_file="app.log")`

Creates a flexible logger that can print to console, file, or both:

```python
logger.info("This message prints to console and file.")
logger.info("This prints only to file.", print_to="file")
```

### `safe_sleep(seconds, logger)`

Sleep while logging to respect API rate limits.

### `keyword_loader(file_path)`

Loads keyword list from file, skipping lines starting with `#`.

---

## 📊 Example Output

Example `video_index.csv`:

```csv
videoId,title
XyZ12345,Introduction to Software Engineering
AbC67890,Machine Learning Basics
```

Example JSON entry:

```json
{
  "id": "XyZ12345",
  "snippet": {
    "title": "Introduction to Software Engineering",
    "publishedAt": "2025-01-01T12:00:00Z"
  },
  "statistics": {
    "viewCount": "15342",
    "likeCount": "876"
  },
  "keyword": "software engineering",
  "comments": []
}
```

---

## 🧩 Command-Line Example (optional script)

You can create a small script `crawl_youtube.py`:

```python
from yt_video_crawler import YouTubeCrawler

if __name__ == "__main__":
    crawler = YouTubeCrawler(api_key="YOUR_API_KEY")
    crawler.run(keyword_file="keywords.txt", fetch_comments=False, max_per_keyword=50)
```

Run it:

```bash
python crawl_youtube.py
```

---

## 🧑‍💻 Developer Notes

* Respects YouTube API quota and sleep intervals.
* Modular design for easy integration with data pipelines.
* Extend `Storage` class for custom database backends (e.g., MongoDB, SQLite).
* Log verbosity can be controlled using `print_to` argument.

---

## 📜 License

MIT License © 2025 [Md. Masud Mazumder](https://github.com/masudmm)

---

## 🧠 Acknowledgments

* [Google API Python Client](https://github.com/googleapis/google-api-python-client)
* [tqdm](https://github.com/tqdm/tqdm) for progress bars
* [pandas](https://pandas.pydata.org/) for data handling

---

## 🤝 Contributing

Pull requests are welcome!