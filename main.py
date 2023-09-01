from pathlib import Path
import logging

from AligoUtil import AligoUtil
from FileBackup import FileBackup

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)

if __name__ == '__main__':
    # log.info(FileBackup().start_backup())
    aligo_util = AligoUtil()
    aligo_util.upload_folder("cache/2023-09-01 11.36.56")
    pass