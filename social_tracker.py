import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys
import urllib.parse

# --- 配置 ---
TOKEN = os.environ.get("PUSHPLUS_TOKEN")
PAGES_TO_SCRAPE = 3 # 设定为抓取前 3 页搜索结果
RESULTS_PER_PAGE = 10 

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
    print(f"Executing Baidu News search for: {query} (Depth: {PAGES_TO_SCRAPE} pages)")
    
    # 百度新闻搜索 URL 参数
    # rtt=4 (新闻模式), gpc=1&qdr=7 (最近 7 天，已更新!)
    base_url = "https://www.baidu.com/s?tn=news&rtt=4&gpc=1&qdr=7&wd="
    
    # ... (其余代码保持不变) ...
    
    full_url = base_url + urllib.parse.quote(query) 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36'
    }
    all_results = []
    
    # --- 核心升级：分页循环 ---
    for page in range(PAGES_TO_SCRAPE):
        offset = page * RESULTS_PER_PAGE # pn=0 (page 1), pn=10 (page 2), pn=20 (page 3)
        
        full_url_with_offset = f"{full_url}&pn={offset}"
        
        try:
            resp = requests.get(full_url_with_offset, headers=headers, timeout=15)
            resp.raise_for_status() 
            resp.encoding = 'utf-8'
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 检查是否命中反爬
            if len(resp.text) < 10000 and page > 0: 
                print(f"Baidu Search Blocked on page {page+1}. Stopping pagination.")
                break
                
            search_results = soup.find_all('div', class_='result') or soup.find_all('div', class_='c-container')
            
            if not search_results:
                break 
                
            for result in search_results:
                title_tag = result.find('a', target='_blank')
                source_tag = result.find('p', class_='c-author') or result.find('span', class_='c-info')
                
                if title_tag and title_tag.get('href'):
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href')
                    source_info = source_tag.get_text(strip=True) if source_tag else '未知来源'
                    
                    if len(title) > 10 and link not in [r['link'] for r in all_results]: # 避免重复
                        all_results.append({
                            "title": title,
                            "link": link,
                            "source": source_info
                        })

        except Exception as e:
            print(f"Baidu Search Error on page {page+1} for query '{query}': {e}")
            break # 出现错误则停止分页

    return all_results

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
    report_parts = [f"## 🔥 全网热点追踪 - 聚焦抖音/小红书 (7 天时效)", "---"]
    all_results_found = False

    for topic, keywords in TOPICS.items():
        query_keywords = ' '.join(keywords) 
        
        # 核心查询：强制要求结果包含 '小红书' 或 '抖音'
        query = f"(小红书 OR 抖音) AND (教育 {query_keywords})" 
        
        results = get_search_results(query) 
        
        if results:
            all_results_found = True
            
            report_parts.append(f"### 🚀 {topic} - 热门讨论")
            report_parts.append(f"*(共发现 {len(results)} 条，已过滤非抖音/小红书结果)*")

            for i, item in enumerate(results[:15]): # 显示前 15 条
                report_parts.append(f"- [{item['title']}]({item['link']}) ({item['source']})")
                
            report_parts.append("\n")

    if not all_results_found:
        report_parts.append("今日未发现符合所有主题的明确热点。当前筛选为最近 7 天。")
        
    report_parts.append("---")
    report_parts.append("*💡 结果来自百度新闻聚合 (最近 7 天，聚焦小红书/抖音)。*")

    send_push(report_title, "\n".join(report_parts))

if __name__ == "__main__":
    main()
