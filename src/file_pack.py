import hashlib
import os
import pickle

from tqdm import tqdm

import config
from bytes_chain.bytes_abstract_processor import BytesAbstractProcessor
from bytes_chain.encrypt_processor import EncryptProcessor
from bytes_chain.gzip_processor import GzipProcessor
from bytes_chain.plain_processor import PlainProcessor
from ddv.ddv_file_info import DdvFileInfo, FileType
from ddv.ddv_file_meta import DdvFileMeta
from log_util import log

MAGIC_NUM = "ddvudo".upper().encode("utf-8")
magic_num_len = len(MAGIC_NUM)
MAGIC_NUM_END = 4294967295


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
                if not os.path.exists(s_file):
                    log.error("文件不存在，跳过" + s_file, exc_info=True, stack_info=True)
                    err_list.append(s_file)
                    continue
                isdir = os.path.isdir(s_file)
                if isdir:
                    for root, dirs, files in os.walk(s_file, True, None, False):
                        if len(os.listdir(root)) == 0:
                            log.info(root)
                            file_list.append(os.path.normpath(root))
                        for sub_file in files:
                            path = os.path.join(root, sub_file)
                            excluded = False

                            # 如果是排除的文件则跳过
                            for ex in exclude_list:
                                if path.startswith(ex) or ex == sub_file or os.path.islink(path):
                                    excluded = True
                                    ignore_list.append(sub_file)
                                    break
                            if excluded:
                                continue
                            file_list.append(path)
                            log.debug("处理文件" + path)
                else:
                    file_list.append(s_file)
                    log.debug("处理文件"+s_file)
        except Exception as e:
            log.error(e, exc_info=True, stack_info=True)
        return [file_list, ignore_list, err_list]

    @staticmethod
    def package(files: list, output_dir: str,
                bytes_processor: BytesAbstractProcessor = PlainProcessor(None),
                use_split: bool = True,
                split_size: int = 1024 * 1024 * 1024,
                buffer_size=1024 * 1024 * 100) -> list:
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
            ddv.write(MAGIC_NUM)
            # 写入当前分卷序号
            ddv.write(current_split.to_bytes(4, "big"))
            for f in files:
                if config.progress:
                    bar = tqdm(total=f.size, colour="green", unit='byte')
                file_index = files.index(f)
                file_seq = file_index.to_bytes(4, "big")
                # 写入当前文件序号
                ddv.write(file_seq)
                curr_file_size = 0
                # 处理目录
                if f.type == FileType.DIR:
                    continue
                # 处理文件
                with open(f.name, "rb") as file:
                    sha224 = hashlib.sha224()
                    while True:
                        curr_buff_size = buffer_size
                        if use_split:
                            curr_buff_size = buffer_size if (ddv.tell() + buffer_size) < split_size else (
                                    split_size - ddv.tell())
                        read = file.read(curr_buff_size)
                        if not read:
                            f.packed_size = curr_file_size
                            f.sha224 = sha224.hexdigest()
                            log.info(
                                f"文件大小记录 文件名：{f.name} 文件类型：{f.type} 文件大小：{f.size} 打包后大小：{f.packed_size}")
                            break
                        sha224.update(read)
                        if config.progress:
                            bar.update(len(read))
                        read = bytes_processor.pack(read)
                        part_size = len(read)
                        curr_file_size += part_size
                        ddv.write(part_size.to_bytes(4, "big"))
                        ddv.write(read)
                        if ddv.tell() >= split_size and use_split:
                            current_split += 1
                            current_tar_name = os.path.join(output_dir, f"package.{str(current_split)}.ddv")
                            ddv.flush()
                            ddv.close()
                            ddv = open(current_tar_name, "wb")
                            # 写入魔数
                            ddv.write(MAGIC_NUM)
                            # 写入当前分卷序号
                            ddv.write(current_split.to_bytes(4, "big"))
            # 写入文件列表整体信息
            file_meta = DdvFileMeta(files, bytes_processor)
            for f in files:
                file_meta.original_total_size += f.size
                file_meta.packaged_total_size += f.packed_size
            log.info(f"源文件总计大小：{file_meta.original_total_size},"
                     f"处理后总计大小：{file_meta.packaged_total_size},"
                     f"比例：{file_meta.packaged_total_size / file_meta.original_total_size}")
            files_info_dumps = pickle.dumps(file_meta)
            file_meta_len = len(files_info_dumps)
            file_meta_len_to_bytes = file_meta_len.to_bytes(4, "big")
            ddv.write(MAGIC_NUM_END.to_bytes(4, "big"))
            ddv.write(files_info_dumps)
            ddv.write(file_meta_len_to_bytes)
            ddv.write(MAGIC_NUM_END.to_bytes(4, "big"))
        return res

    def unpack(self, input_file: str, output_dir):
        with open(input_file, "rb+") as ddv:
            curr_magic_num = ddv.read(magic_num_len)
            if curr_magic_num != MAGIC_NUM:
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
            if MAGIC_NUM_END != curr_magic_end:
                raise Exception(f"文件格式不匹配")
            # 读取文件列表大小
            final_split_ab.seek(final_split_size - 8)
            file_list_size = int.from_bytes(final_split_ab.read(4), "big")
            # 读取文件列表
            final_split_ab.seek(final_split_size - 8 - file_list_size)
            file_list = pickle.loads(final_split_ab.read(file_list_size))
            bar = tqdm(total=file_list.packaged_total_size, colour="green", unit='byte')
            if type(file_list) != DdvFileMeta:
                raise Exception("文件信息已损坏")
            # 读取压缩时使用的分块处理器
            bytes_processor = file_list.bytes_processor
        try:
            for _ in sorted(all_split):
                curr_file = all_split[_]
                with open(curr_file, "rb") as ddv:
                    # 校验魔数
                    curr_magic_num = ddv.read(magic_num_len)
                    if curr_magic_num != MAGIC_NUM:
                        raise Exception(f"文件格式不匹配{curr_magic_num}")
                    # 读取分卷序号
                    split_seq = int.from_bytes(ddv.read(4), "big")

                    while True:
                        if curr_file_readied_size == curr_file_size:
                            sha224 = hashlib.sha224()
                            curr_file_readied_size = 0
                            # 读取文件序号
                            f_seq = int.from_bytes(ddv.read(4), "big")
                            if f_seq == MAGIC_NUM_END:
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
                            # 上一轮循环后，当前文件刚好处理完毕
                            if curr_file_readied_size == curr_file_size:
                                self.handle_file_read_end(curr_file_info, curr_output_file, sha224)
                                break
                            # 读取下一个分块大小
                            buffer_size = int.from_bytes(ddv.read(4), "big")
                            if buffer_size == MAGIC_NUM_END:
                                self.handle_file_read_end(curr_file_info, curr_output_file, sha224)
                                split_break = True
                                break
                            if curr_file_readied_size + buffer_size > curr_file_size:
                                curr_buffer_size = curr_file_size - curr_file_readied_size
                            else:
                                curr_buffer_size = buffer_size
                            read = ddv.read(curr_buffer_size)
                            bar.update(len(read))
                            if not read:
                                if curr_file_readied_size == curr_file_size:
                                    self.handle_file_read_end(curr_file_info, curr_output_file, sha224)
                                else:
                                    split_break = True
                                break
                            else:
                                curr_file_readied_size += len(read)
                                read = bytes_processor.unpack(read)
                                sha224.update(read)
                                curr_output_file.write(read)
                        if split_break:
                            break
        finally:
            if curr_output_file is not None and not curr_output_file.closed:
                curr_output_file.flush()
                curr_output_file.close()

    @staticmethod
    def handle_file_read_end(curr_file_info, curr_output_file, sha224):
        if not curr_output_file.closed:
            curr_output_file.flush()
            curr_output_file.close()
        if curr_file_info.type == FileType.DIR:
            return
        curr_sha224 = sha224.hexdigest()
        log.info(f"校验sha224 当前值：{curr_sha224}，记录值：{curr_file_info.sha224}")
        if curr_sha224 != curr_file_info.sha224:
            log.error(f"{curr_file_info.name} 校验失败")

    @staticmethod
    def find_splits(input_file):
        file_map = {}
        _dir, _ = os.path.split(input_file)
        for f in os.listdir(_dir):
            f_path = os.path.normpath(_dir + "/" + f)
            with open(f_path, "rb") as f_rb:
                f_magic_num = f_rb.read(magic_num_len)
                if f_magic_num == MAGIC_NUM:
                    f_seq = int.from_bytes(f_rb.read(4), "big")
                    file_map[f_seq] = f_path
                else:
                    continue
        return file_map

    def info(self, input_file):
        file_map = {}
        _dir, _ = os.path.split(input_file)
        for f in os.listdir(_dir):
            f_path = os.path.normpath(_dir + "/" + f)
            with open(f_path, "rb") as f_rb:
                f_magic_num = f_rb.read(magic_num_len)
                if f_magic_num == MAGIC_NUM:
                    f_seq = int.from_bytes(f_rb.read(4), "big")
                    file_map[f_seq] = f_path
                else:
                    continue
        with open(input_file, "rb+") as ddv:
            curr_magic_num = ddv.read(magic_num_len)
            if curr_magic_num != MAGIC_NUM:
                raise Exception(f"文件格式不匹配{curr_magic_num}")
            all_split = self.find_splits(input_file)
            log.info(f"分卷信息: {all_split}")
        final_split = all_split[max(sorted(all_split))]
        with open(final_split, "ab+") as final_split_ab:
            final_split_size = os.path.getsize(final_split)
            # 校验文件结束魔数
            final_split_ab.seek(final_split_size - 4)
            curr_magic_end = int.from_bytes(final_split_ab.read(4), "big")
            if MAGIC_NUM_END != curr_magic_end:
                raise Exception(f"文件格式不匹配")
            # 读取文件列表大小
            final_split_ab.seek(final_split_size - 8)
            file_list_size = int.from_bytes(final_split_ab.read(4), "big")
            # 读取文件列表
            final_split_ab.seek(final_split_size - 8 - file_list_size)
            file_list = pickle.loads(final_split_ab.read(file_list_size))
            if type(file_list) != DdvFileMeta:
                raise Exception("文件信息已损坏")
            # 读取压缩时使用的分块处理器
            bytes_processor = file_list.bytes_processor
            log.debug(f"加工序列：{bytes_processor}")
            log.info(f"文件信息：")
            for f in file_list.files:
                log.info(f"文件名：{f.name}，文件类型：{f.type}，源文件大小：{f.size}，打包后大小：{f.packed_size}")
            log.info(f"文件总计原始大小：{file_list.original_total_size}")
            log.info(f"文件总计打包后大小：{file_list.packaged_total_size}")
            log.info(f"打包比例：{file_list.packaged_total_size / file_list.original_total_size}")

    def start_backup(self, is_enc: bool, is_zip: bool, output_dir: str) -> list:
        file_list, ignore_list, err_list = self.fetch_file()
        log.info(f"找到{len(file_list)}个文件，忽略{len(ignore_list)}个文件，{len(err_list)}个文件出错")
        if len(ignore_list) > 0:
            log.info(f"忽略的文件：{ignore_list}")
        if len(err_list) > 0:
            log.info(f"出错的文件：{err_list}")
        if len(file_list) > 0:
            log.info(f"找到的文件：{file_list}")
            processor = None
            if is_enc:
                processor = EncryptProcessor(processor)
            if is_zip:
                processor = GzipProcessor(processor)
            pack_file_list = self.package(file_list, output_dir, processor)
            log.info(f"打包后的文件:{pack_file_list}")
            return pack_file_list
        else:
            raise Exception("未找到任何文件，请检查配置！")
        pass
