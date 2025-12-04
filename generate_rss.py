#!/usr/bin/env python3
"""
聯合新聞網 RSS 生成器
抓取 https://udn.com/news/breaknews/1/99 即時新聞
"""

import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
import re

def fetch_udn_news():
    """抓取聯合新聞網即時新聞"""
    url = "https://udn.com/news/breaknews/1/99"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

def parse_news(html):
    """解析 HTML，提取新聞"""
    # 簡化的解析規則 - 我們先用這個測試，如果不成功再調整
    items = []
    
    # 尋找新聞區塊
    # 聯合新聞網的新聞通常包含在特定結構中
    # 我們先嘗試簡單的標題和連結提取
    import re
    
    # 模式1：尋找新聞連結和標題
    title_pattern = r'<h3[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>\s*</h3>'
    title_matches = re.findall(title_pattern, html, re.DOTALL)
    
    # 模式2：尋找摘要
    summary_pattern = r'<p[^>]*>(.*?)</p>'
    summary_matches = re.findall(summary_pattern, html, re.DOTALL)
    
    # 組合資料（最多15條）
    for i, (link, title) in enumerate(title_matches[:15]):
        # 清理文字
        title = re.sub(r'<[^>]+>', '', title).strip()
        
        # 取得摘要（如果有的話）
        summary = summary_matches[i] if i < len(summary_matches) else ''
        summary = re.sub(r'<[^>]+>', '', summary).strip()[:150]
        
        # 確保連結完整
        if link and not link.startswith('http'):
            link = 'https://udn.com' + link
        
        # 生成假日期（實際應從HTML提取，但先這樣）
        pub_date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        
        items.append({
            'title': title if title else '無標題',
            'link': link if link else 'https://udn.com',
            'pub_date': pub_date,
            'summary': summary if summary else '無摘要'
        })
    
    # 如果沒抓到新聞，使用範例資料
    if not items:
        print("未抓到新聞，使用範例資料")
        items = [
            {
                'title': '範例新聞：聯合新聞網 RSS 測試',
                'link': 'https://udn.com/news/breaknews/1/99',
                'pub_date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z'),
                'summary': '這是 RSS 生成器的測試資料，下次執行會嘗試抓取真實新聞。'
            }
        ]
    
    return items

def create_rss(news_items):
    """生成 RSS XML"""
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    # 頻道資訊
    ET.SubElement(channel, 'title').text = '聯合新聞網 - 即時新聞'
    ET.SubElement(channel, 'link').text = 'https://udn.com/news/breaknews/1/99'
    ET.SubElement(channel, 'description').text = '聯合新聞網即時新聞 RSS 聚合'
    ET.SubElement(channel, 'language').text = 'zh-tw'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
    
    # 添加新聞項目
    for item in news_items:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        ET.SubElement(item_elem, 'description').text = item['summary']
        ET.SubElement(item_elem, 'pubDate').text = item['pub_date']
        ET.SubElement(item_elem, 'guid').text = item['link']
    
    # 美化輸出
    xml_str = ET.tostring(rss, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')

def main():
    print("開始抓取聯合新聞網...")
    html = fetch_udn_news()
    
    news_items = []
    
    if html:
        print("解析新聞內容...")
        news_items = parse_news(html)
    else:
        print("抓取失敗，使用範例資料")
        news_items = [
            {
                'title': '新聞抓取暫時失敗',
                'link': 'https://udn.com',
                'pub_date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z'),
                'summary': 'RSS 生成器正在調整中，請稍後再試。'
            }
        ]
    
    print(f"找到 {len(news_items)} 條新聞")
    
    # 生成 RSS
    rss_xml = create_rss(news_items)
    
    # 寫入檔案
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_xml)
    
    print("RSS 生成完成：feed.xml")
    print("第一行內容:", rss_xml[:100])

if __name__ == '__main__':
    main()