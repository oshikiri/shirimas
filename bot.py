#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import MeCab
import re
import numpy as np
import pandas as pd
import sys
import string

import mysetup as my


re_katakana = re.compile(ur'[ァ-ヴ]')
re_hiragana = re.compile(ur'[ぁ-ゔ]')

class slackBot:
    def __init__(self, name, token, channel):
        self.name = name
        self.token = token
        self.channel = channel
        self.session = requests.session()

    def getMessages(self):
        base_history = 'https://slack.com/api/channels.history?'
        payload = {
            'token' : self.token,
            'channel' : self.channel,
            'pretty' : 1
        }

        r = self.session.get(base_history, params=payload)
        return json.loads(r.text).items()[1]

    def postMessage(self, text):
        base_post = 'https://slack.com/api/chat.postMessage?'
        payload = {
            'username' : self.name,
            'token' : self.token,
            'channel' : self.channel,
            'text' : text,
            'icon_emoji' : ':lips:'
        }

        return self.session.post(base_post, data=payload)

def get_yomi(text):
    tagger = MeCab.Tagger("-Ochasen")
    result = tagger.parseToNode(text)

    yomi_list = []
    while result:
        yomi = ''

        if re.match(re_katakana, result.surface.decode('utf-8')):
            yomi = result.surface
        elif yomi != '*':
            yomi = re.findall(r'([^,]*),[^,]*$', result.feature)[0]

        if yomi != '*':
            yomi_list.append(yomi)

        result = result.next

    return ''.join(yomi_list)


## http://d.hatena.ne.jp/mohayonao/20101213/1292237816
def hiragana(text):
    """ひらがな変換"""
    return re_katakana.sub(lambda x: unichr(ord(x.group(0)) - 0x60), text)

def katakana(text):
    """カタカナ変換"""
    return re_hiragana.sub(lambda x: unichr(ord(x.group(0)) + 0x60), text)

def yomi_shiritori(text):
    u'''textの読みを返す関数(しりとり専用)'''
    yomi0 = get_yomi(text).decode('utf-8')
    yomi0 = katakana(yomi0)  ## カタカナに正規化
    yomi0 = re.sub(ur'[ー\?？。、$＄]', '', yomi0,  re.U)  ## 伸ばす棒を削除
    yomi0 = (yomi0
             .encode('utf-8')
             .translate(string.maketrans('ァィゥェォャュョ',
                                         'アイウエオヤユヨ'))
             .decode('utf-8'))  ## 小さいカタカナを大きくする

    return yomi0


if __name__ == '__main__':

    botname = my.botname
    token = my.token
    channel = my.channel

    sbot = slackBot(botname, token, channel)
    data = sbot.getMessages()
    messages = data[1]
    prev_message = messages[0]
    prev_text = prev_message[u'text'].encode('utf-8')

    if u'username' in prev_message:
        prev_user = prev_message[u'username']
    else:
        prev_user = ''

    prev_yomi = yomi_shiritori(prev_text)
    print prev_yomi.encode('utf-8')
 
    ## しりとりに使うデータを読み込む
    df = pd.DataFrame.from_csv('wikidata.csv', sep=' ', 
                               header=None, index_col=None)

    ## 前の単語につながる単語を探す
    if prev_yomi:
        cand_index = df.ix[:,1] == prev_yomi[-1].encode('utf-8')
    else:
        print '前のtextが読めません'
        sys.exit()
        
    if not cand_index.any():
        print '候補がありません'
        sys.exit()

    candidate = df.ix[cand_index, :]
    rows = np.random.choice(candidate.index.values, 1)
    c = candidate.ix[rows].values[0]

    name = c[0]
    yomi = c[2]
    url = 'http://ja.wikipedia.org' + c[3]

    print name, yomi
    print 

    ## slackにpostする:
    ## 前のメッセージのユーザーが自分でなければ投稿する
    if not prev_user or prev_user != botname:
        postmessage = name + '\n\n' + url
        print postmessage
        sbot.postMessage(postmessage)

        with open('output.txt', 'a') as f:
            f.write(postmessage + '\n\n')
