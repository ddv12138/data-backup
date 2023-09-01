import time
from datetime import datetime
from pathlib import Path
import logging

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




if __name__ == '__main__':
    iter = croniter(config.cron_expression, datetime.now())
    next_execution_time = iter.get_next(datetime)
    while True:
        log.info(f"下次执行倒计时{next_execution_time - datetime.now()}")
        if datetime.now() > next_execution_time:
            do_backup()
            next_execution_time = iter.get_next(datetime)
        time.sleep(1)
