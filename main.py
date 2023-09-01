import time
from datetime import datetime
from pathlib import Path
import logging
import argparse
from croniter import croniter

import config
from AligoUtil import AligoUtil
from FileBackup import FileBackup, clear_cache

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)


def do_backup():
    log.info("开始执行备份")
    backup = FileBackup().start_backup()
    aligo_util = AligoUtil()
    aligo_util.upload_backup(backup)
    clear_cache()


def task():
    iter = croniter(config.cron_expression, datetime.now())
    next_execution_time = iter.get_next(datetime)
    while True:
        log.info(f"下次执行倒计时{next_execution_time - datetime.now()}")
        if datetime.now() > next_execution_time:
            do_backup()
            next_execution_time = iter.get_next(datetime)
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='一个自动的周期性的把文件备份到阿里云的工具')
    parser.add_argument('--mode', '-m', default="task",choices=['task', 'decrypt'], help='运行模式，task 为执行定时备份，decrypt 为解密')
    parser.add_argument('--progress', '-p', action="store_true", help='是否启用进度条')
    parser.add_argument('--cache_dir', help='缓存文件路径')
    parser.add_argument('--password', help='加密用的密钥，妥善保存，解密需要用到')
    parser.add_argument('--cloud_path', help='阿里云用于备份的文件路径')
    parser.add_argument('--config_path', help='配置文件存储路径')
    parser.add_argument('--cron_expression', help='定时任务表达式')
    parser.add_argument('--max_copy_count', help='云端保存的最大备份数量')
    parser.add_argument('file-dir', help='存放备份文件的文件夹路径')

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
    if args.progress is not None:
        config.progress = args.progress
    if args.mode:
        if args.mode == "task":
            task()
        else:
            log.info(args.mode)
            log.info(args.file)
