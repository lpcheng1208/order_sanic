# coding=utf-8
import hashlib

from Crypto.Cipher import DES, AES
import base64


mdes = DES.new(b'!z*EaY0e', 1)


def decode_base64(text, user_agent=""):
    if not text: return text
    if 'iOS' in user_agent or "CFNetwork" in user_agent:
        dec_text = aes_func.decrypt(text)
    else:
        data = text.encode("utf-8")
        ret = mdes.decrypt(base64.decodebytes(data))
        padding_len = ret[-1]
        dec_text = ret[:-padding_len].decode("utf-8")
    return dec_text


def encrypt_base64(text):
    pad_len = 8 - len(text) % 8
    padding = chr(pad_len) * pad_len
    text += padding

    data = text.encode("utf-8")
    data = base64.encodebytes(mdes.encrypt(data))
    return data.decode("utf-8").replace('\n', '')


class PrpCrypt(object):
    """
    AES加密与解密
    """

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
        self.cipher_text = None

    def get_cryptor(self):
        sha384 = hashlib.sha384()
        sha384.update(self.key.encode('utf-8'))
        res = sha384.digest()

        crypt_or = AES.new(res[0:32], self.mode, res[32:48])

        return crypt_or

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):

        if not text:
            return text

        cryptor = self.get_cryptor()

        data = text.encode("utf-8")

        plain_text = cryptor.decrypt(base64.decodebytes(data))

        padding_len = plain_text[-1]

        plain_text = plain_text[:-padding_len].decode('utf-8')

        return plain_text

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):

        cryptor = self.get_cryptor()

        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + (chr(add) * add)

        data = text.encode('utf-8')
        data = base64.encodebytes(cryptor.encrypt(data))

        return data.decode('utf-8').replace('\n', '')


aes_func = PrpCrypt('!z*EaY0e')

if __name__ == '__main__':
    enc_t = decode_base64("JANz27XK5SlLaI0YCr67dY3tvQ73clwHxx0NJu80NdcKTn6oH1IYCA==")
    print(enc_t)
