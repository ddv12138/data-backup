import logging

include_list = [
    "example",
    "config.py"
]
exclude_list = [
    ".DS_Store",
    ".gitignore",
    ".hidden-file"
]
cache_dir = "./cache/"
password = "123456"
cloud_path = "mnt-backup"
aligo_config_path = "aligo_config"
cron_expression = "*/1 * * * * "
max_copy_count = 1
is_enc = True
is_gzip = True
log_level = logging.INFO
