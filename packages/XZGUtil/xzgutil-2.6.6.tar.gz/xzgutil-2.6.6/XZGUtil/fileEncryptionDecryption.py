#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023-05-10 10:40
# @Site    :
# @File    : fileEncryptionDecryption.py
# @Software: PyCharm
"""文件加密解密工具"""
import base64
from decimal import Decimal

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import os
from pathlib import Path
from retrying import retry


def encrypt_path_aes(path, password):
    # 对文件名进行AES加密
    key = SHA256.new(password.encode('utf-8')).digest()
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    path_encoded = iv + cipher.encrypt(path.encode('utf-8'))
    return path_encoded.hex()


def decrypt_path_aes(path_encoded, password):
    # 对文件名进行AES解密
    path_encoded = bytes.fromhex(path_encoded)
    key = SHA256.new(password.encode('utf-8')).digest()
    iv = path_encoded[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    path_decoded = cipher.decrypt(path_encoded[AES.block_size:]).decode('utf-8')
    return path_decoded


def rename_all_files_in_directory(dir_path, passwd, de=False):
    """
    获取文件夹下所有的子文件，将文件名加密解密，不包括文件夹
    :param dir_path:
    :param passwd:
    :param de: True加密  Fase 解密
    :return:
    """
    for root, directories, filenames in os.walk(dir_path):
        for filename in filenames:
            # 使用os.path.join()函数将文件名和文件夹路径拼接成完整的文件路径
            file_path = os.path.join(root, filename)
            # 生成新的文件名
            if de:# 加密
                if filename.endswith("#Md6.bat"):  #已经加密过了
                    continue
                else:  # 没有加密，可以加密
                    if len(filename) > 35:
                        type = f"{filename.split('.')[-1]}"
                        filename = filename[:30] + '.' + type
                    new_filename = encrypt_path_aes(filename, passwd) + "#Md6.bat"
            else:  # 解密
                if filename.endswith("#Md6.bat"):  # 已经加密过了，可以解密
                    new_filename = decrypt_path_aes(filename.split("#Md6.bat")[0], passwd)
                else:
                    continue
            # 使用os.path.join()函数将新的文件名和文件夹路径拼接成完整的文件路径
            new_file_path = os.path.join(root, new_filename)
            # 将文件重命名为新的文件名
            os.rename(file_path, new_file_path)
            print(f'Renamed file {file_path} to {new_file_path}')
    for i in range(1,5):
        try:
            get_all_subfolders(dir_path, passwd, de)
        except Exception as e:
            print(e)

@retry(stop_max_attempt_number=10)
def get_all_subfolders(folder_path, passwd, de=True):
    """获取文件夹下所有文件夹及子文件夹"""
    for root, dirs, files in os.walk(folder_path):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if os.path.isdir(folder_path):
                if de:  # 加密
                    if folder.endswith("#Md6"):  # 已经加密过了
                        continue
                    else:  # 没有加密，可以加密
                        folder = folder[:30]
                        new_folder_name = encrypt_path_aes(folder, passwd) + "#Md6"
                else:  # 解密
                    if folder.endswith("#Md6"):  # 已经加密过了，可以解密
                        new_folder_name = decrypt_path_aes(folder.split("#Md6")[0], passwd)
                    else:
                        continue
                new_folder_name = os.path.join(root, new_folder_name)
                old_path = Path(folder_path)
                new_path = Path(new_folder_name)
                old_path.rename(new_path)
                print(f'Renamed dir {folder_path} to {new_folder_name}')


if __name__ == '__main__':
    path = 'G:\测试文件'
    password = "woshishei"
    rename_all_files_in_directory(path, password)
    # print(encode_string('奥术大师大多撒所大多撒阿打算大所多啊啊爱的爱的a1d23a1d3a313a15da365315335a41d'))
    # print(decrypt_string('11100101101001011010010111100110100111001010111111100101101001001010011111100101101110001000100011100101101001001010011111100101101001001001101011100110100100101001001011100110100010011000000011100101101001001010011111100101101001001001101011100110100100101001001011101001100110001011111111100110100010011001001111100111101011101001011111100101101001001010011111100110100010011000000011100101101001001001101011100101100101011000101011100101100101011000101011100111100010001011000111100111100110101000010011100111100010001011000111100111100110101000010001100001001100010110010000110010001100110110000100110001011001000011001101100001001100110011000100110011011000010011000100110101011001000110000100110011001101100011010100110011001100010011010100110011001100110011010101100001001101000011000101100100'))

