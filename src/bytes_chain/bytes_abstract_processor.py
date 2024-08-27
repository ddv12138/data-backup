import abc
from abc import ABC


class BytesAbstractProcessor(ABC):
    def __init__(self, next_processor) -> None:
        super().__init__()
        self.next_processor = next_processor

    @abc.abstractmethod
    def __pack_process__(self, bytes_data: bytes) -> bytes:
        pass

    @abc.abstractmethod
    def __unpack_process__(self, bytes_data: bytes) -> bytes:
        pass

    def pack(self, bytes_data: bytes) -> bytes:
        result = self.__pack_process__(bytes_data)
        if self.next_processor:
            return self.next_processor.pack(result)
        else:
            return result

    def unpack(self, bytes_data: bytes) -> bytes:
        # if self.next_processor:
        #     return self.__unpack_process__(self.next_processor.unpack(bytes_data))
        # else:
        #     return self.__unpack_process__(bytes_data)
        result = self.__unpack_process__(bytes_data)
        if self.next_processor:
            return self.next_processor.unpack(result)
        else:
            return result

    def __str__(self) -> str:
        proc = self
        rep_str = ""
        while proc:
            rep_str += proc.__class__.__name__
            if proc.next_processor:
                rep_str += "--->"
            proc = proc.next_processor
        return rep_str
