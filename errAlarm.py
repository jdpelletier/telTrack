import ktl
import time
import sys
import select
import matplotlib.pyplot as plt
import csv

el = ktl.cache("dcs", "el")
az = ktl.cache("dcs", "az")
eerr = ktl.cache("dcs", "elpe")
aerr = ktl.cache("dcs", "azpe")
telstat = ktl.cache("dcs", "AXESTST")
wspeed = ktl.cache("met", "WINDSPD")
wdir = ktl.cache("met", "WINDDIR")
el.monitor()
az.monitor()
eerr.monitor()
aerr.monitor()
telstat.monitor()
wspeed.monitor()
wdir.monitor()
ai = 0

ee = []
ae = []
e = []
a = []
t = []
ws = []
wd = []

trackOutFile = open('trackingout.txt', 'w+')
ts = time.time()

#write to file function
def trackOutput(ee, ae, e, a, wind, ai):
    global wspeed
    etime = time.time() - ts
    if wind == True:
        trackOutFile.write('%f, %f, %f, %f, %s, %f, %f\n' % (ee, ae, e, a, etime, wspeed, ai))
    else:
        trackOutFile.write('%f, %f, %f, %f, %s\n' % (ee, ae, e, a, etime))

#plotting function
def trackPlot():
    infile = open('trackingout.txt','r')
    with infile as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            ee.append(float(row[0]))
            ae.append(float(row[1]))
            e.append(float(row[2]))
            a.append(float(row[3]))
            t.append(float(row[4]))
            try: 
                ws.append(float(row[5])
                wd.append(float(row[6])
            except IndexError:
                pass

    fig, ax1 = plt.subplots()

    color = 'red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('El Errors', color=color)
    ax1.plot(t, ee, '.', color = color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = 'blue'
    ax2.set_ylabel('Elevation', color=color)
    ax2.plot(t, e, '.', color = color)
    ax2.tick_params(axis='y', labelcolor=color)


    fig, ax1 = plt.subplots()
    
    color = 'red'
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Az Errors', color=color)
    ax1.plot(t, ae, '.', color = color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    
    color = 'blue'
    ax2.set_ylabel('Azimuth', color=color)
    ax2.plot(t, a, '.', color = color)
    ax2.tick_params(axis='y', labelcolor=color)


    if ws != []:
        fig, ax1 = plt.subplots()
        color = 'red'
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Wind Speed', color=color)
        ax1.plot(t, ae, '.', color = color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()
    
        color = 'blue'
        ax2.set_ylabel('Azimuth - Wind Direction', color=color)
        ax2.plot(t, a, '.', color = color)
        ax2.tick_params(axis='y', labelcolor=color)


    plt.show() 


#main function
def main():
    try:
        while True:
            print("monitoring")
            wind = False
            response = '(Type w and enter to mark as windshake)\a'
            while(abs(eerr) > 0.5 or abs(aerr) > 0.5):
                if telstat == 'SLEW':
                    print("Telescope moving")
                    time.sleep(2)
                else:
                    print("\n%f, %f" % (eerr, aerr))
                    trackOutput(eerr, aerr, el, az, wind, ai)
                    print("Tracking errors are high! %s" % response)
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
            time.sleep(2)

    except KeyboardInterrupt:
        trackOutFile.close()
        yesno = str(raw_input('\nDo you want to display plot? '))
        if yesno in ['yes', 'Yes', 'YES', 'Y', 'y']:
            trackPlot()
        else:
            print('not plotted')

if __name__ == '__main__':
    main()
