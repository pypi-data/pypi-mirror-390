import hashlib
from python_plugins.convert import xml2dict
from .wechat_crypt import MessageCrypt
from .wechat_crypt import get_signature
from .format_response import get_wechat_xml_response


class Wechat:

    def __init__(self, name=None):
        self.name = name
        self.app = self.get_app()

    # 获取app
    def get_app(self) -> dict:
        raise NotImplementedError()

    # 记录信息
    def log_data(self):
        return

    def verify(self, args):
        signature = args["signature"]
        timestamp = args["timestamp"]
        nonce = args["nonce"]
        echostr = args["echostr"]
        token = self.app["token"]
        if get_signature([token, timestamp, nonce]) == signature:
            return echostr
        else:
            return

    def chat(self, args, content):
        self.openid = args.get("openid")
        msg_signature = args.get("msg_signature", "")
        timestamp = args.get("timestamp", "")
        nonce = args.get("nonce", "")
        # 加密标记
        encrypt_type = args.get("encrypt_type")
        xml_dict = xml2dict(content)

        if not encrypt_type:
            self.input = xml_dict
            self.dispatch()
            self.get_xml_response()
            xml_reponse = self.xml_response
        else:
            # decrypt
            mc = MessageCrypt(self.app["appid"], self.app["token"], self.app["aeskey"])
            xml_decrypted = mc.decrypt_msg(
                timestamp, nonce, xml_dict["Encrypt"], msg_signature
            )
            self.input = xml2dict(xml_decrypted)
            self.dispatch()
            self.get_xml_response()
            # encrypt
            xml_reponse = mc.encrypt_msg(self.xml_response, timestamp, nonce)

        # 返回前记录下日志，如果实现记录日志的话
        self.log_data()

        return xml_reponse

    def dispatch(self):
        self.default_answer()
        self.toUser = self.input["ToUserName"]
        self.fromUser = self.input["FromUserName"]
        msgType = self.input["MsgType"]

        if msgType == "text":
            keyword = self.input["Content"]
        elif msgType == "event":
            event = self.input["Event"]
            if event == "subscribe":
                # self.onSubscribe()
                keyword = "subscribe"
            elif event == "unsubscribe":
                # self.onUnsubscribe()
                keyword = "unsubscribe"
            elif event == "CLICK":
                eventKey = self.input["EventKey"]
                keyword = eventKey
            else:
                keyword = "<event:{event}>"
        elif msgType == "image":
            keyword = f"<{msgType}>"
        elif msgType == "voice":
            keyword = f"<{msgType}>"
        elif msgType == "video":
            keyword = f"<{msgType}>"
        elif msgType == "shortvideo":
            keyword = f"<{msgType}>"
        elif msgType == "location":
            location_x = self.input["location_x"]
            location_y = self.input["location_y"]
            keyword = f"<{msgType}({location_x},{location_y})>"
        elif msgType == "link":
            keyword = f"<{msgType}>"
        else:
            keyword = f"<{msgType}>"

        self.keyword = keyword

        self.get_answer()
        return

    def default_answer(self):
        self.answer = {"type": "text", "content": "I'm sorry, I don't understand."}
        return

    def get_answer(self):
        match self.keyword:
            case "subscribe":
                r = f"Hello, welcome to {self.app['name']}!"
                self.answer = {"type": "text", "content": r}
            case _:
                self.answer = {"type": "text", "content": "a:" + self.keyword}
        return

    def get_xml_response(self):
        self.data_response = {
            "type" : self.answer["type"],
            "toUser": self.fromUser,
            "fromUser": self.toUser,
        }
        
        match self.answer["type"]:
            case "text":                
                self.data_response["content"] = self.answer["content"]
            case "news":
                self.data_response["articles"] = self.answer["articles"]
                
        self.xml_response = get_wechat_xml_response(self.data_response)
        
        return
