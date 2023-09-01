from pathlib import Path
import logging

from FileBackup import FileBackup

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)

if __name__ == '__main__':
    # log.info(FileBackup().start_backup())
    pass