// ==UserScript==
// @name         Bing PDF Downloader
// @namespace    http://tampermonkey.net/
// @version      0.3
// @description  在 Bing 上搜索论文标题并下载 PDF
// @author       Your Name
// @match        *://www.bing.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_download
// ==/UserScript==

(function() {
    'use strict';

    // 创建弹出框
    const dialog = document.createElement('div');
    dialog.style.position = 'fixed';
    dialog.style.top = '50%';
    dialog.style.left = '50%';
    dialog.style.width = '450px';
    dialog.style.height = '300px';
    dialog.style.transform = 'translate(-50%, -50%)';
    dialog.style.backgroundColor = 'white';
    dialog.style.padding = '20px';
    dialog.style.border = '1px solid #ccc';
    dialog.style.zIndex = '1000';
    dialog.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.1)';
    dialog.style.overflow = 'auto'; // 确保内容超出时可以滚动

    const closeButton = document.createElement('button');
    closeButton.textContent = '×';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '10px';
    closeButton.style.right = '10px';
    closeButton.style.fontSize = '20px';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.cursor = 'pointer';

    const textarea = document.createElement('textarea');
    textarea.style.width = '100%';
    textarea.style.height = '230px';
    textarea.style.marginBottom = '10px';
    textarea.placeholder = '输入论文标题，每行一个';

    const downloadButton = document.createElement('button');
    downloadButton.textContent = '下载';
    downloadButton.style.display = 'block';
    downloadButton.style.marginTop = '10px';

    const progressBar = document.createElement('div');
    progressBar.style.width = '100%';
    progressBar.style.height = '20px';
    progressBar.style.backgroundColor = '#f3f3f3';
    progressBar.style.position = 'relative';
    progressBar.style.marginBottom = '10px';

    const progress = document.createElement('div');
    progress.style.height = '100%';
    progress.style.width = '0%';
    progress.style.backgroundColor = '#4caf50';
    progress.style.transition = 'width 0.5s';
    progressBar.appendChild(progress);

    
    dialog.appendChild(closeButton);
    dialog.appendChild(textarea);
    dialog.appendChild(progressBar);
    dialog.appendChild(downloadButton);
    document.body.appendChild(dialog);

    // 关闭按钮点击事件
    closeButton.addEventListener('click', () => {
        dialog.remove();
    });

    // 下载按钮点击事件
    downloadButton.addEventListener('click', async () => {
        let totalTitles = 0, completedTitles = 0;
        const titles = Array.from(new Set(textarea.value.split('\n').map(title => title.trim()))).filter(title => title !== '');
        for (const title of titles) {

            const searchQuery = title.replace(/ /g, '+') + "+pdf";
            const searchUrl = `https://www.bing.com/search?q=${searchQuery}`;

            try {
                const html = await fetchSearchResults(searchUrl);
                const resultList = bingParserResultHtml(html);
                const downloadUrl = selectDownloadUrl(resultList);

                if (downloadUrl) {
                    // 替换掉 Windows 文件名中不允许的字符
                    const safeTitle = title.replace(/[\\\/:*?"<>|\r\n]/g, '');

                    GM_download({ url: downloadUrl, name: `${safeTitle}.pdf`,onload: () => {
                        completedTitles++;
                        if(completedTitles >= totalTitles){
                            progressBar.style.display = 'none'; // 全部完成后隐藏进度条
                        } else {
                            progress.style.width = `${(completedTitles / totalTitles) * 100}%`;
                        }
                    }});
                } else {
                    console.warn(`未找到 ${title} 的 PDF 下载链接`);
                }
            } catch (error) {
                console.error(`搜索 ${title} 时出错:`, error);
            }
        }
    });

    // 获取 Bing 搜索结果
    function fetchSearchResults(url) {
        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: 'GET',
                url: url,
                onload: function(response) {
                    resolve(response.responseText);
                },
                onerror: function(error) {
                    reject(error);
                }
            });
        });
    }

    // 解析 Bing 搜索结果
    function bingParserResultHtml(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const mainContainer = doc.querySelector('main');
        const olContainer = mainContainer.querySelector('ol');
        const resultLinks = olContainer.querySelectorAll('li h2 a');
        const resultList = [];

        resultLinks.forEach(aTag => {
            const href = aTag.getAttribute('href');
            if (href) {
                const parsedUrl = new URL(href, window.location.href); // 使用当前页面的URL作为基础
                const queryParams = new URLSearchParams(parsedUrl.search);
                const encodedUrl = queryParams.get('u');
                if (encodedUrl) {
                    let decodedUrl = decodeURIComponent(encodedUrl);
                    try {
                        decodedUrl = decodedUrl.substring(2);
                        decodedUrl = decodedUrl.replace(/_/g, '/').replace(/-/g, '+');
                        while (decodedUrl.length % 4 !== 0) {
                            decodedUrl += '=';
                        }
                        const decodedUrlFinal = atob(decodedUrl);
                        resultList.push(decodedUrlFinal);
                    } catch (e) {
                        console.warn('直接解码失败，修正格式后的编码', decodedUrl);
                    }
                } else {
                    resultList.push(href);
                }
            }
        });
        return resultList;
    }

    // 选择下载链接
    function selectDownloadUrl(urlList) {
        for (let url of urlList) {
            if (url.endsWith(".pdf")) return url;
            if (url.startsWith("https://arxiv.org/pdf")) return url;
            if (url.startsWith("https://arxiv.org/abs/")) return url.replace("abs", "pdf");
            if (url.startsWith("https://arxiv.org/html/")) return url.replace("html", "pdf");
            if (url.startsWith("https://openreview.net/pdf")) return url;
            if (url.startsWith("https://openreview.net/forum")) return url.replace("forum", "pdf");
            if (url.startsWith("https://ojs.aaai.org/index.php/AAAI/article/download/")) return url;
        }
        return null;
    }
})();