import requests
import datetime
import os
import sys

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
    (模拟) 外部搜索引擎API调用
    在实际部署中，此函数需要调用 Google/Baidu API 或爬取其结果页。
    此处为简化和演示结构，返回模拟数据。
    """
    print(f"Executing search for: {query}")
    
    # 模拟真实搜索返回的最新热点
    return [
        {"title": "小红书爆款：高三家长必看！高效冲刺学习法", "link": "https://example.xiaohongshu.com/hot_topic/abc", "platform": "小红书"},
        {"title": "某机构发布：2025年高考志愿填报新趋势分析", "link": "https://example.article.com/article/123", "platform": "权威文章"},
        {"title": "微博热搜：如何正确进行青春期家庭教育", "link": "https://example.weibo.com/topic/family", "platform": "微博"},
        {"title": "抖音视频：孩子厌学怎么办？心理专家支招", "link": "https://example.douyin.com/video/456", "platform": "抖音"},
    ]

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
    report_parts = [f"## 🔥 {report_title} - 最近三天热点追踪", "---"]
    all_results_found = False

    for topic, keywords in TOPICS.items():
        # 构造搜索查询：优先社交媒体 AND (所有关键词) AND 确保时效性
        query = f"({' OR '.join(SOCIAL_PLATFORMS)}) AND ({' OR '.join(keywords)}) \"最近三天\""
        
        results = get_search_results(query) # 模拟搜索执行
        
        if results:
            all_results_found = True
            report_parts.append(f"### 🚀 {topic} - 热门讨论")
            
            for i, item in enumerate(results[:5]): # 每主题展示前5条
                report_parts.append(f"*{item['platform']}*：[{item['title']}]({item['link']})")
                
            report_parts.append("\n")

    if not all_results_found:
        report_parts.append("今日未发现符合所有主题和平台筛选的明确热点。请尝试手动搜索。")
        
    report_parts.append("---")
    report_parts.append("*💡 结果为搜索引擎聚合与模拟，不代表实时抓取。*")

    send_push(report_title, "\n".join(report_parts))

if __name__ == "__main__":
    main()
