#encoding=utf-8
'''
Created on 2015年11月9日

@author: lowitty
'''
import time
from __builtin__ import str
from datetime import datetime, timedelta
if __name__ == '__main__':
    t = datetime.now()
    print t
    print t + timedelta(minutes = 1)
    '''pmcounters = {}
    pmcounters["round"] = 0
    
    counters = {}
    
    counters[0] = [0, 0, 0, 0, 0, 0]
    counters[1] = [0, 0, 0, 0, 0, 0]
    counters[2] = [0, 0, 0, 0, 0, 0]
    counters[3] = [0, 0, 0, 0, 0, 0]
    counters[4] = [0, 0, 0, 0, 0, 0]
    counters[5] = [0, 0, 0, 0, 0, 0]
    counters[6] = [0, 0, 0, 0, 0, 0]
    counters[7] = [0, 0, 0, 0, 0, 0]
    
    pmcounters["counter"] = counters
    
    o = 0
    while(o < 24):
        print 'round: ' + pmcounters["round"]
        for k, v in pmcounters["counter"].iteritems():
            print str(k) + ": " + str(v)
        
        
        o += 1'''
    
    ''''j = 0
    while(True):
        i = pmcounters["round"]
        p = pmcounters[0][0]
        pmcounters["round"] = pmcounters["round"] + 1
        for k, v in pmcounters.iteritems():
            if('round' != k):
                #nk = k % 8
                pmcounters[k] = [(i+1+p) * 1 * (int(k)+1), (i+1+p) * 2 * (int(k)+1), (i+1+p) * 3 * (int(k)+1), (i+1+p) * 4 * (int(k)+1), (i+1+p) * 5 * (int(k)+1), (i+1+p) * 6 * (int(k)+1)]
        for k,v in pmcounters.iteritems():
            print str(k) + ": " + str(v)
        j += 1
        if(j > 11):
            break
    sum = 0
    for i in range(0, 64):
        sum += i
    print sum
    
    print "a" * 4
    print 'a\nb\n'[:-1]
    
    v = [1, 2, 3, 4 ,5 ,6]
    k = 22
    print ' ' * (7- len(str(k))) + str(k) + ' | ' + ' ' * (11 - len(str(v[0]))) + str(v[0]) + ' | ' + ' ' * (10 - len(str(v[1]))) + str(v[1]) + ' | ' + ' ' * (14 - len(str(v[2]))) + str(v[2]) + ' | ' + ' ' * (13 - len(str(v[3]))) + str(v[3]) + ' | ' +  ' ' * (20 - len(str(v[4]))) + str(v[4]) + ' | ' + ' ' * (23 - len(str(v[5]))) + str(v[5])
    
    #print "Channel | sentPackets | sentOctets | droppedPackets | droppedOctets | sentTunnelCreateReqs | successfulTunnelCreates"[115]'''