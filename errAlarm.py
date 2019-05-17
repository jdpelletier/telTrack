import ktl
import time
import sys
import select
import matplotlib.pyplot as plt
import csv

eerr = ktl.cache("dcs", "elpe")
aerr = ktl.cache("dcs", "azpe")
eerr.monitor()
aerr.monitor()
x = []
y = []
z = []

trackOutFile = open('trackingout.txt', 'w+')
ts = time.time()

def trackOutput(ee, ae, wind):
    etime = time.time() - ts
    if wind == True:
        trackOutFile.write('%f, %f, %s, Windshake\n' % (ee, ae, etime))
    else:
        trackOutFile.write('%f, %f, %s\n' % (ee, ae, etime))

def trackPlot():
    infile = open('trackingout.txt','r')
    with infile as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            x.append(float(row[2]))
            y.append(float(row[0]))
            z.append(float(row[1]))

    plt.subplot(2, 1, 1)
    plt.plot(x, y, '.')

    plt.ylabel('Errors')
    plt.title('El Errors')

    plt.subplot(2, 1, 2)
    plt.plot(x, z, '.')

    plt.xlabel('Time')
    plt.ylabel('Errors')
    plt.title('Az Errors')

    plt.show()


try:
    while True:
        wind = False
        response = '(Type w and enter to mark as windshake)\a'
        while(abs(eerr) > 0.5 or abs(aerr) > 0.5):
            print("\n%f, %f" % (eerr, aerr))
            trackOutput(eerr, aerr, wind)
            print("Tracking errors are high! %s" % response)
            sys.stdout.write('>')
            sys.stdout.flush()
            i, o, e = select.select([sys.stdin], [], [], 2)
            if (i):
                if sys.stdin.readline().strip() == 'w':
                    wind = True
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
