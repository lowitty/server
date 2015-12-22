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
    
    def __init__(self, line, xmlPath, logPath):
        self.returnStr = []
        self.avaiableSetCMDs = ['tcp_channel', 'li_activate', 'li_deactivate', 'pm_update', 'get_stat', 'get_config', 'get_appl_trace']
        self.xmlPath = xmlPath
        self.logPath = logPath
        self.line = line
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
            if(self.line.startswith('tcp_channel add')):
                self.addChannel()
            elif(self.line.startswith('tcp_channel remove')):
                self.removeChannel()
            elif(self.line.startswith('li_activate')):
                self.liActive()
            elif(self.line.startswith('li_deactivate')):
                self.liDeactive()
            elif(self.line.startswith('pm_update')):
                self.pmUpdate()
            elif(self.line.startswith('get_config')):
                self.getConfig()
            elif(self.line.startswith('get_appl_trace')):
                self.getApplTrace()
            elif(self.line.startswith('get_stat')):
                self.getStat()
            else:
                msg = 'OPERATION FAILED DUE TO COMMAND NOT SUPPORT.'
                self.returnStr.append(msg)
                logSbcHander.error(msg)
        else:
            msg = 'OPERATION FAILED DUE TO COMMAND NOT SUPPORT.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
    
    def getStat(self):
        lineSplit = self.line.split()
        nodeInfoInstance = SbcNodeInfo(self.xmlPath)
        node = nodeInfoInstance.getNodeInfoMap()
        if(lineSplit[1] != node['nodeParas']['froID']):
            msg = 'OPERATION FAILED DUE TO FROID MISMATCH.'
            self.returnStr.append(msg)
            logSbcHander.error(msg)
        else:
            froID = node['nodeParas']['froID']
            sortedKeys = sorted(node['channels'].keys())
            self.returnStr.append('LIC ID: ' + str(froID))
            self.returnStr.append('Channel | sentPackets | sentOctets | droppedPackets | droppedOctets | sentTunnelCreateReqs | successfulTunnelCreates')
            for k in sortedKeys:
                v = node['channels'][k]
                #' ' * (7- len(str(k))) + str(k) + ' | ' + ' ' * (11 - len(str(v[0]))) + str(v[0]) + ' | ' + ' ' * (10 - len(str(v[1]))) + str(v[1]) + ' | ' + ' ' * (14 - len(str(v[2]))) + str(v[2]) + ' | ' + ' ' * (13 - len(str(v[3]))) + str(v[3]) + ' | ' +  ' ' * (20 - len(str(v[4]))) + str(v[4]) + ' | ' + ' ' * (23 - len(str(v[5]))) + str(v[5]) + '\n'
                self.returnStr.append(' ' * (7 - len(k)) + str(k) + ' | ' + ' ' * (11 - len(v['c1'])) + str(v['c1']) + ' | ' + ' ' * (10 - len(v['c2'])) + str(v['c2']) + ' | ' + ' ' * (14 - len(v['c3'])) + str(v['c3']) + ' | ' + ' ' * (13 - len(v['c4'])) + str(v['c4']) + ' | ' + ' ' * (20 - len(v['c5'])) + str(v['c5']) + ' | ' + ' ' * (23 - len(v['c6'])) + str(v['c6']))
            logSbcHander.info('GET COUNTER SUCCESSFULLY.')
    
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
                
                if(node['channels'].has_key(lineSplit[3]) or (not isChannelIDValid) or len(node['channels']) > 7):
                    msg = 'OPERATION FAILED DUE TO CHANNEL ID EXIST OR NOT IN [0, 63] OR ALREADY 8 CHANNELS.'
                    self.returnStr.append(msg)
                    logSbcHander.error(msg)
                elif('CONFIGURED' != node['nodeParas']['state']):
                    msg = 'OPERATION FAILED DUE TO CANNOT ADD CHANNEL WHEN INTERFACE IS CLOSED .'
                    self.returnStr.append(msg)
                    logSbcHander.error(msg)
                else:
                    if('CONFIGURED' != node['nodeParas']['state']):
                        msg = 'OPERATION FAILED DUE TO IINTERFACE NOT UP.'
                        self.returnStr.append(msg)
                        logSbcHander.error(msg)
                    else:
                        cmds = {}
                        for index in range(4, 14, 2):
                            cmds[lineSplit[index].lower().strip()[1:]] = lineSplit[index + 1].strip()
                        
                        if(cmds.has_key('licid') and cmds.has_key('localip') and cmds.has_key('localport') and cmds.has_key('remoteip') and cmds.has_key('remoteport')):
                            pat = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
                            prog = re.compile(pat)
                            res0 = prog.match(cmds['localip'])
                            res1 = prog.match(cmds['remoteip'])
                            if(res0 and res1):
                                try:
                                    lPort = int(cmds['localport'])
                                    rPort = int(cmds['remoteport'])
                                except Exception as e:
                                    #Local port or Remote port is not number.
                                    msg = 'OPERATION FAILED DUE TO PORT IS NOT NUMBER.'
                                    self.returnStr.append(msg)
                                    logSbcHander.error(msg)
                                if(-1 < lPort < 65536 and -1 < rPort < 65536):
                                    #Can check if IP already in other channels, will not check in this version.
                                    try:
                                        newChannel = ElementTree.Element('channel')
                                        channelId = ElementTree.SubElement(newChannel, 'channelId')
                                        channelId.text = lineSplit[3]
                                        channelId.tail = "\n\t\t"
                                        licid = ElementTree.SubElement(newChannel, 'licId')
                                        licid.text = cmds['licid']
                                        licid.tail = "\n\t\t"
                                        localIp = ElementTree.SubElement(newChannel, 'localIp')
                                        localIp.text = cmds['localip']
                                        localIp.tail = "\n\t\t"
                                        localTcpPort = ElementTree.SubElement(newChannel, 'localTcpPort')
                                        localTcpPort.text = cmds['localport']
                                        localTcpPort.tail = "\n\t\t"
                                        remoteIp = ElementTree.SubElement(newChannel, 'remoteIp')
                                        remoteIp.text = cmds['remoteip']
                                        remoteIp.tail = "\n\t\t"
                                        remoteTcpPort = ElementTree.SubElement(newChannel, 'remoteTcpPort')
                                        remoteTcpPort.text = cmds['remoteport']
                                        remoteTcpPort.tail = "\n\t\t"
                                        
                                        c1 = ElementTree.SubElement(newChannel, 'c1')
                                        c1.text = '0'
                                        c1.tail = "\n\t\t"
                                        c2 = ElementTree.SubElement(newChannel, 'c2')
                                        c2.text = '0'
                                        c2.tail = "\n\t\t"
                                        c3 = ElementTree.SubElement(newChannel, 'c3')
                                        c3.text = '0'
                                        c3.tail = "\n\t\t"
                                        c4 = ElementTree.SubElement(newChannel, 'c4')
                                        c4.text = '0'
                                        c4.tail = "\n\t\t"
                                        c5 = ElementTree.SubElement(newChannel, 'c5')
                                        c5.text = '0'
                                        c5.tail = "\n\t\t"
                                        c6 = ElementTree.SubElement(newChannel, 'c6')
                                        c6.text = '0'
                                        c6.tail = "\n\t\t"
                                        
                                        newChannel.tail = "\n\t\t"
                                        newChannel.text = "\n\t\t"
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
                            logSbcHander.info('R SUCCESSFULLY.')
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
        if(18 != len(lineSplit)):
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
                if len(node['channels']) > 0:
                    msg = 'OPERATION FAILED DUE TO CANNOT CLOSE INTERFACE WHEN CHANELLS EXIST ON NODE.'
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
                
                sortedKeys = sorted(node['channels'].keys())
                for k in sortedKeys:
                    #for k, v in node['channels'].iteritems():
                    v = node['channels'][k]
                    self.returnStr.append('VPP: 0 tcpChannelId: ' + k + ' config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 0>')
                    self.returnStr.append('VPP: 1 tcpChannelId: ' + k + ' config: SET vpp state: CONFIGURED lastReturnCode: 0 lastReturnMsg: <VPP: 1>') 
                    self.returnStr.append('\t-licId:\t\t' + v['licId'])
                    self.returnStr.append('\t-localIp:\t\t' + v['localIp'])
                    self.returnStr.append('\t-localTcpPort:\t\t' + v['localTcpPort'])
                    self.returnStr.append('\t-remoteIp:\t\t' + v['remoteIp'])
                    self.returnStr.append('\t-remoteTcpPort:\t\t' + v['remoteTcpPort'])
                    self.returnStr.append('')
                self.returnStr.append('No of TCP channels: ' + str(len(node['channels'])))
                self.returnStr.append('')
    
    def getApplTrace(self):
        global lock
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
                try:
                    lock.acquire()
                    f = open(self.logPath, 'r')
                    lines = f.readlines()
                    f.close()
                    lock.release()
                    self.returnStr = [k.strip() for k in lines]
                    logSbcHander.info('SBC GET LOG SUCCESSFULLY.')
                except Exception as e:
                    msg = "OPERATION FAILED DUE TO ERROR: " + str(e).upper()
                    self.returnStr.append(msg)
                    logSbcHander.error(msg)
    
    def writeBack2XmlFile(self):
        global version, lock
        lock.acquire()
        if('2.7' == version):
            self.er.write(self.xmlPath, encoding='utf-8', xml_declaration=True, method='xml')
        else:
            self.er.write(self.xmlPath, encoding='utf-8')
        lock.release()
            
    def getActionResult(self):
        encodedStr = [k.encode('utf-8') for k in self.returnStr]
        return encodedStr
