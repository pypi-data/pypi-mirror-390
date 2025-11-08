import pytest
import time
import hashlib
from python_plugins.weixin.wechat import Wechat
from python_plugins.weixin.wechat_crypt import get_signature
from python_plugins.weixin.wechat_crypt import MessageCrypt
from python_plugins.random import rand_digit, rand_letter
from python_plugins.convert.xml import xml2dict


test_wechat_app = {
    "name": "test",
    "appid": "wxabcdefghijklmnop",
    "token": "testtest",
    "aeskey": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
    "appsecret": "abcdefghijklmnopqrstuvwxyz012345",
}

server_id = "gh_1234567890ab"
openid = "abcdefghijklmnopqrstuvwxyz01"


class MyWechat(Wechat):
    def get_app(self) -> dict:
        return test_wechat_app


class TestWechat:
    def test_verify(self):
        mywechat = MyWechat()
        timestamp = str(int(time.time()))
        nonce = rand_digit(10)
        token = test_wechat_app["token"]
        signature = get_signature([token, timestamp, nonce])
        echostr = rand_digit(18)
        query = {
            "timestamp": timestamp,
            "nonce": nonce,
            "signature": signature,
            "echostr": echostr,
        }
        r = mywechat.verify(query)
        assert r == echostr

    def test_chat(self):
        """chat（明文）"""
        input_text = rand_letter(10)
        timestamp = str(int(time.time()))
        nonce = rand_digit(10)

        xml = (
            "<xml>"
            f"<ToUserName><![CDATA[{server_id}]]></ToUserName>"
            f"<FromUserName><![CDATA[{openid}]]></FromUserName>"
            f"<CreateTime>{timestamp}</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{input_text}]]></Content>"
            "<MsgId>23533248665819413</MsgId>"
            "</xml>"
        )
        query = {
            "timestamp": timestamp,
            "nonce": nonce,
            "openid": f"{openid}",
        }

        mywechat = MyWechat()
        r = mywechat.chat(query, xml)
        data = xml2dict(r)
        # print(data)
        assert data["ToUserName"] == openid
        assert data["FromUserName"] == server_id
        assert data["MsgType"] == "text"
        assert input_text in data["Content"]

    def test_chat_aes(self):
        """chat（密文）"""
        input_text = rand_letter(10)
        timestamp = str(int(time.time()))
        nonce = rand_digit(10)
        mywechat = MyWechat()
        app = mywechat.app
        mc = MessageCrypt(app["appid"], app["token"], app["aeskey"])

        xml = (
            "<xml>"
            f"<ToUserName><![CDATA[{server_id}]]></ToUserName>"
            f"<FromUserName><![CDATA[{openid}]]></FromUserName>"
            f"<CreateTime>{timestamp}</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{input_text}]]></Content>"
            "<MsgId>23533248665819413</MsgId>"
            "</xml>"
        )

        # 获取密文和签名
        encrypt, msg_signature = mc.get_encrypt_sig(xml, timestamp, nonce)

        xml2 = (
            "<xml>"
            f"<ToUserName><![CDATA[{server_id}]]></ToUserName>"
            f"<FromUserName><![CDATA[{openid}]]></FromUserName>"
            f"<CreateTime>{timestamp}</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{input_text}]]></Content>"
            "<MsgId>6054768590064713728</MsgId>"
            f"<Encrypt><![CDATA[{encrypt}]]></Encrypt>"
            "</xml>"
        )

        query = {
            "timestamp": timestamp,
            "nonce": nonce,
            "encrypt_type": "aes",
            "msg_signature": msg_signature,
        }

        r = mywechat.chat(query, xml2)
        # print(r)
        r_dict = xml2dict(r)
        r_xml = mc.decrypt_msg(
            r_dict["TimeStamp"],
            r_dict["Nonce"],
            r_dict["Encrypt"],
            r_dict["MsgSignature"],
        )
        data = xml2dict(r_xml)
        # print(data)
        assert data["ToUserName"] == openid
        assert data["FromUserName"] == server_id
        assert data["MsgType"] == "text"
        assert input_text in data["Content"]
