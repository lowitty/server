#encoding=utf-8
'''
Created on Aug 24, 2015

@author: lowitty
'''
#This will try to init the logger
import sys, os, platform
import logging
from logging.handlers import RotatingFileHandler
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s %(funcName)s(%(lineno)d) %(message)s')

#get the root directory of the parent folder
pardir = os.path.dirname(os.path.abspath(__file__))


log_file = pardir + os.path.sep + 'logs' + os.path.sep + 'server.log'
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


libstype = "libsLinux"

if('Linux' == platform.system()):
    libstype = "libsLinux"
elif('Darwin' == platform.system()):
    libstype = "libsDarwin"
else:
    server_log.critical("This program is surpposed to be run on OSX or Linux platforms, other platforms have not been tested!")

sys.path.insert(0, os.path.join(pardir, libstype))


from com.ericsson.xn.server.common.CommonFunc import TwRealm
from com.ericsson.xn.server.common.CusProtocols import SshCusProtocol
from com.ericsson.xn.server.common.CommonFunc import TwFactory
from twisted.cred import portal
from twisted.cred.checkers import FilePasswordDB
from twisted.conch.checkers import SSHPublicKeyChecker, InMemorySSHKeyDB
from twisted.conch.ssh import keys
from twisted.internet import reactor
from com.ericsson.xn.server.prop.PyProperties import Properties

publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

if __name__ == '__main__':
    if(len(sys.argv) < 3):
        server_log.critical('Please feed the node type and node configuration name as parameter.')
    else:
        cfg_path = pardir + os.path.sep + 'config' + os.path.sep + str(sys.argv[2]).strip()
        if(not os.path.isdir(cfg_path) or not os.path.isfile(cfg_path + os.path.sep + str(sys.argv[2]).strip() + ".properties")):
            server_log.error('The configuration file that you have specified does not exist!')
        else:
            cfg_file = os.path.normpath(cfg_path + os.path.sep + str(sys.argv[2]).strip() + ".properties")
            server_log.info('Get properties from the configuration file: ' + cfg_file + '. ')
            p = Properties(cfg_file)
            
            #username = p.getProperty('username')
            #password = p.getProperty('password')
            
            host = p.getProperty('host')
            portno = p.getProperty('port')
            
            #if(username is None or password is None or host is None or portno is None):
            #    server_log.error('The configuration file: ' + cfg_file + " need to provide username, password, host and port information.")
                
            if(host is None or portno is None):
                server_log.error('The configuration file: ' + cfg_file + " need to provide host and port information.")
            else:
                try:
                    iPort = int(portno)
                except Exception as e:
                    server_log.warning('Unable to parse port NO. to integer, will use 22 as default port NO.')
                    iPort = 22
                
                portal = portal.Portal(TwRealm(SshCusProtocol))
                
                #passwdDB = InMemoryUsernamePasswordDatabaseDontUse()
                #server_log.info('Add user with username: ' + username + ", password: " + password + ".")
                #passwdDB.addUser(username, password)
                
                passwdDB = FilePasswordDB(pardir + os.path.sep + "passwd" + os.path.sep + "passwddbfile")
                
                sshDB = SSHPublicKeyChecker(InMemorySSHKeyDB({'user': [keys.Key.fromString(data=publicKey)]}))
                portal.registerChecker(passwdDB)
                portal.registerChecker(sshDB)
                TwFactory.portal = portal
                server_log.debug('Bind server listener at port: ' + str(iPort) + ' and bind to host: ' + host + '.')
                reactor.listenTCP(interface="0.0.0.0", port=2222, factory=TwFactory())
                server_log.debug('Try to start the server.')
                reactor.run()