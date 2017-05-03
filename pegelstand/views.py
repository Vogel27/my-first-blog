from django.shortcuts import render
import logging
import datetime
import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from pegelstand.models import PegelZeit, Pegel_long
import pytz



def index(request):
	a=datetime.datetime.today()
	uhrzeit=str(a.hour)+":"+str(a.minute)
	c=verbindungen2(uhrzeit)
	a1=c[0]
	a2=c[1]
	a3=c[2]
	b1 = a1.strftime('%d.%m.%y, %H:%M Uhr')
	b2 = a2.strftime('%d.%m.%y, %H:%M Uhr')
	b3 = a3.strftime('%d.%m.%y, %H:%M Uhr')

	#a1= datetime.datetime.strptime(c[0],"%Y%m%d%H%M%S")
	#a2= datetime.datetime.strptime(c[1],"%Y%m%d%H%M%S")
	#a3= datetime.datetime.strptime(c[2],"%Y%m%d%H%M%S")
	#der neue pegelstand wird aus dem Netz geholt
	aktualisiert=pegelausdemnetz()
	#aus dem letzten aus dem netz geholten Pegel_long soll jetzt alles in PegelZeit überführt werden
	if aktualisiert==1:
		#Zunächst die bestehenden Daten löschen
		pegelstand_loschen()
		#Dann aus der neuen Pegelhtml alles in die lesbare Datenbank übertragen.
		pegel_in_lesbar()
	
	#karl='andere testes'
	karl = uhrzeitfinden2(a1)
	peter = uhrzeitfinden2(a2)
	robert = uhrzeitfinden2(a3)

	abfrage1 = pegelabgleich(karl)
	abfrage2 = pegelabgleich(peter)
	abfrage3 = pegelabgleich(robert)

	
	#b=PegelZeit(Uhrzeit=datetime.datetime.today(), Pegelstand=100, Notation="Test", Kommentar="Testgröße", downloadzeitpunkt=datetime.datetime.today())
	#b.save()
	#peter=PegelZeit.objects.get(zeittext="12:00")
	#karl=str(peter)
	#Die def pegelstand_loschen ermöglicht ein Leeren ALLER DATEN aus dem PegelZeit Modell! Hier also nur für manuelle Arbeiten während der Tests belassen!!!
	#pegelstand_loschen()
	#schreibeinezeit()
	return render(request, 'pegelstand/start.html',{'abfahrt1':b1, 'abfahrt2':b2, 'abfahrt3':b3, 'pegel1':karl, 'pegel2':peter, 'pegel3':robert, 'outcome1':abfrage1, 'outcome2':abfrage2, 'outcome3':abfrage3})
	
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

def pegelausdemnetz():
	#Diese def soll das Prüfen, wann der letzte Pegel_long geholt wurde, und in Abhängigkeit davon das Updaten übernehmen.
	#zunächst muss die Zeitzone definiert werden, damit alle datumsfunktionen vergleichbar sind
	utc=pytz.UTC	
	#Das Abspeichern der Pegel_long funktioniert, allerdings fehlt die If-abfrage zum Zeitpunkt des letzten herunterladens.
	tester2=Pegel_long.objects.all().order_by('-id')[0]
	zeitpuffer=tester2.pegel_html_zeitstempel
	#zeitpuffer scheint seine utc schon zu kennen daher ist die folgende Zeile ausgeblendet
	#zeitpuffer = utc.localize(zeitpuffer)
	#zunächst die aktuelle Zeit
	zeitpuffer2 = datetime.datetime.today()
	#zeitpuffer2 kennt seine utc noch nicht, daher wird diese hier zugewiesen.
	zeitpuffer2 = utc.localize(zeitpuffer2)

	sicherheitsabstand = datetime.timedelta(hours = 1)
	zeitpuffer3 = zeitpuffer+sicherheitsabstand
	aktualisiert=0
	if zeitpuffer3 < zeitpuffer2:
		pegelhtml=pegelstand_holen2()
		pegelhtmlspeichern(pegelhtml)
		aktualisiert=1
	else:
		aktualisiert=0
	return (aktualisiert)
		
def pegelstand_holen2():	
	#Hier soll der Pegelstand geholt und in die datei pegel geschrieben werden
	#Enthalten in pegelausdemnetz
	#print("hier ist pegelstand_holen")
	my_url = 'http://www.bsh.de/aktdat/wvd/lf/StPauli_lf.htm'
	#print("Der aktuelle Pegelstand findet sich online unter: ")
	#print(my_url)
	#HIer wird die Verbindung ins Internet erstellt und die gesammte website herunter  geladen.
	uClient = uReq(my_url)
	#Jetzt wird der gesammte HTML-Text der Internetseite in die Variable page_html gespeichert.
	page_html = uClient.read()
	#Hier wird die Internetverbindung wieder geschlossen (Wichtig!)
	uClient.close()
	#html parsing
	page_soup = soup(page_html, "html.parser")
	#Ausgabe bestimmter Stellen des html-textes
	#print("Das ist der html-ausschnitt: ")
	#print(page_soup.body.div.table.tbody)
	#print(type(page_soup.body.div.table.tbody))
	#Holt sich den den Messwertblock:
	#print("jetzt kommt das find-kommando: ")
	#contents = page_soup.find_all("div",{"id":"content2"})
	#print(contents)
	#contents = page_soup.find_all("table",{"summary":"Messwertgeber am Pegel"})
	#print(contents)
	
	# Das wars früher mal:                                   contents = page_soup.find_all("td",{"align":"right"})
	
	#print(contents)
	
	#contents = page_soup.find_all("map",{"name":"int"})
	contents = page_soup.find_all("area",{"shape":"rect"})
	#print(contents)
	#print("wieviele contents sind es?")
	#print(len(contents))
	#print("Abschnitt 0")
	#print(contents[0])
	#print("Abschnitt 1")
	#print(contents[1])
	#print("Abschnitt 2")
	#print(contents[2])
	
	#print("Abschnitt 2 TEXT:")
	#print(contents[2].text)
	
	#print("Abschnitt 3")
	#print(contents[3])
	
	#Original:                                              pegelausmnetz=contents[2].text
	#print("Hier ist er!!!:")
	#print(pegelausmnetz)
	#Original:                                              pegelausmnetz = int(pegelausmnetz)
	#print(type(pegelausmnetz))
	#Original:                                              return(pegelausmnetz)
	return(contents[0])	
	
