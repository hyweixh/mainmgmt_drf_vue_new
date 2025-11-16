'''
密码通过哈希加盐进行加密
用setting.py中的SECRET_KEY作为盐
SECRET_KEY = 'django-insecure-9$0t$^qrr-w_a#mcd=m6^!!)a$u!jyx=$2cx+u73mjz&qjj73i'

通过AES进行密码加密和解密

'''

from django.conf import settings
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from binascii import b2a_hex, a2b_hex

KEY = (b'DongxinGS@3911#$')  # key：16或16的倍数
IV = b'QinYuanChun--Xue'  # iv:16位
# ----------------------------------------------------------------------------------------------------------------------
def md5(data_string):
    obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()

# ----------------------------------------------------------------------------------------------------------------------
# AES加密
def encrypt_pwd(pass_str):
    # 检查pass_str是否为整型，如果是，则转换为字符串
    # if isinstance(pass_str, int):
    #     pass_str = str(pass_str)
    # 确保 pass_str 是字符串
    if not isinstance(pass_str, str):
        pass_str = str(pass_str)

    pwdstr_b = pass_str.encode('utf-8')
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padtext = pad(pwdstr_b, 16, style='pkcs7')  # 填充模式：Zero,pkcs7,pkcs5,只能用pkcs7，为何？？
    cipherText = cipher.encrypt(padtext)

    # b2a_hex: 字符串转16进制;decode('ascii'):b'abc'--> abc
    return (b2a_hex(cipherText)).decode('ascii')
# ----------------------------------------------------------------------------------------------------------------------
# AES解密
def decode_pwd(Text_Str):
    #print('Text_Str:',Text_Str)
    cipherText = a2b_hex(Text_Str)  # # 16进制转字符串
    decrypter = AES.new(KEY, AES.MODE_CBC, IV)
    plaintext = decrypter.decrypt(cipherText)
    # 不够16位，补全到16位
    unpadtext = unpad(plaintext, 16, 'pkcs7')  # 填充模式：Zero,pkcs7,pkcs5,只能用pkcs7，为何？？
    # return unpadtext.decode('ascii')  # decode('ascii') 把二进制字符串b'abc',转为文本：abc
    return unpadtext.decode('utf-8')