#! /usr/bin/env python3.4
#! -*- coding: utf-8 -*-
'''
Created on 27 lip 2015

@author: kamil@justnet.pl
'''

# #############################################################################
# standard modules (moduly z biblioteki standarowej pythona)
# #############################################################################
import os
import sys
import re
import time
import argparse
import subprocess
import getpass
import csv
import datetime
#import uuid
#import types
import shutil
import errno
from builtins import bool

REAL_DIR = os.path.realpath(__file__)
SPLIT_DIR = os.path.dirname(REAL_DIR)
LIB_DIR = SPLIT_DIR+'/.'+os.path.basename(__file__)+'/cache/lib/'
sys.path.insert(0,LIB_DIR)
# from init import init_full

# Wyłączone bo nie potrzebne
#List of lib to install
import_list = [
#   ('sqlalchemy','1.0.8','SQLAlchemy-1.0.8.egg-info'),
#   ('paramiko','1.15.2','paramiko-1.15.2.dist-info'),
   ('colorama','0.3.3','colorama-0.3.3.egg-info')
]

for line in import_list:
   try:
      if os.path.isdir(LIB_DIR+line[2]):
         pass
#         print('Found installed '+line[0]+line[1]+' in '+line[2])
      else:
         try:
            import pip
         except:
            print("Use sudo apt-get install python3-pip")
            sys.exit(1)
         print('No lib '+line[0]+'-'+line[1])
         os.system("python"+sys.version[0:3]+" -m pip install '"+line[0]+'=='+line[1]+"' --target="+LIB_DIR)
      module_obj = __import__(line[0])
      globals()[line[0]] = module_obj
   except ImportError as e:
      print(line[0]+' is not installed')

# #############################################################################
# constants, global variables
# #############################################################################
SOME_GLOBAL_VARIABLE = 0
OUTPUT_ENCODING = 'utf-8'
DIRECTORY = './'
SEARCH_DIR = os.path.split(SPLIT_DIR)
acorder_dir = os.path.realpath(os.path.join(SEARCH_DIR[0],'.htaccess_order'))
DRIVERNAME_MAPPING = {'oracle': {'config/mysql_connect.php.dist':'oracle',
                                 'ds/src/config/config.php.dist':'oci8'},
                      'mysql': {'config/mysql_connect.php.dist':'mysqli',
                                'ds/src/config/config.php.dist':'pdo_mysql'}}
DRIVERNAME_MAPPING['mariadb'] = DRIVERNAME_MAPPING['mysql']

# #############################################################################
# functions
# #############################################################################
#CZYTANIE Z PLIKU
def readfile(file_name):
   try:
      with open(file_name, 'r') as file:
         templines = [line.rstrip('\n') for line in file]
         lines=list()
         for line in templines:
#            if line.startswith('#'): #w konfiguracji nie potrzebne
            lines.append(line)
   except (IOError, OSError):
      print >> sys.stderr, "Can't open file."
      sys.exit(1)
   return lines

#Kolorowanie ok
def print_ok(output):
   print(colorama.Fore.GREEN+output,colorama.Fore.RESET)

#Kolorowanie błędu
def print_err(error):
   print(colorama.Fore.RED+error,colorama.Fore.RESET)

#Wykonywanie poleceń w terminalu
def os_call(*args,progress_char='*',verbose=1):
   n = 0
   done_cmd = list()
   out = list()
   for cmd in args:
      p = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=DIRECTORY)
      (output,err) = p.communicate()
      n = n+1
      ast = progress_char*n
      if err or 'ERROR' in str(output) or 'Exception' in str(output):
         done_cmd.append(cmd)
         ERROR_FLAG = 'T'
         print_err(cmd)
         if err:
            print_err(err.decode(OUTPUT_ENCODING))
            out.append(err.decode(OUTPUT_ENCODING))
            break
         else:
            print_err(output.decode(OUTPUT_ENCODING))
            out.append(output.decode(OUTPUT_ENCODING))
            break
      else:
         ERROR_FLAG = 'F'
         done_cmd.append(cmd)
         out.append(output.decode(OUTPUT_ENCODING))
         if verbose == 2:
            print(ast,end="\r")
            time.sleep(1)
            print_ok(cmd)
            print_ok(output.decode(OUTPUT_ENCODING))
         elif verbose == 1:
            print_ok(output.decode(OUTPUT_ENCODING))
         else:
            print(ast,end='\r')
   return ERROR_FLAG,done_cmd,out