def pegelhtmlspeichern(pegelhtml):
	#speichert den html pegel als Pegel_long datei (siehe Models)
	#Enthalten in pegelausdemnetz
	#print("hier ist pegelspeichern")
	#print(pegelhtml)
	timestamp = datetime.datetime.today()
	pegeltitel=str(timestamp)
	pegelstr = str(pegelhtml)
	
	newentry = Pegel_long(pegel_html_titel=pegeltitel, pegel_html_long=pegelstr, pegel_html_zeitstempel=datetime.datetime.today())
	newentry.save()

def schreibeinezeit():
	#hier wird einfach irgendeine Pegelzeit gespeiechert.
	testpegel=PegelZeit(Uhrzeit=datetime.datetime.today(), zeittext='15:00', Pegelstand=100, Notation='Test', Kommentar='Dies ist ein Testeintrag')
	testpegel.save()

def schreibeinezeit2():
	testpegel=PegelZeit(Uhrzeit=datetime.datetime.today(), zeittext='15:00', Pegelstand=100, Notation='Test', Kommentar='Dies ist ein Testeintrag')
	testpegel.save()
	
def pegelstand_loschen():
	PegelZeit.objects.all().delete()
	
def pegel_in_lesbar():
	#hier soll aus dem html-wust ein lesbarer Pegel mit Prognose werden
	lastPegel_long=Pegel_long.objects.all().order_by('-id')[0]
	lasthtml = lastPegel_long.pegel_html_long
	report = 0
	mitternacht = 0
	for line in lasthtml.split('\n'):
		#Die Uhrzeit in eine variabele
		zeit_pegel = line[11:16]
		if zeit_pegel[0:2]=="Ko":
			break
		stunde_ist = int(zeit_pegel[0:2])
		minute_ist = int(zeit_pegel[3:5])
		if stunde_ist==0:
			mitternacht=mitternacht+1
	
		if mitternacht==0:
			b=datetime.datetime(lastPegel_long.pegel_html_zeitstempel.year,lastPegel_long.pegel_html_zeitstempel.month,lastPegel_long.pegel_html_zeitstempel.day, stunde_ist, minute_ist)
		elif mitternacht>0:
			extra=lastPegel_long.pegel_html_zeitstempel.day+1
			b=datetime.datetime(lastPegel_long.pegel_html_zeitstempel.year,lastPegel_long.pegel_html_zeitstempel.month, extra, stunde_ist, minute_ist)
		else:
			report=1
		cm_pegel = line[18:21]
		cm_pegel = int(cm_pegel)
		
		textfornotation=str(stunde_ist)+':'+str(minute_ist)+' Pegel: '+str(cm_pegel)
		
		testpegel=PegelZeit(Uhrzeit=b, zeittext='15:00', Pegelstand=cm_pegel, Notation=textfornotation)
		testpegel.save()
	
def uhrzeitfinden2(uhrzeit):
	#hier soll die gelieferte Uhrzeit in der Liste die unter zeit gespeichert wurde gefunden werden und der dazugehörige pegel zurück geliefert werden
	utc=pytz.UTC	

	uhrzeit_soll = uhrzeit
	uhrzeit_soll = utc.localize(uhrzeit_soll)

	zeitdatei = PegelZeit.objects.all()
	gefunden = 0
	index=0
	letzte_zeit=datetime.datetime.today()
	letzter_pegel=0
	
	
	while gefunden!=1:
		datensatz_ist = zeitdatei[index]
		uhrzeit_ist = datensatz_ist.Uhrzeit
		#uhrzeit_ist = utc.localize(uhrzeit_ist)

		if uhrzeit_ist<uhrzeit_soll:
			letzte_zeit=uhrzeit_ist
			letzter_pegel=datensatz_ist.Pegelstand			
		elif uhrzeit_ist==uhrzeit_soll:
			gefundenezeit=uhrzeit_ist
			gefundenerpegel=datensatz_ist.Pegelstand
			gefunden=gefunden+1			
		elif uhrzeit_ist>uhrzeit_soll:
			gefundenezeit=letzte_zeit
			gefundenerpegel=letzter_pegel
			gefunden=gefunden+1
		else:
			break
		index=index+1
	return (gefundenerpegel)
		
def pegelabgleich(pegel):
	#pegelabgleich soll den aktuellen Pegelstand mit der Durchfahrtshohe vergleichen
	if pegel<415:
		outcome = "0"
		#"der Pegelstand liegt bei " + str(pegel) + " und erlaubt ein problemloses durchfahren der Brucke"
	elif pegel<450:
		outcome = "1"
		#"der Pegelstand liegt bei "+ str(pegel) +" die Durchfahrt unter der Brucke ist problematisch"
	elif pegel<600:
		outcome = "2"
		#"der Pegelstand liegt bei "+ str(pegel) +" der Pegelstand ist extrem hoch! liegt hier ein Fehler vor oder ist Sturmflut?"
	else:
		outcome = "999"
		#"der Pegelstand liegt bei "+ str(pegel) +" der Gefundene Pegelstand ist fehlerhaft!"

	return (outcome)
	
	
	
	
