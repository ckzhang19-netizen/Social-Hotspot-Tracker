import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys
import urllib.parse

# --- 配置 ---
TOKEN = os.environ.get("PUSHPLUS_TOKEN")

# 四大主题关键词
TOPICS = {
    "高考/中考教育": ["高考", "中考", "志愿填报", "分数线", "强基计划"],
    "家庭教育": ["家庭教育", "亲子关系", "教育方法", "情商培养"],
    "成长学习": ["学习方法", "高效学习", "成长思维", "记忆力"],
}

# --- 核心功能 ---

def get_search_results(query):
    """
    实际聚合：调用百度新闻搜索，并限制时间范围在最近 7 天内
    """
    
    
        # 百度新闻搜索 URL
    # gpc=1&qdr=1: 限制搜索时间为最近 24 小时 (qdr=1)
    base_url = "https://www.baidu.com/s?tn=news&rtt=4&gpc=1&qdr=1&wd="
    
    # ...
    
    headers = {
        # 模拟三星 S24U 上的最新 Chrome 浏览器 User-Agent
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36'
    }

    results = []

    try:
        # 添加超时和状态码检查
        resp = requests.get(full_url, headers=headers, timeout=15)
        resp.raise_for_status() 
        print(f"DEBUG BAIDU STATUS: {resp.status_code}, Length: {len(resp.text)}")

        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 百度新闻搜索结果的通用 CSS 选择器
        search_results = soup.find_all('div', class_='result') or soup.find_all('div', class_='c-container')
        
        for result in search_results:
            title_tag = result.find('a', target='_blank')
            source_tag = result.find('p', class_='c-author') or result.find('span', class_='c-info')
            
            if title_tag and title_tag.get('href'):
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                source_info = source_tag.get_text(strip=True) if source_tag else '未知来源'
                
                if len(title) > 10:
                    results.append({
                        "title": title,
                        "link": link,
                        "source": source_info
                    })

    except Exception as e:
        print(f"Baidu Search Error: {e}")
        return []

    return results

def send_push(title, content):
    """发送到微信"""
    if not TOKEN: sys.exit(1)
    url = 'http://www.pushplus.plus/send'
    data = {"token": TOKEN, "title": title, "content": content, "template": "markdown"}
    
    try:
        requests.post(url, json=data, timeout=15)
        print("Push successful.")
    except Exception as e:
        print(f"Push failed: {e}")

def main():
    report_title = f"全网热点追踪 ({datetime.date.today().strftime('%Y-%m-%d')})"
    report_parts = [f"## 🔥 全网热点追踪 - 最近一周趋势 (扩大范围)", "---"]
    all_results_found = False

    for topic, keywords in TOPICS.items():
        # *** 关键升级：简化查询，只搜索主题关键词，扩大匹配范围 ***
        query_keywords = ' '.join(keywords) 
        
        # 搜索内容：包含教育 AND 核心关键词
        # 移除社交平台关键词，让百度自己去聚合
        query = f"教育 {query_keywords}" 
        
        results = get_search_results(query) 
        
        if results:
            all_results_found = True
            report_parts.append(f"### 🚀 {topic} - 热门讨论")
            
            # 报告中展示最相关的 10 条结果 (增加数量)
            for i, item in enumerate(results[:10]): 
                # Markdown 格式：[标题](链接) - 来源
                report_parts.append(f"- [{item['title']}]({item['link']}) ({item['source']})")
                
            report_parts.append("\n")

    if not all_results_found:
        report_parts.append("今日未发现符合所有主题的明确热点。请尝试手动扩大搜索范围。")
        
    report_parts.append("---")
    report_parts.append("*💡 结果来自百度新闻聚合 (最近七天，范围已扩大)。*")

    send_push(report_title, "\n".join(report_parts))

if __name__ == "__main__":
    main()
