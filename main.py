import logging
import os
import shutil
import time
from datetime import datetime
import argparse
from croniter import croniter

import config
from AligoUtil import AligoUtil
from FilePack import FilePack
from LogUtil import log


def do_backup():
    clear_cache()
    log.info("开始执行备份")
    output_dir = os.path.normpath(config.cache_dir + "/package/" + datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
    file_pack = FilePack()
    file_pack.start_backup(is_enc=config.is_enc, is_gzip=config.is_gzip,use_zlib=config.use_zlib, output_dir=output_dir)
    log.info(output_dir)
    aligo_util = AligoUtil()
    aligo_util.upload_backup(output_dir)


def task():
    iterator = croniter(config.cron_expression, datetime.now())
    next_execution_time = iterator.get_next(datetime)
    while True:
        now_ = next_execution_time - datetime.now()
        if now_.seconds % 5 == 0:
            log.debug(f"下次执行倒计时 {now_} 下次执行时间 {next_execution_time}")
        if datetime.now() > next_execution_time:
            do_backup()
            next_execution_time = iterator.get_next(datetime)
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
    parser.add_argument('--mode', '-m', default="task", choices=['task', 'backup', 'unpack', "info"],
                        help='运行模式，task 为执行定时备份，decrypt 为解密，backup为即可执行一次备份，info用于查看已有的包信息')
    parser.add_argument('--disable_enc', '-e', action='count', help='不需要加密')
    parser.add_argument('--disable_gzip', '-g', action='count', help='不需要压缩')
    parser.add_argument('--use_zlib', '-z', action='count', help='使用zlib压缩')
    parser.add_argument('--cache_dir', help='缓存文件路径')
    parser.add_argument('--password', help='加密用的密钥，妥善保存，解密需要用到')
    parser.add_argument('--cloud_path', help='阿里云用于备份的文件路径')
    parser.add_argument('--config_path', help='配置文件存储路径')
    parser.add_argument('--cron_expression', help='定时任务表达式')
    parser.add_argument('--max_copy_count', help='云端保存的最大备份数量')
    parser.add_argument('--verbose', "-v", action="count", help='展示更详细的执行过程')
    parser.add_argument('--disable_email', action="count", help='展示更详细的执行过程')
    parser.add_argument('file', nargs='?', help='存放备份文件的文件夹路径或者备份文件之一', )

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
    if args.cache_dir:
        config.cache_dir = args.cache_dir
    if args.disable_enc:
        config.is_enc = False
    if args.disable_gzip:
        config.is_gzip = False
    if args.use_zlib:
        config.is_gzip = False
        config.use_zlib = True
    if args.verbose:
        config.log_level = logging.DEBUG
    if args.disable_email:
        config.use_email = False
    if args.mode:
        if args.mode == "task":
            task()
        elif args.mode == "backup":
            do_backup()
        elif args.mode == "unpack" and args.file:
            output_dir = os.path.join(config.cache_dir, "unpack")
            file_pack = FilePack()
            file_pack.unpack(input_file=args.file, output_dir=output_dir)
        elif args.mode == "info" and args.file:
            file_pack = FilePack()
            file_pack.info(input_file=args.file)
        else:
            raise Exception("无法识别")
