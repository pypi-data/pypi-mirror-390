#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @XZGUtil    : 2020-12-23 21:28
# @Site    :
# @File    : __init__.py.py
# @Software: PyCharm
"""
### 1. dealFile.py
- **文件名**：dealFile.py
- **类名**：无
- **方法名**：
    - clean_directory
    - create_excel_xlsx
    - write_excel_xlsx_append
    - read_excel_xlsx
    - read_excel
- **作用**：该文件主要用于读取和写入表格文件，支持的文件格式有 Excel（.xlsx、.xls）和 CSV。提供了清空文件夹、创建 Excel 文件、追加写入 Excel 文件、读取 Excel 文件和读取多种格式文件的功能。

### 2. re_xzg.py
- **文件名**：re_xzg.py
- **类名**：无
- **方法名**：loads_jsonp
- **作用**：解析 jsonp 数据格式为 json，若输入无效则抛出 `ValueError` 异常。

### 3. messageUtil.py
- **文件名**：messageUtil.py
- **类名**：无
- **方法名**：
    - init_emal
    - send_ding_message
- **作用**：该文件包含消息发送相关的方法，支持发送邮件和钉钉消息。可以通过配置邮件的标题、内容、收件人、发件人、密码、服务器和端口来发送邮件，也可以通过提供钉钉消息的 URL、消息内容和 @ 人员列表来发送钉钉消息。

### 5. SYCMCryptUtil.py
- **文件名**：SYCMCryptUtil.py
- **类名**：无
- **方法名**：
    - encrypt
    - transitId
    - decrypt
- **作用**：该文件是生意参谋解密库，提供了 RSA 算法公钥加密数据的方法 `encrypt`，以及根据该加密方法生成特定加密字符串的 `transitId` 方法，还有对加密数据进行解密并处理的 `decrypt` 方法。

### 6. ImagePositioning.py
- **文件名**：ImagePositioning.py
- **类名**：无
- **方法名**：find_img
- **作用**：在指定窗口的截图中查找模板图片，并标记匹配位置。可以设置匹配阈值，只有匹配程度大于等于该值的位置才会被选中，还可以选择是否显示匹配结果。

### 7. timeUtil.py
- **文件名**：timeUtil.py
- **类名**：无
- **方法名**：parse_datetime
- **作用**：将字符串转换为时间对象，支持多种常见的日期格式。如果没有匹配的格式，则返回 `None`。

### 8. quickTooling.py
- **文件名**：quickTooling.py
- **类名**：无
- **方法名**：
    - split_list
    - remove_duplicates
    - sort_list
- **作用**：提供了一些小工具方法，包括列表切片、列表元素去重和列表元素排序。

### 9. pyqt5Logger.py
- **文件名**：pyqt5Logger.py
- **类名**：
    - _FloatingLoggerImpl
    - LoggerSignals
    - FloatingLogger
- **方法名**：多个（如 append_log、log、start_application 等）
- **作用**：该文件实现了一个基于 PyQt5 的浮动日志窗口工具，支持线程安全的日志记录。可以记录不同级别的日志信息，如信息、警告、错误和调试信息，并在日志窗口中显示。

### 10. updateSpider.py
- **文件名**：updateSpider.py
- **类名**：upconfig
- **方法名**：
    - get_information
    - set_information
    - check_update
- **作用**：用于记录爬虫的更新时间，提供了获取更新日期、修改更新日期配置文件和检查今日是否更新的功能。

### 11. 生意参谋指数转换.py
- **文件名**：生意参谋指数转换.py
- **类名**：无
- **方法名**：多个（如 f_sales、f_uv、tradeindex、uvindex 等）
- **作用**：该文件是一个 Flask 应用，用于将生意参谋的指数进行转换。提供了多个路由，支持对不同类型的指数（如销售额、UV、加购数等）进行转换，并返回转换结果。

### 12. downFile.py
- **文件名**：downFile.py
- **类名**：无
- **方法名**：
    - check_folder
    - dl_file
    - check_file_isexist_local
    - deal_cookie
    - __send_req
- **作用**：该文件用于下载文件，支持检查文件夹是否存在并创建，发送请求下载文件，检查文件是否存在本地，处理 cookie 等功能。

### 13. logger.py
- **文件名**：logger.py
- **类名**：无
- **方法名**：conlog
- **作用**：该文件提供了一个日志记录方法 `conlog`，可以记录当前时间、文件名、方法名、行号和日志信息，并将其打印输出。
### 14. screenShot.py
截图

"""
