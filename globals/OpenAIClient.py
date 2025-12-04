from openai import OpenAI

llm_config = {
    "model": "qwen3:8b",
    "base_url": "http://192.168.0.129:11434/v1",
    "api_key": "yuanyuan"
}

def chat(messages:[]):
    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    return client.chat.completions.create(messages=messages, model=llm_config["model"])