import os.path
import sys
import tarfile
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import config
import logging
from FileEnc import FileEnc

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)


def fetch_file() -> []:
    log.info("start")
    include_list = config.include_list
    exclude_list = config.exclude_list

    file_list = []
    ignore_list = []
    err_list = []
    try:
        for s_file in include_list:
            log.info("开始处理文件:" + s_file)
            if os.path.exists(s_file):
                log.debug(s_file + " 文件存在")
            else:
                log.error("文件不存在，跳过" + s_file, exc_info=True, stack_info=True)
                err_list.append(s_file)
                continue
            isdir = os.path.isdir(s_file)
            if isdir:
                log.debug("[" + s_file + "]为目录，开始扫描目录下文件")
                for root, dirs, files in os.walk(s_file, True, None, False):
                    if len(os.listdir(root)) == 0:
                        log.info(root)
                        file_list.append(os.path.normpath(root))
                    for sub_file in files:
                        path = os.path.join(root, sub_file)
                        excluded = False

                        # 如果是排除的文件则跳过
                        for ex in exclude_list:
                            if path.startswith(ex) or ex == sub_file:
                                excluded = True
                                ignore_list.append(sub_file)
                                break
                        if excluded:
                            continue
                        file_list.append(path)
            else:
                file_list.append(s_file)
    except Exception as e:
        log.error(e, exc_info=True, stack_info=True)
    return [file_list, ignore_list, err_list]


def tar_package(files: list) -> str:
    progress_bar = tqdm(total=len(files), desc="文件打包中....", file=sys.stderr)
    target = config.cache_dir + "/package.tar.gz"
    target = os.path.normpath(target)
    with tarfile.open(target, 'w:gz') as zipf:
        for f in files:
            filename = f.replace(os.path.normpath(config.cache_dir), "")
            zipf.add(f, arcname="/" + filename)
            progress_bar.update(1)
    progress_bar.close()
    return target


if __name__ == '__main__':
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    file_list, ignore_list, err_list = fetch_file()
    log.info(f"文件扫描完毕，扫描结果包含{len(file_list)}个文件，忽略{len(ignore_list)}个文件，出现{len(err_list)}个错误")
    tar_file = tar_package(file_list)
    log.info(f"文件打包完成,开始进行加密")
    file_enc = FileEnc(passwd=config.password)
    enc_file = tar_file + ".enc"
    file_enc.encrypt(tar_file, enc_file)
    # file_enc = FileEnc(passwd=config.password + "")
    # file_enc.decrypt(file=enc_file, output=enc_file + ".tar.gz")
