#encoding=utf-8
import logging
#from __builtin__ import getattr, str
#from Canvas import Line
protocol_log = logging.getLogger('server.SshCusProtocol')

protocol_log.info('SSH Protocol Class start to log.')

from twisted.conch import recvline
import sys, os
from com.ericsson.xn.server.prop.PyProperties import Properties
from com.ericsson.xn.server.parser.OcgsParser import OcgsNodeInfo
from com.ericsson.xn.server.parser.SbcParser import SbcNodeInfo
from com.ericsson.xn.server.handler.SbcSetHandler import SbcSetOperations
from com.ericsson.xn.server.handler.OcgsSetHandler import OcgsSetValue, OcgsLicAddRemove
from com.ericsson.xn.server.globargvs import globalarguments
#from com.ericsson.xn.server.pm.SbcPMGen import SbcPMHolder, SbcPMWriter
#print sys.path

class SshCusProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        protocol_log.info('SSH Protocal Class inited.')
        self.user = user
        
        pkg_path = 'com' + os.path.sep + 'ericsson' + os.path.sep + 'xn' + os.path.sep + 'server' + os.path.sep + 'common'
        self.pardir = os.path.dirname(os.path.abspath(__file__)).split(pkg_path)[0]
        prop_file = self.pardir + 'config' + os.path.sep + str(sys.argv[2]).strip() + os.path.sep + str(sys.argv[2]).strip() + '.properties'
        protocol_log.info('Property file path: ' + prop_file)
        p = Properties(prop_file)
        self.prompt = p.getProperty('prompt')
        self.nodeType = str(sys.argv[1]).strip()
        
        self.addhelp = ""
        if(self.nodeType == 'ocgs'):
            self.addhelp = "x_view_conf\nx_modify_conf [-nodepara value] [-licid id] [-licpara value]\nocgslicaddone\nocgslicremoveone"
            self.nodexml = self.pardir  + 'config' + os.path.sep + str(sys.argv[2]).strip() + os.path.sep + str(sys.argv[2]).strip() + '_node.xml'
            if(not os.path.isfile(self.nodexml)):
                protocol_log.error('The node XML configuration file does not exist! XML Path: ' + self.nodexml)
                raise StandardError('Unable to find the NODE XML Configuration file.')
        elif('sbc' == self.nodeType):
            #Init the counter simulator
            self.sbcPMHolder = globalarguments.SBC_PM_Holder
            self.sbcmode = 0
            self.sbcprops = p
            self.xmlPath = self.pardir  + 'config' + os.path.sep + str(sys.argv[2]).strip() + os.path.sep + str(sys.argv[2]).strip() + '_node.xml'
            self.logPath = self.pardir  + 'config' + os.path.sep + str(sys.argv[2]).strip() + os.path.sep + str(sys.argv[2]).strip() + '_log.now'
    
    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Welcome to SSH Server, this server is supposed to be used for simulator is E///.")
        self.terminal.nextLine()
        self.do_help()
        self.showPrompt()
    
    def showPrompt(self):
        self.terminal.write(self.prompt)

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
                self.showPrompt()
            elif('ocgs' == self.nodeType or 'sbc' == self.nodeType):
                #check that the given type of node is supported or not
                nodeHandler = getattr(self, 'handler_' + self.nodeType, None)
                if(nodeHandler):
                    nodeHandler(line)
                else:
                    self.terminal.write('The node type you specified does not support, NodeType: ' + self.nodeType)
                    self.terminal.nextLine()
            else:
                self.terminal.write('Command not supported.')
                self.terminal.nextLine()
                self.showPrompt()
        else:
            self.showPrompt()
        
    def handler_sbc(self, line):
        protocol_log.info('Current mode is: ' + str(self.sbcmode))
        protocol_log.info('Current commands is: ' + str(line))
        if(0 == self.sbcmode):
            protocol_log.info('Mode is 1: ' + 'lhsh ' + self.sbcprops.getProperty('SMN') + self.sbcprops.getProperty('APN') + '00 li_enter PRC')
            if('lhsh ' + self.sbcprops.getProperty('SMN') + self.sbcprops.getProperty('APN') + '00 li_enter PRC' == line):
                self.sbcmode = 1
                self.terminal.write('password: ')
            else:
                self.showPrompt()
        elif(1 == self.sbcmode):
            if(self.sbcprops.getProperty('LIENTERPASSWD') == line):
                self.sbcmode = 2
                self.prompt = self.sbcprops.getProperty('prompt0')
            else:
                self.sbcmode = 0
            self.showPrompt()
        elif(2 == self.sbcmode):
            if('exit' == line.lower()):
                self.sbcmode = 0
                self.prompt = self.sbcprops.getProperty('prompt')
            else:
                sbcHandler = SbcSetOperations(line, self.xmlPath, self.logPath)
                returnStrs = sbcHandler.getActionResult()
                for line in returnStrs:
                    self.terminal.write(line + '\n')
                self.showPrompt()
            
            '''if(line.startwith('get_stat')):
                froid = line.split()[1]
                
            
            if('get_stat 2' == line):
                if(self.sbcPMHolder is not None):
                    licID = 2
                    self.terminal.write("LIC ID: " + str(licID) +"\n")
                    self.terminal.write("Channel | sentPackets | sentOctets | droppedPackets | droppedOctets | sentTunnelCreateReqs | successfulTunnelCreates\n")
                    for k, v in self.sbcPMHolder.getCounters().iteritems():
                        self.terminal.write(' ' * (7- len(str(k))) + str(k) + ' | ' + ' ' * (11 - len(str(v[0]))) + str(v[0]) + ' | ' + ' ' * (10 - len(str(v[1]))) + str(v[1]) + ' | ' + ' ' * (14 - len(str(v[2]))) + str(v[2]) + ' | ' + ' ' * (13 - len(str(v[3]))) + str(v[3]) + ' | ' +  ' ' * (20 - len(str(v[4]))) + str(v[4]) + ' | ' + ' ' * (23 - len(str(v[5]))) + str(v[5]) + '\n')
                else:
                    self.terminal.write('FAILED TO GET COUNTERS.')
                    protocol_log.error('Try to get the SBC PM counter instance failed.')
            elif('exit' == line.lower()):
                self.sbcmode = 0
                self.prompt = self.sbcprops.getProperty('prompt')
            self.showPrompt()'''
            #self.terminal.write(' ' * (7- len(str(k))) + str(k) + + ' | ' + ' ' * (11 - len(repr(v[0]))) + repr(v[0]) + '\n')
            

    def handler_ocgs(self, line):
        if('x_view_conf' == line):
            protocol_log.info('ocgs setting action with command: ' + line)
            nodeinfo = OcgsNodeInfo(self.nodexml)
            info = nodeinfo.getNodeInfo()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the getting command: ' + info.replace("\n", " | "))
        elif(line.startswith('x_modify_conf')):
            protocol_log.info('ocgs getting action with command: ' + line)
            handler = OcgsSetValue(line, self.nodexml)
            info = handler.returnRes()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the getting command: ' + info.replace("\n", " | "))
        elif(line.startswith("ocgslic")):
            protocol_log.info('ocgs add or remove LIC with command: ' + line)
            handler = OcgsLicAddRemove(line, self.nodexml)
            info = handler.getRes()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the add/remove action: ' + info.replace("\n", " | "))
        else:
            protocol_log.error('Unkown command found.')
            self.terminal.write("result=failed\nerrordesc=Command Un-supported!")
            self.terminal.nextLine()
        self.showPrompt()

    def do_help(self, cmd=''):
        "Get help on a command. Usage: help command"
        if cmd:
            func = self.getCommandFunc(cmd)
            if func:
                self.terminal.write(func.__doc__)
                self.terminal.nextLine()
                return

        publicMethods = filter(lambda funcname: funcname.startswith('do_'), dir(self))
        handlerMethods = filter(lambda funcname: funcname.startswith('handler_'), dir(self))
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        cmd_hanlder =  [cmd.replace('handler_', '', 1) for cmd in handlerMethods]
        helpMsg = "Commands: \n" + "\n".join(commands)
        if('ocgs' == self.nodeType):
            helpMsg = "Commands: \n" + "\n".join(commands) + "\nNode handlers: \n" + "\n".join(cmd_hanlder) + "\n" + self.addhelp
        elif(1 == 2):
            pass
        
        self.terminal.write(helpMsg)
        self.terminal.nextLine()

    def do_quit(self):
        "Ends your session. Usage: quit"
        self.terminal.write("Thanks for playing!")
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_clear(self):
        "Clears the screen. Usage: clear"
        self.terminal.reset()