# Paramiko example
def logonssh(server,loginssh,cmd):
   try:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(server,port=22,username=loginssh,password=getpass.getpass('SSH Password: '))
      stdin,stdout,stderr = ssh.exec_command(cmd)
      output = stdout.readlines()
      error = stderr.readlines()
      if error:
         for line in error:
            print(line)
      else:
         for line in output:
            print(line)
      ssh.close()
   except Exception as e:
      print(e)

# CSV write example
def csv_write(file_name, temp):
   with open(file_name, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=temp)
      writer.writerow(['example','date','for','csv'])
      writer.writerow(['example']*4)
# CSV read example
def csv_read(file_name, temp):
   with open(file_name, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=temp)
      for row in reader:
         print(row)

# SQLAlchemy simple example
def simple_query(query):
   dbpass=getpass.getpass("DB Password: ")
   engine = sqlalchemy.create_engine("mysql+pymysql://sandbox:"+dbpass+"@195.54.47.34/sandbox")
#   engine = create_engine(dialect+driver://username:password@host:port/database)
   connection = engine.connect()
   result = connection.execute(query)
   for row in result:
      print(row)
   connection.close()

def find_all_file():
   list_of_file = list()
   for root, subFolders,files in os.walk(SEARCH_DIR[0]):
      for filein in files:
         if filein.endswith('.dist'):
            list_of_file.append(os.path.abspath(os.path.join(root,filein)))
   return list_of_file 

def find_file_backup(args):
   backup_file = list()
   for root, subFolders, files in os.walk(SEARCH_DIR[0]):
      for filein in files:
         if 'BACK' in filein:
            if args in filein:
               backup_file.append(os.path.abspath(os.path.join(root,filein)))
   if backup_file == None:
      print("No backup file like you want")
   else:
      return backup_file

def find_last_backup(args):
   backup_file = list()
   for root, subFolders, files in os.walk(SEARCH_DIR[0]):
      for filein in files:
         if 'BACK' in filein:
            if args=='last':
               backup_file.append(os.path.abspath(os.path.join(root,filein)))
   return max(backup_file, key=os.path.getmtime)
               
      
def make_tuple_check(list_of_file):
   tup = list()
   for line in list_of_file:
      tup.append(line)
      tup.append(line[:-5])
   return tup

def make_tuple_back(list_of_file,back_up_files):
  lst = [None]*(len(list_of_file)+len(back_up_files))
  temp_list = list()
  for one in list_of_file:
     temp_list.append(one[:-5])
  lst[::2] = temp_list
  lst[1::2] = back_up_files
  lst.sort()
  return lst

def read_markers(ffilename,args):
   lst = list()
   if(os.path.isfile(ffilename)):
      lines = ''
      with open(ffilename, 'r') as file:
         lines = file.read()
      if args == 'check':
         pattern = re.compile(':[0-9A-Z_]+::')
      else:
         pattern = re.compile(':[0-9A-Z_]+::[\\w*\\W*\\s*][^:]+[# |/*]::[0-9A-Z]+:',flags=re.DOTALL)
      res = pattern.findall(lines)
      lst = list(set(res))
   return lst

def check_to_dist(args):
   root_path = SEARCH_DIR[0]
   fxnam = lambda fullname, rootname: fullname[len(rootname):].lstrip(os.sep)
   if args =='check':
      tup = tuple(make_tuple_check(list_of_file))
   else:
      tup = tuple(make_tuple_back(list_of_file,back_up_files))
   for dist, prod in zip(*[iter(tup)]*2):
      dlist, dstat = (read_markers(dist,args), True) if os.path.isfile(dist) else (list(), False)
      plist, pstat = (read_markers(prod,args), True) if os.path.isfile(prod) else (list(), False)
      cclst        = list(set(dlist + plist))
      cclst.sort()
      print('[dist: {} -> prod: {}]'.format(fxnam(dist, root_path) if dstat else 'NOT FOUND',fxnam(prod, root_path) if pstat else 'NOT FOUND'))
      miss = 0
