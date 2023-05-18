import os
import sys
import pyinotify
from loguru import logger
from multiprocessing import Queue
from threading import Thread
sys.path.append("..")
from utils.job_classes import InputJob

class LjobReceiver(Thread):
    def __init__(self, ljob_dir, qout, name="ljob_receiver"):
        super().__init__(daemon=True, name=name)
        self.ljob_dir = ljob_dir
        self.qout = qout
        self._sn = 0
    def process_input_job(self, ljob_path):
        if LjobReceiver.check_valid_ljob(ljob_path):
            input_job = InputJob(ljob_path=ljob_path, \
                                image=None, \
                                sn=self._sn)
            self.qout.put(input_job)
            self._sn += 1
            logger.debug(f"ljob_path = {ljob_path}")
            logger.debug(f"qin.qsize() = {self.qout.qsize()}")
    def run(self):
        logger.info(f"The Pid of {self.name} is {os.getpid()}")
        watch_manager = pyinotify.WatchManager()
        pyinotify_flags = pyinotify.IN_MOVED_TO
        watch_manager.add_watch(self.ljob_dir, pyinotify_flags, rec=False)
        logger.info(f"Watching dir : {self.ljob_dir}")
        event_handler = LjobEventHandler(ljob_receiver)
        notifier = pyinotify.Notifier(watch_manager, event_handler)
        notifier.loop()

    @classmethod
    def check_valid_ljob(cls, ljob_path):
        if not ljob_path.endswith('.ljob'):
            logger.error(f"got a not-ljob file : {ljob_path}")
            assert ljob_path.endswith('.ljob'), "ljob_path should be endswith '.ljob'"
            return False
        return True




class LjobEventHandler(pyinotify.ProcessEvent):
    def __init__(self, ljob_receiver):
        super().__init__()
        self.ljob_receiver = ljob_receiver
    def process_IN_MOVED_TO(self, event):
        ljob_path = event.pathname
        ljob_receiver.process_input_job(ljob_path)


if __name__ == "__main__":
    import sys
    sys.path.append("../../test")
    from ljob_maker import shoot_ljob
    logger.info("TESTING LjobReceiver")

    ljob_dir = "/mnt/ramdisk/dpeng/human/in"
    qout = Queue(maxsize=10)
    ljob_receiver = LjobReceiver(ljob_dir, qout)
    ljob_receiver.start()
    shoot_ljob(img_path="../../data/Kintetsu1.jpg", num=1)
    ljob_receiver.join()
    