import time
from typing import Dict ,List
from ncatbot.core import BotClient, NoticeEvent, GroupMessage
from ncatbot.core.event.message_segment import Video, MessageArray,Text,At,Node,Record, Image
import loadimage, bilibili,  myollama, audio_generator, aiChat, pjsk, myds
from Config import Config
import os, json, random 
from ncatbot.utils import ncatbot_config

rootDir = os.getcwd()
messageList={}

bot = BotClient()
BotName = 'ATRI'
BotQQ = '2368017024'

config = Config(BotQQ)

@bot.on_group_message()
async def update_msg_lis(msg: GroupMessage):
    
    messageList[msg.group_id] = await bot.api.get_group_msg_history(msg.group_id,count=config[msg.group_id]["msgListLen"])
 
@bot.on_group_message()
async def debug_by_group_msg(msg: GroupMessage):
        print(msg.message)
        print(msg.message_id)
        if "list" in msg.raw_message:
            for i in messageList:
                await bot.api.post_group_array_msg("348244932", i.message)
        #ms = msg.message
        #await bot.api.post_group_array_msg("348244932", ms)

@bot.on_group_message(filter=At)
async def help_info(msg: GroupMessage):
    self_introduction = "你好啊, 我可是高性能的机器人哦!"
    if msg.message.filter(At)[0].qq==BotQQ and "你是谁" in msg.message.filter(Text)[0].text:
        await bot.api.post_group_msg( msg.group_id,text=self_introduction)


@bot.on_group_message(filter=Text)
async def command_of_group(msg: GroupMessage):
    config.update_group_config(msg)
    msg_text = msg.message.filter(Text)[0].text
    if msg_text[0] != "/":
        return
    
    if msg_text[1:3] == "设置" :
        setting_text: str = msg_text.replace("/设置","").replace(" ", "")
        if  not setting_text:
            print(config.output(msg.group_id))
            await bot.api.post_group_msg( msg.group_id,text=config.output(msg.group_id))
        else:
            for key, keyword in config.config_to_show.items():
                keyword : str= keyword.replace(":","").replace(" ", "")
                if keyword not in  msg.message.filter(Text)[0].text:
                    continue
                change =  setting_text.replace("=","").replace(keyword, "")
                if type(config[msg.group_id][key])==int:
                    config[msg.group_id][key]= int(change)
                elif type(config[msg.group_id][key])==bool:
                    if change=='是' :
                        config[msg.group_id][key]=True
                    elif change=='否':
                        config[msg.group_id][key]=False
                elif type(config[msg.group_id][key])==str:
                    config[msg.group_id][key]= change
                await bot.api.post_group_msg( msg.group_id,text=config.output(msg.group_id))
    elif msg_text[1] == 'h':
        await bot.api.post_group_array_msg(msg.group_id, MessageArray(Text(
            '''指令(要加/的): \n 设置:  什么都不加显示设置, 加"设置项"="参数"可改设置\n简介: 加BV号\n 标题: 加BV号 \n chart pjskid 和 难度(e, n, h, m, a)下载谱面预览\n 电棍 \n 不用加/的: \n 随机 \n''')))
    elif msg_text[1:3] == "简介" :
        bv = msg_text.replace("/简介","").replace(" ","")
        b_video = bilibili.BilibiliVideo(bv)
        info =b_video.info[0:min(config[str(msg.group_id)]["info_bvideo_words"],len(b_video.info)-1)]+" "
        print(info)
        await bot.api.post_group_msg(msg.group_id,text=info)
    elif msg_text[1:3] ==  "标题":
        bv = msg_text.replace("/标题","").replace(" ","")
        b_video = bilibili.BilibiliVideo(bv)
        title =b_video.title
        print(title)
        await bot.api.post_group_msg(msg.group_id,text=title)
    elif msg_text[1:3] ==  "电棍":
        audio_text=msg_text.replace("/电棍","").replace(" ", "")
        audio_path=audio_generator.generate_and_download_audio(audio_text)
        await bot.api.post_group_array_msg(msg.group_id,MessageArray(Record(file=audio_path)))
    elif msg_text[1:6] == "chart":
        song_id =msg_text.replace("/chart", "").split()[0]
        d = {'e':'easy', 'n':'normal', 'h':'hard', 'e':"expert", 'm':"master", 'a':"append"}
        difficulty = d[msg_text.replace("/chart", "").split()[1]]
        await bot.api.post_group_array_msg(msg.group_id,pjsk.get_id_chart(song_id, difficulty))

@bot.on_group_message()
async def random_image(msg: GroupMessage):
    global config
    config.update_group_config(msg)
    if "随机" in msg.raw_message:
        for keyword  in config["images_path"]:
            if keyword in  msg.raw_message.replace("随机","") and config[msg.group_id][keyword]:
                image = loadimage.random_image(config["images_path"][keyword])
                print(image)
                await bot.api.post_group_msg(msg.group_id, image=image)
                break


@bot.on_notice()
async def poke_notice(event: NoticeEvent):
    notice = event.sub_type
    print(event.raw_info)
    poke_msg_list=[
        "呜哇呜哇","又欺负我😖", "诶？",  "哔 哔 哔! 欺负机器人可是犯法的", "人家可是高性能的!"]
    if notice == 'poke' and event.is_group_event():  # 群聊戳一戳消息
        if event.target_id == event.self_id:
            await  bot.api.post_group_msg(event.group_id, text=poke_msg_list[random.randint(0,len(poke_msg_list)-1)])

@bot.on_group_message(filter=Text)
async def group_ai_chat(msg: GroupMessage):
    if not config[msg.group_id]["chat"]:
        return
    messageList[msg.group_id] = await bot.api.get_group_msg_history(msg.group_id,count=config[msg.group_id]["msgListLen"])
    reply_desire = 0   #aiChat.set_chat_desire(messageList[msg.group_id])
    if msg.message.filter_at() and msg.message.filter_at()[0].qq == msg.self_id:
        reply_desire = 1
    print(reply_desire)
    if random.random()>reply_desire or '/' in msg.message.filter(Text)[0].text:
        return
    
    await bot.api.post_group_array_msg(msg.group_id,MessageArray(Text(aiChat.chat_complication(messageList[msg.group_id]))))


#print(print_config(348244932))
bot.run()
