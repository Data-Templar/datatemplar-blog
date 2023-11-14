## Created the 23/04/2023
## By Quentin BEDENEAU
##
## Purpose is to extract contact information from Linkedin recruiter search

import json
import argparse

# Argument creation
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Input file that stored the Sharepoint list")
args = parser.parse_args()

#Sélection du fichier input
if args.input is None:
    linkedinList = json.loads(open("D:\q_bed\Téléchargement\liste linkedin client.txt",'r',encoding='utf-8').read())
else:
    try:
        linkedinList = json.loads(open(args.input,'r',encoding='utf-8').read())
    except FileNotFoundError as e:
        print("Are you sure your file exist?")
        raise e


with open("D:\q_bed\Téléchargement\linkedin contact"+".csv",'w',encoding='utf-8') as file:
    print("Prénom;Nom;Profession;Société;Date de début;Localisation;lien linkedin",file=file)
    for individu in linkedinList["elements"]:
        lastname=individu["linkedInMemberProfileUrnResolutionResult"]["lastName"]
        firstname=individu["linkedInMemberProfileUrnResolutionResult"]["firstName"]
        profession=individu["linkedInMemberProfileUrnResolutionResult"]["firstName"]
        lienlinkedin=individu["linkedInMemberProfileUrnResolutionResult"]["publicProfileUrl"]
        if len(individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"])!=0:
            profession=individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"][0]["title"]
            societe=individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"][0]["companyName"]
            try:
                localisation=individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"][0]["location"]["displayName"]
            except KeyError as e:
                print("No location for the company?")
                localisation=""
                # raise e
            try:
                stardate=str(individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"][0]["startDateOn"]["month"]) \
                        +"/"+ \
                        str(individu["linkedInMemberProfileUrnResolutionResult"]["currentPositions"][0]["startDateOn"]["year"])
            except KeyError as e:
                print("No startdate for the company?")
                stardate=""
                # raise e
        else:
            profession=societe=localisation=stardate=""
        print(f'{lastname};{firstname};{profession};{societe};{stardate};{localisation};{lienlinkedin}',file=file)



