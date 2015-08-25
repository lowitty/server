#encoding=utf-8
'''
Created on Aug 24, 2015

@author: lowitty
'''
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
from com.ericsson.xn.server.common.CommonFunc import TwRealm
from com.ericsson.xn.server.common.CusProtocols import SshCusProtocol
from com.ericsson.xn.server.common.CommonFunc import TwFactory
from twisted.cred import portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.conch.checkers import SSHPublicKeyChecker, InMemorySSHKeyDB
from twisted.conch.ssh import keys
from twisted.internet import reactor

publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

if __name__ == '__main__':
    portal = portal.Portal(TwRealm(SshCusProtocol))
    passwdDB = InMemoryUsernamePasswordDatabaseDontUse()
    passwdDB.addUser('root', 'root')
    sshDB = SSHPublicKeyChecker(InMemorySSHKeyDB({'user': [keys.Key.fromString(data=publicKey)]}))
    portal.registerChecker(passwdDB)
    portal.registerChecker(sshDB)
    TwFactory.portal = portal
    reactor.listenTCP(interface="0.0.0.0", port=2222, factory=TwFactory())
    reactor.run()