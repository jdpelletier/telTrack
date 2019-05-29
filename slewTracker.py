import ktl
import time
import numpy as np
import matplotlib.pyplot as plt

az = ktl.cache("dcs", "az")
telstate = ktl.cache("dcs", "AXESTST")
telstate.monitor()

aa = []
ta = []
dsa = []
i = 0

slewOutFile = open('slewOutFile.txt', 'w+')

def main():
    global i
    check = telstate.waitFor("=='SLEW'", timeout=1)
    if check == True:
        ts = time.time()
        azs = float(az.read())
        print("Telescope slewing!")
        telstate.waitFor("=='TRACK'")
        ta.append(time.time() - ts)
        if ta[i] > 1:
            aa.append(abs(azs - float(az.read())))
            dsa.append(aa[i]/ta[i])
            print("Slewed %f at %f d/s." % (aa[i], dsa[i]))
            slewOutFile.write('%f, %f, %f\n' % (aa[i], ta[i], dsa[i]))
            i += 1
            print("Waiting for next slew...")
        else:
            print("Offset ignored.")


if __name__ == '__main__':

    print("Tracking slew times. Waiting for slew....")
    try:
        while True:
            main()

    except KeyboardInterrupt:
        slewOutFile.close()
        dsAverage = np.mean(dsa)
        print("Slewed at an average of %f during tonight." % dsAverage)
        plt.plot(aa, ta, '.') 
        plt.ylabel("Time of slew")
        plt.xlabel("Az distance slewed")
        plt.title("Slew distance vs time")
        plt.show()

