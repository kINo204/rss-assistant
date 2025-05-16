# RSS Assistant: Paper Tracking with LLM

Using RSS feeds to track latest news in your research field? Getting hundreds of papers
from reviewing websites a day? This tool is here to help. Add RSS feed URLs, fetch for
update, and use LLM to summarize the latest papers.

## Usage

For now, a ".env" configuration file is required at the project's root, which may look like:

```
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RSSProcessor/1.0"
TIMEOUT = 10
MAX_RETRIES = 3
API_KEY = "..."
FIELD = "Artifitial General Intelligence"
```

Then, add your feed URLs in `config/feeds.txt`, and run the script `main.py`.
