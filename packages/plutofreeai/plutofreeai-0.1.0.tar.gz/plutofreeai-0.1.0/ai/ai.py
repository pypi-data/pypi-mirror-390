# ai.py Made my NoahOlomu
import time
import uuid
import requests
import re
import json
from uuid import uuid4
from webscout.AIutel import Conversation, AwesomePrompts, Optimizers
from webscout.AIbase import Provider

# Custom exception in case you want it
class FailedToGenerateResponseError(Exception):
    pass

class YouChat(Provider):
    def __init__(self, max_tokens=600, timeout=30, intro=None, filepath=None, update_file=True, proxies=None):
        self.session = requests.Session()
        self.max_tokens_to_sample = max_tokens
        self.chat_endpoint = "https://you.com/api/streamingSearch"
        self.timeout = timeout
        self.last_response = {}
        self.payload = {
            "q": "",
            "page": 1,
            "count": 10,
            "safeSearch": "Off",
            "onShoppingPage": False,
            "mkt": "",
            "responseFilter": "WebPages,Translations,TimeZone,Computation,RelatedSearches",
            "domain": "youchat",
            "queryTraceId": str(uuid.uuid4()),
            "conversationTurnId": str(uuid.uuid4()),
            "pastChatLength": 0,
            "selectedChatMode": "default",
            "chat": "[]",
        }
        self.headers = {
            "cache-control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": f'https://you.com/search?q={self.payload["q"]}&fromSearchBar=true&tbm=youchat&chatMode=default'
        }
        self.session.headers.update(self.headers)
        self.conversation = Conversation(max_tokens=self.max_tokens_to_sample, filepath=filepath, update_file=update_file)
        Conversation.intro = intro or Conversation.intro
        if proxies:
            self.session.proxies = proxies

    def ask(self, prompt: str, stream=False):
        self.payload["q"] = prompt
        response_text = ""
        try:
            response = self.session.get(self.chat_endpoint, params=self.payload, stream=True, timeout=self.timeout)
            if not response.ok:
                raise FailedToGenerateResponseError(f"Request failed: {response.status_code}")
            for line in response.iter_lines(decode_unicode=True, chunk_size=64):
                if line:
                    clean_line = re.sub("data:", "", line)
                    try:
                        data = json.loads(clean_line)
                        if "youChatToken" in data:
                            response_text += data["youChatToken"]
                    except:
                        continue
        except Exception as e:
            response_text = f"Error: {str(e)}"

        self.last_response = {"text": response_text}
        self.conversation.update_chat_history(prompt, self.get_message(self.last_response))
        return self.last_response

    def chat(self, prompt: str, stream=False):
        return self.get_message(self.ask(prompt, stream=stream))

    def get_message(self, response: dict) -> str:
        return response.get("text", "")


# Create a default instance for easy use
_ai_instance = YouChat()

def chat(prompt: str, stream=False):
    return _ai_instance.chat(prompt, stream=stream)

def ask(prompt: str, stream=False):
    return _ai_instance.chat(prompt, stream=stream)
