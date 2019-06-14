import ktl 
import time
import sys 
import select
#import matplotlib.pyplot as plt 
#import numpy as np
#import csv
#from statistics import mean 


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
startTime = time.time()
ava = 0
eva = 0
meanca = 0
meance = 0
event = 0
eevent = 0
ai = 0
i = 0
errBreak = 0

trackOutFile = open('trackingoutput.txt', 'w+')
slewOutFile = open('slewingoutput.txt', 'w+')
pointingOutFile = open('pointingoutput.txt', 'w+')

def mean(array):
    sm = 0
    for y in array:
        sm += y
    av = sm / len(array)
    return av

def slewTrack():
    global i, ava, eva
    if telstate == 'SLEW':
        ts = time.time()
        azstart = float(az)
        elstart = float(el)
        print("Telescope slewing!")
        telstate.waitFor("=='TRACK'")
        if abs((azstart - float(az)) or abs(elstart - float(el)))> 1:
            tsa.append(time.time() - ts)
            azst.append(abs(azstart - float(az)))
            elst.append(abs(elstart - float(el)))
            adps.append(azst[i]/tsa[i])
            edps.append(elst[i]/tsa[i])
            print("Slewed %f at %f d/s in AZ." % (azst[i], adps[i]))
            print("Slewed %f at %f d/s in EL." % (elst[i], edps[i]))
            i += 1
            ava = mean(adps)
            eva = mean(edps)
            slewOutFile.write('%f, %f, %f' % (azst[i], elst[i], tsa[i]))
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
    global errBreak, eevent, event, ai, wind
    if errBreak == 1 and wind == True:
        response = ''
        print('High errors marked as windshake, hit enter if not windshake')
        sys.stdout.write('>')
        sys.stdout.flush()
        errBreak = 0
        x = 0
    else:
        wind = False
        x = 0
        errBreak = 0
        response = '\nTracking errors are high! (Type w and enter to mark as windshake)\a'
    while(abs(eerr) > 0.5 or abs(aerr) > 0.5) and (errBreak == 0):
        eevent = 1
        if telstat != 'SLEW':
            x+=1
           # trackOutput(eerr, aerr, el, az, wind, ai) removing for daytime testing
            if response != '':
                print(response)
                print("\n%f, %f" % (eerr, aerr))
                sys.stdout.write('> ')
                sys.stdout.flush()
            i, o, e = select.select([sys.stdin], [], [], 2)
            if (i):
                if sys.stdin.readline().strip() == 'w':
                    wind = True
                    ai = abs(az - wdir)
                    print('Marked as windshake, hit enter if not windshake')
                    response = ''
                    sys.stdout.write('>')
                    sys.stdout.flush()
                else:
                    wind = False
                    response = 'Tracking errors are high! (Type w and enter to mark as windshake)'
            if x == 450:
                eevent = 0
                errBreak = 1
                x = 0
                break

    if eevent == 1:
        event += 1
        eevent = 0
        print('Tracking errors back to nominal values.')


def pointingTrack():
    global castart, cestart, meanca, meance
    if float(ca) != castart or float(ce) != cestart:
        caa.append(castart - float(ca))
        cae.append(cestart - float(ce))
        castart = float(ca)
        cestart = float(ce)
        meanca = mean(caa)
        meance = mean(cae)
        pointingOutFile.write('%f, %f' % (caa[i], cae[i]))

def main():
    global errBreak
    k = 1
    print(
    '''
    Starting Tel Track! This script will monitor telescope performance
    during the night, and will output stats every 30 minutes.  Use 
    ctrl-c to end the script, and print a final output.

    An alarm will also sound if tracking errors are high.
    '''
    )
    try:
        while True:
            slewTrack()
            errTrack()
            pointingTrack()
            if ((time.time() - startTime)%1800 == 0) or (errBreak == 1):
               updatetime = k*30
               print('Update after %d minutes:' % updatetime)
               print('Average slew speed (AZ, EL): %f %f' % (ava, eva))
               print('Average pointing change (CA, CE): %f, %f' % (meanca, meance))
               print('Number of high tracking error events: %d' % event)
               print('-----------------------------------------')
               k+=1

    except KeyboardInterrupt:
        print('\nScript ended. Final stats:')
        print('Average slew speed (AZ, EL): %f %f' % (ava, eva))
        print('Average pointing change (CA, CE): %f, %f' % (meanca, meance))
        print('Number of high tracking error events: %d' % event)
        trackOutFile.close()


if __name__ == '__main__':
    main()

