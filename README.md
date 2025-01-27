
# Paper Downloader

This project provides a tool to download academic papers based on their titles using Bing search. It supports two download methods: `requests` and `aria2`.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup4
- requests
- EdgeDriver (for Selenium)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/paper-downloader.git
   cd paper-downloader
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the EdgeDriver executable and place it in a known location. Update the path in `paper_downloader.py` if necessary:
   ```python
   service = Service(r"D:\Applications\edgedriver\msedgedriver.exe")
   ```

## Usage

1. Prepare a text file (`title_list.txt`) containing the titles of the papers you want to download, one title per line.

2. Run the script with the following command:
   ```bash
   python paper_downloader.py --title_list_path title_list.txt --downloader requests --save_dir ./output
   ```

### Arguments

- `--title_list_path`: Path to the file containing the list of titles.
- `--start_char_idx`: Starting character index for reading titles (default: 0).
- `--downloader`: Downloader to use (`requests` or `aria2`, default: `requests`).
- `--save_dir`: Directory to save downloaded files (default: `./output`).

## Example

Given a `title_list.txt` file with the following content:
```
Deep Learning for Image Recognition
Reinforcement Learning: An Introduction
```

Running the script:
```bash
python paper_downloader.py --title_list_path title_list.txt --downloader requests --save_dir ./papers
```

This will search for each title on Bing, find the corresponding PDF URL, and download the PDFs to the `./papers` directory.

## Notes

- The script uses Bing search to find the PDF URLs. Ensure that the titles are precise to get accurate results.
- The `requests` downloader is used by default. You can switch to `aria2` for potentially faster downloads.
- The script is configured to run in headless mode, meaning it won't open a browser window.
