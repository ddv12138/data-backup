import logging
from pathlib import Path

from aligo import Aligo, EMailConfig, set_config_folder

import config
import email_config

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)


class AligoUtil:
    def __init__(self) -> None:
        super().__init__()
        set_config_folder(config.aligo_config_path)
        self.email_config = EMailConfig(
            email=email_config.notify_email,
            user=email_config.user,
            password=email_config.password,
            host=email_config.host,
            port=email_config.port
        )
        self.aligo = Aligo(email=self.email_config)

    def upload_folder(self, folder: str):
        cloud_path = self.aligo.get_folder_by_path(config.cloud_path)
        log.info(cloud_path)
        #请修改名称，不能包含字符 /*?:<>\"|
        self.aligo.upload_folder(folder, parent_file_id=cloud_path.file_id)
