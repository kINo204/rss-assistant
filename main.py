from utils import cleaner, dedup, llm
import feedparser
import datetime
import sys


""" Init env variables """
import os, dotenv
dotenv.load_dotenv()
USER_AGENT = os.getenv('USER_AGENT')
TIMEOUT = os.getenv('TIMEOUT')


def run():
    outdir = "outputs/" + \
             f"{datetime.datetime.today().strftime("%Y-%m-%d#%H-%M")}"

    def save(directory, filename, content):
        os.makedirs(directory, exist_ok=True)

        filename = "".join([c if (c.isalnum() or c == '.')
                            else "_" for c in filename])[:50]
        filepath = os.path.join(directory, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def process_entries(entries, category):
        nonlocal progress
        for entry in entries:
            progress += 1
            print(f"\rRunning ({progress}/{nentries}) ...")
            sys.stdout.flush()

            if dedup.search(entry.id):
                continue
            dedup.mark(entry.id)

            text = cleaner.clean_content(entry, min_length=600)
            if not text:
                continue

            content = f"Category: {category}\nTitle: {entry.title}\n\n{text}"
            feeddir = os.path.join(outdir, "feeds", category)

            llm.restart(llm.hints["background"]+llm.hints["article_structure"])
            rating = float(llm.ask(llm.hints["rating"]+content))
            save(feeddir, entry.title, content)

            if rating > 7.15:
                nonlocal contents
                contents += f"{content}\nRating: {rating}"

    with open('config/feeds.txt') as f:
        feeds = [line.strip() for line in f
                 if line.strip() and not line.startswith('#')]

    ds = []
    contents = ""
    try:
        for feed_url in feeds:
            d = feedparser.parse(feed_url, agent=USER_AGENT)
            if d.status == 200:
                ds.append(d)
            else:
                print(f"请求失败: {feed_url} 状态码: {d.status}")
    finally:
        dedup.sync()

    nentries = sum([len(d.entries) for d in ds])
    progress = 0

    for d in ds:
        process_entries(d.entries, category=d.feed.title)

    print("Summarizing ...")
    llm.restart(llm.hints["background"]+llm.hints["article_structure"])
    summary = llm.ask(llm.hints["summary"]+contents, model="deepseek-reasoner")
    summary = llm.ask(llm.hints["translation"]+summary, model="deepseek-reasoner")
    save(outdir, "summary.md", summary)


if __name__ == "__main__":
    run()
