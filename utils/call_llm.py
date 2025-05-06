from openai import OpenAI
import os
import requests
import json
import sys

# Learn more about calling the LLM: https://the-pocket.github.io/PocketFlow/utility_function/llm.html
def call_deepseek_chat_api_stream(api_key, messages):
    """
    调用 DeepSeek Chat API（支持控制台流式输出）
    参数：
        api_key: 你的 API 密钥
        messages: 对话消息列表
    返回：
        模型完整回复字符串
    """
    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 1.5,
        "max_tokens": 8000,
        "stream": True  # 启用流式响应
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                if line.startswith("data: "):
                    payload = line[len("data: "):]
                    if payload.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(payload)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
                    except json.JSONDecodeError:
                        print("\n[!] 无法解析的一段响应:", line)

        print()  # 输出完成后换行
        return full_response

    except requests.exceptions.RequestException as e:
        print(f"[请求异常] {str(e)}")
        return ""
    except Exception as e:
        print(f"[处理响应错误] {str(e)}")
        return ""

def call_llm(prompt):
    """
    简化的LLM调用接口
    参数：
        prompt: 提示词
    返回：
        模型回复
    """
    # 从环境变量获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("[错误] 未设置DEEPSEEK_API_KEY环境变量")
        return ""
    messages = [{"role": "user", "content": prompt}]
    return call_deepseek_chat_api_stream(api_key, messages)

if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    print(call_llm(prompt))
