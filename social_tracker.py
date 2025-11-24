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

# 社交媒体平台 (用于搜索聚合)
SOCIAL_PLATFORMS = ["小红书", "抖音", "微博"]

# --- 核心功能 ---

def get_search_results(query):
    """
    实际聚合：调用百度新闻搜索，并限制时间范围在最近 7 天内
    """
    print(f"Executing Baidu News search for: {query}")
    
    # 百度新闻搜索 URL
    # gpc=1&qdr=7: 限制搜索时间为最近 7 天 (qdr=1为24小时，qdr=7为最近一周)
    base_url = "https://www.baidu.com/s?tn=news&rtt=4&gpc=1&qdr=7&wd="
    
    # URL 编码查询字符串
    full_url = base_url + urllib.parse.quote(query)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    results = []

    try:
        resp = requests.get(full_url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 百度新闻搜索结果的通用 CSS 选择器
        # 查找 class="result" 标签
        search_results = soup.find_all('div', class_='result') or soup.find_all('div', class_='c-container')
        
        for result in search_results:
            title_tag = result.find('a', target='_blank')
            source_tag = result.find('p', class_='c-author') or result.find('span', class_='c-info')
            
            if title_tag and title_tag.get('href'):
                # 清理标题，去除可能的多余空格或标签
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href')
                
                # 提取来源和时间
                source_info = source_tag.get_text(strip=True) if source_tag else '未知来源'
                
                # 简单过滤，确保标题有内容
                if len(title) > 10:
                    results.append({
                        "title": title,
                        "link": link,
                        "source": source_info
                    })

    except Exception as e:
        print(f"Baidu Search Error: {e}")
        # 如果搜索失败，返回空列表，确保程序继续运行
        return []

    return results

def send_push(title, content):
    """发送到微信"""
    if not TOKEN: 
        print("Error: PUSHPLUS_TOKEN missing.")
        sys.exit(1)
        
    url = 'http://www.pushplus.plus/send'
    data = {"token": TOKEN, "title": title, "content": content, "template": "markdown"}
    
    try:
        requests.post(url, json=data, timeout=15)
        print("Push successful.")
    except Exception as e:
        print(f"Push failed: {e}")

def main():
    report_title = f"全网热点追踪 ({datetime.date.today().strftime('%Y-%m-%d')})"
    report_parts = [f"## 🔥 全网热点追踪 - 最近一周趋势", "---"]
    all_results_found = False

    for topic, keywords in TOPICS.items():
        # 构造搜索查询：所有关键词 OR 平台关键词
        # 关键词之间用空格隔开，百度默认是 AND 关系
        query_keywords = ' '.join(keywords) 
        platform_keywords = ' OR '.join(SOCIAL_PLATFORMS)
        
        # 最终查询：(核心关键词) AND (社交媒体 OR 权威来源)
        query = f"({query_keywords}) ({platform_keywords} OR 教育部 OR 官网)"
        
        results = get_search_results(query) # 执行真实搜索
        
        if results:
            all_results_found = True
            report_parts.append(f"### 🚀 {topic} - 热门讨论")
            
            # 报告中只展示最相关的 5 条结果
            for i, item in enumerate(results[:5]): 
                # Markdown 格式：[标题](链接) - 来源
                report_parts.append(f"- [{item['title']}]({item['link']}) ({item['source']})")
                
            report_parts.append("\n")

    if not all_results_found:
        report_parts.append("今日未发现符合所有主题和平台筛选的明确热点。请尝试扩大搜索范围。")
        
    report_parts.append("---")
    report_parts.append("*💡 结果来自百度新闻聚合 (最近七天)，点击链接查看详情。*")

    send_push(report_title, "\n".join(report_parts))

if __name__ == "__main__":
    main()
