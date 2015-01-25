#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 追加するときは cat result.csv >> wikidata.csv など

import re 
import csv

from bot import get_yomi


if __name__ == '__main__':

    with open('./wiki-html/ru.html', 'r') as f:
        text = f.read()

    regex = re.compile(ur'<a href="(/wiki/[^"]*)" title="([^"()]*)(?:\s\([^)]*\))?">[^"]*<', re.U)
    match = re.findall(regex, text)

    writer = csv.writer(open('result.csv', 'wb'), delimiter=' ')

    for m in match:
        yomi = get_yomi(m[1])

        ## 読みが取得できている
        ## ンで終わっていない
        ## `:`がurlに入っていない
        ## アルファベットで始まっていない
        if (yomi 
            and not yomi.decode('utf-8')[-1] == u'ン'
            and not re.search(u':', m[0])  
            and not re.match('[\da-zA-Zα-ωΑ-Ω]', m[1])  
        ): 

            yomi_u = yomi.decode('utf-8')
            head = yomi_u[0].encode('utf-8')
            writer.writerow([m[1], head, yomi, m[0]])

        else:
            print yomi

