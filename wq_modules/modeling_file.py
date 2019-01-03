import os
import csv
import pandas as pd
from datetime import datetime

def minutes_between_date(ini_date,end_date):
    daysDiff = (end_date-ini_date).days
    print(daysDiff)
    # Convert days to minutes
    minutesDiff = daysDiff * 24 * 60
    return minutesDiff

def update_param_value(dic,f1):

    for line in f1:
        if line[0:line.find('=')] in dic:
            f2.write(line.replace(line,line[0:line.find('=')]+" = "+dic[line[0:line.find('=')]]))
        elif line[0:line.find('=')-1] in dic:
            f2.write(line.replace(line, line[0:line.find('=')-1]+" = "+dic[ line[0:line.find('=')-1]]))
        else:
            f2.write(line)
    return f2

def get_grid_resolution(f1):
    m = ''
    n = ''
    k = ''
    for line in f1:
        if 'MNKmax' in line:
            mnk = line[line.find('=')+2:len(line)]
            m = mnk[0:mnk.find(' ')]
            mnk = mnk[mnk.find(' ')+1:len(mnk)]
            n = mnk[0:mnk.find(' ')]
            mnk = mnk[mnk.find(' ')+1:len(mnk)]
            k = mnk[0:len(mnk)]

    return m,n,k

def csv_to_wind(path, ini_date, end_date, output):
    data = pd.read_csv(path,delimiter=';')
    data['date'] = pd.to_datetime(data['date'])
    f = open(output, 'w')
    line = ''
    #Check date
    if (data['date'].min() <= ini_date):
        i = 0
        while i < len(data['date']):
            if (data['date'][i] >= ini_date) and (data['date'][i] <= end_date):
                if (len(line) == 0) and (data['date'][i] != ini_date):
                    line = "0 %5.3f %5.3f\n" % (data['speed'][i],data['dir'][i])
                    f.write(line)
                line = "%i %5.3f %5.3f\n" % ((data['date'][i]-ini_date).seconds/60, data['speed'][i],data['dir'][i])
                f.write(line)
            i = i + 1
        if (data['date'][i-1] != end_date):
            line = "%i %5.3f %5.3f\n" % (minutes_between_date(ini_date,end_date), data['speed'][i-1],data['dir'][i-1])
            f.write(line)
    else:
        print('Invalid wind file')
    f.close()

def csv_to_tem(path, ini_date, end_date, output):
    data = pd.read_csv(path,delimiter=';')
    data['date'] = pd.to_datetime(data['date'])
    f = open(output, 'w')
    line = ''
    #Check date
    if (data['date'].min() <= ini_date):
        i = 0
        while i < len(data['date']):
            if (data['date'][i] >= ini_date) and (data['date'][i] <= end_date):
                if (len(line) == 0) and (data['date'][i] != ini_date):
                    line = "0 %5.2f %5.2f 0 %5.5f\n" % (data['hum'][i],data['temp'][i],data['rad'][i])
                    f.write(line)
                line = "%i %5.2f %5.2f 0 %5.5f\n" % ((data['date'][i]-ini_date).seconds/60, data['hum'][i],data['temp'][i],data['rad'][i])
                f.write(line)
            i = i + 1
        if (data['date'][i-1] != end_date):
            line = "%i %5.2f %5.2f 0 %5.5f\n" % (minutes_between_date(ini_date,end_date), data['hum'][i-1],data['temp'][i-1],data['rad'][i-1])
            f.write(line)
    else:
        print('Invalid radiation file')
    f.close()

def gen_ini_value(k,value):
    values = ''
    for i in range(0,k):
        values = values + ('    %5.3f\n' % value)
    return values

#TODO eliminate (only for testing)
#for line in f1:
#    if "Itdate=" in line or "Itdate =" in line:
#            print(line[-12:-2])
#            f2.write(line.replace(line[-12:-2],'2010-01-01'))
#    else:
#        f2.write(line)
print("miau")
f1 = open('data/f34.mdf','r')
f2 = open('data/f34_v2.mdf','w')

#Parameters
ini_date_str = '2012-01-01 00:00:00'
end_date_str = '2013-04-05 00:00:00'

fmt = '%Y-%m-%d %H:%M:%S'
ini_date = datetime.strptime(ini_date_str, fmt)
end_date = datetime.strptime(end_date_str, fmt)

#Layers
print("Get GRID resolution")
m,n,k = get_grid_resolution(f1)
print(minutes_between_date(ini_date,end_date))

#Check Wind file
print("Searching Wind data")
print("Getting data")
wind_input = 'data/wind_test.csv'
print("Creating file .wnd")
wind_file_name = "wind_"+ini_date.strftime('%Y-%m-%d%H%M%S')+"_"+end_date.strftime('%Y-%m-%d%H%M%S')+".wnd"
csv_to_wind(wind_input, ini_date, end_date, wind_file_name)
print("Wind file created: %s" % wind_file_name)


#Check initial conditions
#TODO For the moment, only with uniform values
print("Searching Initial data")
print("Getting initial data")
print("Creating initial data file .ini")
ini_file_name = "initial_"+ini_date.strftime('%Y-%m-%d%H%M%S')+"_"+end_date.strftime('%Y-%m-%d%H%M%S')+".ini"
print("Initial file created: %s" % ini_file_name)

#Check Radiation file
print("Searching Radiation data")
print("Getting data")
rad_input = 'data/rad_test.csv'
print("Creating file .tem")
rad_file_name = "rad_"+ini_date.strftime('%Y-%m-%d%H%M%S')+"_"+end_date.strftime('%Y-%m-%d%H%M%S')+".tem"
csv_to_tem(rad_input, ini_date, end_date, rad_file_name)
print("Radiation file created: %s" % rad_file_name)

#Input-Output flow
print("Searching flow data")
print("Getting data")


#Input-Output physical
print("Searching tributaries data")
print("Getting data")

#Parameters update
dic = {'Itdate': "#"+ini_date.strftime('%Y-%m-%d')+"#\n", 
       'Tstart': "%i\n" % minutes_between_date(datetime.strptime(ini_date.strftime('%Y-%m-%d'),'%Y-%m-%d'),ini_date), 
       'Tstop': "%i\n" % minutes_between_date(ini_date,end_date),
       'Filwnd': "#" + wind_file_name + "#\n",
       'Filtmp': "#" + rad_file_name + "#\n",
       'S0' : ""+ gen_ini_value(35,0.03),
       'T0' : ""+ gen_ini_value(35,10.2),
       'Zeta0' : "0\n"
      }
#Update params
#f2 = update_param_value(dic,f1)

f1.close()
f2.close()
#os.rename('data/f34.mdf', 'data/f34_old.mdf')
#os.rename('data/f34_v2.mdf', 'data/f34.mdf')
