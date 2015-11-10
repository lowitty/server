#encoding=utf-8
'''
Created on 2015年11月9日

@author: lowitty
'''
import logging
sbcPMlogger = logging.getLogger('server.SBCPM')

import threading, time
from datetime import datetime, timedelta
from threading import Lock
lock = Lock()

class SbcPMHolder():
    def __init__(self):
        self.pmcounters = {}
        self.pmcounters["round"] = 0
        mapCounters = {}
        mapCounters[0] = [0, 0, 0, 0, 0, 0]
        mapCounters[1] = [0, 0, 0, 0, 0, 0]
        mapCounters[2] = [0, 0, 0, 0, 0, 0]
        mapCounters[3] = [0, 0, 0, 0, 0, 0]
        mapCounters[4] = [0, 0, 0, 0, 0, 0]
        mapCounters[5] = [0, 0, 0, 0, 0, 0]
        mapCounters[6] = [0, 0, 0, 0, 0, 0]
        mapCounters[7] = [0, 0, 0, 0, 0, 0]
        self.pmcounters["counter"] = mapCounters
    
    def getCounters(self):
        return self.pmcounters["counter"]
    
    def getPMCounters(self):
        return self.pmcounters
    
    def updatePMCounters(self, mapCounter, iRound = None):
        lock.acquire()
        self.pmcounters["counter"] = mapCounter
        if(iRound):
            self.pmcounters["round"] = iRound
        lock.release()
    
class SbcPMWriter(threading.Thread):
    def __init__(self, pmHolderInstance):
        threading.Thread.__init__(self)
        self.stopThread = False
        self.pmHoler = pmHolderInstance
        sbcPMlogger.info('The thread which simulate to increase the SBC counter started.')
        pass
    
    def run(self):
        while(not self.stopThread):
            tNow = datetime.now()
            min = tNow.minute
            sec = tNow.second
            if((min + 1) % 5 == 0 and sec < 35 and sec >= 30):
                sbcPMlogger.info('About 30 seconds that the minutes will be multiples of 5, will simulate to update the counters.')
                originalMap = self.pmHoler.getPMCounters()
                counters = {}
                r = originalMap['round']
                mapCounter = originalMap['counter']
                firEle = self.getFirstEle(r)
                
                for k, v in mapCounter.iteritems():
                    nk = k % 8
                    counters[k] = [(firEle + r + 1) * (nk + 1) * 1, (firEle + r + 1) * (nk + 1) * 2, (firEle + r + 1) * (nk + 1) * 3, (firEle + r + 1) * (nk + 1) * 4, (firEle + r + 1) * (nk + 1) * 5, (firEle + r + 1) * (nk + 1) * 6]
                    if(r + 1 > 11):
                        counters[k] = [0, 0, 0, 0, 0, 0]
                r += 1
                if(r > 11):
                    r = 0
                self.pmHoler.updatePMCounters(counters, r)
                deltaSec = 5 - (datetime.now().second % 5)
                time.sleep(deltaSec)
            else:
                time.sleep(5)
    
    def stop(self):
        self.stopThread = True
    
    def getFirstEle(self, num):
        sum = 0
        for i in range(0, num + 1):
            sum += i
        return sum