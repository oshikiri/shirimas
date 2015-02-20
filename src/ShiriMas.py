#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'oshikiri'
__email__ = 't.oshikiri.0137@gmail.com'
__date__ = '2015-02-19'


import os
import sys
import re
import string
import MeCab
import pandas as pd
import sqlite3

from SlackBot.SlackBot import SlackBot


columns = ['type', 'subtype', 'purpose', 'channel',
           'ts', 'user', 'username', 'text']

small_kana = 'ァィゥェォャュョッ'
large_kana = 'アイウエオヤユヨツ'
re_hiragana = re.compile('[ぁ-ゔ]', re.U)


def katakana(text):
    '''ひらがなをカタカナに置換

    以下のページを参考にした:
    http://d.hatena.ne.jp/mohayonao/20101213/1292237816
    '''
    return re_hiragana.sub(lambda x: chr(ord(x.group(0)) + 0x60), text)


def get_yomi(text):
    '''MeCabが出力したtextの読みを返す
    '''
    tagger = MeCab.Tagger("-Ochasen")
    result = tagger.parse(text)

    yomi_list = []
    for r in result.split('\n')[0:-2]:
        r_list = r.split('\t')
        yomi_list.append(r_list[1])

    return ''.join(yomi_list)


def yomi_shiritori(text):
    '''textのしりとり用の読みを返す関数

    textの読みに以下の処理を適用したものを返す:

    1 カタカナに正規化
    2 伸ばす棒などを削除
    3 小さいカタカナを大きくする

    Args
    ===========
    text : string
        読みを取得したい単語
    '''

    # カッコとその中身と改行を無視
    text = re.sub(r'(<[^>]+>|\([^)]+\)|\n)', '', text)

    yomi0 = get_yomi(text)
    yomi0 = katakana(yomi0)
    yomi0 = re.sub(r'[^ァ-ヴ]*', '', yomi0)
    yomi0 = yomi0.translate(str.maketrans(small_kana, large_kana))

    return yomi0



class ShiriMas(SlackBot):
    '''shiritori bot for Slack

    shiritori-master
    '''
    def __init__(self, botname, db_path, table_name, channel_name='shiritori'):
        super().__init__(botname)
        self.botname = botname
        self.table_name = table_name
        self.set_channel(channel_name)
        
        ## もともとSQLiteのファイルが存在しない場合，
        ## 初期化する必要があると判定
        to_initialize = not os.path.exists(db_path)
        
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()
        
        if to_initialize:
            print('DBを初期化')
            self.initialize_db()

    def set_channel(self, channel_name):
        '''ShiriMasが投稿するchannelを指定する．

        複数のchannelに投稿することは想定しにくいので，
        こうしておく．

        Args
        ===========
        channel_name: string, optional (default='shiritori')
            投稿するchannelの名前 (idではない) を指定する．
            とりあえず不正な値が設定されることは想定していない．
        '''
        self.channel = super().get_channel_dict()[channel_name]


    def get_messages(self, count=1):
        '''Slackから最新のメッセージ(count)件を取得する

        Args
        ===========
        count : int, optional (default=1)
            取得する件数
        '''
        return super().get_messages(channel=self.channel, count=count)


    def post_message(self, message):
        '''メッセージをpostする

        Args
        ===========
        message: string
            postするメッセージ
        '''
        super().post_message(message, self.channel)


    def get_slack_newest_message(self):
        '''channelの中で最新のメッセージを取ってくる
        '''
        return self.get_messages(count=1)[0]


    def get_db_newest_message(self):
        '''DBの中で最新のメッセージを取ってくる
        '''
        query = ('SELECT * FROM {0} ' 
                 'WHERE ts = (SELECT max(ts) FROM {0}) ' 
                 'LIMIT 1').format(self.table_name)
        return pd.read_sql(query, self.connect).ix[0,:].to_dict()


    def initialize_db(self):
        '''DBの初期化

        最新1000件のメッセージを取得してDBに追加する
        '''
        
        messages = self.get_messages(count=1000)
        df = pd.DataFrame(messages, columns=columns)
        df['username'] = df.user.map(super().get_users_list())
        df['yomi'] = df.text.map(yomi_shiritori)

        df.to_sql(self.table_name, self.connect, index=False)

        
    def append_messages(self, slack_newest_message, db_newest_message):
        '''DBに格納していないメッセージがある場合,それをDBに追加

        Args
        ===========
        slack_newest_message : 
            Slackの中で最新のメッセージのデータのdict
        db_newest_message : 
            DBの中で最新のメッセージのデータのdict
        '''

        slack_newest_ts = float(slack_newest_message['ts'])
        db_newest_ts = float(db_newest_message['ts'])

        if slack_newest_ts > db_newest_ts:

            messages = self.get_messages(count=100)
            df = pd.DataFrame(messages, columns=columns)
            df['username'] = df.user.map(super().get_users_list())
            df['yomi'] = df.text.map(yomi_shiritori)

            additional_df = df.ix[df.ts.map(float) > db_newest_ts, :]
            additional_df.to_sql(self.table_name, self.connect, 
                                 index=False, if_exists='append')
        

    def get_candidate(self, prev_yomi):
        '''prev_yomiにつながる単語の候補を返す

        Args
        ===========
        prev_yomi : string
            前の単語の読み
        '''

        df = pd.DataFrame.from_csv('wikidata.csv', sep=' ',
                                   header=None, index_col=None)

        if prev_yomi:
            cand_index = df.ix[:, 1] == prev_yomi[-1]
        else:
            print('前のtextが読めません')
            sys.exit()

        if not cand_index.any():
            print('候補がありません')
            sys.exit()

        return df.ix[cand_index, :]


    def get_proper_candidate(self, candidates):
        '''単語の候補の中から適切な単語を探して1つ返す

        Args
        ===========
        candidates : pd.DataFrame
            単語の候補
        '''

        for i_cand in candidates.index:
            cand_tmp = candidates.ix[i_cand, ]
            cand_yomi = yomi_shiritori(str(cand_tmp[2]))
            
            ## cand_yomiを読みに含んでいる単語が無かったか調べる
            query = ('SELECT count(*) '
                     'FROM ' + self.table_name + ' '
                     'WHERE yomi = \'' + cand_yomi + '\';')
            self.cursor.execute(query)
            res_shape = self.cursor.fetchall()[0]
       
            if res_shape == (0,):
                ## 読みに含んでいる単語が1つも無かった場合
                cand = cand_tmp
                break
        else:
            ## 使える候補単語が無かった場合
            sys.exit()

        return cand


    def get_ans(self, prev_yomi):
        '''prev_yomiにつながる既出でない単語を返す

        Args
        ===========
        prev_yomi : string
            前の単語の読み
        '''
        candidates = self.get_candidate(prev_yomi)
        return self.get_proper_candidate(candidates)


    def post_shiritori(self, cand, prev_user, prev_yomi):
        '''slackにしりとりの回答をpostする

        Args
        ===========
        cand : pd.Series
            前の単語の読み
        prev_user : string
            直前に発言したユーザー名
        prev_yomi : string
            直前の単語の読み
        '''

        name = cand[0]
        yomi = cand[2]
        url = 'http://ja.wikipedia.org' + cand[3]

        ## 連投しないようにする
        if not prev_user or prev_user != self.botname:
            postmessage = name + '\n\n' + url
            self.post_message(postmessage)
            
            print(prev_yomi)
            print(name, yomi)
