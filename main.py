import time
from ncatbot.core import BotClient, NoticeEvent, GroupMessage
from ncatbot.core.event.message_segment import Video, MessageArray,Text,At,Json
import loadimage, bilibili
import os, json, random


rootDir = os.getcwd()
config_json_path = os.path.join(rootDir, "config.json")
config = {}

messageList=[]

bot = BotClient()
BotName = 'ATRI'
BotQQ = '2368017024'

config_to_show={    # 方便打印 
    "pjsk":"是否开启pjsk图:  ",
    "info_bvideo_words": "简介字数:  ",
    "touhou":"是否开启随机东方图:  ",
    "ATRI": "是否开启ATRI图:  "

}


def init():
    global config
    if not os.path.exists(config_json_path):
        with open(config_json_path, "w") as f:
            f.write('''{ 
                "inited": false,
                "images_path": {"pjsk":"image1","touhou":"image2","ATRI":"image3"}, 
                "groups_id": []
                }''')
    with open(config_json_path, "r") as f:
        config = json.load(f)
    with open(config_json_path, "w") as f:
        f.write(json.dumps(config, indent=4))
    print("config:", config)

def print_config(group_id: int):
    global config
    text ="这是一些设置：\n"
    for key in config[str(group_id)]:
        
        #print(key, text)
        #目前只有bool,int处理
        if key not in config_to_show:
            continue
        text=text+config_to_show[key]
        if type(config[str(group_id)][key])==bool:

                if config[str(group_id)][key]:
                    text+="是"
                else:
                    text+="否"
        elif type(config[str(group_id)][key])==int:
                text+=str(config[str(group_id)][key])
        #结束换行
        text+="\n"
    text =text[:-1]
    return text

#每个config的fun都要用
#用于判断群是否第一次出现
def detect_gruop_id(msg: GroupMessage):
    global config, config_json_path
    if msg.group_id not in config["groups_id"]:
        config[str(msg.group_id)]={     
            #每个群的配置
            #和config_to_show关键字一致
            "pjsk":True,
            "downloadbv":True,
            "info_bvideo_words": 70,
            "touhou":True,
            "ATRI":True
        }
        config["groups_id"].append(msg.group_id)
        #更新配置
        with open(config_json_path, "w") as f:
            f.write(json.dumps(config, indent=4))

@bot.on_group_message()
async def update_msg_lis(msg: GroupMessage):
    if len(messageList) > 70: #最大存储信息数:
        pass


@bot.on_group_message()
async def debug_by_group_msg(msg: GroupMessage):
        print(msg.message)
        print(msg.message_id)
        ms = msg.message
        #await bot.api.post_group_array_msg("348244932", ms)

@bot.on_group_message(filter=At)
async def help_info(msg: GroupMessage):
    self_introduction = "你好啊, 我可是高性能的机器人哦!"
    if msg.message.filter(At)[0].qq==BotQQ and "你是谁" in msg.message.filter(Text)[0].text:
        await bot.api.post_group_msg( msg.group_id,text=self_introduction)
    if msg.message.filter(At)[0].qq==BotQQ and "关机" in msg.message.filter(Text)[0].text:
        os.system("shutdown")
        await bot.api.post_group_msg( msg.group_id,text="亚托莉又要陷入沉睡了呢...")
        


@bot.on_group_message(filter=Text)
async def setting_by_group(msg: GroupMessage):
    global config
    detect_gruop_id(msg)
    msg_text = msg.message.filter(Text)[0].text.replace(" ", "")
    if "设置" in msg_text and msg.message.filter(At)[0].qq==BotQQ and not msg_text.replace("设置",""):
        print(print_config(msg.group_id))
        await bot.api.post_group_msg( msg.group_id,text=print_config(msg.group_id))

@bot.on_group_message()
async def random_image(msg: GroupMessage):
    global config
    detect_gruop_id(msg)
    if "随机" in msg.raw_message:
        for keyword  in config["images_path"]:
            if keyword in  msg.raw_message.replace("随机","") and config[msg.group_id][keyword]:
                image = loadimage.random_image(config["images_path"][keyword])
                print(image)
                await bot.api.post_group_msg(msg.group_id, image=image)
                break

@bot.on_group_message(filter=Text)
async def download_video(msg: GroupMessage):
    detect_gruop_id(msg)
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


@bot.on_notice()
async def poke_notice(event: NoticeEvent):
    notice = event.sub_type
    print(event.raw_info)
    poke_msg_list=["呜哇呜哇", "又欺负我😖", "诶？",  "哔 哔 哔! 欺负机器人可是犯法的", "人家可是高性能的!"]
    if notice == 'poke' and event.is_group_event():  # 群聊戳一戳消息
        if event.target_id == event.self_id:
            # Bot 被戳时戳回去
            await  bot.api.post_group_msg(event.group_id, text=poke_msg_list[random.randint(0,len(poke_msg_list)-1)])

# ========== 启动 BotClient==========
init()
#print(print_config(348244932))
bot.run()
