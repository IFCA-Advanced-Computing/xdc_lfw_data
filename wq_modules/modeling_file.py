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
    print(f1)
    print(f2)
    for line in f1:
        if line[0:line.find('=')] in dic:
            f2.write(line.replace(line,line[0:line.find('=')]+" = "+dic[line[0:line.find('=')]]))
        elif line[0:line.find('=')-1] in dic:
            f2.write(line.replace(line, line[0:line.find('=')-1]+" = "+dic[ line[0:line.find('=')-1]]))
        else:
            f2.write(line)
    return f2

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

def gen_uniform_output_bct(out_dic,output,ini_date,end_date):
    f = open(output, 'w')
    for e in out_dic:
        f.write("table-name           'Boundary Section : %i'\n" % e)
        f.write("contents             'Logarithmic         '\n")
        f.write("location             '" + out_dic[e]['Name'] + "               '\n")
        f.write("time-function        'non-equidistant'\n")
        f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
        f.write("time-unit            'minutes'\n")
        f.write("interpolation        'linear'\n")
        f.write("parameter            'time                '                     unit '[min]'\n")
        f.write("parameter            'total discharge (t)  end A'               unit '[m3/s]'\n")
        f.write("parameter            'total discharge (t)  end B'               unit '[m3/s]'\n")
        f.write("records-in-table     2\n")
        f.write("0 %5.2f 9.9999900e+002\n" % out_dic[e]['Flow'])
        f.write("%i %5.2f 9.9999900e+002\n" % (minutes_between_date(ini_date,end_date),out_dic[e]['Flow']))
    f.close()

def csv_to_bct(out_dic,output,input_csv,ini_date,end_date):
    f = open(output, 'w')
    for e in out_dic:
        data = pd.read_csv(input_csv+out_dic[e]['Name']+'.csv',delimiter=';')
        print("Opening ",input_csv+out_dic[e]['Name']+'.csv')
        data['date'] = pd.to_datetime(data['date'])
        line = ''
        #Check date
        if (data['date'].min() <= ini_date):
            i = 0
            f.write("table-name           'Boundary Section : %i'\n" % e)
            f.write("contents             'Logarithmic         '\n")
            f.write("location             '" + out_dic[e]['Name'] + "               '\n")
            f.write("time-function        'non-equidistant'\n")
            f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
            f.write("time-unit            'minutes'\n")
            f.write("interpolation        'linear'\n")
            f.write("parameter            'time                '                     unit '[min]'\n")
            f.write("parameter            'total discharge (t)  end A'               unit '[m3/s]'\n")
            f.write("parameter            'total discharge (t)  end B'               unit '[m3/s]'\n")
            if (data['date'][len(data['date'])-1] < end_date):
                f.write("records-in-table    %i\n" % (len(data['date'])+1))
            else:
                f.write("records-in-table    %i\n" % len(data['date']))
            while i < len(data['date']):
                if (data['date'][i] >= ini_date) and (data['date'][i] <= end_date):
                    if (len(line) == 0) and (data['date'][i] != ini_date):
                        line = "0 %5.2f 9.9999900e+002\n" % (data['Flow'][i])
                        f.write(line)
                    line = "%i %5.2f 9.9999900e+002\n" % ((data['date'][i]-ini_date).seconds/60, data['Flow'][i])
                    f.write(line)
                i = i + 1
            if (data['date'][i-1] != end_date):
                line = "%i %5.2f 9.9999900e+002\n" % (minutes_between_date(ini_date,end_date), data['Flow'][i-1])
                f.write(line)
        else:
            print('Invalid Output flow file')
    f.close()

