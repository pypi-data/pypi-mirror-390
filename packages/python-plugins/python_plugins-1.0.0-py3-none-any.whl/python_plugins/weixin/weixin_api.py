import datetime, json
import requests

HTTPS_API_WEIXIN = "https://api.weixin.qq.com/"
API_WEIXIN_ACCESSTOKEN = (
    HTTPS_API_WEIXIN
    + "cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
)
API_WEIXIN_GETMENU = HTTPS_API_WEIXIN + "cgi-bin/menu/get?access_token={ACCESS_TOKEN}"
API_WEIXIN_SETMENU = (
    HTTPS_API_WEIXIN + "cgi-bin/menu/create?access_token={ACCESS_TOKEN}"
)
API_WEIXIN_CODE2SESSION = (
    HTTPS_API_WEIXIN
    + "sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={JSCODE}&grant_type=authorization_code"
)
API_WEIXIN_MSGSECCHECK = (
    HTTPS_API_WEIXIN + "wxa/msg_sec_check?access_token={ACCESS_TOKEN}"
)
API_WEIXIN_IMGSECCHECK = (
    HTTPS_API_WEIXIN + "wxa/img_sec_check?access_token={ACCESS_TOKEN}"
)
API_WEIXIN_MEDIACHECKASYNC = (
    HTTPS_API_WEIXIN + "wxa/media_check_async?access_token={ACCESS_TOKEN}"
)


class WeixinApi:
    def __init__(self, app):
        self.app = app

    def get_local_access_token(self) -> dict | None:
        """从本地获取access_token"""
        raise NotImplementedError()

    def update_local_access_token(self, token):
        """更新本地的access_token"""
        raise NotImplementedError()

    def get_access_token(self):
        """get access_token from local, if expire then get from api of weixin and update local data."""
        access_token = self.get_access_token_from_local()
        if access_token and access_token["expires_at"] > datetime.datetime.now():
            return access_token["token"]
        r = requests.get(
            API_WEIXIN_ACCESSTOKEN.format(
                APPID=self.app["appid"], APPSECRET=self.app["appsecret"]
            )
        )
        if r.status_code == 200:
            rtoken = r.json()
            token = rtoken["access_token"]
            expires_at = datetime.datetime.now() + datetime.timedelta(
                seconds=rtoken["expires_in"]
            )
            self.update_local_access_token(token, expires_at)
            return token
        return None

    def get_menu(self):
        token = self.get_access_token()
        r = requests.get(API_WEIXIN_GETMENU.format(ACCESS_TOKEN=token))
        return r.json()

    def set_menu(self, menu):
        token = self.get_access_token()
        r = requests.post(
            API_WEIXIN_SETMENU.format(ACCESS_TOKEN=token),
            data=json.dumps(menu, ensure_ascii=False).encode("utf-8"),
        )
        if r.status_code == 200:
            return r.json()
        else:
            return r

    def code2Session(self, code):
        """调用 auth.code2Session 接口，换取 用户唯一标识 OpenID 和 会话密钥 session_key"""
        response = requests.get(
            API_WEIXIN_CODE2SESSION.format(
                APPID=self.app["appid"], SECRET=self.app["appsecret"], JSCODE=code
            )
        )
        return response.json()

    def msgseccheck(self, content):
        """检查一段文本是否含有违法违规内容"""
        token = self.get_access_token()
        r = requests.post(
            API_WEIXIN_MSGSECCHECK.format(ACCESS_TOKEN=token),
            data=json.dumps({"content": content}, ensure_ascii=False).encode("utf-8"),
        )
        if r.status_code == 200:
            return r.json()
        return r
