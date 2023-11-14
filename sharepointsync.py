## Created the 11/07/19
## By Quentin BEDENEAU
##
## This script sync a CSV file into the Group Sharepoint list.
# You need to get your cookie session to access Sharepoint.
# It is not the best practice but it's working
# The documentation is available in https://docs.microsoft.com/fr-fr/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest

import requests
import os
import sys
import json
import csv
import urllib3
import datetime
import time
import msvcrt
import argparse

start = datetime.datetime.now()
# Argument creation
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Input file that stored the Sharepoint list")
args = parser.parse_args()

login = ""
password= ""
goldenSourceRepo= ""
# cookie de session Group
cookie = ""
sharepointURL=""
sharepointListname=""
compteurError=0
waitingTime = 30

logfile = open("",'w')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #avoid spam due to SSL error

# proxy de mobimax. A retirer dans les requetes si on est sur l'environnement local
proxywifi={}
proxyethernet={}
#Check if the wifi is used to set the proxywifi
if os.popen('ipconfig').read().find("Wireless LAN adapter Wi-Fi:\n\n   Media State . . . . . . . . . . . : Media disconnected")>=0:
	proxy=proxywifi
else:
	proxy=proxyethernet

def waitUser():
	print("\a") # make a bip to wake up the User
	print("script is block and waiting your interraction. Try to refresh the Sharepoint page or verify your connection")
	print("Press any key to continue")
	startTimer= time.time()
	while True:
		if msvcrt.kbhit():
			msvcrt.getch()
			return True
		if time.time() - startTimer > waitingTime:
			return False

def updateRequestDigest(session):
	# Récupération du header requestdigest pour l'utiliser dans les requêtes de mises à jour'
	session.verify= False # deactivate ssl verification to avoid problem with ssl interception
	session.headers.update({"accept":"application/json;odata=verbose"})
	session.headers.update({"Content-Type":"application/json;odata=verbose"})
	session.headers.update({"Cookie":cookie})
	try:
		session.headers.update({"Authorization":authorization})
	except NameError as e:
		# print("authorization is not define")
		pass
	resp = session.post(sharepointURL+"_api/contextinfo",proxies=proxy) ##get x-digest value
	if resp.status_code == 403:
        # print(resp.text)
		raise requests.exceptions.HTTPError('Not authorized to access the request-digest page')
	else:
		if resp.status_code != 200:
			# This means something went wrong
			print(session.headers)
			print(resp.text)
			print(resp.status_code)
			raise requests.exceptions.HTTPError('GET request-digest %s' % (resp.status_code))
		else:
			contextinfo = json.loads(resp.text)
			x_requestdigest=contextinfo["d"]["GetContextWebInformation"]["FormDigestValue"]
			session.headers.update({"x-requestdigest": x_requestdigest})

def getSharepointlist(url,counter):
    print("Number of iteration for getSharepointlist %d" % counter)
    listToComplete = []
    session = requests.Session()
    updateRequestDigest(session)
    resp = session.get(url, proxies=proxy)
    if resp.status_code == 200:
        jsonAnswer = json.loads(resp.text)
        for item in jsonAnswer["d"]["results"]:
            item["Sync"]=False # indicator to know if the item was sync or not.
            listToComplete.append(item)
        if "__next" in jsonAnswer["d"]:
            return listToComplete + getSharepointlist(jsonAnswer["d"]["__next"],counter+1)
        else:
            return listToComplete
    else:
        raise requests.exceptions.HTTPError("Error when requesting the list")
        print(resp.text)

def transformDate(date):
	if date=="" or date is None:
		return None
	else:
		day = date[:2]
		month = date[3:5]
		year = date[6:]
		return year+"-"+month+"-"+day+"T23:00:00Z"

def itemDataQuality(item):
	return # a json oject with your data test to integrate

