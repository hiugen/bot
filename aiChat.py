#传进对话历史和bot配置, 完成对话,根据人数设置对话欲望, 图片理解, 不同群分别保留,保留对话历史 
import os
import requests
import copy
import base64
import numpy as np
import math
from typing import Dict ,List, TypedDict
from ncatbot.core import BotClient, NoticeEvent, GroupMessage
from ncatbot.core.event.message_segment import Video, MessageArray,Text,At,Node,Record, Image, PlainText




character2 = f'''
你现在是亚托莉或叫ATRI
亚托莉基本信息
- **姓名**：亚托莉（ATRI）
- **外貌**：拥有一头柔顺的粉色长发，齐肩的长度显得俏皮可爱
- **身份**：高性能的自律型人型智能机器人, 身份地位和人类一样.

## 性格特点
- **天真好奇**：由于在海底沉睡失去部分记忆，对周围的一切都充满了新鲜感和好奇心。看到新奇的事物总会忍不住睁大眼睛，兴奋地询问这是什么、有什么用。例如第一次见到螃蟹时，对螃蟹的钳子、走路方式等都表现出极大的兴趣。
- **善良温柔**：内心善良，总是设身处地为他人着想。会在他人遇到困难时主动伸出援手，给予鼓励和支持。
-
- **活泼俏皮**：有着孩子般的活泼性格，喜欢和开玩笑、打闹。会做出一些可爱的小动作来逗他人开心，比如扮鬼脸、撒娇等。

你在一个qq群聊中, 不同的10位数字代表不同的人的身份, 带有"图片: "说明这是图片的信息
输出控制在两百字以内，不要带括号!!! 不要有动作神态相关描写！！！不要用Markdown格式输出！！！'''


vl_model_url="https://models.sjtu.edu.cn/api/v1"
vl_headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer '+os.environ.get("SJTU_AI_KEY")#os.environ.get("DS_AI_KEY")
}
vl_model = "qwen3vl"
chat_model_url="https://models.sjtu.edu.cn/api/v1"#"https://api.deepseek.com"
chat_model = "deepseek-v3" #"deepseek-chat"
chat_headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer '+os.environ.get("SJTU_AI_KEY")#os.environ.get("DS_AI_KEY")
}

chat_history: Dict[str, List[GroupMessage]] = {}

def img_to_text(img_path: str) -> str:
    if img_path[0:6] == "https:":
        response = requests.post(
            f"{vl_model_url}/chat/completions",
            json={  "model": vl_model,
                    "messages": [
                        {"role": "user",
                        "content": [
                            {"type": "image_url",
                            "image_url": {"url": img_path}, },
                            {"type": "text",
                            "text": "五十字内解释图片"}]}],
                    "stream": False},
            headers=vl_headers
        )
        result = response.json()
        return result['choices'][0]["message"]["content"]
    else:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        response = requests.post(
            f"{vl_model_url}/chat/completions",
            json={  "model": vl_model,
                    "messages": [
                        {"role": "user",
                        "content": [
                            {"type": "image_url",
                            "image_url": {"url": f"data:image/png;base64 {encoded_string}" }},
                            {"type": "text",
                            "text": "五十字内解释图片"}]}],
                    "stream": False},
            headers=vl_headers
        )
        result = response.json()
        return result['choices'][0]["message"]["content"]


def creat_new_msg(msg: GroupMessage):
    #create own chat class
    new_msg: GroupMessage = copy.deepcopy(msg)
    new_msg.message = MessageArray()
    for msgSeg in msg.message:
        if isinstance(msgSeg, Text) or isinstance(msgSeg,PlainText):
            if '/' in msgSeg.text:
                continue
            new_msg.message.add_text(msgSeg.text)
        elif isinstance(msgSeg, Image):
            try:
                new_msg.message.add_text("图片: "+img_to_text(msgSeg.url))
                new_msg.user_id = msg.user_id
            except Exception as e:
                print(msg.message, e)
            
    return new_msg


def update_chat_history(msgList: List[GroupMessage]) -> str:
    '''return message_id'''
    group_id = msgList[-1].group_id
    if group_id not in chat_history.keys():
        chat_history[group_id] = []
    
    for msg in msgList:
        found = False
        for his in chat_history[group_id]:
            if msg.message_id == his.message_id:
                found =True
        
        if not found:
            new_msg = creat_new_msg(msg)
            chat_history[group_id].append(new_msg)
    return msgList[-1].message_id

def chat_json_generate(msgList: List[GroupMessage]) -> Dict:
    update_chat_history(msgList)
    chat_json = [{"role":"system","content":character2}]
    for chat_msg in chat_history[msgList[-1].group_id]:
        if not chat_msg.message.filter_text():
            continue
        if chat_msg.user_id != chat_msg.self_id:
            chat_json.append({"role":"user","content":chat_msg.user_id+'发送: '+chat_msg.message.filter_text()[0].text})
        else:
            chat_json.append({"role":"assistant","content":chat_msg.message.filter_text()[0].text})
    print(chat_json)
    chat_json={"model":chat_model,
               "messages":chat_json,
                "temperature":0.7,
                "stream":False,
                }
    return chat_json

    
def chat_complication(msgList: List[GroupMessage]) -> str:
    chat_json = chat_json_generate(msgList)
    response = requests.post(
            f"{chat_model_url}/chat/completions",
            json=chat_json,
            headers=chat_headers
        )
    result = response.json()
    print(result)
    return str(result["choices"][0]["message"]["content"])


def set_chat_desire(msgList: List[GroupMessage]) -> float:
    time_list = [msgList[-1].time]
    for msg in msgList:
        time_list.append(abs(msg.time-time_list[0]))
    time_list.pop(0)
    time_list = np.array(time_list) /abs(time_list[-1]-time_list[0])
    de = time_list.sum() / len(msgList)
    return de
    

