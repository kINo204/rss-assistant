import re
import requests
from bs4 import BeautifulSoup
from readability import Document


def get_full_content(entry):
    """ 从文章链接抓取全文 """
    print(f"抓取全文: {entry.link}")

    try:
        # 设置浏览器头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) RSSBot/1.0'
        }

        # 带超时和重试的请求
        response = requests.get(entry.link,
                                headers=headers,
                                timeout=10)
        response.raise_for_status()

        return response.text

    except Exception as e:
        print(f"抓取失败: {entry.link} - {str(e)}")
        return None


def clean_content(entry, min_length=500) -> str:
    """
    深度清理HTML内容，保留语义结构
    返回: 清洗后的纯文本
    """
    if hasattr(entry, 'content') and entry.content[0].value:
        content = entry.content[0].value
    elif hasattr(entry, 'summary') and entry.summary:
        content = entry.summary
    else:
        content = entry.description

    if len(content) < min_length:
        content = get_full_content(entry)

    try:
        # 使用readability提取正文
        doc = Document(content)
        content_html = doc.summary(html_partial=True, keep_all_images=False)

        soup = BeautifulSoup(content_html, 'lxml')

        # 移除干扰元素
        for tag in soup(['img', 'script', 'style', 'aside', 'nav',
                         'header', 'footer', 'form']):
            tag.decompose()

        # 优化列表显示
        for ul in soup('ul'):
            ul.insert_before('\n• ')

        # 提取文本并优化格式
        text = '\n'.join([p.get_text(separator=' ', strip=True)
                         for p in soup.find_all(['p', 'h2', 'h3'])])

        return text

    except Exception as e:
        print(f"内容清洗失败: {str(e)}")
        return None
