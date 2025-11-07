# coding: utf8
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5, AES
import base64
from binascii import a2b_hex


"""
生意参谋解密库，更改在此文件，加密时运行pyarmor obfuscate SYCMCryptUtil.py,加密后会在当前文件夹下生成dist文件夹，将文件夹内容复制出来，放到XZGUtil下，上传到库文件时，误将此文件上传，此文件只可上传到GitHub
"""

def encrypt(message):
    '''
    RSA算法公钥加密数据，公钥泄露无关紧要
    :return:
    '''
    public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCJ50kaClQ5XTQfzkHAW9Ehi+iXQKUwVWg1R0SC3uYIlVmneu6AfVPEj6ovMmHa2ucq0qCUlMK+ACUPejzMZbcRAMtDAM+o0XYujcGxJpcc6jHhZGO0QSRK37+i47RbCxcdsUZUB5AS0BAIQOTfRW8XUrrGzmZWtiypu/97lKVpeQIDAQAB
-----END PUBLIC KEY-----"""
    rsa_key_obj = RSA.importKey(public_key)
    cipher_obj = Cipher_PKCS1_v1_5.new(rsa_key_obj)
    cipher_text = base64.b64encode(cipher_obj.encrypt(message.encode('utf-8')))
    return cipher_text.decode('utf-8')


def transitId():
     return encrypt('w28Cz694s63kBYk4')

def decrypt(text):
    """
    对数据解密并处理
    :return: 解密处理后的店铺信息列表
    """
    password = "w28Cz694s63kBYk4"
    key = password.encode("utf-8")
    mode = AES.MODE_CBC
    b_data = bytes(text, encoding="utf-8")
    cryptor = AES.new(key, mode, b"4kYBk36s496zC82w")  # 偏移量
    plain_text = cryptor.decrypt(a2b_hex(b_data))
    result_data = bytes.decode(plain_text).rstrip("\0")
    return result_data

