import argparse
import os
import requests

def download_file(url, directory):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_name = os.path.basename(url)

        file_path = os.path.join(directory, file_name)
        if not file_path.endswith(".pdf"):
            file_path += ".pdf"

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"File has been saved to {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="download file to the directory")

    parser.add_argument("-d", "--directory", required=True, help="save directory")
    parser.add_argument("url", help="file URL")

    args = parser.parse_args()

    download_file(args.url, args.directory)