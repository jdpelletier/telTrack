import os
import matplotlib.pyplot as plt 
import csv 

efile = open('EFiles/envAutK1.arM', 'r')
ofile = open('output.txt', 'w+')

i = 0
c = []
ee = []

with efile as infile, ofile as outfile:
    reader = csv.reader(infile)
    next(reader, None)
    next(reader, None)
    writer = csv.writer(outfile)
    for row in reader:
        if row[0] != '31-Dec-1989' and row[2] == ' ---k1:dcs:pnt:cam0:aut.ELCR   ':
            writer.writerow(row)
            ee.append(float(row[3]))
            c.append(float(i))
            i+=1

plt.plot(c, ee, '.')
plt.show()

os.remove('output.txt')
