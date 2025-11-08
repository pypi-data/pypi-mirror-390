# /**
#  * error code 说明.
#  * <ul>
#  *    <li>-40001: 签名验证错误</li>
#  *    <li>-40002: xml解析失败</li>
#  *    <li>-40003: sha加密生成签名失败</li>
#  *    <li>-40004: encodingAesKey 非法</li>
#  *    <li>-40005: appid 校验错误</li>
#  *    <li>-40006: aes 加密失败</li>
#  *    <li>-40007: aes 解密失败</li>
#  *    <li>-40008: 解密后得到的buffer非法</li>
#  *    <li>-40009: base64加密失败</li>
#  *    <li>-40010: base64解密失败</li>
#  *    <li>-40011: 生成xml失败</li>
#  * </ul>
#  */
class ErrorCode:
    OK = 0
    ValidateSignatureError = -40001
    ParseXmlError = -40002
    ComputeSignatureError = -40003
    IllegalAesKey = -40004
    ValidateAppidError = -40005
    EncryptAESError = -40006
    DecryptAESError = -40007
    IllegalBuffer = -40008
    EncodeBase64Error = -40009
    DecodeBase64Error = -40010
    GenReturnXmlError = -40011