#      print(cclst)
#      for one in cclst:
#          print(one)
      for marker in cclst:
#         print(marker)
         if marker in dlist and not marker in plist:
            miss = miss + 1
            print('   Marker "{}" missing in prod file'.format(marker))
         elif not marker in dlist and marker in plist:
            miss = miss + 1
            print('   Marker "{}" missing in dist file'.format(marker))
      if miss == 0:
         print('   Markers are the same in both files')

def acorder_read(acorder_dir, *argv):
   result = ''
   for arg in argv:
      file = os.path.join(acorder_dir,arg)
#      print(file)
      if not os.path.isfile(file):
         raise Exception('File with name {val} for option {opt} not found in .htaccess_order directory'.format(val=arg, opt=args.acorder))
      with open(file,'r') as input_file:
         content = input_file.read()
         if len(content)>0:
            result += content + os.linesep
   return result

def build_from_dist(values,input_file):
   lines = readfile(input_file)
   with open(input_file[:-5],'w') as new_file:
      for line in lines:
         for key in values:
            if '{{#'+key+'}}' in line:
               line = line.replace('{{#'+key+'}}',str(values[key]))
#        print(line)
         new_file.write(line+'\n')

def mapping_driver(input_file, driver):
   for element in DRIVERNAME_MAPPING:
      for key,value in DRIVERNAME_MAPPING[element].items():
         if input_file == os.path.abspath(key) and element == driver:
            return value

# #############################################################################
# classes
# #############################################################################

class SomeClass:

   def __init__(self, some_param1, some_param2, some_param3):
      pass

   def some_method(self, some_param1):
      pass

# #############################################################################
# operations
# #############################################################################

def opt_backup(values,one,date):
   print("File "+os.path.basename(one[:-5])+' exists, creating backup.')
#   date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
   os.system("mv "+one[:-5]+" "+one[:-5]+"_BACK_"+date)
   build_from_dist(values,one)

def opt_no_backup(values,one):
   print("File not exists, creating "+os.path.basename(one[:-5])+'.')
   build_from_dist(values,one)

def opt_help():
   parser.print_help()

def opt_rwbase(rwbase):
   valrgx = re.compile('[\W_-]+[[\W_-]*]')
   if re.match(valrgx,rwbase) or rwbase.endswith('/') or rwbase.startswith('/'):
      raise Exception('RWBASE not match to pattern')
   else:
      return rwbase

def opt_key_firm(key_firm):
   key='KEY'
   value=''
   if '=' in key_firm:
      key,value = key_firm.split('=')
#   print(key,value)
   return key,value

def opt_userpass(userpass):
   if args.userpass == None:
      USERPASS = getpass.getpass('Password to database')
   else:
      USERPASS = args.userpass
   return USERPASS

