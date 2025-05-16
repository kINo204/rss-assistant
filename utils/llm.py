from openai import OpenAI, AsyncOpenAI
import asyncio

import os
import dotenv
dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')
FIELD = os.getenv('FIELD')

cli = OpenAI(api_key=API_KEY, base_url='https://api.deepseek.com')
async_cli = AsyncOpenAI(api_key=API_KEY, base_url='https://api.deepseek.com')

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant"
    }
]

hints = {
    "background": f"""
You're an expert in {FIELD}. The user
is seeking progress in this field, and thus has subscribed several RSS
CATEGORIES for latest papers. Now you're assigned the task to
take a look at the papers from a recent update.
Note that the papers are from different categories, but all categories
come together to serve as inspirations for the central topic of {FIELD}.
""",

    "article_structure": """
You'll be given the information of each paper in the following structure:
<category> <title> <content>
- <category> is the RSS source where the paper is from.
- <title> is the title of the paper.
- <content> is basically the abstract of the paper.
""",

    "rating": f"""
Now, given the article below, rate from 0-10 (float number allowed),
with the following standard:
- highly associated with, and be of fundamental/theoretical meaning
  for the {FIELD} field?
- solving important problems of the field?
- create new methods, and not a summary of existing works?
Answer with a single number(rating) and don't say anything else.
""",

    "summary": f"""
Here are some best papers selected from the recent batch of papers, each
separated by "(separation of article)".
Now generate for me a easy-to-read "Summary of the latest {FIELD} Papers",
in markdown format.
The goal is to help me, a new learner in this field who is not
familiar with the domain knowledge, to get started and learn about it
through these summaries on the RSS paper update every day, so design it wisely.
Also, better link the paper title to its original website link.
""",

    "translation": """
将这段话进行翻译，不需要解释翻译的方法等。
注意保留原有的格式，即输出为一个markdown文件内容，但不要包裹在markdown代码块中。
涉及原论文内容（如论文标题）的部分，需要把英文也列出。
"""
}


def restart(sys_hint: str):
    global messages
    messages = [
        {
            "role": "system",
            "content": sys_hint
        }
    ]


def ask(question: str, model="deepseek-chat") -> str:
    messages.append({"role": "user", "content": question})

    response = cli.chat.completions.create(
        model=model,
        messages=messages)
    res_text = response.choices[0].message.content

    messages.append({"role": "assistant", "content": res_text})

    return res_text


async def async_ask(question: str, model="deepseek-chat") -> str:
    q = {"role": "user", "content": question}
    to_ask = [m for m in messages]
    to_ask.append(q)

    response = await async_cli.chat.completions.create(
        model=model,
        messages=to_ask)
    res_text = response.choices[0].message.content
    messages.append(q)
    messages.append({"role": "assistant", "content": res_text})

    return res_text
