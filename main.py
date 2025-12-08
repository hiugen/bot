import time
from typing import Dict ,List
from ncatbot.core import BotClient, NoticeEvent, GroupMessage
from ncatbot.core.event.message_segment import Video, MessageArray,Text,At,Json,Record
import loadimage, bilibili, Config, myollama, audio_generator
import os, json, random 
from ncatbot.utils import ncatbot_config

ncatbot_config.napcat.report_self_message=True


rootDir = os.getcwd()
messageList: List[GroupMessage] =[]

bot = BotClient()
BotName = 'ATRI'
BotQQ = '2368017024'

config = Config.Config()

@bot.on_group_message()
async def update_msg_lis(msg: GroupMessage):
    
    if len(messageList) > config[msg.group_id]["msgListLen"]: #最大存储信息数:
        messageList.pop(0)
        messageList.append(msg)
    else:
        messageList.append(msg)
 
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
    if msg.message.filter(At)[0].qq==BotQQ and "关机" in msg.message.filter(Text)[0].text:
        os.system("shutdown")
        await bot.api.post_group_msg( msg.group_id,text="亚托莉又要陷入沉睡了呢...")
        


@bot.on_group_message(filter=At)
async def setting_by_group(msg: GroupMessage):
    global config
    config.detect_gruop_id(msg)
    msg_text = msg.message.filter(Text)[0].text.replace(" ", "")
    if "设置" in msg_text and msg.message.filter(At)[0].qq==BotQQ and not msg_text.replace("设置",""):
        print(config.output(msg.group_id))
        await bot.api.post_group_msg( msg.group_id,text=config.output(msg.group_id))
    if msg.message.filter(At)[0].qq==BotQQ:
        for key, keyword in config.config_to_show.items():
            keyword : str= keyword.replace(":","").replace(" ", "")
            if keyword not in  msg.message.filter(Text)[0].text:
                continue
            change =  msg.message.filter(Text)[0].text.replace(" ", "").replace("=","").replace(keyword, "")
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

@bot.on_group_message(filter=Text)
async def single_chat(msg: GroupMessage):
    global config
    msg_text = msg.message.filter(Text)[0].text.replace(" ", "")
    if msg_text=='对话' and msg.message.filter(At)[0].qq==BotQQ :
        config[msg.group_id]["chat_target"]=msg.user_id
    elif msg_text=='结束' and msg.message.filter(At)[0].qq==BotQQ :
        config[msg.group_id]["chat_target"]=''
    if msg.message.filter(At):
        return
    if config[msg.group_id]["chat_target"] == msg.user_id:
        rpe_text = myollama.chat_with(config[msg.group_id]["chat_target"],messageList)
        msg.message= MessageArray(Text(rpe_text))
        msg.user_id = BotQQ
        messageList.append(msg)
        await bot.api.post_group_msg( msg.group_id,text=rpe_text)

@bot.on_group_message()
async def random_image(msg: GroupMessage):
    global config
    config.detect_gruop_id(msg)
    if "随机" in msg.raw_message:
        for keyword  in config["images_path"]:
            if keyword in  msg.raw_message.replace("随机","") and config[msg.group_id][keyword]:
                image = loadimage.random_image(config["images_path"][keyword])
                print(image)
                await bot.api.post_group_msg(msg.group_id, image=image)
                break

@bot.on_group_message(filter=Text)
async def download_video(msg: GroupMessage):
    config.detect_gruop_id(msg)
    if "下载" in msg.raw_message:
        bv = msg.raw_message.replace("下载","").replace(" ","")
        b_video = bilibili.BilibiliVideo(bv)
        b_video.download_video()
        vs=MessageArray(Video(b_video.video_address))
        print(vs)
        await bot.api.post_group_array_msg(msg.group_id, vs)
        b_video.delete_video()
        print(b_video.title,"send")
    elif "简介" in msg.message.filter(Text)[0].text:
        bv = msg.raw_message.replace("简介","").replace(" ","")
        b_video = bilibili.BilibiliVideo(bv)
        info =b_video.info[0:min(config[str(msg.group_id)]["info_bvideo_words"],len(b_video.info)-1)]+" "
        print(info)
        await bot.api.post_group_msg(msg.group_id,text=info)
    elif "标题" in msg.message.filter(Text)[0].text:
        bv = msg.raw_message.replace("标题","").replace(" ","")
        b_video = bilibili.BilibiliVideo(bv)
        title =b_video.title
        print(title)
        await bot.api.post_group_msg(msg.group_id,text=title)

@bot.on_group_message(filter=Text)
async def download_audio(msg: GroupMessage):
    msg_text = msg.message.filter(Text)[0].text.replace(" ", "")
    if "/电棍" in msg_text:
        msg_text=msg_text.replace("/电棍","").replace(" ", "")
        audio_path=audio_generator.generate_and_download_audio(msg_text)
        await bot.api.post_group_array_msg(msg.group_id,MessageArray(Record(file=audio_path)))


@bot.on_notice()
async def poke_notice(event: NoticeEvent):
    notice = event.sub_type
    print(event.raw_info)
    poke_msg_list=["呜哇呜哇", "又欺负我😖", "诶？",  "哔 哔 哔! 欺负机器人可是犯法的", "人家可是高性能的!"]
    if notice == 'poke' and event.is_group_event():  # 群聊戳一戳消息
        if event.target_id == event.self_id:
            await  bot.api.post_group_msg(event.group_id, text=poke_msg_list[random.randint(0,len(poke_msg_list)-1)])

# ========== 启动 BotClient==========
#print(print_config(348244932))
bot.run()
