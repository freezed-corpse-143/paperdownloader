import subprocess
import os

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import base64
import time

import argparse

def download_from_url(save_dir, url, downloader="requests"):
    if downloader == "requests":
        cmd_prefix = f"python {os.path.abspath('./requests_download.py')} "
    elif downloader == "aria2":
        cmd_prefix = "aria2c "
    else:
        raise ValueError(f"don't support downloader {downloader}")

    cmd = cmd_prefix + f"-d {os.path.abspath(save_dir)} {url}"

    try:
        # 启动子进程执行下载命令
        print(cmd
              )
        subprocess.run(cmd, shell=True, check=True)
        print(f"Download completed successfully to {save_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Download failed with error: {e}")

def read_title_list(title_list_path, start_char_idx):
    title_list = []
    with open(title_list_path) as f:
        for line in f.readlines():
            title = line[start_char_idx:].strip("\n").strip(".")
            if title not in title_list:
                title_list.append(title)
    return title_list


# parser
def bing_parser_result_html(html_txt):
    # 使用BeautifulSoup解析页面源码
    soup = BeautifulSoup(html_txt, 'html.parser')

    # 找到<main>容器
    main_container = soup.find('main')

    # 找到<ol>容器
    ol_container = main_container.find('ol')

    # 初始化大列表
    result_list = []

    # 遍历每个<li>容器
    for li in ol_container.find_all('li'):
        # 找到第一个<h2>容器下的<a>容器
        h2 = li.find('h2')
        if h2:
            a_tag = h2.find('a')
            if a_tag:
                # 提取href和内部文本
                text = a_tag.get_text(strip=True)
                href = a_tag.get('href')

                parsed_url = urlparse(href)
                query_params = parse_qs(parsed_url.query)

                encoded_url = query_params.get('u', [''])[0][2:]
                encoded_url += "=" * ((4 - len(encoded_url) % 4) % 4)
                encoded_url = encoded_url.replace("_","/").replace("-","+")
                
                try:
                    decoded_url = base64.b64decode(encoded_url).decode('utf-8')
                except Exception as e:
                    print(parsed_url.query)
                    raise e
                # 将结果添加到列表中
                result_list.append(decoded_url)
    return result_list

def select_download_url(url_list):
    # 筛选出包含pdf的url
    for url in url_list:
        if url.endswith(".pdf"):
            return url
        if url.startswith("https://arxiv.org/pdf"):
            return url
        if url.startswith("https://arxiv.org/abs/"):
            return url.replace("abs", "pdf")
        if url.startswith("https://openreview.net/pdf"):
            return url
        if url.startswith("https://openreview.net/forum")
            return url.replace("forum", "pdf")
    return None

# search title
def bing_search_title_url(title):
    options = Options()
    options.add_argument('log-level=INT')
    options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
    options.add_argument("--disable-gpu")  # 禁用 GPU 渲染
    options.add_argument("--no-sandbox")  # 禁用沙盒模式
    service = Service(r"D:\Applications\edgedriver\msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)

    url = f"https://www.bing.com/search?q={title.replace(' ', '+')}+pdf&num=10"
    print(url)
    driver.get(url)
    time.sleep(5)
    response_txt = driver.page_source
    driver.quit()
    title_url_list = bing_parser_result_html(response_txt)
    target_url = select_download_url(title_url_list)
    print(f"target url: {target_url}")
    return target_url

def process_title(title, downloader, save_dir):
    url = bing_search_title_url(title)
    if url is None:
        print(f"No URL found for title: {title}")
    else:
        download_from_url(save_dir, url, downloader)

def get_pdf_from_title_list(title_list, downloader, save_dir):
    for title in title_list:
        process_title(title, downloader, save_dir)
def main():
    parser = argparse.ArgumentParser(description="Download papers based on titles.")
    parser.add_argument("--title_list_path", type=str, help="Path to the file containing the list of titles.")
    parser.add_argument("--start_char_idx", type=int, default=0, help="Starting character index for reading titles.")
    parser.add_argument("--downloader", type=str, default="requests", choices=["requests", "aria2"], help="Downloader to use.")
    parser.add_argument("--save_dir", type=str, default="./output", help="Directory to save downloaded files.")
    args = parser.parse_args()

    title_list = read_title_list(args.title_list_path, args.start_char_idx)

    get_pdf_from_title_list(title_list, downloader=args.downloader, save_dir=args.save_dir)
    

if __name__ == "__main__":
    main()