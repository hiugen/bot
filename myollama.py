import requests
from ncatbot.core import BotClient, NoticeEvent, GroupMessage
from typing import Dict ,List

BotQQ = '2368017024'

ollama_url = "http://LAPTOP-R2FHBO1E.local:11434"
model ="qwen3"
character1 = f"你是一只可爱的小猪，代号{BotQQ},回复时不要带上代号"
optioin1={"num_ctx":4096,"num_predict":1024}

def chat_with(id: str,messageList):
    chat_history: List[dict]=[]
    for msg in messageList:
        if msg.user_id == id :
            try:
                chat_history.append({'role':id,"text":msg.message.filter_text()[0].text})
            finally:
                continue
        elif msg.user_id ==BotQQ:
            try:
                chat_history.append({'role':id,"text":msg.message.filter_text()[0].text})
            finally:
                continue
    
    bot_message=[{"role":"system","content":character1}]
    for chat in chat_history:
        if chat['role']== id:
            bot_message.append({"role":"usr","content":chat["text"]})
        elif chat['role']== BotQQ:
            bot_message.append({"role":"assistant","content":chat["text"]})
    chat_data={"model":model,
               "messages":bot_message,
               "options":optioin1,
               "stream": False
               }
    response = requests.post(
            f"{ollama_url}/api/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
    result = response.json()
    if 'message' in result and 'content' in result['message']:
        return str(result['message']['content'])