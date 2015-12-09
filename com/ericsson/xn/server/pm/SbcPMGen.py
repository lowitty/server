#encoding=utf-8
'''
Created on 2015年11月9日

@author: lowitty
'''
import logging, os, random, sys
sbcPMlogger = logging.getLogger('server.SBCPM')
from com.ericsson.xn.server.parser.SbcParser import SbcNodeInfo
from xml.etree import ElementTree as ET

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
        if(iRound is not None):
            self.pmcounters["round"] = iRound
        lock.release()
    
class SbcPMWriter(threading.Thread):
    def __init__(self, pmHolderInstance):
        threading.Thread.__init__(self)
        self.stopThread = False
        filePath = os.path.dirname(os.path.abspath(__file__))
        #/com/ericsson/xn/server/pm
        sep = os.path.sep
        self.sep = sep
        packagePath = sep + 'com' + sep + 'ericsson' + sep + 'xn' + sep + 'server' + sep + 'pm'
        self.parPath = filePath.split(packagePath)[0]
        
        self.pmHoler = pmHolderInstance
        sbcPMlogger.info('SBCPMGEN started.')
        self.updateSBCCounters()
        pass
    
    def run(self):
        while(not self.stopThread):
            tNow = datetime.now()
            min = tNow.minute
            sec = tNow.second
            if((min + 1) % 5 == 0 and sec < 35 and sec >= 30):
            #if(True):
                sbcPMlogger.info('About 30 seconds that the minutes will be multiples of 5, will simulate to update the counters, also random the next period logs.')
                try:
                    f = open(self.parPath + self.sep + 'config' + self.sep + 'sbc' + self.sep + 'sbc_log.x', 'r')
                    lines = f.readlines()
                    f.close()
                    lenth = len(lines)
                    intsRandom = sorted(random.sample(range(0, lenth), random.randint(0, lenth)))
                    sbcPMlogger.info(str(intsRandom))
                    newLines = []
                    tStart = tNow + timedelta(seconds = -270)
                    for ir in intsRandom:
                        tStampt = tStart + timedelta(seconds = 24 * ir)
                        newLines.append('[' + tStampt.strftime('%Y-%m-%d %H:%M:%S') + '.' + str(tStampt.microsecond % 1000) + '] ' + lines[ir].strip() + '\n')
                    nowFile = self.parPath + self.sep + 'config' + self.sep + 'sbc' + self.sep + 'sbc_log.now'
                    lock.acquire()
                    open(nowFile, 'w').close()
                    f = open(nowFile, 'w')
                    f.writelines(newLines)
                    f.flush()
                    f.close()
                    lock.release()
                    nowTime = datetime.now()
                    t1 = nowTime + timedelta(minutes = 1)
                    t2 = nowTime + timedelta(minutes = 6)
                    msg = t1.strftime('%Y-%m-%d %H:%M') + ' to ' + t2.strftime('%H:%M')
                    sbcPMlogger.warn(msg + ', logs are: ' + '||'.join([k.strip() for k in newLines]))
                    self.updateSBCCounters()
                except Exception as e:
                    sbcPMlogger.error('ERROR: ' + str(e))
                
                '''originalMap = self.pmHoler.getPMCounters()
                sbcPMlogger.info('Dic of counters: ' + str(originalMap))
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
                
                nowTime = datetime.now()
                t1 = nowTime + timedelta(minutes = 1)
                t2 = nowTime + timedelta(minutes = 6)
                msg = t1.strftime('%Y-%m-%d %H:%M') + ' to ' + t2.strftime('%H:%M')
                
                sbcPMlogger.info(msg + ', PM counters are: ' + str(self.pmHoler.getCounters()))'''
                
                deltaSec = 5 - (datetime.now().second % 5)
                time.sleep(deltaSec)
            else:
                time.sleep(5)
    def updateSBCCounters(self):
        xmlPath = self.parPath + self.sep + 'config' + self.sep + 'sbc' + self.sep + 'sbc_node.xml'
        #insNode = SbcNodeInfo(xmlPath)
        #node = insNode.getNodeInfoMap()
        et = ET.parse(xmlPath)
        tNow = datetime.now()
        r = (tNow + timedelta(seconds = 30)).minute / 5 - 1
        firEle = self.getFirstEle(r)
        cMap = {}
        channels = et.findall('./channel')
        for channel in channels:
            k = int(channel.find('./channelId').text)
            nk = k % 8
            cMap[k] = []
            c1 = str((firEle + r + 1) * (nk + 1) * 1)
            c2 = str((firEle + r + 1) * (nk + 1) * 2)
            c3 = str((firEle + r + 1) * (nk + 1) * 3)
            c4 = str((firEle + r + 1) * (nk + 1) * 4)
            c5 = str((firEle + r + 1) * (nk + 1) * 5)
            c6 = str((firEle + r + 1) * (nk + 1) * 6)
            channel.find('./c1').text = c1
            channel.find('./c2').text = c2
            channel.find('./c3').text = c3
            channel.find('./c4').text = c4
            channel.find('./c5').text = c5
            channel.find('./c6').text = c6
            cMap[k].append(c1)
            cMap[k].append(c2)
            cMap[k].append(c3)
            cMap[k].append(c4)
            cMap[k].append(c5)
            cMap[k].append(c6)
        versionTuple = sys.version_info[:2]
        version = '.'.join(repr(v) for v in versionTuple)
        lock.acquire()
        if('2.7' == version):
            et.write(xmlPath, encoding='utf-8', xml_declaration=True, method='xml')
        else:
            et.write(xmlPath, encoding='utf-8')
        lock.release()
        
        t1 = tNow + timedelta(minutes = 1)
        t2 = tNow + timedelta(minutes = 6)
        msg = t1.strftime('%Y-%m-%d %H:%M') + ' to ' + t2.strftime('%H:%M')
        sbcPMlogger.info(msg + ', Counters: ' + str(cMap))
    
    def stop(self):
        self.stopThread = True
    
    def getFirstEle(self, num):
        sum = 0
        for i in range(0, num + 1):
            sum += i
        return sum