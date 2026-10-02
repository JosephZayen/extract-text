from openai import OpenAI
import os
from configs import configs
import traceback
import time

MAX_RETRIES = configs.get("MAX_RETRIES") or 3

def parser_init():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("api key doesn't exist")
    client = OpenAI(
        api_key = api_key,
        base_url = "https://api.deepseek.com",
        timeout = 300
    )
    return client

def parse(client, messages):
    for i in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=configs.get("deepseek-weak-model") or "deepseek-v4-flash",
                messages=messages,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exc())
            time.sleep(10 * (i+1)**2)

def parse_tool(client, messages, sysprompt):
    if(isinstance(messages, str)):
        sys_message = {"role": "system", "content": sysprompt or configs.get("sysprompt") or "分析，提取文本内容，尽量简短"}
        user_message = {"role": "user", "content": messages}
        messages = [sys_message, user_message]
    elif(not isinstance(messages, list)):
        raise TypeError("messages incorrect")
    return parse(client, messages)
    



