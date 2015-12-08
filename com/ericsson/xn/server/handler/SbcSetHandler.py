#encoding=utf-8
'''
Created on Dec 8, 2015

@author: lowitty
'''
import logging, sys, os, re
from tmp.test import channel
logSbcHander = logging.getLogger('server.SbcHandler')
from xml.etree import ElementTree
from threading import Lock
from com.ericsson.xn.server.parser.SbcParser import SbcNodeInfo
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
        pkg_path = 'com' + os.path.sep + 'ericsson' + os.path.sep + 'xn' + os.path.sep + 'server' + os.path.sep + 'handler'
        self.pardir = os.path.dirname(os.path.abspath(__file__)).split(pkg_path)[0]
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
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(os.path.normpath(self.pardir + os.path.sep + 'config' + os.path.sep + 'sbc' + os.path.sep + 'sbc_node.xml'))
        node = nodeInfoInstance.getNodeInfoMap()
        
        if(14 != len(lineSplit)):
            self.returnStr = 'OPERATION FAILED DUE TO the add channel command\'s length is not correct.'
            logSbcHander.error(self.returnStr)
        else:
            if(lineSplit[2] != node['nodeParas']['froID']):
                self.returnStr = 'OPERATION FAILED DUE TO froID mismatch.'
                logSbcHander.error(self.returnStr)
            else:
                isChannelIDValid = True
                try:
                    newChannelID = int(lineSplit[3])
                except Exception as e:
                    isChannelIDValid = False
                if(newChannelID < 0 or newChannelID > 63):
                    isChannelIDValid = False
                
                if(node['channels'].has_key(lineSplit[3]) or (not isChannelIDValid)):
                    self.returnStr = 'OPERATION FAILED DUE TO the given channel ID already exist or extend the scope of [0, 63].'
                    logSbcHander.error(self.returnStr)
                else:
                    for index in range(4, 14, 2):
                        cmds = {}
                        cmds[lineSplit[index].lower().strip()[1:]] = lineSplit[index + 1].strip()
                    flag = 0
                    if(cmds.has_key('licid') and cmds.has_key('localip') and cmds.has_key('localtcpport') and cmds.has_key('remoteip') and cmds.has_key('remotetcpport')):
                        pat = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
                        prog = re.compile(pat)
                        res0 = prog.match(cmds['localip'])
                        res1 = prog.match(cmds['remoteip'])
                        if(res0 and res1):
                            try:
                                lPort = int(cmds['localtcpport'])
                                rPort = int(cmds['remotetcpport'])
                            except Exception as e:
                                flag = 3 #Local port or Remote port is not number.
                                self.returnStr = 'OPERATION FAILED DUE TO Local port or Remote port is not number.'
                                logSbcHander.error(self.returnStr)
                            if(-1 < lPort < 65536 and -1 < rPort < 65536):
                                #Can check if IP already in other channels, will not check in this version.
                                try:
                                    newChannel = ElementTree.Element('channel')
                                    ElementTree.SubElement(newChannel, 'channelId').text = lineSplit[3]
                                    ElementTree.SubElement(newChannel, 'licId').text = cmds['licid']
                                    ElementTree.SubElement(newChannel, 'localIp').text = cmds['localip']
                                    ElementTree.SubElement(newChannel, 'localTcpPort').text = cmds['localtcpport']
                                    ElementTree.SubElement(newChannel, 'remoteIp').text = cmds['remoteip']
                                    ElementTree.SubElement(newChannel, 'remoteTcpPort').text = cmds['remotetcpport']
                                    self.er.getroot().append(newChannel)
                                    self.writeBack2XmlFile()
                                except Exception as e:
                                    self.returnStr = 'OPERATION FAILED DUE TO set to xml file failed, ERROR: ' + str(e)
                                    logSbcHander.error(self.returnStr)
                                self.returnStr = 'OPERATION SUCCESSFUL - VPP: 0\nOPERATION SUCCESSFUL - VPP: 1'
                                logSbcHander.error(self.returnStr)
                            else:
                                flag = 4 #Local port or Remote port is invalid number.
                                self.returnStr = 'OPERATION FAILED DUE TO Local port or Remote port is invalid number.'
                                logSbcHander.error(self.returnStr)
                        else:
                            flag = 2 #Local IP or Remote IP's format is wrong.
                            self.returnStr = 'OPERATION FAILED DUE TO Local IP or Remote IP\'s format is wrong.'
                            logSbcHander.error(self.returnStr)
                    else:
                        flag = 1 #command format is wrong.
                        self.returnStr = 'OPERATION FAILED DUE TO command format is wrong.'
                        logSbcHander.error(self.returnStr)
    
    def removeChannel(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(os.path.normpath(self.pardir + os.path.sep + 'config' + os.path.sep + 'sbc' + os.path.sep + 'sbc_node.xml'))
        node = nodeInfoInstance.getNodeInfoMap()
        if(4 != len(lineSplit)):
            self.returnStr = 'OPERATION FAILED DUE TO the add channel command\'s length is not correct.'
            logSbcHander.error(self.returnStr)
        else:
            if(lineSplit[2] != node['nodeParas']['froID']):
                self.returnStr = 'OPERATION FAILED DUE TO froID mismatch.'
                logSbcHander.error(self.returnStr)
            else:
                if(node['channels'].has_key(lineSplit[3])):
                    try:
                        channels = self.er.findall('./channel')
                        for channel in channels:
                            if(channel.find('./channelId').text == lineSplit[3]):
                                self.er.getroot().remove(channel)
                                break
                        self.writeBack2XmlFile()
                    except Exception as e:
                        self.returnStr = 'OPERATION FAILED DUE TO Write Back To XML File Failed, ERROR: ' + str(e)
                        logSbcHander.error(self.returnStr)
                else:
                    self.returnStr = 'OPERATION FAILED DUE TO Given Channel ID not exist.'
                    logSbcHander.error(self.returnStr)
    
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

