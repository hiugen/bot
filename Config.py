import json, os
from ncatbot.core import GroupMessage


rootDir = os.getcwd()
class Config:
    def __init__(self):
        self.config_json_path = os.path.join(rootDir, "config.json")
        self.config={
            "inited": False,
            "images_path": {"pjsk":"image1","touhou":"image2","ATRI":"image3","优食": "foodimage"}, 
            "groups_id": []
            }
        self.config_to_show={    # 方便打印 
            "pjsk":"是否开启pjsk图:     ",
            "info_bvideo_words": "简介字数:  ",
            "touhou":"是否开启随机东方图:  ",
            "ATRI": "是否开启ATRI图:  ",
            "msgListLen":"AI最大保存对话数: ",
            "chat_target":"对话对象: "
        }
        if not os.path.exists(self.config_json_path):
            with open(self.config_json_path, "w") as f:
                f.write(json.dumps(self.config, indent=4))
        with open(self.config_json_path, "r") as f:
            self.config = json.load(f)
        print("config:", self.config)
    
    def detect_gruop_id(self, msg: GroupMessage):
        if msg.group_id not in self.config["groups_id"]:
            #每个群的配置
            #和config_to_show关键字一致
            self.config[str(msg.group_id)]={     
                "pjsk":True,
                "downloadbv":True,
                "info_bvideo_words": 70,
                "touhou":True,
                "ATRI":True,
                "优食":True,
                "msgListLen":70,
                "chat_target":""
            }
            self.config["groups_id"].append(msg.group_id)
            #更新配置
            with open(self.config_json_path, "w") as f:
                f.write(json.dumps(self.config, indent=4))

    def output(self, group_id: int):
        text ="这是一些设置：\n"
        for key in self.config[str(group_id)]:
            
            #print(key, text)
            #目前只有bool,int处理
            if key not in self.config_to_show:
                continue
            text=text+self.config_to_show[key]
            if type(self.config[str(group_id)][key])==bool:

                    if self.config[str(group_id)][key]:
                        text+="是"
                    else:
                        text+="否"
            elif type(self.config[str(group_id)][key])==int:
                    text+=str(self.config[str(group_id)][key])
            elif type(self.config[str(group_id)][key])==str:
                 text+=self.config[str(group_id)][key]
            #结束换行
            text+="\n"
        text =text[:-1]
        return text
    
    
    #每个config的fun都要用
    #用于判断群是否第一次出现
    

    def __getitem__(self,key):
         return self.config[key]
    def __setitem__(self, key, val):
        self.config[key]=val
