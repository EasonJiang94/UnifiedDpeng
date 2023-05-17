import pyinotify

def dpeng_pyinotify(watch_dir, qin, qout):
    print(f"[{datetime.now(global_tz)}]the pid of [dpeng_pyinotify] is {os.getpid()}")

    # watch manager
    wm = pyinotify.WatchManager()
    pyinotify_flags = pyinotify.IN_MOVED_TO
    wm.add_watch(watch_dir, pyinotify_flags, rec=False)

    print('[Pyinotify] Watching dir : {}'.format(watch_dir))

    eh = MyEventHandler()
    eh.set_que_info(qin, qout)

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    print("[Pyinotify] Waiting for ljobs ...")
    notifier.loop()

class MyEventHandler(pyinotify.ProcessEvent):
    def set_que_info(self, qin, qout):
        self.qin = qin
        self.qout = qout
        self.sn = Value('d', 0)
    def process_IN_MOVED_TO(self, event):
        # print("[Pyinotify] Found file:", event.pathname)
        ljob_path = event.pathname
        print(f"[{datetime.now(global_tz)}][pyinotify] orig : ljob_path = {ljob_path}")
        if ljob_path.endswith('.ljob'):
            # print("[Pyinotify] qsize : {} get job {}".format(self.qin.qsize(), ljob_path))
            with self.sn.get_lock():
                print(f"[{datetime.now(global_tz)}][pyinotify]ljob_path = {ljob_path}")
                print(f"[{datetime.now(global_tz)}][pyinotify] qin.qsize() = {self.qin.qsize()}")

                self.qin.put((self.sn.value, ljob_path))
                self.sn.value += 1


if __name__ == "__main__":

    pass