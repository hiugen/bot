import json
import os
import langid
from typing import Dict, Literal
import numpy as np
from ncatbot.core.event.message_segment import MessageArray, Text,Image
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine
import jieba
import requests

root =os.getcwd()
pjsk_dir = os.path.join(root,"pjsk")

local_music_difficulty_json = open(os.path.join(pjsk_dir, "musicDifficulty.json"))
local_music_json = open(os.path.join(pjsk_dir, "music.json"))

music_difficulty = json.load(local_music_difficulty_json)
music = json.load(local_music_json)

music_zh_txt = open(os.path.join(pjsk_dir, "title_zh.txt"), encoding='utf-8')
music_en_txt = open(os.path.join(pjsk_dir, "title_en.txt"), encoding='utf-8')

music_zh = music_zh_txt.readlines()
music_en = music_en_txt.readlines()

music_id = {}
music_title = {}
music_title_zh = {}
music_title_en = {}

zh_model = ''
def init():
    global zh_model
    zh_model = KeyedVectors.load_word2vec_format(os.path.join(pjsk_dir, "word_vectors_zh_50.vec"))




def make_music_id():
    title_txt = open(os.path.join(pjsk_dir, "title.txt"),'w')
    count = 0
    for song in music:
        temp = {song["id"]:{"title":song["title"], "difficulty": {}}}
        for diff in music_difficulty:
            if diff["musicId"] == song["id"]:
                temp[song["id"]]["difficulty"][diff["musicDifficulty"]]=diff["playLevel"]
        music_id[song["id"]] = temp[song["id"]]

        music_title[song["title"]] = song["id"]
        title_txt.write(song["title"]+'\n')
        music_title_en[music_en[count][:-1]] = song["id"]
        music_title_zh[music_zh[count][:-1]] = song["id"]



        count+=1

    with open(os.path.join(pjsk_dir,"musicId.json"),'w') as f:
        json.dump(music_id, f, indent=4)
    with open(os.path.join(pjsk_dir,"musicTitle.json"),'w') as f:
        json.dump(music_title, f, indent=4)
    with open(os.path.join(pjsk_dir,"musicZhTitle.json"),'w') as f:
        json.dump(music_title_zh, f, indent=4)
    with open(os.path.join(pjsk_dir,"musicEnTitle.json"),'w') as f:
        json.dump(music_title_en, f, indent=4)

    title_txt.close()


def get_sentence_vector(sentence, model,song_title):
    words = list(sentence)
    if song_title in sentence:
        words+list(song_title) + list(song_title)
    vectors = []
    vector_size = model.vector_size if hasattr(model, 'vector_size') else model.wv.vector_size
    for word in words:
        try:
            if hasattr(model, 'wv'):
                if word in model.wv:
                    vectors.append(model.wv[word])
                else:
                    vectors.append(model.wv.get_vector(word, norm=True))
            elif hasattr(model, 'get_vector'):
                vectors.append(model.get_vector(word, norm=True))
            elif word in model:
                vectors.append(model[word])
        except Exception:
            # 如果无法获取词向量，使用随机向量作为 fallback
            vectors.append(np.random.rand(vector_size))
    
    if not vectors:
        return np.zeros(vector_size)
    return np.mean(vectors, axis=0)


def find_song(title: str):
    lang = langid.classify(title)[0]
    if lang == 'zh':
        input_vec = get_sentence_vector(title, zh_model,title)
        similarities = []
        with open(os.path.join(pjsk_dir,"musicZhTitle.json"),'r') as f:
            f_js: Dict = json.load(f)
            for song in f_js.keys():
                song_vec = get_sentence_vector(song, zh_model,title)
                similarity = 1 - cosine(input_vec, song_vec)
                similarities.append((f_js[song], similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
    else:
        input_vec = get_sentence_vector(title, zh_model,title)
        similarities = []
        with open(os.path.join(pjsk_dir,"musicZhTitle.json"),'r') as f:
            f_js: Dict = json.load(f)
            for song in f_js.keys():
                song_vec = get_sentence_vector(song, zh_model,title)
                similarity = 1 - cosine(input_vec, song_vec)
                similarities.append((f_js[song], similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)

    top_5 = "你要找的是不是:\n"

    for i in range(5):
        top_5 += str(i+1)+'. '+ music_id[similarities[i][0]]["title"]+"  id:"+ str(similarities[i][0])+" \n"
        

    return top_5


def get_id_chart(song_id, diffi:Literal["easy", "hard", "normal", "expert", "master", "append"]):
    chart_url = "https://storage.sekai.best/sekai-music-charts/jp/"
    song_id = int(song_id)
    song_id_str = str(song_id)
    for i in range(4-len(song_id_str)):
        song_id_str = '0'+song_id_str
    picture_path = os.path.join(pjsk_dir, song_id_str+diffi[0]+'.png')

    if os.path.exists(picture_path):
        return MessageArray(Text(music_id[song_id]["title"]+"  "+diffi+' '+str(music_id[song_id]["difficulty"][diffi])),Image(picture_path))
    img_url =  chart_url+song_id_str+'/'+diffi+'.png'
    headers = {
    "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'''
    }
    with open(picture_path, 'wb') as f:
        f.write(requests.get(img_url,headers=headers).content)
    print("picture download")
    return MessageArray(Text(music_id[song_id]["title"]+"  "+diffi+' '+str(music_id[song_id]["difficulty"][diffi])))





make_music_id()
#init()

local_music_difficulty_json.close()
local_music_json.close()
if __name__=="__main__":
    init()
    while(1):
        print(find_song(input("input:")))