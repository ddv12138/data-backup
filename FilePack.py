import gzip
import logging
import os
import pickle
import shutil
from pathlib import Path

import config
from ddv.DdvFileInfo import DdvFileInfo, FileType
from ddv.DdvFileMeta import DdvFileMeta

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s %(filename)s:%(lineno)d - %(message)s"
                    , level=logging.DEBUG)

log = logging.getLogger(Path(__file__).stem)

magic_num = "ddvudo".encode("utf-8")
magic_num_len = len(magic_num)
magic_num_end = 4294967295


class FilePack:
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
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

    @staticmethod
    def package(files: list, output_dir: str, use_split: bool = False,
                split_size: int = 1024 * 1024 * 1024,
                buffer_size=1024 * 1024 * 10) -> list:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        current_split = 1
        current_tar_name = os.path.join(output_dir,
                                        f"package.{str(current_split)}.ddv" if use_split else f"package.ddv")
        res = []

        # 移除不受支持的文件
        files = [DdvFileInfo(file, os.path.getsize(file), FileType.DIR if os.path.isdir(file) else FileType.File) for
                 file in files if
                 not os.path.islink(file)]

        with open(current_tar_name, "wb") as ddv:
            res.append(current_tar_name)
            # 写入魔数
            ddv.write(magic_num)
            # 写入当前分卷序号
            ddv.write(current_split.to_bytes(4, "big"))
            for f in files:
                file_seq = files.index(f).to_bytes(4, "big")
                # 写入当前文件序号
                ddv.write(file_seq)
                curr_file_size = 0
                # 处理目录
                if f.type == FileType.DIR:
                    continue
                # 处理文件
                with open(f.name, "rb") as file:
                    while True:
                        curr_buff_size = buffer_size
                        if use_split:
                            curr_buff_size = buffer_size if (ddv.tell() + buffer_size) < split_size else (
                                    split_size - ddv.tell())
                        read = file.read(curr_buff_size)
                        if not read:
                            f.packed_size = curr_file_size
                            log.info(
                                f"文件大小记录 文件名：{f.name} 文件类型：{f.type} 文件大小：{f.size} 打包后大小：{f.packed_size}")
                            break
                        curr_file_size += len(read)
                        ddv.write(read)
                        if ddv.tell() >= split_size and use_split:
                            current_split += 1
                            current_tar_name = os.path.join(output_dir, f"package.{str(current_split)}.ddv")
                            ddv.flush()
                            ddv.close()
                            ddv = open(current_tar_name, "wb")
                            # 写入魔数
                            ddv.write(magic_num)
                            # 写入当前分卷序号
                            ddv.write(current_split.to_bytes(4, "big"))
            # 写入文件列表整体信息
            file_meta = DdvFileMeta(files)
            files_info_dumps = pickle.dumps(file_meta)
            file_meta_len = len(files_info_dumps)
            file_meta_len_to_bytes = file_meta_len.to_bytes(4, "big")
            ddv.write(magic_num_end.to_bytes(4, "big"))
            ddv.write(files_info_dumps)
            ddv.write(file_meta_len_to_bytes)
            ddv.write(magic_num_end.to_bytes(4, "big"))
        return res

    def unpack(self, input_file: str, output_dir, buffer_size=1024 * 1024 * 5):
        with open(input_file, "rb+") as ddv:
            curr_magic_num = ddv.read(magic_num_len)
            if curr_magic_num != magic_num:
                raise Exception(f"文件格式不匹配{curr_magic_num}")
            all_split = self.find_splits(input_file)
            log.info(f"分卷信息: {all_split}")
        file_list = None
        curr_file_size = 0
        curr_output_file = None
        curr_file_readied_size = 0

        final_split = all_split[max(sorted(all_split))]
        with open(final_split, "ab+") as final_split_ab:
            final_split_size = os.path.getsize(final_split)
            # 校验文件结束魔数
            final_split_ab.seek(final_split_size - 4)
            curr_magic_end = int.from_bytes(final_split_ab.read(4), "big")
            if magic_num_end != curr_magic_end:
                raise Exception(f"文件格式不匹配")
            # 读取文件列表大小
            final_split_ab.seek(final_split_size - 8)
            file_list_size = int.from_bytes(final_split_ab.read(4), "big")
            # 读取文件列表
            final_split_ab.seek(final_split_size - 8 - file_list_size)
            file_list = pickle.loads(final_split_ab.read(file_list_size))
            if type(file_list) != DdvFileMeta:
                raise Exception("文件信息已损坏")
        try:
            for _ in sorted(all_split):
                curr_file = all_split[_]
                with open(curr_file, "rb") as ddv:
                    # 校验魔数
                    curr_magic_num = ddv.read(magic_num_len)
                    if curr_magic_num != magic_num:
                        raise Exception(f"文件格式不匹配{curr_magic_num}")
                    # 读取分选序号
                    split_seq = int.from_bytes(ddv.read(4), "big")

                    while True:
                        if curr_file_readied_size == curr_file_size:
                            curr_file_readied_size = 0
                            # 读取文件序号
                            f_seq = int.from_bytes(ddv.read(4), "big")
                            if f_seq == magic_num_end:
                                log.info("处理完毕，退出")
                                break
                            curr_file_info = file_list.files[f_seq]
                            # 获取文件大小
                            curr_file_size = curr_file_info.packed_size
                            log.info(
                                f"文件读取 分卷序号：{split_seq} 文件序号：{f_seq} 文件名称：{curr_file_info.name} 文件大小：{curr_file_size}")
                            if curr_file_info.type == FileType.DIR:
                                f_output = os.path.normpath(output_dir + "/" + curr_file_info.name)
                                if not os.path.exists(f_output):
                                    os.makedirs(f_output)
                                    continue
                            else:
                                f_output = output_dir + "/" + curr_file_info.name
                                f_dir, f_name = os.path.split(f_output)
                                f_dir = os.path.normpath(f_dir)
                                if not os.path.exists(f_dir):
                                    os.makedirs(f_dir)
                                curr_output_file = open(os.path.normpath(f_output), "wb")

                        split_break = False
                        while True:
                            if curr_file_readied_size + buffer_size > curr_file_size:
                                curr_buffer_size = curr_file_size - curr_file_readied_size
                            else:
                                curr_buffer_size = buffer_size
                            read = ddv.read(curr_buffer_size)
                            if not read:
                                if curr_file_readied_size == curr_file_size:
                                    curr_output_file.flush()
                                    curr_output_file.close()
                                else:
                                    split_break = True
                                break
                            else:
                                curr_file_readied_size += len(read)
                                curr_output_file.write(read)
                        if split_break:
                            break
        finally:
            if curr_output_file is not None and not curr_output_file.closed:
                curr_output_file.flush()
                curr_output_file.close()

    @staticmethod
    def find_splits(input_file):
        file_map = {}
        dir, _ = os.path.split(input_file)
        for f in os.listdir(dir):
            f_path = os.path.normpath(dir + "/" + f)
            with open(f_path, "rb") as f_rb:
                f_magic_num = f_rb.read(magic_num_len)
                if f_magic_num == magic_num:
                    f_seq = int.from_bytes(f_rb.read(4), "big")
                    file_map[f_seq] = f_path
                else:
                    continue
        return file_map


def clear_cache():
    directory_path = config.cache_dir
    try:
        # 确保目录存在
        if os.path.exists(directory_path):
            # 遍历目录中的文件和子目录
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 删除文件
                    os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    # 删除子目录
                    shutil.rmtree(dir_path)
    except Exception as e:
        print(f"清空目录出错：{str(e)}")


if __name__ == '__main__':
    # clear_cache()
    # backup = FilePack()
    # backup.package(backup.fetch_file()[0], config.cache_dir, use_split=True)
    # backup.unpack("cache/package.1.ddv", config.cache_dir + "unpack/")
    encode = "dddd".encode("utf-8")
    print(len(encode))
    print(len(gzip.compress(encode)))
