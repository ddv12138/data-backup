import logging
from pathlib import Path

import config

logging.basicConfig(format="%(asctime)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=config.log_level)
log = logging.getLogger(Path(__file__).stem)
