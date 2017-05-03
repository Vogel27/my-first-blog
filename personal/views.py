from django.shortcuts import render
import logging
import datetime
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

def index(request):
	return render(request, 'personal/home.html')
	
def contact(request):
	buch = {'content':['Diese Seite ist kein Angebot der Verkehrsbetriebe HVV oder Hadag.','Bei Fragen Kontaktieren sie mich unter','johannes.nostadt[at]gmail.com']}
	return render(request, 'personal/basic.html', buch )

def abfrage(request):
	a=datetime.datetime.today()
	b='pegel3'
	uhrzeit=str(a.hour)+":"+str(a.minute)
	c=verbindungen2(uhrzeit)
	c1=c[0]
	c2=c[1]
	c3=c[2]
	return render(request, 'personal/abfrage.html', {'pegel':['pegel1','pegel2',b] , 'abfahrt1':c1, 'abfahrt2':c2, 'abfahrt3':c3 })

def beispiel(uhrzeit):
	return("pegel200")
	
def beispiel2(uhrzeit):
	if uhrzeit=="12:00":
		var="100"
	else:
		var="200"
	return(var)

	
def verbindungen2(uhrzeit):
	#Hier wird in der neueren Variante eine Liste mit 3 Variablen im Uhrzeitformat weitergegeben!
	zeit_in_einzel=str.split(uhrzeit,":")
	#hier wird das aktuelle datum zum datum1 um daraus, in Verbindung mit der eingegebenen Uhrzeit (zeit_in_einzel) die neue zu suchende Zeitangabe zu machen
	datum1=datetime.datetime.today()
	zeitin1=int(zeit_in_einzel[0])
	zeitin2=int(zeit_in_einzel[1])
	l_zeiteingabe=datetime.datetime(datum1.year,datum1.month,datum1.day, zeitin1, zeitin2)	
	#hier wird geprüft ob es sich um eine Uhrzeit vor der aktuelle handelt, denn dann muss eine Abfahrtszeit am Folgetag gemeint sein
	if l_zeiteingabe.hour<datum1.hour:
		logging.info("es handelt sich um eine Abfahrtszeit vor der aktuellen Stunde, es muss also morgen gemeint sein!")
		l_zeiteingabe=l_zeiteingabe+datetime.timedelta(days=1)
	elif l_zeiteingabe.hour==datum1.hour:
		if l_zeiteingabe.minute<datum1.minute:
			logging.info("es handelt sich um eine Abfahrtszeit vor der aktuellen Minute, es muss also morgen gemeint sein!")
			l_zeiteingabe=l_zeiteingabe+datetime.timedelta(days=1)
	else:
		logging.info("es handelt sich um einen späteren Zeitpunkt am selben Tag!")
	
	#hier wird überprüft ob morgen Samstag oder Sonntag ist, und jeh nachdem der Tag auf den kommenden Werktag geschoben. (Montag wäre 0, Sonntag 6)
	logging.info("Wochentag der Abfrage: ")
	logging.info(l_zeiteingabe.weekday())
	
	if l_zeiteingabe.weekday()==5:
		logging.info("es wird für Samstag gesucht")
		l_zeiteingabe=l_zeiteingabe+datetime.timedelta(days=2)
		#l_zeiteingabe=l_zeiteingabe.hour(0)
		#l_zeiteingabe=l_zeiteingabe.minute(0)
		logging.info(l_zeiteingabe)
	elif l_zeiteingabe.weekday()==6:
		logging.info("es wird für einen Sonntag gesucht")
		l_zeiteingabe=l_zeiteingabe+datetime.timedelta(days=1)
		#l_zeiteingabe=l_zeiteingabe.hour(0)
		#l_zeiteingabe=l_zeiteingabe.minute(0)
		logging.info(l_zeiteingabe)
	
	#print("Eingegebene Zeit zur ubergabe: ")
	#print(l_zeiteingabe)
	taktuell=l_zeiteingabe
	#Fahrplan offenen und counter zuruck setzten
	fahrplandatei=['05:50' , '06:10' , '06:30' , '06:50' , '07:10' , '07:30' , '07:50' , '08:10' , '08:30' , '08:50' , '09:30' , '10:10' , '10:50' , '11:30' , '12:10' , '12:50' , '13:30' , '14:10' , '14:50' , '15:10' , '15:30' , '15:50' , '16:10' , '16:30' , '16:50' , '17:10' , '17:50' , '18:30' , '19:10' , '19:50' , '20:30' , '21:10' , '21:50' , 'end']
	#fahrplandatei = open('fahrplan73' ,'r')
	fahrplandateiindex=0
	gefunden=0
	#hier wird in einer variable die position des zeigers am anfang des dokumentes gemerkt um am ende des fahrplans zuruck zu springen
	#last_pos=fahrplandatei.tell()
	#dayplus ist 0 und wird um 1 erhöht falls der fahrplan zuenede ist
	dayplus=0

	while gefunden!=3:
		#print("start")
		zeit_ist=fahrplandatei[fahrplandateiindex]
		fahrplandateiindex=fahrplandateiindex+1
		if zeit_ist=="end":
			#print("Das Ende des Tages ist erreicht")
			dayplus=dayplus+1
			#wenn das Ende des fahrplans erreicht ist wird der zeiger wieder an den anfang gesetzt
			fahrplandateiindex=0
		else:
			zeit_ist_einzel=str.split(zeit_ist,":")
			datum2=datetime.date.today()
			zeitist1=int(zeit_ist_einzel[0])
			zeitist2=int(zeit_ist_einzel[1])
			if dayplus==0:
				l_zeitfahrplan=datetime.datetime(datum2.year,datum2.month,datum2.day, zeitist1, zeitist2)	
			else:
				datum2=datum2+datetime.timedelta(days=dayplus)
				l_zeitfahrplan=datetime.datetime(datum2.year,datum2.month,datum2.day, zeitist1, zeitist2)
			#print("Gefundene Zeit")
			#print(l_zeitfahrplan)
			t=l_zeitfahrplan
			
			if t<taktuell:
				#print("ist kleiner als gesuchte Zeit")
				t_last=t
			elif t==taktuell:
				#print("treffer, genau")
				if gefunden==0:
					t1=t
				elif gefunden==1:
					t2=t
				elif gefunden==2:
					t3=t
				else:
					print("ERROR")
					break
				gefunden=gefunden + 1
			elif t>taktuell:
				#print("übers Ziel hinaus, also super")
				if gefunden==0:
					t1=t
				elif gefunden==1:
					t2=t
				elif gefunden==2:
					t3=t
				else:
					print("ERROR")
					break
				gefunden=gefunden + 1
			else:
				print("ERROR")
				break		

			
	#print("Abfahrt1:")
	#print(t1)
	#print("Abfahrt2:")
	#print(t2)
	#print("Abfahrt3:")
	#print(t3)
	#fahrplandatei.close()
	return(t1, t2, t3)
	#return(t1)