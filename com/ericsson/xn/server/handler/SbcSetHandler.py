#encoding=utf-8
'''
Created on Dec 8, 2015

@author: lowitty
'''
import logging, sys, os, re
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
        self.returnStr = []
        self.avaiableSetCMDs = ['tcp_channel', 'li_activate', 'li_deactivate', 'pm_update', 'get_stat', 'get_config']
        self.xmlPath = xmlPath
        self.line = xmlPath
        self.er = None
        #pkg_path = 'com' + os.path.sep + 'ericsson' + os.path.sep + 'xn' + os.path.sep + 'server' + os.path.sep + 'handler'
        #self.pardir = os.path.dirname(os.path.abspath(__file__)).split(pkg_path)[0]
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
            elif(self.line.startwith('get_config')):
                self.getConfig()
            else:
                msg = 'OPERATION FAILED DUE TO COMMAND NOT SUPPORT.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
        else:
            msg = 'OPERATION FAILED DUE TO COMMAND NOT SUPPORT.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
            
    def checkCmd(self):
        if(self.line.split()[0].strip() not in self.avaiableSetCMDs):
            return False
        return True
    
    def addChannel(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        
        if(14 != len(lineSplit)):
            msg = 'OPERATION FAILED DUE TO COMMAND LENGTH IS WRONG.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            if(lineSplit[2] != node['nodeParas']['froID']):
                msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
            else:
                isChannelIDValid = True
                try:
                    newChannelID = int(lineSplit[3])
                except Exception as e:
                    isChannelIDValid = False
                if(newChannelID < 0 or newChannelID > 63):
                    isChannelIDValid = False
                
                if(node['channels'].has_key(lineSplit[3]) or (not isChannelIDValid)):
                    msg = 'OPERATION FAILED DUE TO CHANNEL ID EXIST OR NOT IN [0, 63].'
                    self.returnStr.append(msg)
                    logSbcHander.error(msg)
                else:
                    if('CONFIGURED' != node['nodeParas']['state']):
                        msg = 'OPERATION FAILED DUE TO IINTERFACE NOT UP.'
                        self.returnStr.append(msg)
                        logSbcHander.error(msg)
                    else:
                        for index in range(4, 14, 2):
                            cmds = {}
                            cmds[lineSplit[index].lower().strip()[1:]] = lineSplit[index + 1].strip()
                        
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
                                    #Local port or Remote port is not number.
                                    msg = 'OPERATION FAILED DUE TO PORT IS NOT NUMBER.'
                                    self.returnStr.append(msg)
                                    logSbcHander.error(msg)
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
                                        msg = ('OPERATION FAILED DUE TO set to xml file failed, ERROR: ' + str(e)).upper()
                                        self.returnStr.append(msg)
                                        logSbcHander.error(msg)
                                    self.returnStr.append('OPERATION SUCCESSFUL - VPP: 0')
                                    self.returnStr.append('OPERATION SUCCESSFUL - VPP: 1')
                                    logSbcHander.info('ADD CHANNEL SUCCESSFULLY.')
                                else:
                                    #Local port or Remote port is invalid number.
                                    msg = 'OPERATION FAILED DUE TO PORT IS INVALID NUMBER.'
                                    self.returnStr.append(msg)
                                    logSbcHander.error(msg)
                            else:
                                #Local IP or Remote IP's format is wrong.
                                msg = 'OPERATION FAILED DUE TO IP FORMAT IS WRONG.'
                                self.returnStr.append(msg)
                                logSbcHander.error(msg)
                        else:
                            #command format is wrong.
                            msg = 'OPERATION FAILED DUE TO COMMAND FORMAT IS WRONG.'
                            self.returnStr.append(msg)
                            logSbcHander.error(msg)
    
    def removeChannel(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        if(4 != len(lineSplit)):
            msg = 'OPERATION FAILED DUE TO COMMAND LENGTH IS WRONG.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            if(lineSplit[2] != node['nodeParas']['froID']):
                msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
            else:
                if('CONFIGURED' != node['nodeParas']['state']):
                    msg = 'OPERATION FAILED DUE TO INTERFACE NOT UP.'
                    self.returnStr.append(msg)
                    logSbcHander.error(msg)
                else:
                
                    if(node['channels'].has_key(lineSplit[3])):
                        try:
                            channels = self.er.findall('./channel')
                            for channel in channels:
                                if(channel.find('./channelId').text == lineSplit[3]):
                                    self.er.getroot().remove(channel)
                                    break
                            self.writeBack2XmlFile()
                            self.returnStr.append('OPERATION SUCCESSFUL - VPP: 0')
                            self.returnStr.append('OPERATION SUCCESSFUL - VPP: 1')
                            logSbcHander.info('ACTIVE INTERFACE SUCCESSFULLY.')
                        except Exception as e:
                            msg = ('OPERATION FAILED DUE TO Write Back To XML File Failed, ERROR: ' + str(e)).upper()
                            self.returnStr.append(msg)
                            logSbcHander.error(msg)
                    else:
                        msg = 'OPERATION FAILED DUE TO CHANNEL ID NOT EXIST.'
                        self.returnStr.append(msg)
                        logSbcHander.error(msg)
    
    def liActive(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        if(2 != len(lineSplit)):
            msg = 'OPERATION FAILED DUE TO COMMAND FORMAT IS WRONG.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            if(lineSplit[1] != node['nodeParas']['froID']):
                msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
            else:
                if('CONFIGURED' != node['nodeParas']['state']):
                    try:
                        self.er.find('./state').text = 'CONFIGURED'
                        self.writeBack2XmlFile()
                        self.returnStr.append('OPERATION SUCCESSFUL - VPP: 0')
                        self.returnStr.append('OPERATION SUCCESSFUL - VPP: 1')
                        logSbcHander.info('ACTIVE INTERFACE SUCCESSFULLY.')
                    except Exception as e:
                        msg = ('OPERATION FAILED DUE TO Write Back To XML File Failed, ERROR: ' + str(e)).upper()
                        self.returnStr.append(msg)
                        logSbcHander.error(msg)
    
    def liDeactive(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        if(2 != len(lineSplit)):
            msg = 'OPERATION FAILED DUE TO COMMAND FORMAT IS WRONG.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            if(lineSplit[1] != node['nodeParas']['froID']):
                msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
            else:
                if('NOT_CONFIGURED' != node['nodeParas']['state']):
                    try:
                        self.er.find('./state').text = 'NOT_CONFIGURED'
                        self.writeBack2XmlFile()
                        self.returnStr.append('OPERATION SUCCESSFUL - VPP: 0')
                        self.returnStr.append('OPERATION SUCCESSFUL - VPP: 1')
                        logSbcHander.info('ACTIVE INTERFACE SUCCESSFULLY.')
                    except Exception as e:
                        msg = ('OPERATION FAILED DUE TO Write Back To XML File Failed, ERROR: ' + str(e)).upper()
                        self.returnStr.append(msg)
                        logSbcHander.error(msg)
    
    def pmUpdate(self):
        pass
    
    '''
    Ch_li> get_config 2

    OPERATION SUCCESSFUL -
    
    BGF: 2
    
    
    VPP: 0 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -neId:            BGF01
        -nextHopIp:       10.166.89.97
        -vlanId:          150
        -portLocation:    0
        -tos:             0
        -pbits:           0
        -checkTime:       30
    
    VPP: 0 tcpChannelId: 0 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 0 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30000
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 1 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 1 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30001
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 2 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 2 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30002
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 3 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 3 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30003
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 4 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 4 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30004
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 5 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 5 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30005
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 6 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 6 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.100
        -localTcpPort:    30006
        -remoteIp:        10.185.127.90
        -remoteTcpPort:   30001
    
    VPP: 0 tcpChannelId: 7 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>
    VPP: 1 tcpChannelId: 7 config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>
        -licId:           LIC
        -localIp:         10.166.89.101
        -localTcpPort:    30001
        -remoteIp:        10.185.127.91
        -remoteTcpPort:   30001
    
    No of TCP channels: 8
    '''
    def getConfig(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        if(2 != len(lineSplit)):
            msg = 'OPERATION FAILED DUE TO COMMAND FORMAT IS WRONG.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            if(lineSplit[1] != node['nodeParas']['froID']):
                msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
            else:
                self.returnStr.append('')
                self.returnStr.append('OPERATION SUCCESSFUL -')
                self.returnStr.append('')
                self.returnStr.append('BGF: ' + node['nodeParas']['froID'])
                self.returnStr.append('')
                state = node['nodeParas']['state']
                self.returnStr.append('VPP: 0 config: SET vpp state: ' + state +' lastReturnCode: 0 lastReturnMsg: <VPP: 0>')
                self.returnStr.append('VPP: 1 config: SET vpp state: ' + state +' lastReturnCode: 0 lastReturnMsg: <VPP: 1>')
                self.returnStr.append('\t-neId:\t\t' + node['nodeParas']['neId'])
                self.returnStr.append('\t-nextHopIp:\t\t' + node['nodeParas']['nextHopIp'])
                self.returnStr.append('\t-vlanId:\t\t' + node['nodeParas']['vlanId'])
                self.returnStr.append('\t-portLocation:\t\t' + node['nodeParas']['portLocation'])
                self.returnStr.append('\t-tos:\t\t' + node['nodeParas']['tos'])
                self.returnStr.append('\t-pbits:\t\t' + node['nodeParas']['pbits'])
                self.returnStr.append('\t-checkTime:\t\t' + node['nodeParas']['checkTime'])
                self.returnStr.append('')
                for k, v in node['channels']:
                    self.returnStr.append('VPP: 0 tcpChannelId: ' + k + ' config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>')
                    self.returnStr.append('VPP: 1 tcpChannelId: ' + k + ' config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>') 
                    self.returnStr.append('\t-licId:\t\t' + v['licId'])
                    self.returnStr.append('\t-localIp:\t\t' + v['localIp'])
                    self.returnStr.append('\t-localTcpPort:\t\t' + v['localTcpPort'])
                    self.returnStr.append('\t-remoteIp:\t\t' + v['remoteIp'])
                    self.returnStr.append('\t-remoteTcpPort:\t\t' + v['remoteTcpPort'])
                    self.returnStr.append('')
                self.returnStr.append('No of TCP channels: ' + str(len(node['channels'])))
    
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
