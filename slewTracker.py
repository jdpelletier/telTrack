import ktl
import time
import numpy as np

az = ktl.cache("dcs", "az")
telstate = ktl.cache("dcs", "AXESTST")
az.monitor()
telstate.monitor()

aa = []
ta = []
dsa = []
i = 0

slewOutFile = open('slewOutFile.txt', 'w+')

def main():
    try:
        while True:
            print("Tracking slew times.")
            print("Waiting for slew....")
            telstate.waitFor("=='SLEW'")
            ts = time.time()
            azs = az
            print("Telescope slewing")
            telstate.waitFor("=='TRACKING'")
            ta[i] = time.time() - ts
            aa[i] = abs(azs - az)
            dsa[i] = azd/tf
            print("Slewed %f at %f d/s.", % (aa[i], dsa[i]))
            slewOutFile.write('%f, %f, %f', % (aa[i], ta[i], dsa[i]))
            i += 1

    except KeyboardInterrupt:
        slewOutFile.close()
        dsAverage = np.mean(dsa)
        print("Slewed at an average of %f during tonight.", % dsAverage)
        plt.plot(aa, ta)
        plt.ylabel("Time of slew")
        plt.xlabel("Az distance slewed")
        plt.title("Slew distance vs time")
        plt.show()

if __name__ == '__main__':
    main()
