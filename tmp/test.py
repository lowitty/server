#encoding=utf-8
'''
Created on 2015年11月9日

@author: lowitty
'''
import time, re, copy, sys, random
from __builtin__ import str
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

if __name__ == '__main__':
    
    
    
    
    #i = sorted(random.sample(range(1, 13), random.randint(1, 13)))
    #print i
    
    print random.sample(range(1,3), 0)
    '''print random.randint(1, 2)
    tnow = datetime.now()
    print tnow.microsecond % 1000
    
    li = ["a\n","b\n","c\n","d\n"]
    print [k.strip() for k in li]
    print "||".join([k.strip() for k in li])'''
    
    #print sys.path
    '''et = ET.parse('/Users/lowitty/git/server/config/sbc/sbc_node0.xml')
    channel = ET.Element('channel')
    licId = ET.SubElement(channel, 'licId')
    licId.text = 'licNew'
    licId.tail = "\n\t\t"
    localIp = ET.SubElement(channel, 'localIp')
    localIp.text = '1.1.1.1'
    localIp.tail = "\n\t\t"
    localPort = ET.SubElement(channel, 'localPort')
    localPort.text = '1111'
    localPort.tail = "\n\t\t"
    remoteIp = ET.SubElement(channel, 'remoteIp')
    remoteIp.text = '2.2.2.2'
    remoteIp.tail = "\n\t\t"
    remotePort = ET.SubElement(channel, 'remotePort')
    remotePort.text = '2222'
    remotePort.tail = "\n\t\t"
    channel.tail = "\n\t\t"
    #channel.text = "\n\t\t"
    
    cs = et.findall('./channel')
    c = copy.deepcopy(cs[0])
    i = 1
    
    et.getroot().append(channel)
    et.write('/Users/lowitty/git/server/config/sbc/sbc_node1.xml', encoding='utf-8', xml_declaration=True, method='xml')
    
    m = {"2":2, "1":1}
    print sorted(m)'''
    
    
    
    ''''c.find('./licId').text = 'licNew'
    c.find('./localIp').text = '1.1.1.1'
    c.find('./localTcpPort').text = '1111'
    c.find('./remoteIp').text = '2.2.2.2'
    c.find('./remoteTcpPort').text = '2222'
    
    et.getroot().append(c)
    et.write('/home/lowitty/git/server/config/sbc/sbc_node1.xml', encoding='utf-8', xml_declaration=True, method='xml')'''