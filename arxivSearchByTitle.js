// ==UserScript==
// @name         Arxiv Search and Extract
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  A script to search Arxiv and extract titles
// @author       You
// @match        https://arxiv.org/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // 创建输入框
    const inputBox = document.createElement('input');
    inputBox.type = 'text';
    inputBox.placeholder = 'Enter your search terms here';

    // 创建搜索按钮
    const searchButton = document.createElement('button');
    searchButton.textContent = 'Search';
    searchButton.onclick = async () => {
        const query = inputBox.value.trim();
        if (!query) {
            outputBox.value = 'Error: Input is empty or only contains spaces.';
            return;
        }

        const terms = query.split(/\s+/).filter(term => term !== '');
        const encodedQuery = encodeURIComponent(terms.join('+'));
        const url = `https://arxiv.org/search/?query=${encodedQuery}&searchtype=title&abstracts=show&order=-announced_date_first&size=50&start=0`;

        try {
            const response = await fetch(url);
            const text = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');

            let texts = [];
            const paragraphs = doc.querySelectorAll('p.title.is-5.mathjax');
            paragraphs.forEach(p => {
                const text = p.textContent.replace(/\n\s+/g, '');
                texts.push(text);
            });

            let nextPageUrl = null;
            const navLinks = doc.querySelector('nav').querySelectorAll('a');
            if (navLinks.length > 1 && navLinks[1].className === 'pagination-next') {
                nextPageUrl = navLinks[1].href;
            }
            while (nextPageUrl) {
                const nextPageResponse = await fetch(nextPageUrl);
                const nextPageText = await nextPageResponse.text();
                const nextPageDoc = parser.parseFromString(nextPageText, 'text/html');

                const nextParagraphs = nextPageDoc.querySelectorAll('p.title.is-5.mathjax');
                nextParagraphs.forEach(p => {
                    const text = p.textContent.replace(/\n\s+/g, '').replace(/\.+$/, '');
                    texts.push(text);
                });

                const nextNavLinks = nextPageDoc.querySelector('nav').querySelectorAll('a');
                if (nextNavLinks.length > 1 && nextNavLinks[1].className === 'pagination-next') {
                    nextPageUrl = nextNavLinks[1].href;
                } else {
                    nextPageUrl = null;
                }
            }

            outputBox.value = texts.join('\n');
        } catch (error) {
            outputBox.value = `Error: ${error.message}`;
        }
    };

    // 创建输出框
    const outputBox = document.createElement('textarea');
    outputBox.rows = 10;
    outputBox.cols = 50;
    outputBox.readOnly = true;

    // 创建复制按钮
    const copyButton = document.createElement('button');
    copyButton.textContent = 'Copy';
    copyButton.onclick = () => {
        outputBox.select();
        document.execCommand('copy');
    };

    // 创建容器
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '10px';
    container.style.right = '10px';
    container.style.zIndex = '1000';
    container.style.backgroundColor = 'white';
    container.style.padding = '10px';
    container.style.border = '1px solid black';
    container.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.2)';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '10px';

    // 第一行：输入框和搜索按钮
    const firstRow = document.createElement('div');
    firstRow.style.display = 'flex';
    firstRow.style.gap = '10px';
    firstRow.appendChild(inputBox);
    firstRow.appendChild(searchButton);

    // 将元素添加到页面
    container.appendChild(firstRow);  // 输入框和搜索按钮
    container.appendChild(outputBox);  // 输出框
    container.appendChild(copyButton);  // 复制按钮

    document.body.appendChild(container);
})();