def gen_uniform_output_bcc(out_dic,output,ini_date,end_date):
    f = open(output, 'w')
    for e in out_dic:
        if "Salinity" in out_dic[e]:
            f.write("table-name           'Boundary Section : %i'\n" % e)
            f.write("contents             'Uniform         '\n")
            f.write("location             '" + out_dic[e]['Name'] + "               '\n")
            f.write("time-function        'non-equidistant'\n")
            f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
            f.write("time-unit            'minutes'\n")
            f.write("interpolation        'linear'\n")
            f.write("parameter            'time                '  unit '[min]'\n")
            f.write("parameter            'Salinity            end A uniform'               unit '[ppt]'\n")
            f.write("parameter            'Salinity            end B uniform'               unit '[ppt]'\n")
            f.write("records-in-table     2\n")
            f.write("0 %5.2f %5.2f\n" % (out_dic[e]['Salinity'],out_dic[e]['Salinity']))
            f.write("%i %5.2f %5.2f\n" % (minutes_between_date(ini_date,end_date),out_dic[e]['Salinity'],out_dic[e]['Salinity']))
        if "Temperature" in out_dic[e]:
            f.write("table-name           'Boundary Section : %i'\n" % e)
            f.write("contents             'Uniform         '\n")
            f.write("location             '" + out_dic[e]['Name'] + "               '\n")
            f.write("time-function        'non-equidistant'\n")
            f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
            f.write("time-unit            'minutes'\n")
            f.write("interpolation        'linear'\n")
            f.write("parameter            'time                '  unit '[min]'\n")
            f.write("parameter            'Temperature           end A uniform'               unit '[C]'\n")
            f.write("parameter            'Temperature           end B uniform'               unit '[C]'\n")
            f.write("records-in-table     2\n")
            f.write("0 %5.2f %5.2f\n" % (out_dic[e]['Temperature'],out_dic[e]['Temperature']))
            f.write("%i %5.2f %5.2f\n" % (minutes_between_date(ini_date,end_date),out_dic[e]['Temperature'],out_dic[e]['Temperature']))
        else:
            print("ERROR: Missing Salinity/Temperature for bcc")  
        
    f.close()

def gen_uniform_intput_dis(in_dic,output,ini_date,end_date):
    f = open(output, 'w')
    for e in in_dic:
        f.write("table-name          'Discharge : %i'\n" % e)
        f.write("contents            'walking   '\n")
        f.write("location            '"+ in_dic[e]['Name'] + "               '\n")
        f.write("time-function       'non-equidistant'\n")
        f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
        f.write("time-unit           'minutes'\n")
        f.write("interpolation       'block'\n")
        f.write("parameter           'time                '                     unit '[min]'\n")
        f.write("parameter           'flux/discharge rate '                     unit '[m3/s]'\n")
        f.write("parameter           'Salinity            '                     unit '[ppt]'\n")
        f.write("parameter           'Temperature         '                     unit '[C]'\n")
        f.write("records-in-table    2\n")
        f.write("0 %5.2f %5.2f %5.2f\n" % (in_dic[e]['Flow'],in_dic[e]['Salinity'],in_dic[e]['Temperature']))
        f.write("%i %5.2f %5.2f %5.2f\n" % (minutes_between_date(ini_date,end_date),in_dic[e]['Flow'],in_dic[e]['Salinity'],in_dic[e]['Temperature']))
    f.close()

def csv_to_dis(in_dic,output_folder,output_name,ini_date,end_date):
    f = open(output_name, 'w')

    for e in in_dic:
        data = pd.read_csv(output_folder+in_dic[e]['Name']+'.csv',delimiter=';')
        print("Opening ",output_folder+e+'.csv')
        data['date'] = pd.to_datetime(data['date'])
        line = ''
        #Check date
        if (data['date'].min() <= ini_date):
            i = 0
            f.write("table-name          'Discharge : %i'\n" % e)
            f.write("contents            'walking   '\n")
            f.write("location            '"+ in_dic[e]['Name'] + "               '\n")
            f.write("time-function       'non-equidistant'\n")
            f.write("reference-time       " + ini_date.strftime("%Y%m%d") + "\n")
            f.write("time-unit           'minutes'\n")
            f.write("interpolation       'block'\n")
            f.write("parameter           'time                '                     unit '[min]'\n")
            f.write("parameter           'flux/discharge rate '                     unit '[m3/s]'\n")
            f.write("parameter           'Salinity            '                     unit '[ppt]'\n")
            f.write("parameter           'Temperature         '                     unit '[C]'\n")
            if (data['date'][len(data['date'])-1] < end_date):
                f.write("records-in-table    %i\n" % (len(data['date'])+1))
            else:
                f.write("records-in-table    %i\n" % len(data['date']))
            while i < len(data['date']):
                if (data['date'][i] >= ini_date) and (data['date'][i] <= end_date):
                    if (len(line) == 0) and (data['date'][i] != ini_date):
                        line = "0 %5.2f %5.2f %5.2f\n" % (data['Flow'][i],data['Sal'][i],data['Temp'][i])
                        f.write(line)
                    line = "%i %5.2f %5.2f %5.2f\n" % ((data['date'][i]-ini_date).seconds/60, data['Flow'][i],data['Sal'][i],data['Temp'][i])
                    f.write(line)
                i = i + 1
            if (data['date'][i-1] != end_date):
                line = "%i %5.2f %5.2f %5.2f\n" % (minutes_between_date(ini_date,end_date), data['Flow'][i-1],data['Sal'][i-1],data['Temp'][i-1])
                f.write(line)
        else:
            print('Invalid Tributary file')

    f.close()