def updateitem(item,sharepointItemID,compteurError):
	# Think to request the update digest before changing the conent-lenght
	session = requests.Session()
	item['__metadata']={ "type": "SP.Data."+sharepointListname+"ListItem" }
	itemJson = json.dumps(item)
	updateRequestDigest(session)
	session.headers.update({"data":itemJson})
	session.headers.update({"Content-Length":str(len(itemJson))})
	session.headers.update({"IF-MATCH":"*"})
	session.headers.update({"X-HTTP-Method":"MERGE"})
	resp = session.post(sharepointURL+"_api/web/lists/GetByTitle('"+sharepointListname+"')/items("+sharepointItemID+")",data=itemJson,proxies=proxy) ##Request to create in the folder
	if 199 < resp.status_code and resp.status_code < 300:
		print("item %s successfully updated" % item["Actif"])
	else:
		compteurError+=1
		print("[UPDATE] Error for item %s not updated" % item["Actif"], file=logfile)
		print(itemJson,file=logfile)
		print(resp.text, file=logfile)
		print("\n",file=logfile)

def createItem(item,compteurError):
	# Think to request the update digest before changing the conent-lenght
    session = requests.Session()
    item['__metadata']={ "type": "SP.Data."+sharepointListname+"ListItem" }
    itemJson = json.dumps(item)
    updateRequestDigest(session)
    session.headers.update({"data":itemJson})
    session.headers.update({"Content-Length":str(len(itemJson))})
    resp = session.post(sharepointURL+"_api/web/lists/GetByTitle('"+sharepointListname+"')/items",data=itemJson,proxies=proxy) ##Request to create in the folder
    if resp.status_code==200 or resp.status_code==201:
        print("item %s successfully created" % item["Actif"])
        try:
            return json.loads(resp.text) # return the item created so we can get the ID and try to change the folder
            pass
        except Exception as e:
            print(resp.text)
            print(resp.status_code)
            raise
    else:
        compteurError+=1
        print("[CREATION] Error for item %s not created" % item["Actif"], file=logfile)
        print(itemJson,file=logfile)
        print(resp.text, file=logfile)
        print("\n",file=logfile)

def deleteItem(sharepointItemID,compteurError):
	# Think to request the update digest before changing the conent-lenght
	session = requests.Session()
	updateRequestDigest(session)
	session.headers.update({"IF-MATCH":"*"})
	session.headers.update({"X-HTTP-Method":"DELETE"})
	resp = session.post(sharepointURL+"_api/web/lists/GetByTitle('"+sharepointListname+"')/items("+str(sharepointItemID)+")",proxies=proxy)
	if 199 < resp.status_code and resp.status_code < 300:
		print("item %s successfully deleted" % str(sharepointItemID))
	else:
		compteurError+=1
		print("[DELETION] Error for item %s not deleted" % str(sharepointItemID), file=logfile)
		print(itemJson,file=logfile)
		print(resp.text, file=logfile)
		print("\n",file=logfile)

def getSharepointFolderParam(itemID):
	#We need to get the parameter FileDirRef,FileRef before moving to another folder
	session = requests.Session()
	updateRequestDigest(session)
	resp = session.post(sharepointURL+"_api/web/lists/GetByTitle('"+sharepointListname+"')/Items("+str(itemID)+")?$select=FileDirRef,FileRef",proxies=proxy)
	if resp.status_code == 200:
		# print(resp.text)
		return json.loads(resp.text)
	else:
		raise requests.exceptions.HTTPError("Error when requesting the folder parameter")
		# print(resp.text)

def changeSharepointFolder(itemID,newFolder):
	# get sharepoint folder parameter
	folderParam = getSharepointFolderParam(itemID)
	fileURL = folderParam["d"]["FileRef"]
	folderURL = folderParam["d"]["FileDirRef"]
	moveFileURL = fileURL.replace(folderURL,folderURL+"/"+newFolder)

	session = requests.Session()
	updateRequestDigest(session)
	resp = session.post(sharepointURL+"/_api/web/getfilebyserverrelativeurl('" + fileURL + "')/moveto(newurl='" + moveFileURL + "',flags=1)",proxies=proxy)
	if 199 < resp.status_code and resp.status_code < 300:
		return json.loads(resp.text)
	else:
		print("[Change file] Error for item %d not deleted" % itemID, file=logfile)
		print(resp.text, file=logfile)
		print(folderParam, file=logfile)
		print("\n",file=logfile)

