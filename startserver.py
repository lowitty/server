#encoding=utf-8
'''
Created on Aug 24, 2015

@author: lowitty
'''
#This will try to init the logger
import sys, os
import logging
from logging.handlers import RotatingFileHandler
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s %(funcName)s(%(lineno)d) %(message)s')
log_file = os.path.dirname(__file__) + os.path.sep + 'logs' + os.path.sep + 'server.log'
log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=10, encoding='utf-8', delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

server_log = logging.getLogger('server')
server_log.setLevel(logging.DEBUG)

server_log.addHandler(log_handler)
server_log.addHandler(console_handler)

server_log.info('********************************************************************************************')


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
from com.ericsson.xn.server.common.CommonFunc import TwRealm
from com.ericsson.xn.server.common.CusProtocols import SshCusProtocol
from com.ericsson.xn.server.common.CommonFunc import TwFactory
from twisted.cred import portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.checkers import SSHPublicKeyChecker, InMemorySSHKeyDB
from twisted.conch.ssh import keys
from twisted.internet import reactor
from com.ericsson.xn.server.prop.PyProperties import Properties

publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

if __name__ == '__main__':
    if(len(sys.argv) < 2):
        server_log.critical('Please feed the node configuration name as parameter.')
    else:
        cfg_path = os.path.dirname(__file__) + os.path.sep + 'config' + os.path.sep + str(sys.argv[1]).strip()
        if(not os.path.isdir(cfg_path) or not os.path.isfile(cfg_path + os.path.sep + str(sys.argv[1]).strip() + ".properties")):
            server_log.error('The configuration file that you have specified does not exist!')
        else:
            cfg_file = os.path.normpath(cfg_path + os.path.sep + str(sys.argv[1]).strip() + ".properties")
            p = Properties(cfg_file)
            username = p.getProperty('username')
            password = p.getProperty('password')
            host = p.getProperty('host')
            portno = p.getProperty('port')
            if(username is None or password is None or host is None or portno is None):
                server_log.error('')
    
    
    portal = portal.Portal(TwRealm(SshCusProtocol))
    passwdDB = InMemoryUsernamePasswordDatabaseDontUse()
    passwdDB.addUser('root', 'root')
    sshDB = SSHPublicKeyChecker(InMemorySSHKeyDB({'user': [keys.Key.fromString(data=publicKey)]}))
    portal.registerChecker(passwdDB)
    portal.registerChecker(sshDB)
    TwFactory.portal = portal
    server_log.debug('Try to start the server listener.')
    reactor.listenTCP(interface="0.0.0.0", port=2222, factory=TwFactory())
    reactor.run()