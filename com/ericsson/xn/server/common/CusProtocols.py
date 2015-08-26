#encoding=utf-8
import logging
from __builtin__ import getattr
protocol_log = logging.getLogger('server.SshCusProtocol')

protocol_log.info('SSH Protocol Class start to log.')

from twisted.conch import recvline
import sys, os
from com.ericsson.xn.server.prop.PyProperties import Properties
from com.ericsson.xn.server.parser.OcgsParser import OcgsNodeInfo
from com.ericsson.xn.server.handler.OcgsSetHandler import OcgsSetValue, OcgsLicAddRemove
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
        self.nodexml = self.pardir  + 'config' + os.path.sep + str(sys.argv[2]).strip() + os.path.sep + str(sys.argv[2]).strip() + '_node.xml'
        if(not os.path.isfile(self.nodexml)):
            protocol_log.error('The node XML configuration file does not exist! XML Path: ' + self.nodexml)
            raise StandardError('Unable to find the NODE XML Configuration file.')
        
        self.addhelp = ""
        if(self.nodeType == 'ocgs'):
            self.addhelp = "x_view_conf\nx_modify_conf [-nodepara value] [-licid id] [-licpara value]\nocgslicaddone\nocgslicremoveone"
    
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
            else:
                #check that the given type of node is supported or not
                nodeHandler = getattr(self, 'handler_' + self.nodeType, None)
                if(nodeHandler):
                    nodeHandler(line)
                else:
                    self.terminal.write('The node type you specified does not support, NodeType: ' + self.nodeType)
                    self.terminal.nextLine()
        self.showPrompt()

    def handler_ocgs(self, line):
        if('x_view_conf' == line):
            nodeinfo = OcgsNodeInfo(self.nodexml)
            info = nodeinfo.getNodeInfo()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the getting command: ' + info.replace("\n", " | "))
        elif(line.startswith('x_modify_conf')):
            handler = OcgsSetValue(line, self.nodexml)
            info = handler.returnRes()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the getting command: ' + info)
        elif(line.startswith("ocgslic")):
            handler = OcgsLicAddRemove(line, self.nodexml)
            info = handler.getRes()
            self.terminal.write(info)
            self.terminal.nextLine()
            protocol_log.info('Success execute the add/remove action: ' + info)
        else:
            protocol_log.error('Unkown command found.')
            self.terminal.write("result=failed\nerrordesc=Command un-supported!")
            self.terminal.nextLine()

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
        
        self.terminal.write("Commands: \n" + "\n".join(commands) + "\nNode handlers: \n" + "\n".join(cmd_hanlder) + "\n" + self.addhelp)
        self.terminal.nextLine()

    def do_quit(self):
        "Ends your session. Usage: quit"
        self.terminal.write("Thanks for playing!")
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_clear(self):
        "Clears the screen. Usage: clear"
        self.terminal.reset()