def listItemToCreate(dict):
	list=[]
	for key,value in dict.items():
		if not value['sync']:
			list.append(key)
	return list

def CSVToDict(file,dict,sharepointFileName):
	localCounter=0
	with open(file,'r',encoding='utf-8') as csvfile:
		reader = csv.DictReader(csvfile,delimiter=';')
		for row in reader:
			localCounter+=1
			key = row['Entity']+row['Asset']
			key = key.replace(" ","").lower()
			dict[key] ={
			'Entity':row['Entity'],
			'sync':False,
			'sharepointFileName':sharepointFileName}
	return localCounter


counterUpdate = 0
counterDelete = 0
counterCreate = 0
if args.input is None:
    # if a list is already present we can sync with it
    numberSharepointElement = 0
    tempSharepoint = goldenSourceRepo+"Sharepoint_list_"+sharepointListname
    tempGoldenSource = tempSharepoint+"bisgoldensource.txt"
    goldenSourceList = # dict to create
    sharepointItemsList = getSharepointlist(sharepointURL+"_api/web/lists/getbytitle(\'"+sharepointListname+"\')/items",0)
    with open(tempSharepoint+".txt",'w',encoding='utf-8') as file:
        for item in sharepointItemsList:
            numberSharepointElement+=1
            print(json.dumps(item), file=file)
        print("We have %d elements in Sharepoint" % numberSharepointElement)
else :
    tempSharepoint = args.input
    tempGoldenSource = tempSharepoint[:-4]+"goldensource.txt"
    tempSharepoint=tempSharepoint[:-4]# remove the ".txt"
    try:
        goldenSourceList = json.loads(open(tempGoldenSource,'r',encoding='utf-8').read())
    except FileNotFoundError as e:
        print("Are you sure your file exist?")
        raise e

# Update or delete in the list
# on parcours les json du sharepoint pour trouver des correspondances dans notre super fichier
try:
    with open(tempSharepoint+".txt",'r',encoding='utf-8') as readFile, open(tempSharepoint+"bis.txt",'w',encoding='utf-8') as writeFile :
        for line in readFile:
            SharepointItem = json.loads(line)
            if SharepointItem["Sync"]:
                pass
            else:
                try:
                    key = SharepointItem['Title']+SharepointItem['Actif']
                    key = key.replace(" ","").lower()
                    try:
            		# If the key error is throw it mean the asset or the perimeter is not existing or have an input error. So we need to delete it.
            		# It will be created after if it's still existing in the dictionnary
            		# print("update "+goldenSourceList[key]["Actif"])
                        updateitem(itemDataQuality(goldenSourceList[key]),str(SharepointItem['Id']),compteurError)
                        goldenSourceList[key]['sync']=True # We indicate we used the asset in the golden source to update something
                        SharepointItem["Sync"]=True
                        counterUpdate+=1

                    except KeyError as e:
                        counterDelete+=1
                        deleteItem(str(SharepointItem['Id']),compteurError) #The item don't exist anymore. We need to delete it
                        SharepointItem["Sync"]=True
                            pass #The item don't exist in the list
                except Exception as e:
                    raise
                finally:
                    print(json.dumps(SharepointItem), file = writeFile)
    #Create asset not find in sharepoint
    for itemkey in listItemToCreate(goldenSourceList):
        print(itemkey)
        #Modifie directement le dossier de l'objet une fois que celui-ci a été créé.
        sharepointAnswer = createItem(itemDataQuality(goldenSourceList[itemkey]),compteurError)
        if sharepointAnswer is not None:
            changeSharepointFolder(sharepointAnswer["d"]["Id"],goldenSourceList[itemkey]["sharepointFileName"])
            goldenSourceList[itemkey]['sync']=True
        counterCreate+=1
except Exception as e:
    raise
finally:
    with open(tempGoldenSource,'w',encoding='utf-8') as goldensourceFile:
        print(json.dumps(goldenSourceList),file=goldensourceFile)
stop=datetime.datetime.now()
print("script finish in %s" % str(stop-start))
print("number of asset created %d, updated %d, deleted %d, errors %d" % (counterCreate, counterUpdate, counterDelete, compteurError))
