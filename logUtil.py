import logging
from pathlib import Path

logging.basicConfig(format="%(asctime)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)
log = logging.getLogger(Path(__file__).stem)
