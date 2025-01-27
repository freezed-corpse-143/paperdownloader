import argparse
import os
import requests

def download_file(url, directory):
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 从 URL 中提取文件名
        file_name = os.path.basename(url)

        # 构建完整的文件保存路径
        file_path = os.path.join(directory, file_name)
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"

        # 保存文件
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"文件已下载到: {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"下载文件时出错: {e}")

if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="下载文件到指定目录")

    # 添加命令行参数
    parser.add_argument("-d", "--directory", required=True, help="文件保存的目录")
    parser.add_argument("url", help="要下载的文件的 URL")

    # 解析命令行参数
    args = parser.parse_args()

    # 调用下载函数
    download_file(args.url, args.directory)