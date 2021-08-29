#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author:    Jaks Wildman
@email:     Jaks.Wildman@Charter.com
@version:   '2.0'
@created:   2021-08-26
@copyright: Cool-Kids ltd 2021
@status:    Complete

@Description:
    Takes a csv list of devices, either hostname or ip and returns a csv file with 
    the input_value, nslookup hostname, nslookup ip, and 'up/down' based on a ping
    
    Output file will be saved in the same location as the script if not specified

v2.0 - remove unused code, change ' if ID_COL == None' to ' if ID_COL is None:', altered pyping to return unknown host
     - supressed ping operation from screen, added id_col pass through
v1.4 - add optional args to allow for output file location, output file name, input_name, input_id cols
v1.3 - Added exception handling around file writing
v1.2 - Changed from 'time' module to 'datetime' module. added input/output vars

"""
import os
import csv
import platform
import socket
import subprocess
from datetime import datetime
import argparse
from dns import resolver


# >>> import dns
# >>> hn = 'FRBRTXJI1CW'
# >>> ip = dns.resolver.query('FRBRTXJI1CW','A')

# >>> for val in ip:
# ...     ip_list.append(val.to_text())
# ...
# >>> print(ip_list)



def pyping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'
    #TODO: Add ping timeout param option (-W)
    
    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]
   
    with open(os.devnull, 'w') as devnull:
        cmd_out = subprocess.call(command,stdout=devnull,stderr=devnull)
        if cmd_out == 68:
            result = 'unknown host'
        elif cmd_out == 2:
            result = 'down'
        elif cmd_out == 0:
            result = 'up'
        else: 
            result = 'down'
        return result
        
    

if __name__== '__main__':
    parser = argparse.ArgumentParser(description="""This script takes a csv of device ips or hostnames and returns status,hostname, and ipAddr""")
    
    parser.add_argument('i',metavar='input_filename',help = 'Name of the Input file')
    parser.add_argument('--l', metavar='lookup_column', default='input_val',help='Which column has the search string? default: %(default)s)')

    parser.add_argument('--o',metavar='output_filename',default='[input_filename]-[date-time].csv',help='Output Filename. default: %(default)s)')
    parser.add_argument('--id',metavar = 'id_column_name',help='Column name of included ID column',default=None)

    args = parser.parse_args()
    
    INPUT_FILENAME = args.i
    INPUT_COL = args.l
    OUTPUT_FILE = args.o
    ID_COL = args.id
    
    
    #devices = {'google.com','24.43.182.51'}
    
    # Define filename variables
    
    SPLIT_FILENAME = INPUT_FILENAME.split(".")
    FILE_TIME = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    if OUTPUT_FILE == '[input_filename]-[date-time].csv':
        OUTPUT_FILENAME = SPLIT_FILENAME[0] + '-output-'+ FILE_TIME +'.csv'
       
    else:
        OUTPUT_FILENAME = OUTPUT_FILE
    

    

    try:
        with open(INPUT_FILENAME,'r') as device_list,open(OUTPUT_FILENAME,'w',newline='') as csvoutput:
            # setup reader
            reader = csv.DictReader(device_list)
            # setup writer with headers
            output = csv.writer(csvoutput)
            csv_hr_list = reader.fieldnames
           
            
            if ID_COL is None:
                headers = [INPUT_COL,'ret_nslookup_hn','ret_nslookup_ip','ret_ping_stat']
            else:
                headers = [INPUT_COL,'ret_nslookup_hn','ret_nslookup_ip','ret_ping_stat',ID_COL]
                
            # write headers
            output.writerow([h for h in headers])
            for r in reader:
                # set column names from input file
                input_val = r[INPUT_COL]
                id_col =''
                if len(headers) == 5:
                    id_col = r[ID_COL]
                
                #reset vals
                ip = ''
                fqdn = ''
                status = ''
                data = ''
                ping_stat = ''

   
                # Run nslookup on hostname
                try: 
                    ip = socket.gethostbyname(input_val)
                except socket.error:
                    ip = 'gethostbyname error'
                    pass
                
                # apply status value based on ping reslts
                ping_stat = pyping(input_val)
                status = ping_stat
                if ping_stat == 'unknown host':
                    fqdn = 'unknown host'
                else:
                    data = socket.getfqdn(input_val)
                    fqdn = data
        
                
        
                # write data 
                output.writerow([input_val]+[fqdn]+[ip]+[status]+[id_col])
        print('\nOutput File:',OUTPUT_FILENAME)
    except FileNotFoundError:
        print('Input file not found')
    except KeyError:
        print('Column value provided not found')
    

