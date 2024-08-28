import logging
import os
import shutil
import time
from datetime import datetime
import argparse
from croniter import croniter

import config
from aligo_util import AligoUtil
from file_pack import FilePack
from log_util import log


def do_backup():
    clear_cache()
    log.info("开始执行备份")
    output_dir = os.path.normpath(config.cache_dir + "/package/" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    file_pack.start_backup(is_enc=config.is_enc, is_zip=config.is_zip, output_dir=output_dir)
    log.info(f"output_dir:{output_dir}")
    aligo_util.upload_backup(output_dir)


def task():
    iterator = croniter(config.cron_expression, datetime.now())
    next_execution_time = iterator.get_next()
    next_execution_time_2 = iterator.get_next()
    while True:
        now_ = next_execution_time - datetime.now()
        if now_.seconds % 5 == 0:
            log.info(f"定时任务表达式:{config.cron_expression},下次执行倒计时 {now_} 接下来两次执行时间 {next_execution_time} {next_execution_time_2}")
        if now_.seconds % 900 == 0:
            log.debug(aligo_util.history())
        if datetime.now() > next_execution_time:
            do_backup()
            next_execution_time = next_execution_time_2
            next_execution_time_2 = iterator.get_next()
            log.info(f"备份执行完成,等待下次激活,下次执行时间 {next_execution_time}")
        time.sleep(1)


def clear_cache():
    directory_path = config.cache_dir
    try:
        # 确保目录存在
        if os.path.exists(directory_path):
            # 遍历目录中的文件和子目录
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 删除文件
                    os.remove(file_path)
                for _dir in dirs:
                    dir_path = os.path.join(root, _dir)
                    # 删除子目录
                    shutil.rmtree(dir_path)
    except Exception as e:
        print(f"清空目录出错：{str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='一个自动的周期性的把文件备份到阿里云的工具')
    parser.add_argument('mode', default="task", choices=['task', 'backup', 'unpack', "info"],
                        help='运行模式，task 为执行定时备份，decrypt 为解密，backup为即可执行一次备份，info用于查看已有的包信息')
    parser.add_argument('--disable_enc', action='count', help='不需要加密')
    parser.add_argument('--disable_zip', action='count', help='不需要压缩')
    parser.add_argument('--cache_dir', help='缓存文件路径')
    parser.add_argument('--cloud_path', help='阿里云盘用于备份的文件路径')
    parser.add_argument('--config_path', help='配置文件存储路径')
    parser.add_argument('--cron_expression', help='定时任务表达式')
    parser.add_argument('--max_copy_count', help='云端保存的最大备份数量')
    parser.add_argument('--progress', action='count', help='进度条开关')
    parser.add_argument('--verbose', "-v", action="count", help='展示更详细的执行过程')
    parser.add_argument('--input', '-i', help='配合info或者unpack模式，传入已有的打包文件路径，或是任意分包路径', )
    parser.add_argument('--output', '-o', help='配合unpack模式,传入解包后文件的存放路径')

    # 创建互斥组
    password_group = parser.add_mutually_exclusive_group()
    password_group.add_argument('--password', help='加密用的密钥，妥善保存，解密需要用到')
    password_group.add_argument('--passwd_file', help='(文件中读取)加密用的密钥，妥善保存，解密需要用到')

    args = parser.parse_args()

    if args.max_copy_count:
        config.max_copy_count = args.max_copy_count
    if args.cron_expression:
        config.cron_expression = args.cron_expression
    if args.config_path:
        config.config_path = args.config_path
    if args.cloud_path:
        config.cloud_path = args.cloud_path
    if args.password:
        config.password = args.password
    if args.passwd_file:
        with open(args.passwd_file, "r") as passwd_reader:
            config.password = passwd_reader.readline()
    if args.cache_dir:
        config.cache_dir = args.cache_dir
    if args.disable_enc:
        config.is_enc = False
    if args.disable_zip:
        config.is_zip = False
    if args.verbose:
        log.setLevel(logging.DEBUG)
        config.log_level = logging.DEBUG
    if args.progress:
        config.progress = True

    aligo_util = AligoUtil()
    file_pack = FilePack()

    if args.mode:
        if args.mode == "task":
            task()
        elif args.mode == "backup":
            do_backup()
        elif args.mode == "unpack":
            if not args.input:
                log.info("请给出需要解包的文件路径，具体参见帮助信息")
                exit(-1)
            if not args.output:
                log.info("请给出解包的文件的存放路径，具体参见帮助信息")
                exit(-1)
            file_pack = FilePack()
            file_pack.unpack(input_file=args.input, output_dir=args.output)
        elif args.mode == "info":
            if not args.input:
                log.info("请给出需要解包的文件路径，具体参见帮助信息")
            file_pack = FilePack()
            file_pack.info(input_file=args.input)
        else:
            raise Exception("参数错误，请检查后重试")
