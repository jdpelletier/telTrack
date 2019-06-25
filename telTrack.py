import ktl 
import time
import sys 
import select
import os
import datetime
#import matplotlib.pyplot as plt 
#import numpy as np
#import csv
#from statistics import mean 


#Start monitoring
telState = ktl.cache("dcs", "AXESTST")
elevation = ktl.cache("dcs", "el")
azimuth = ktl.cache("dcs", "az")
elevationError = ktl.cache("dcs", "elpe")
azimuthError = ktl.cache("dcs", "azpe")
ca = ktl.cache("dcs", "CA")
ce = ktl.cache("dcs", "CE")
windSpeed = ktl.cache("met", "WINDSPD")
windDir = ktl.cache("met", "WINDDIR")
telState.monitor()
elevation.monitor()
azimuth.monitor()
elevationError.monitor()
azimuthError.monitor()
ca.monitor()
ce.monitor()
windSpeed.monitor()
windDir.monitor()

now = datetime.datetime.now()
path = "/home/k1obstcs/jptest/%s" % now.strftime("%Y-%m-%d")

if not os.path.exists(path):
    os.makedirs(path)

trackOutFile = open('%s/trackingoutput.txt' % path, 'w+')
slewOutFile = open('%s/slewingoutput.txt' % path, 'w+')
pointingOutFile = open('%s/pointingoutput.txt' % path, 'w+')

def mean(array):
    total = 0
    for y in array:
        total += y
    average = total / len(array)
    return average

def slewTrack(i, azAverageSpeed, elAverageSpeed):
    if telState == 'SLEW':
        startTime = time.time()
        azstart = float(az)
        elstart = float(el)
        print("Telescope slewing!")
        telState.waitFor("=='TRACK'")
        if abs((azstart - float(az)) or abs(elstart - float(el)))> 1:
            tsa.append(time.time() - ts)
            azSlews.append(abs(azstart - float(az)))
            elSlews.append(abs(elstart - float(el)))
            azDegreesPerSecond.append(azSlews[i]/slewTimes[i])
            elDegreesPerSecond.append(elSlews[i]/slewTimes[i])
            print("Slewed %f at %f d/s in AZ." % (azSlews[i], azDegreesPerSecond[i]))
            print("Slewed %f at %f d/s in EL." % (elSlews[i], elDegreesPerSecond[i]))
            slewOutFile.write('%f, %f, %f' % (azSlews[i], elSlews[i], slewTimes[i]))
            i += 1
            azAverageSpeed = mean(azDegreesPerSecond)
            elAverageSpeed = mean(elDegreesPerSecond)
        else:
            print("Offset ignored.")
    return i, azAverageSpeed, elAverageSpeed


def trackOutput(elerr, azerr, el, az, wind, windIncidenceAngle, windSpeed, startTime):
    elapsedTime = time.time() - startTime
    if wind == True:
        trackOutFile.write('%f, %f, %f, %f, %s, %f, %f\n' % (elerr, azerr, el, az, elapsedTime, windSpeed, windIncidenceAngle))
    else:
        trackOutFile.write('%f, %f, %f, %f, %s\n' % (elerr, azerr, el, az, elapsedTime))



def errTrack(eevent, event, windIncidenceAngle, wind):
    global errBreak
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
    while(abs(elevationError) > 0.5 or abs(azimuthError) > 0.5) and (errBreak == 0):
        eevent = 1
        if telState != 'SLEW':
            x+=1
           # trackOutput(eerr, aerr, el, az, wind, windIncidenceAngle, windSpeed, startTime) removing for daytime testing
            if response != '':
                print(response)
                print("\n%f, %f" % (elevationError, azimuthError))
                sys.stdout.write('> ')
                sys.stdout.flush()
            i, o, e = select.select([sys.stdin], [], [], 2)
            if (i):
                if sys.stdin.readline().strip() == 'w':
                    wind = True
                    windIncidenceAngle = abs(azimuth - windDir)
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


def pointingTrack(j, castart, cestart, meanca, meance):
    if float(ca) != castart or float(ce) != cestart:
        caArray.append(castart - float(ca))
        ceArray.append(cestart - float(ce))
        castart = float(ca)
        cestart = float(ce)
        meanca = mean(caArray)
        meance = mean(ceArray)
        pointingOutFile.write('%f, %f' % (caArray[i], ceArray[i]))
        j+=1

def main():
    global errBreak
    #Initialize arrays, variables
    castart = float(ca)
    cestart = float(ce)
    slewTimes = [] #time array for slews
    azSlews = [] #slew total az array
    elSlews = [] #slew total el array
    azDegreesPerSecond = [] #slew degrees/second az
    elDegreesPerSecond = [] #slew degrees/second el
    caArray = [] #pointing ca array
    ceArray = [] #pointing ce array
    startTime = time.time()
    azAverageSpeed = 0 
    elAverageSpeed = 0 
    meanca = 0 
    meance = 0 
    event = 0 
    eevent = 0
    wind = False 
    windIncidenceAngle = 0 
    i = 0 
    k = 1
    j = 0 
    errBreak = 0
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
            i, azAverageSpeed, elAverageSpeed = slewTrack(i, azAverageSpeed, elAverageSpeed)
            eevent, event, windIncidenceAngle, wind = errTrack(eevent, event, windIncidenceAngle, wind)
            j, castart, cestart, meanca, meance = pointingTrack(j, castart, cestart, meanca, meance)
            if ((time.time() - startTime)%1800 == 0) or (errBreak == 1):
               updatetime = k*30
               print('Update after %d minutes:' % updatetime)
               print('Average slew speed (AZ, EL): %f %f' % (azAverageSpeed, elAverageSpeed))
               print('Average pointing change (CA, CE): %f, %f' % (meanca, meance))
               print('Number of high tracking error events: %d' % event)
               print('-----------------------------------------')
               k+=1

    except KeyboardInterrupt:
        print('\nScript ended. Final stats:')
        print('Average slew speed (AZ, EL): %f %f' % (azAverageSpeed, elAverageSpeed))
        print('Average pointing change (CA, CE): %f, %f' % (meanca, meance))
        print('Number of high tracking error events: %d' % event)
        slewOutFile.close()
        trackOutFile.close()
        pointingOutFile.close()

if __name__ == '__main__':
    main()

