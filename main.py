from utils import cleaner, dedup, llm
import feedparser
import datetime
import sys
from pathlib import Path
import asyncio


""" Init env variables """
import os
import dotenv
dotenv.load_dotenv()
USER_AGENT = os.getenv('USER_AGENT')
TIMEOUT = os.getenv('TIMEOUT')


def save(directory, filename, content):
    """ Save relative to `outdir`. """
    directory = os.path.join(outdir, directory)
    os.makedirs(directory, exist_ok=True)
    filename = "".join([c if (c.isalnum() or c == '.')
                        else "_" for c in filename])[:50]
    filename = os.path.join(directory, filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def feed():
    with open('config/feeds.txt') as file_feeds:
        feed_urls = [line.strip() for line in file_feeds
                     if line.strip() and not line.startswith('#')]

    feed_objs = []
    for url in feed_urls:
        print(f"fetching from: {url}")
        o = feedparser.parse(url, agent=USER_AGENT)
        feed_objs.append(o)

    # entries = [ [category, entry], [category, entry], ... ]
    entries = [e for s in [
        [[o.feed.title, e] for e in o.entries]
        for o in feed_objs] for e in s]
    updates = [e for e in entries if not dedup.search(e[1])]
    if not updates:
        print("Nothing new, you're up to date.")
        exit(0)

    return updates


progress = 0


def totxt(entry):
    [category, entry] = entry
    return f"""category: {category}
    title: {entry.title}
    content: {cleaner.clean_content(entry, min_length=200)}
    """.lstrip()


async def rate(entry, semaphore):
    async with semaphore:
        global progress
        text = totxt(entry)
        llm.restart(llm.hints["background"]+llm.hints["article_structure"])
        rating = await llm.async_ask(llm.hints["rating"]+text)
        progress += 1
        print(f"\r({progress}/{total}) {entry[1].title[:50]} ...: {rating}",
              end="")
        if progress == total:
            print("")
        return float(rating)


def summary(updates, ratings):
    bests = [updates[i] for i in range(total)
             if ratings[i] > 7.2]
    best_text = '\n(separation of article)\n' \
        .join([totxt(b) for b in bests])
    save("", "bests.txt", best_text)
    llm.restart(llm.hints["background"]+llm.hints["article_structure"])
    summary = llm.ask(llm.hints["summary"]+best_text,
                      model="deepseek-reasoner")
    translated = llm.ask(llm.hints["translation"]+summary)
    save("", "summary.md", translated)


async def main():
    global outdir
    outdir = os.path.join(
        "outputs",
        f"{datetime.datetime.today().strftime("%Y%m%d-%H-%M")}")

    print("feeding ...")
    updates = feed()
    global total
    total = len(updates)

    print(f"{total} feeds fetched, rating ...")
    sem = asyncio.Semaphore(50)
    ratings = await asyncio.gather(*[rate(e, sem) for e in updates])

    print("summarizing ...")
    summary(updates, ratings)

    for e in updates:
        dedup.mark(e[1])
    dedup.sync()


if __name__ == "__main__":
    asyncio.run(main())
