#encoding=utf-8
import logging
protocol_log = logging.getLogger('server.SshCusProtocol')

protocol_log.info('SSH Protocol Class start to log.')

from twisted.conch import recvline
import sys, os

class SshCusProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        protocol_log.info('SSH Protocal Class inited.')
        self.user = user
        
        pkg_path = 'com' + os.path.sep + 'ericsson' + os.path.sep + 'xn' + os.path.sep + 'server' + os.path.sep + 'common'
        pardir = os.path.dirname(os.path.abspath(__file__)).split(pkg_path)[0]
        
        
        self.propt = "HelloWorld "
    
    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Welcome to my test SSH server.")
        self.terminal.nextLine()
        self.do_help()
        self.showPrompt()
    
    def showPrompt(self):
        self.terminal.write(self.propt + "$ ")

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        print os.path.dirname(os.path.abspath(__file__)).split('com' + os.path.sep)
        protocol_log.info(os.path.dirname(os.path.abspath(__file__)))
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
                self.terminal.write("No such command.")
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
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        self.terminal.write("Commands: \n" + "\n".join(commands))
        self.terminal.nextLine()

    def do_quit(self):
        "Ends your session. Usage: quit"
        self.terminal.write("Thanks for playing!")
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_clear(self):
        "Clears the screen. Usage: clear"
        self.terminal.reset()