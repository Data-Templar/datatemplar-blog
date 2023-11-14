## Created the 09/11/2021
## By Quentin BEDENEAU
## Requirements : datetime, holidays
##
## This script create a csv with the name of the collaborator 
## for the on-call duty based on the parameters 


from datetime import date, timedelta
import holidays

#Variables
#Structure dict : employé name : (nb day, restreindre l'accès, score total)
# nb day = 6 ou 7 si la personne ne veut travailler que le samedi ou le dimanche. Sinon =0 ou autre valeur
dict_employee = {
                    "Albert":[6,0,0],
                    "Bernard":[6,0,0],
                    "Camille":[6,0,0],
                    "Denis":[7,0,0],
                    "Etienne":[7,0,0],
                    "François":[7,0,0],
                    "Greg":[0,1,0],
                    "Hercule":[0,1,0],
                    "Isabelle":[0,0,0],
                    "Julie":[0,0,0],
                    "Kevin":[0,0,0],
                    "Leon":[0,0,0],
                    "Manon":[0,0,0],
                    "Natalie":[0,0,0],
                    "Papa":[0,0,0]
                }
score_moyen = 0
valeur_samedi = 1
valeur_dimanche = 1.5
nb_person_perday = 2
date_debut = date(2021,1,1)
date_fin = date(2021,12,31) 

# def daterange(date1, date2):
#     for n in range(int ((date2 - date1).days)+1):
#         yield date1 + timedelta(n)

def daterange2(date1):
    result=[]
    for i in range(365):
        result.append(date1+timedelta(i))
    return result

def prioriseremployee(dictemployee):
    result = sorted(dictemployee.items(), key=lambda x:x[1][2])
    return result
    # list=[]
    # for employee,score in dictemployee.items():
    #     return



#Création des jours fériés
fr_holidays = holidays.CountryHoliday('FR', years = date_debut.year)
print("nb jour fériée %d"%len(fr_holidays))

#Créer tous les week-end
week_end = [6,7]
list_week_end=[]
for dt in daterange2(date_debut):
    if dt.isoweekday() in week_end:
        #print(dt)
        list_week_end.append(dt)

#construction liste globale à part car fr_holidays est un dictionnaire:
for date in fr_holidays:
    list_week_end.append(date)
all_available_day = list(dict.fromkeys(list_week_end))

## Algo
## Pour chaque jour on affecte le nb de personne nécessaire en vérifiant le score
#Affectation est un dictionnaire avec la date et le personnel associé
affectation = {}
nb_employee = len(dict_employee.keys())
print("Nombre d'employée %d" % nb_employee)

for dt in all_available_day:
    if dt.isoweekday()==6 and dt not in fr_holidays:
        value = valeur_samedi
    if dt.isoweekday()==7 or dt in fr_holidays:
        value = valeur_dimanche
    toassign = [] #Liste des personnes à ajouter à dt
     
    # Permet d'assurer qu'il y a tous les jours d'inclus. ne devrez pas exister
    affectation[dt]=toassign
    compteur = 0
    while compteur < nb_person_perday:
        #priorise les employée
        list_prior = sorted(dict_employee.items(), key=lambda x:x[1][2])
        for tupleemployee in list_prior:
            #tupleemployee[0] = nom de l'employée
            #tupleemployee[1] = score
            if tupleemployee[1][0] == dt.isoweekday() or tupleemployee[1][0] == 0:
                toassign.append(tupleemployee[0])
                if tupleemployee[1][1]==1:
                    coef=2
                else:
                    coef=1
                dict_employee[tupleemployee[0]]=[tupleemployee[1][0],tupleemployee[1][1],tupleemployee[1][2]+value*coef]
                compteur +=1
                break

    # # solution avec boucle for crée des éléments vides
    # for employee,score in dict_employee.items():
    #     if score[0] == dt.isoweekday() or score[0] == 0:
    #         if score[1] == 1:
    #             #calcul moyenne réduite
    #             if score[2] <= score_moyen/2+1:
    #                 toassign.append(employee)
    #                 dict_employee[employee]=[score[0],score[1],score[2]+value]
    #                 score_moyen = score_moyen + value/nb_employee
    #         else:
    #             #calcul normal
    #             if score[2] <= score_moyen+1:
    #                 toassign.append(employee)
    #                 dict_employee[employee]=[score[0],score[1],score[2]+value]
    #                 score_moyen = score_moyen + value/nb_employee

    #     if len(toassign)==nb_person_perday:
    #         affectation[dt] = toassign
    #         break

print(len(affectation))
print(len(all_available_day))
for employee, score in dict_employee.items():
    if score[1]==1:
        print("l'employee %s a un score de %f" %(employee,score[2]/2))
    else:
        print("l'employee %s a un score de %f" %(employee,score[2]))

#Verification du nombre de jour avec un seul collaborateur
for dt,list in affectation.items():
    if len(list)<2:
        print("il manque un collaborateur le %s; liste des collab %s" %(dt,list))

#Extract CSV
with open("listeastreinte.csv",'w',encoding='utf-8') as file:
    for dateastreinte,employee in affectation.items():
        if len(employee) == 2:
            print("%s,%s,%s" % (dateastreinte,employee[0],employee[1]),file=file)
        else:
            print("Erreur sur %s,%s," % (dateastreinte,employee),file=file)