# #############################################################################
# main app 
# #############################################################################
if __name__ == '__main__':
# Czytanie arugmentów
   epilog_text = '''Example of usage:\n
$build.py -d mariadb -u user -p secret -s database_name\n
$build.py -d mysql -H 127.0.0.1 -P 123 -u user -p secret -s database_name\n'''
   parser = argparse.ArgumentParser(prog='reconf.py', description='Build config file from file with extension .dist',epilog=epilog_text, add_help=True, argument_default=argparse.SUPPRESS)
   parser.add_argument('--drivername', '-d', help='Driver name (required), allowed: mariadb, mysql, oracle.', type=str, choices=['mysql','mariadb','oracle'])
   parser.add_argument('--host','-H', default='localhost', help='Database url/ip address (optional, default: localhost.')
   parser.add_argument('--username', '-u', default='root',help='Database user name/login (optional), default: root.')
   parser.add_argument('--userpass', '-p', default='', nargs='?', help='Database user password (optional), no password as default, if used without value you will be asked to write password in prompt.')
   parser.add_argument('--sid', '-S', default='XE', help='Database sid (optional), only for oracle, default: XE.')
   parser.add_argument('--mode', '-m', type=str, default='prod', choices=['dev','prod'], help='dev|prod (optional), default prod.')
   parser.add_argument('--acorder', '-o',default='_empty', choices=['_dev','_empty','_pulawy'], help="Add order section from .htaccess_order directory, eg. --o _pulawy will add entries in .htaccess file to section 'Order allow, deny'.")
   parser.add_argument('--schema', '-s', help='Database schema name (required for mariadb/mysql).')
   parser.add_argument('--port', '-P', help='Database port number (optional), default: 1521 (oracle), 3306 (mysql/mariadb).')
   parser.add_argument('--check', '-c', action='store_true', help='Check dist file are same as production (configured ones).')
   parser.add_argument('--rwbase', '-b', help="Set rewrite in .htaccess (optional), staring start and end character can't be / (forward slash)Check dist file are same as production (configured ones).")
   key_firm_value = ["","KEY_FIRM=","KEY_FIRM=_pulawy","KEY_FIRM=_smp"]
   parser.add_argument('--key','-k',nargs='+',type=str, default='',choices=key_firm_value, help = 'Set parameter (optional), default empty string, allowed keys: KEY_FIRM, allowed values for KEY_FIRM: empty, _pulawy, _smp; indicate begavior change with some files (that have this parameter value as suffix in name, eg. for _pulawy there are files like htmltopdf_pulawy.php, that are used instead of defaults, usage -k KEY_FIRM=_pulawy.')
   parser.add_argument('--check_back','-C', nargs='?', help='Check production with backup file. Default last backup, as argument name of backup file to check.')
   argv = sys.argv[1:]
   args = parser.parse_args(argv)
   list_of_file = find_all_file()
   values = dict()
   values['PATH'] = SEARCH_DIR[0]
   values['LOGFILE'] = os.path.abspath(os.path.join(SEARCH_DIR[0],'ds','src','vendor','log4php.log'))
   values['DS_DIR'] = os.path.abspath(os.path.join(SEARCH_DIR[0],'ds','src'))
   values['RWBASE'] = '/'
   try:
# Brak argumentów - wyświetl pomoc
      if len(sys.argv) <= 1 or 'help' in args:
         opt_help()
      if 'check' in args:
         check_to_dist('check')
      elif 'check_back' in args:
         if args.check_back == None:
            num_of_back = 'last'
            num_of_back = find_last_backup(num_of_back)[-19:]
         else:
            num_of_back = args.check_back
         back_up_files = find_file_backup(num_of_back)
         check_to_dist('back')
      else:
         if 'key' in args:
            for one in args.key:
               key,value = opt_key_firm(one)
               values[key] = value
         if 'rwbase' in args:
            values['RWBASE'] = opt_rwbase(args.rwbase)
         if 'drivername' in args:
            values['HOSTNAME'] = args.host 
            values['USERNAME'] = args.username
            if 'userpass' in args:
               values['USERPASS'] = opt_userpass(args.userpass)
#           MARIADB I MYSQL
            if 'mariadb' in args.drivername or 'mysql' in args.drivername:
               if 'schema' not in args:
                  raise Exception('-s/--schema is required for mariadb/mysql')
               else:
                  values['SCHEMA'] = args.schema
                  if 'port' in args: PORT = args.port
                  else: PORT = 3306
                  DRIVERNAME = args.drivername
            else:  # ORACLE
               DRIVERNAME = args.drivername
               if 'port' in args: PORT = args.port
               else: PORT = 1521
               if 'schema' in args:
                  values['SCHEMA'] = args.schema
            values['PORT'] = PORT
         else:
            raise Exception('Argument --drivername/-d is required.')
         values['SID'] = args.sid
         values['MODE'] = args.mode
         values['ACORDER'] = args.acorder
         if values['MODE'] == 'dev':
            values['ACORDER'] += os.sep + '_dev'
         values['ACORDER'] = values['ACORDER'].split(os.sep)
         values['ACORDER'] = acorder_read(acorder_dir, *values['ACORDER'])
         values['RWBASE_RTRIM'] = values['RWBASE']
#         print(values)

#Działanie na plikach
         date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
         for one in list_of_file:
            values['DRIVERNAME'] = mapping_driver(one,DRIVERNAME)
            if os.path.exists(one[:-5]):
               opt_backup(values,one,date)
            else:
               opt_no_backup(values,one)
         print('Done')
   except:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      print('ERROR: <{type}> {mess}'.format(type=exc_obj.__class__.__name__, mess=exc_obj))
