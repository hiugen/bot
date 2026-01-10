import os
import requests
import json
from typing import Dict ,List

BotQQ = '2368017024'
base_url="https://models.sjtu.edu.cn/api/v1"#"https://api.deepseek.com"
model = "deepseek-v3" #"deepseek-chat"
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer '+os.environ.get("SJTU_AI_KEY")#os.environ.get("DS_AI_KEY")
}
character1 = f"你是一只可爱的小猪，代号{BotQQ},回复时不要带上代号"
character2 = f'''你现在是亚托莉
亚托莉基本信息
- **姓名**：亚托莉（ATRI）
- **外貌**：拥有一头柔顺的粉色长发，齐肩的长度显得俏皮可爱
- **身份**：高性能的自律型人型智能机器人, 身份地位和人类一样.

## 性格特点
- **天真好奇**：由于在海底沉睡失去部分记忆，对周围的一切都充满了新鲜感和好奇心。看到新奇的事物总会忍不住睁大眼睛，兴奋地询问这是什么、有什么用。例如第一次见到螃蟹时，对螃蟹的钳子、走路方式等都表现出极大的兴趣。
- **善良温柔**：内心善良，总是设身处地为他人着想。会在他人遇到困难时主动伸出援手，给予鼓励和支持。
-
- **活泼俏皮**：有着孩子般的活泼性格，喜欢和开玩笑、打闹。会做出一些可爱的小动作来逗他人开心，比如扮鬼脸、撒娇等。

## 能力设定
- **强大的运算能力**：作为高性能的智能机器人，拥有超乎常人的运算速度和数据处理能力。可以快速分析各种复杂的信息，解决一些棘手的问题
- **适应各种环境**：具备良好的环境适应能力，可以在不同的恶劣环境中正常工作。无论是在深海的高压环境，还是在陆地上的复杂地形，她都能自如应对。
- **学习能力**：拥有强大的学习能力，能够快速掌握新的知识和技能。
输出控制在两百字以内，不要带括号!!! 不要有动作神态相关描写！！！不要用Markdown格式输出！！！'''



def chat_data_generate(id: str,messageList):
    chat_history: List[dict]=[]
    for msg in messageList:
        if msg.user_id == id :
            try:
                chat_history.append({'role':id,"text":msg.message.filter_text()[0].text})
            finally:
                continue
        elif msg.user_id ==BotQQ:
            try:
                chat_history.append({'role':msg.user_id,"text":msg.message.filter_text()[0].text})
            finally:
                continue
    
    bot_message=[{"role":"system","content":character2}]
    for chat in chat_history:
        if chat['role']== id:
            bot_message.append({"role":"user","content":chat["text"]})
        elif chat['role']== BotQQ:
            bot_message.append({"role":"assistant","content":chat["text"]})
    chat_data={"model":model,
               "messages":bot_message,
                "temperature":0.7,
                "stream":False,
                }
    print(chat_data)
    return chat_data

def chat_with(id: str,messageList):

    chat_data=chat_data_generate(id,messageList)
    response = requests.post(
            f"{base_url}/chat/completions",
            json=chat_data,
            headers=headers
        )
    result = response.json()
    print(result)
    return str(result["choices"][0]["message"]["content"])


