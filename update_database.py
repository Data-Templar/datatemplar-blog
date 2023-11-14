## Created by Quentin BEDENEAU
##
## This script update a database (option with dev) with a SQL files.
## It delete the mysql data and then update the data from the files

import pymysql, datetime, argparse, re, warnings
try:
    from tqdm import tqdm
    tqdmimport = True
except ImportError as e:
    tqdmimport = False
    print("Enable to import the progress bar value. Please install tqdm if you want a progress bar")

# Argument creation
parser = argparse.ArgumentParser()
parser.add_argument("--dev", help="Update data in dev instead of production", action='store_true')
parser.add_argument("sqlfile", help="Path of the sql file to import")
args = parser.parse_args()

if args.dev:
    database='devdatabaseurl'
    port=3945
    user="databaseusername"
    passwd="databasepassword"
else:
    database='databaseurl'
    port=3945
    user="databaseusername"
    passwd="databasepassword"

def exec_sql_file(cursor, sql_file):
    statement = ""
    if tqdmimport:
        #count the number of line for the progress bar
        i=0
        for count in sql_file:
            i+=1
        linenumber = i
        print("%s lines to integrate " % str(linenumber))
        sql_file.seek(0) #reset the file readiness
        for line in tqdm(sql_file,total=linenumber):
            if re.match(r'--', line) or line=="\n" or line=="\r\n":  # ignore sql comment lines
                continue
            if not re.search(r';$', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for next statement
                statement = statement + line
                #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                    # print("at ligne %d, the statement is %s" %(j,statement))
                        cursor.execute(statement)
                except Exception as e:
                    print("\n[WARN] MySQLError during execute statement \n\tArgs: %s" % (str(e.args)))
                    print(statement)
                statement=""
    else:
        for line in sql_file:
            if re.match(r'--', line) or line=="\n" or line=="\r\n":  # ignore sql comment lines
                continue
            if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for next statement
                statement = statement + line
                #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                    # print("at ligne %d, the statement is %s" %(j,statement))
                        cursor.execute(statement)
                except (pymysql.err.InternalError, pymysql.err.ProgrammingError) as e:
                    print("\n[WARN] MySQLError during execute statement \n\tArgs: %s" % (str(e.args)))
                statement = ""

with open(args.sqlfile,'r',encoding='utf-8') as file:
    print("0-Connection to the database")
    connection = pymysql.connect(host=database, port=port, user=databaseusername, passwd=databasepassword, db='tablename',cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    print("1-Deletion of previous data")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cursor.execute("DROP TABLE IF EXISTS ") # to complete
    cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    print("2-Updating Data")
    exec_sql_file(cursor,file)
    connection.commit() #push change in the database
    cursor.close()
    connection.close()
    print("Enjoy")
