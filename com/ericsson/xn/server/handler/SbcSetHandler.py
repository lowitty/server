#encoding=utf-8
'''
Created on Dec 8, 2015

@author: lowitty
'''
import logging, sys
logSbcHander = logging.getLogger('server.SbcHandler')
from xml.etree import ElementTree
from threading import Lock
lock = Lock()
versionTuple = sys.version_info[:2]
version = '.'.join(repr(v) for v in versionTuple)
logSbcHander.info('Python version is: ' + str(version)) 

class SbcSetOperations():
    
    def __init__(self, line, xmlPath):
        self.returnStr = ''
        self.avaiableSetCMDs = ['tcp_channel', 'li_activate', 'li_deactivate', 'pm_update']
        self.xmlPath = xmlPath
        self.line = xmlPath
        self.er = None
        self.performAction()
    
    def performAction(self):
        try:
            self.er = ElementTree.parse(self.xmlPath)
        except Exception as e:
            logSbcHander.error('Read the XML as DOM failed, Error Info: ' + str(e))
        if(self.checkCmd()):
            if(self.line.startwith('tcp_channel add')):
                self.addChannel()
            elif(self.line.startwith('tcp_channel remove')):
                self.removeChannel()
            elif(self.line.startwith('li_activate')):
                self.liActive()
            elif(self.line.startwith('li_deactivate')):
                self.liDeactive()
            elif(self.line.startwith('pm_update')):
                self.pmUpdate()
            else:
                self.returnStr = 'OPERATION FAILED DUE TO Set Command not Supported'
                logSbcHander.error(self.returnStr)
        else:
            self.returnStr = 'OPERATION FAILED DUE TO Set Command not Supported'
            logSbcHander.error(self.returnStr)
            
    def checkCmd(self):
        if(self.line.split()[0].strip() not in self.avaiableSetCMDs):
            return False
        return True
    
    def addChannel(self):
        channel = ElementTree.Element('channel')
        licId = ElementTree.SubElement(channel, 'licId', 'LIC')
    
    def removeChannel(self):
        pass
    
    def liActive(self):
        pass
    
    def liDeactive(self):
        pass
    
    def pmUpdate(self):
        pass
    
    def writeBack2XmlFile(self):
        global version, lock
        lock.acquire()
        if('2.7' == version):
            self.er.write(self.xmlPath, encoding='utf-8', xml_declaration=True, method='xml')
        else:
            self.er.write(self.xmlPath, encoding='utf-8')
        lock.release()
            
    def getActionResult(self):
        return self.returnStr

