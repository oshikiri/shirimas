#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'oshikiri'
__email__ = 't.oshikiri.0137@gmail.com'
__date__ = '2015-02-19'


import os
import sys

from ShiriMas import *


if __name__ == '__main__':

    db_path = './db/shiritori-history.sqlite3'
    table_name = 'history'

    sbot = ShiriMas('shiritori-master', db_path, table_name)

    ## Slackでの直近のメッセージ
    slack_newest_message = sbot.get_slack_newest_message()
    slack_newest_text = slack_newest_message['text']
    slack_newest_yomi = yomi_shiritori(slack_newest_text)
    slack_newest_user = slack_newest_message.get('username')

    ## DBで直近のメッセージ
    db_newest_message = sbot.get_db_newest_message()

    ## 更新された分のメッセージをDBに追加
    sbot.append_messages(slack_newest_message, db_newest_message)

    ## しりとりの答えを返す
    ans = sbot.get_ans(slack_newest_yomi)
#    sbot.post_shiritori(ans, slack_newest_user, slack_newest_yomi)
