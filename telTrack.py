import ktl 
import time
import sys 
import select
import matplotlib.pyplot as plt 
import numpy as np
import csv 


#Start monitoring
telstate = ktl.cache("dcs", "AXESTST")
el = ktl.cache("dcs", "el")
az = ktl.cache("dcs", "az")
eerr = ktl.cache("dcs", "elpe")
aerr = ktl.cache("dcs", "azpe")
telstat = ktl.cache("dcs", "AXESTST")
ca = ktl.cache("dcs", "CA")
ce = ktl.cache("dcs", "CE")
wspeed = ktl.cache("met", "WINDSPD")
wdir = ktl.cache("met", "WINDDIR")
telstate.monitor()
el.monitor()
az.monitor()
eerr.monitor()
aerr.monitor()
telstat.monitor()
wspeed.monitor()
wdir.monitor()
ca.monitor()
ce.monitor()

#Initialize arrays, variables
castart = float(ca)
cestart = float(ce)
tsa = [] #time array for slews
azst = [] #slew total az array
elst = [] #slew total el array
adps = [] #slew degrees/second az
edps = [] #slew degrees/second el
caa = [] #pointing ca array
cae = [] #pointing ce array

ava = 0
eva = 0
meanca = 0
meance = 0
event = 0
eevent = 0
ai = 0
i = 0
k = 0

def slewTrack():
    global i, ava, eva
    if telstate == 'SLEW':
        ts = time.time()
        azstart = float(az)
        elstart = float(el)
        print("Telescope slewing!")
        telstate.waitFor("=='TRACK'")
        tsa.append(time.time() - ts) 
        if abs((azstart - float(az)) or abs(elstart - float(el)))> 1:
            azst.append(abs(azstart - float(az)))
            elst.append(abs(elstart - float(el)))
            adps.append(azst[i]/tsa[i])
            edps.append(elst[i]/tsa[i])
            print("Slewed %f at %f d/s in AZ." % (azst[i], adps[i]))
            print("Slewed %f at %f d/s in EL." % (elst[i], edps[i]))
            i += 1
            ava = np.mean(adps)
            eva = np.mean(edps)
        else:
            print("Offset ignored.")


def trackOutput(ee, ae, e, a, wind, ai):
    global wspeed, startTime
    etime = time.time() - startTime
    if wind == True:
        trackOutFile.write('%f, %f, %f, %f, %s, %f, %f\n' % (ee, ae, e, a, etime, wspeed, ai))
    else:
        trackOutFile.write('%f, %f, %f, %f, %s\n' % (ee, ae, e, a, etime))



def errTrack():
    global eevent, event
    wind = False
    response = '(Type w and enter to mark as windshake)\a'
    while(abs(eerr) > 0.5 or abs(aerr) > 0.5):
        eevent = 1
        if telstat != 'SLEW':
            trackOutput(eerr, aerr, el, az, wind, ai)
            print("Tracking errors are high! %s" % response)
            print("\n%f, %f" % (eerr, aerr))
            sys.stdout.write('> ')
            sys.stdout.flush()
            i, o, e = select.select([sys.stdin], [], [], 2)
            if (i):
                if sys.stdin.readline().strip() == 'w':
                    wind = True
                    ai = abs(az - wdir)
                    response = '(Marked as windshake, hit enter if not windshake)'
                else:
                    wind = False
                    response = '(Type w and enter to mark as windshake)'
    if eevent == 1:
        event += 1
        eevent = 0

    return event

def pointingTrack():
    global castart, cestart, meanca, meance
    if float(ca) != castart or float(ce) != cestart:
        caa.append(castart - float(ca))
        cea.append(cestart - float(ce))
        castart = float(ca)
        cestart = float(ce)
        meanca = np.mean(caa)
        meance = np.mean(cae)

def main():
    print(
    '''
    Starting Tel Track! This script will monitor telescope performance
    during the night, and will output stats every 30 minutes.  Use 
    ctrl-c to end the script, and print a final output.

    An alarm will also sound if tracking errors are high.
    '''
    )
    startTime = time.time()
    try:
        while True:
            slewTrack()
            errEvent = errTrack()
            pointingTrack()
            if (time.time() - startTime)%1800 == 0:
               updatetime = k*30
               print('Update after %d minutes:' % updatetime)
               print('Average slew speed (AZ, EL): %f %f' % (ava, eva))
               print('Number of high tracking error events: %d' % errEvent)
               print('-----------------------------------------')
               k+=1

    except KeyboardInterrupt:
        print('\nScript ended. Final stats:')
        print('Average slew speed (AZ, EL): %f %f' % (avaslew, aveslew))
        print('Average pointing change (CA, CE): %f, %f' % (camean, cemean))
        print('Number of high tracking error events: %d' % errEvent)



if __name__ == '__main__':
    main()

