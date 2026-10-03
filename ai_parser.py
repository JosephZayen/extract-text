from openai import OpenAI
import os
from configs import configs
import traceback
import time

MAX_RETRIES = configs.get("MAX_RETRIES")

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
                model=configs.get("deepseek-weak-model"),
                messages=messages,
                extra_body={"thinking": {"type": "enabled"}}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(type(e).__name__, repr(e), traceback.format_exc())
            time.sleep(10 * (i+1)**2)
    print("returns nothing")
    return ""


def parse_tool(client, user_content, sysprompt):
    sys_message = {"role": "system", "content": sysprompt}
    user_message = {"role": "user", "content": user_content}
    messages = [sys_message, user_message]
    return parse(client, messages)
    



