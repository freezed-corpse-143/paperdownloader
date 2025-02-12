import subprocess
import os

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import argparse

def download_from_url(save_dir, url, downloader="requests"):
    if downloader == "requests":
        cmd_prefix = f"python {os.path.abspath('./requests_download.py')} "
    elif downloader == "aria2":
        cmd_prefix = "aria2c "
    else:
        raise ValueError(f"don't support downloader {downloader}")

    cmd = cmd_prefix + f"-d {os.path.abspath(save_dir)} {url}"
    return cmd

def run_command(cmd):
    try:
        # 使用 subprocess.run 执行命令
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        return cmd, result.stdout, None  # 返回命令、标准输出和错误（无错误时为 None）
    except subprocess.CalledProcessError as e:
        return cmd, e.stdout, e.stderr  # 如果命令执行失败，返回错误信息

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
    soup = BeautifulSoup(html_txt, 'html.parser')

    main_container = soup.find('main')

    ol_container = main_container.find('ol')

    result_list = []

    for li in ol_container.find_all('li'):
        h2 = li.find('h2')
        if h2:
            a_tag = h2.find('a')
            if a_tag:
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
                result_list.append(decoded_url)
    return result_list

def select_download_url(url_list):
    for url in url_list:
        if url.endswith(".pdf"):
            return url
        if url.startswith("https://arxiv.org/pdf"):
            return url
        if url.startswith("https://arxiv.org/abs/"):
            return url.replace("abs", "pdf")
        if url.startswith("https://openreview.net/pdf"):
            return url
        if url.startswith("https://openreview.net/forum"):
            return url.replace("forum", "pdf")
        if url.startswith("https://ojs.aaai.org/index.php/AAAI/article/download/"):
            return url
    return None
# search title
def bing_search_title_url(title):
    options = Options()
    options.add_argument('log-level=INT')
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
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
        return "", title
    else:
        return download_from_url(save_dir, url, downloader), title

def get_pdf_from_title_list(title_list, downloader, save_dir):
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(process_title, title, downloader, save_dir) for title in title_list]

    cmd_list = []
    error_title_list = []
    for future in as_completed(futures):
        try:
            cmd, title = future.result()
            if cmd != "" and cmd not in cmd_list:
                cmd_list.append(cmd)
            else:
                error_title_list.append(title)
        except Exception as e:
            print(f"An error occurred: {e}")
    with open("./cmd_list.txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(cmd_list))

    with open("./error_title_list.txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(error_title_list))

def batch_run_cmd(cmd_list):
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务到线程池
        futures = {executor.submit(run_command, cmd): cmd for cmd in cmd_list}

        # 遍历已完成的任务
        for future in as_completed(futures):
            cmd = futures[future]  # 获取对应的命令
            try:
                cmd, stdout, stderr = future.result()  # 获取任务结果
                if stderr:
                    print(f"Command failed: {cmd}\nError: {stderr}")
                else:
                    print(f"Command succeeded: {cmd}\nOutput: {stdout}")
            except Exception as e:
                print(f"Unexpected error occurred while running command {cmd}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download papers based on titles.")
    parser.add_argument("--title_list_path", type=str, help="Path to the file containing the list of titles.")
    parser.add_argument("--start_char_idx", type=int, default=0, help="Starting character index for reading titles.")
    parser.add_argument("--downloader", type=str, default="requests", choices=["requests", "aria2"], help="Downloader to use.")
    parser.add_argument("--save_dir", type=str, default="./output", help="Directory to save downloaded files.")
    args = parser.parse_args()

    title_list = read_title_list(args.title_list_path, args.start_char_idx)

    get_pdf_from_title_list(title_list, downloader=args.downloader, save_dir=args.save_dir)
    
    with open("./cmd_list.txt", encoding='utf-8') as f:
        cmd_list = f.read().split("\n")

    batch_run_cmd(cmd_list)

if __name__ == "__main__":
    main()