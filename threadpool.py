#!/usr/bin/python
#-*-coding:utf-8 -*-

import log
import time
import threading
import Queue


class WorkThread(threading.Thread):
    
    tasks = None

    def __init__(self, tasks):
        threading.Thread.__init__(self)
        self.tasks = tasks
    
    def run(self):
        while True:
            try:
                task =  self.tasks.get(False)
            except Exception, e:
                break
            try:
                task.run()
            except Exception, e:
                log.warning('Exception in task: ' + str(e))

class ThreadPool:
    
    tasks = None
    threads = None
    threadNumber = None

    def __init__(self, threadNumber):
        self.threadNumber = threadNumber
        self.tasks = Queue.Queue()
        self.threads = []

    def start(self, tasks):
        for task in tasks:
            self.tasks.put(task, False)

        threads = []
        for i in range(0, self.threadNumber):
            thread = WorkThread(self.tasks)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
            