#TODO eliminate (only for testing)
#for line in f1:
#    if "Itdate=" in line or "Itdate =" in line:
#            print(line[-12:-2])
#            f2.write(line.replace(line[-12:-2],'2010-01-01'))
#    else:
#        f2.write(line)
print("miau")
f1 = open('test_1.mdf','r')
f2 = open('test_1_v2.mdf','w')

#Parameters
ini_date_str = '2012-01-01 00:00:00'
end_date_str = '2012-01-05 00:00:00'

fmt = '%Y-%m-%d %H:%M:%S'
ini_date = datetime.strptime(ini_date_str, fmt)
end_date = datetime.strptime(end_date_str, fmt)

#Layers
k = 35
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

#Uniform output
#out_dic = {'Presa': 0.5}
out_dic = {1: {'Name': 'Presa', 'Flow': 1.5}}
presa_bct = 'Presa.bct'
input_csv = 'data/'
csv_to_bct(out_dic,presa_bct,input_csv,ini_date,end_date)
#gen_uniform_output_bct(out_dic,presa_bct,ini_date,end_date)

#out_dic = {'Presa': {'Temperature': 12.5, 'Salinity': 0.03}}
out_dic = {1: {'Name': 'Presa', 'Temperature': 12.5, 'Salinity': 0.03}}
presa_bcc = 'Presa.bcc'
gen_uniform_output_bcc(out_dic,presa_bcc,ini_date,end_date)

#input_dic = {'Duero': {'Flow': 0.4, 'Temperature': 12.5, 'Salinity': 0.03}, 'Revinuesa': {'Flow': 0.4, 'Temperature': 12.5, 'Salinity': 0.03}, 'Ebrillos': {'Flow': 0.4, 'Temperature': 12.5, 'Salinity': 0.03}, 'Dehesa': {'Flow': 0.4, 'Temperature': 12.5, 'Salinity': 0.03}, 'Remonicio': {'Flow': 0.4, 'Temperature': 12.5, 'Salinity': 0.03}}
input_dic = {1: {'Name': 'Duero', 'Salinity': 0.03, 'Temperature': 12.5, 'Flow': 0.4}, 2: {'Name': 'Revinuesa', 'Salinity': 0.03, 'Temperature': 12.5, 'Flow': 0.4}, 3: {'Name': 'Ebrillos', 'Salinity': 0.03, 'Temperature': 12.5, 'Flow': 0.4}, 4: {'Name': 'Dehesa', 'Salinity': 0.03, 'Temperature': 12.5, 'Flow': 0.4}, 5: {'Name': 'Remonicio', 'Salinity': 0.03, 'Temperature': 12.5, 'Flow': 0.4}}
input_dis = 'tributaries.dis'
input_dis_csv_folder = 'data/'
try:
    csv_to_dis(input_dic,input_dis_csv_folder,input_dis,ini_date,end_date)
except:
    gen_uniform_intput_dis(input_dic,input_dis,ini_date,end_date)

#Parameters update
dic = {'Itdate': "#"+ini_date.strftime('%Y-%m-%d')+"#\n", 
       'Tstart': "%i\n" % minutes_between_date(datetime.strptime(ini_date.strftime('%Y-%m-%d'),'%Y-%m-%d'),ini_date), 
       'Tstop': "%i\n" % minutes_between_date(ini_date,end_date),
       'Filwnd': "#" + wind_file_name + "#\n",
       'Filtmp': "#" + rad_file_name + "#\n",
       'FilbcT': "#" + presa_bct + "#\n",
       'FilbcC':"#" + presa_bcc + "#\n",
       'Fildis': "#" + input_dis + "#\n",
       'Zeta0' : "0\n"
      }
#Update params
f2 = update_param_value(dic,f1)

f1.close()
f2.close()
os.rename('test_1.mdf', 'test_1_old.mdf')
os.rename('test_1_v2.mdf', 'test_1.mdf')
