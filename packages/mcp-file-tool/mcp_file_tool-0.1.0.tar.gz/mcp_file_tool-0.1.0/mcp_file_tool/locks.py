import os
import time
from typing import Iterator

from .logging_conf import get_logger

logger = get_logger("locks")


class FileLock:
    """简单基于fcntl的文件锁（POSIX）。

    在目标文件旁创建`.lock`文件并对其加排他锁，避免并发写导致数据错乱。
    """

    def __init__(self, target_path: str, timeout_sec: int = 10) -> None:
        """初始化锁对象。

        参数:
        - target_path: 目标文件路径
        - timeout_sec: 获取锁的超时时间（秒）
        """

        self.target_path = target_path
        self.timeout_sec = timeout_sec
        base = os.path.basename(target_path)
        dirn = os.path.dirname(target_path) or "."
        self.lock_path = os.path.join(dirn, f".{base}.lock")
        self._fd = None

    def __enter__(self):
        """进入上下文，尝试获取锁。"""

        import fcntl

        os.makedirs(os.path.dirname(self.lock_path) or ".", exist_ok=True)
        self._fd = open(self.lock_path, "a+")
        start = time.time()
        while True:
            try:
                fcntl.flock(self._fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                logger.info("lock_acquired", extra={"lock": self.lock_path})
                break
            except BlockingIOError:
                if time.time() - start > self.timeout_sec:
                    logger.error("lock_timeout", extra={"lock": self.lock_path, "timeout_sec": self.timeout_sec})
                    raise TimeoutError(f"Acquire lock timeout: {self.lock_path}")
                time.sleep(0.05)
        return self

    def __exit__(self, exc_type, exc, tb):
        """退出上下文，释放锁。"""

        import fcntl

        try:
            if self._fd:
                fcntl.flock(self._fd.fileno(), fcntl.LOCK_UN)
                self._fd.close()
                logger.info("lock_released", extra={"lock": self.lock_path})
        finally:
            self._fd = None


def file_lock(target_path: str, timeout_sec: int = 10) -> FileLock:
    """创建文件锁上下文管理器。"""

    return FileLock(target_path, timeout_sec)