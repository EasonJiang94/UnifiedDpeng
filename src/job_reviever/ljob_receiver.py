import pyinotify
from multiprocessing import Queue
from loguru import logger
from threading import Thread
import os
import sys
sys.path.append("..")
from utils.job_classes import InputJob

class LjobReceiver(Thread):
    def __init__(self, ljob_dir, qout, name="ljob_receiver"):
        super().__init__(daemon=True, name=name)
        self.ljob_dir = ljob_dir
        self.qout = qout
    def run(self):
        logger.info(f"the pid is {os.getpid()}")
        wm = pyinotify.WatchManager()
        pyinotify_flags = pyinotify.IN_MOVED_TO
        wm.add_watch(self.ljob_dir, pyinotify_flags, rec=False)
        logger.info("Watching dir : {self.ljob_dir}")

        eh = LjobEventHandler(self.ljob_dir, self.qout)
        notifier = pyinotify.Notifier(wm, eh)
        notifier.loop()



class LjobEventHandler(pyinotify.ProcessEvent):
    def __init__(self, ljob_dir, qout):
        super().__init__()
        self.ljob_dir = ljob_dir
        self.qout = qout
        self.sn = 0
    def process_IN_MOVED_TO(self, event):
        ljob_path = event.pathname
        if not ljob_path.endswith('.ljob'):
            logger.error(f"got a not-ljob file : {ljob_path}")
            
        logger.debug(f"ljob_path = {ljob_path}")
        logger.debug(f"qin.qsize() = {self.qout.qsize()}")
        input_job = InputJob(ljob_path=ljob_path, \
                                image=None, \
                                sn=self.sn)
        self.qout.put(input_job)
        self.sn += 1


if __name__ == "__main__":
    import sys
    sys.path.append("../../test")
    from ljob_maker import shoot_ljob
    logger.info("TESTING LjobReceiver")

    ljob_dir = "/mnt/ramdisk/dpeng/human/in"
    qout = Queue(maxsize=10)
    ljob_receiver = LjobReceiver(ljob_dir, qout)
    ljob_receiver.start()
    shoot_ljob(img_path="../../data/Kintetsu1.jpg", num=10)
    ljob_receiver.join()
    