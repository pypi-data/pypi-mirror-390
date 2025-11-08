import time

# see https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html

# 文本消息
# Content 回复的消息内容（换行：在content中能够换行\n,支持超链接<a href="url">xxx</a>）,
XML_TEXT_TEMPLATE = """<xml>
<ToUserName><![CDATA[{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""


# 图片消息
# MediaId 是 通过素材管理中的接口上传多媒体文件，得到的id
XML_IMAGE_TEMPLATE = """<xml>
<ToUserName><![CDATA [{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Image>
</xml>"""


# 语音消息
# MediaId 是 通过素材管理中的接口上传多媒体文件，得到的id

XML_VOICE_TEMPLATE = """<xml>
<ToUserName><![CDATA [{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<Voice>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Voice>
</xml>"""

# 视频消息
# MediaId 是 通过素材管理中的接口上传多媒体文件，得到的id
# Title 否 视频消息的标题
# Description 否 视频消息的描述

XML_VIDEO_TEMPLATE = """<xml>
<ToUserName><![CDATA [{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[video]]></MsgType>
<Video>
<MediaId><![CDATA[{media_id}]]></MediaId>
<Title><![CDATA[{title}]]></Title>
<Description><![CDATA[{description}]]></Description>
</Video>
</xml>"""

# 音乐消息

# Title 否 音乐标题
# Description 否 音乐描述
# MusicURL 否 音乐链接
# HQMusicUrl 否 高质量音乐链接，WIFI环境优先使用该链接播放音乐
# ThumbMediaId 是 缩略图的媒体id，通过素材管理中的接口上传多媒体文件，得到的id

XML_MUSIC_TEMPLATE = """<xml>
<ToUserName><![CDATA [{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[music]]></MsgType>
<Music>
<Title><![CDATA[{title}]]></Title>
<Description><![CDATA[{description}]]></Description>
<MusicUrl><![CDATA[{music_url}]]></MusicUrl>
<HQMusicUrl><![CDATA[{hq_music_url}]]></HQMusicUrl>
<ThumbMediaId><![CDATA[{media_id}]]></ThumbMediaId>
</Music>
</xml>"""

# 图文消息

# ArticleCount  是 图文消息个数；当用户发送文本、图片、语音、视频、图文、地理位置这六种消息时，开发者只能回复1条图文消息；其余场景最多可回复8条图文消息
# Articles      是 图文消息信息，注意，如果图文数超过限制，则将只发限制内的条数
# Title         是 图文消息标题
# Description   是 图文消息描述
# PicUrl        是 图片链接，支持JPG、PNG格式，较好的效果为大图360*200，小图200*200
# Url           是 点击图文消息跳转链接

XML_NEWS_TEMPLATE_OLD = """<xml>
  <ToUserName><![CDATA [{toUser}]]></ToUserName>
  <FromUserName><![CDATA[{fromUser}]]></FromUserName>
  <CreateTime>{createtime}</CreateTime>
  <MsgType><![CDATA[news]]></MsgType>
  <ArticleCount>{article_count}</ArticleCount>
  <Articles>
    <item>
      <Title><![CDATA[{title}]]></Title>
      <Description><![CDATA[{description}]]></Description>
      <PicUrl><![CDATA[{pic_url}]]></PicUrl>
      <Url><![CDATA[{url}]]></Url>
    </item>
  </Articles>
</xml>"""

XML_ARTICLE_ITEM = """<item>
<Title><![CDATA[{title}]]></Title>
<Description><![CDATA[{description}]]></Description>
<PicUrl><![CDATA[{pic_url}]]></PicUrl>
<Url><![CDATA[{url}]]></Url>
</item>"""

XML_NEWS_TEMPLATE = """<xml>
<ToUserName><![CDATA [{toUser}]]></ToUserName>
<FromUserName><![CDATA[{fromUser}]]></FromUserName>
<CreateTime>{createtime}</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>{article_count}</ArticleCount>
<Articles>
{xml_articles_items}
</Articles>
</xml>"""


def get_wechat_xml_response(data):
    if "createtime" not in data:
        data["createtime"] = int(time.time())

    match data["type"]:
        case "text":
            xml = XML_TEXT_TEMPLATE.format(**data)
        case "image":
            xml = XML_IMAGE_TEMPLATE.format(**data)
        case "voice":
            xml = XML_VOICE_TEMPLATE.format(**data)
        case "video":
            xml = XML_VIDEO_TEMPLATE.format(**data)
        case "music":
            xml = XML_MUSIC_TEMPLATE.format(**data)
        case "news":
            xml_articles_items = ""
            for article in data["articles"]:
                xml_articles_items += XML_ARTICLE_ITEM.format(**article)
            data["article_count"] = len(data["articles"])
            data["xml_articles_items"] = xml_articles_items
            xml = XML_NEWS_TEMPLATE.format(**data)

    return xml
