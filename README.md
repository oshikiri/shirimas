shirimas
===============

**Slack用しりとりbot shiritori-master**


## これはなに？
チャットツール[Slack](https://slack.com/)上でしりとりの相手をしてくれるbotです．

*「しりとりをする相手がいない…」*

そんな場合でも，Slack上でしりとりが楽しめます．

![人間とbotの貴重な対話シーン](doc/example.png)


## 実際に使いたい場合

実際にshirimasを動作させる環境を構築したい場合は，[kafku/docker-shirimas](https://github.com/kafku/docker-shirimas)を使うと簡単にできます．

また実際に動かす場合は，環境変数 `SLACKTOKEN` に Slack API の token を指定する必要があります．(cf.[Slack Web API | Slack](https://api.slack.com/web))


## shirimasの特徴

- **MeCab**を利用して読みを取得
- デフォルトではWikipediaの数学関係やその他もろもろの記事から取得した**マニアックな**単語候補を使う
- しりとりが行われているチャンネルで既出の単語は(できるかぎり)発言しない
- 単語と一緒にWikipediaの記事を紹介してくれるので**勉強になる**

## 作成したもの
`*.py`はPython3.4.2で作成した

### autoexec.py
数秒ごとに main_shiritori.py を実行する

### main_shiritori.py
shirimasのmain関数

### ShiriMas.py
shirimas用ライブラリ

### parse_wiki.py
wikipediaのhtmlファイルから単語候補を抽出する

(これだけPython2.7.6で作成．いつか書きなおす)

### wikidata.csv
parse_wiki.py で生成したデータ

Wikipediaの記事より作成した


## 依存関係

[oshikiri/SlackBot](https://github.com/oshikiri/SlackBot)
