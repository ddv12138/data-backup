from aligo import Aligo, EMailConfig, set_config_folder
from LogUtil import log
import config



class AligoUtil:
    def __init__(self) -> None:
        super().__init__()
        set_config_folder(config.aligo_config_path)
        try:
            import email_config
            self.email_config = EMailConfig(
                email=email_config.notify_email,
                user=email_config.user,
                password=email_config.password,
                host=email_config.host,
                port=email_config.port
            )
            self.aligo = Aligo(email=self.email_config, level=config.log_level)
        except ImportError:
            log.error("未找到邮箱配置，将使用命令行二维码验证")
            self.aligo = Aligo(level=config.log_level)

    def upload_backup(self, file: str):
        cloud_path = self.aligo.get_folder_by_path(config.cloud_path)
        log.info("开始上传: " + file + "--->" + str(cloud_path))
        # 不能包含字符 /*?:<>\"|
        self.aligo.upload_folder(file, parent_file_id=cloud_path.file_id)
        log.info("上传成功")
        self.history_check()

    def history(self):
        cloud_path = self.aligo.get_folder_by_path(config.cloud_path)
        return self.aligo.get_file_list(parent_file_id=cloud_path.file_id)

    def history_check(self, ):
        log.info("开始进行备份历史检查")
        history = self.history()
        max_count = config.max_copy_count
        log.info(f"当前允许持有的最大备份数{max_count}")
        curr_count = len(history)
        log.info(f"当前已经持有的备份数{curr_count}")
        if curr_count > max_count:
            for _ in range(curr_count - max_count):
                old = history.pop()
                log.info(f"删除过期备份 {old}")
                self.aligo.move_file_to_trash(file_id=old.file_id)


if __name__ == '__main__':
    log.info(AligoUtil().history())
