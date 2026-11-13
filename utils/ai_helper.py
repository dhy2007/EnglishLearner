# utils/ai_helper.py
import requests

# ⚠️ 如果你有通义千问的 API Key，请填在这里；没有就先空着，不影响其他功能
API_KEY = "sk-你的API密钥" 

def call_qwen_ai(prompt):
    if not API_KEY or API_KEY == "sk-你的API密钥":
        return "⚠️ 请先在 ai_helper.py 中填入你的真实 API Key 才能使用 AI 功能哦！"
        
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-turbo",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一个专业的英语老师，耐心解答和批改。"},
                {"role": "user", "content": prompt}
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['output']['text']
    except Exception as e:
        return f"AI 接口出错: {e}\n请检查你的 API Key 是否正确或网络是否通畅。"