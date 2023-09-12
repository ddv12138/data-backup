import logging

# 需要备份的文件和文件夹
include_list = [
    "backup/",
]
# 需要排除的文件和文件夹(暂不支持通配符等方式匹配)
exclude_list = [
    ".DS_Store",
    ".gitignore",
    ".hidden-file"
]
# 用来存放备份缓存的文件夹
cache_dir = "cache/"
# 加密的密钥
password = "123456"
# 备份在阿里云盘的存放位置
cloud_path = "mnt-backup"
# 阿里云盘认证信息存放位置位置
aligo_config_path = "aligo_config/"
# 任务执行周期的cron表达式
cron_expression = "*/1 * * * * "
# 最大同时保留多少份备份
max_copy_count = 10
# 是否加密
is_enc = True
# 是否压缩
is_zip = True
# 日志级别
log_level = logging.INFO
progress = False
