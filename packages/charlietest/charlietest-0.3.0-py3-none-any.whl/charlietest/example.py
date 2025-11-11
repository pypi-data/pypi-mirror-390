import requests


def chat_completion(api_key: str, content: str) -> str:
    """调用 2brain Chat Completion 接口并返回回复文本。"""
    url = "https://ai.2brain.cn/api/bot/chat/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "stream": False,
    }
    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("choices")[0]["message"]["content"]
    else:
        try:
            error = response.json().get("error")
            error_type = error.get("type") if isinstance(error, dict) else None
            error_msg = error.get("message") if isinstance(error, dict) else None
        except Exception:
            error_type = None
            error_msg = response.text
        raise RuntimeError(
            f"请求异常, 错误码={response.status_code}, 错误类型={error_type}, 错误信息={error_msg}"
        )


def add(left: int, right: int) -> int:
    """返回两个整数相加的结果。"""
    return left + right


def multiply(left: int, right: int) -> int:
    """返回两个整数相乘的结果。"""
    return left * right

