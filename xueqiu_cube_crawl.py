#!/usr/bin/env python2
# vim: set fileencoding=utf8

from Queue import Queue
from threading import Thread, Lock
import traceback
import os,signal,sys
import pymongo
import requests

url_template = 'http://xueqiu.com/cubes/list.json?user_id=%d&count=20'

client = pymongo.MongoClient()
db = client.xueqiudb
users = db.users
cubes = db.cubes


d_lock = Lock()

THREAD_POOL_SIZE = 5

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ThreadPool implementation
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ThreadPool(object):
    def __init__(self, size):
        self.size = size
        self.tasks = Queue(size)
        for i in range(size):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func,args,kargs))

    def wait_completion(self):
        self.tasks.join()

class Worker(Thread):
    def __init__(self, taskQueue):
        Thread.__init__(self)
        self.tasks = taskQueue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func ,args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except:
                print traceback.format_exc()

            finally:
                self.tasks.task_done()

class Terminate_Watcher:
    """this class solves two problems with multithreaded
    programs in Python, (1) a signal might be delivered
    to any thread (which is just a malfeature) and (2) if
    the thread that gets the signal is waiting, the signal
    is ignored (which is a bug).

    The watcher is a concurrent process (not thread) that
    waits for a signal and the process that contains the
    threads.

    I have only tested this on Linux.  I would expect it to
    work on the Macintosh and not work on Windows.

    The Watcher should be instantiated before the threads were
    created. It would kill threads when Ctrl-C was pressed.

    """

    def __init__(self):
        """ Creates a child thread, which returns.  The parent
            thread waits for a KeyboardInterrupt and then kills
            the child thread.
        """
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError: pass


headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml; " \
        "q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding":"text/html",
    "Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
    "Content-Type":"text/html; charset=utf-8",
    "Referer":"http://xueqiu.com/",
    "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 "\
        "(KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36"
}

cookies = {
    'xq_a_token':'JxDkzB0RJmf8aSDaHul92x',
    'xq_r_token':'69oXi8d7F1GWLWqFPFyBKP',
    '__utma':'1.1271487583.1422842143.1422842143.1422842595.2',
    '__utmc':'1',
    '__utmz':'__utmz=1.1422842595.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic|utmctr=雪球 api',
    'Hm_lvt_1db88642e346389874251b5a1eded6e3':'1422766155,1422842595,1422842617',
    'Hm_lpvt_1db88642e346389874251b5a1eded6e3':'1422845131'
}

def fetcher(uid):
    url = url_template % uid
    r = requests.get(url, headers=headers, cookies=cookies)
    if r.status_code == requests.codes.ok:
        print 'got cubes of user: %d\n' % uid
        j_result = r.json()
        for cube in j_result['list']:
            cubes.insert(cube)
    else:
        print 'status_code: %d' % r.status_code
        print 'headers: %s' % r.headers

def get_all_uids():
    print 'Start to get all uids\n'
    uids = []
    for user in users.find():
        uids.append(user['id'])

    print 'Finished getting all uids\n'
    return uids

def main():
    Terminate_Watcher()
    pool = ThreadPool(THREAD_POOL_SIZE)
    for uid in get_all_uids():
        pool.add_task(fetcher, uid)
    pool.wait_completion()
    client.close()

if __name__ == '__main__':
    main()
