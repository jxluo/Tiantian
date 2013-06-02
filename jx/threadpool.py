#!/usr/bin/python
#-*-coding:utf-8 -*-

import log
import time
import threading
import Queue


class WorkThread(threading.Thread):
    
    tasks = None
    taskInterval = None # Time between two task in same thread.

    def __init__(self, tasks, taskInterval):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.taskInterval = taskInterval
    
    def run(self):
        firstRun = True
        while True:
            try:
                task =  self.tasks.get(False)
            except Exception, e:
                break

            if not firstRun and self.taskInterval:
                time.sleep(self.taskInterval)

            try:
                task.run()
            except Exception, e:
                log.warning('Exception in task: ' + str(e))
            firstRun = False

class ThreadPool:
    
    tasks = None
    threads = None
    threadNumber = None

    startInterval = None # Time interval between two thread start.
    taskInterval = None # Time between two task in same thread.

    def __init__(self, threadNumber):
        self.threadNumber = threadNumber
        self.tasks = Queue.Queue()
        self.threads = []

    def setStartInterval(self, interval):
        self.startInterval = interval

    def setTaskInterval(self, interval):
        self.taskInterval = interval

    def start(self, tasks):
        for task in tasks:
            self.tasks.put(task, False)

        threads = []
        for i in range(0, self.threadNumber):
            thread = WorkThread(self.tasks, self.taskInterval)
            threads.append(thread)
            thread.start()
            if self.startInterval:
                time.sleep(self.startInterval)

        for thread in threads:
            thread.join()
            

