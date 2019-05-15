import ktl
import time
import sys
import select

eerr = ktl.cache("dcs", "elpe")
aerr = ktl.cache("dcs", "azpe")
eerr.monitor()
aerr.monitor()
response = '(Type w and enter to mark as windshake)\a'

try:
    while True:
        print("%f, %f" % (eerr, aerr))
        if(abs(eerr) < 0.5 or abs(aerr) < -1):
            print("Tracking errors are high! %s" % response)
            i, o, e = select.select([sys.stdin], [], [], 2)
            if (i):
                if sys.stdin.readline().strip() == 'w':
                    response = '(Marked as windshake)'
        else:
            time.sleep(2)
except KeyboardInterrupt:
    pass
