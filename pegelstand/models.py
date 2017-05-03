from django.db import models

class PegelZeit(models.Model):
	Uhrzeit = models.DateTimeField()
	zeittext = models.CharField(default='notim', max_length=5)
	Pegelstand = models.IntegerField()
	Notation = models.CharField(default='Error?', max_length=15)
	Kommentar = models.TextField(blank=True, null=True)
	downloadzeitpunkt = models.DateTimeField(auto_now_add=True, auto_now=False)
	
	def __str__(self):
		return self.Notation

class Pegel_long(models.Model):
	pegel_html_titel = models.CharField(default='999: Leerer Datensatz', max_length=30)
	pegel_html_long = models.TextField(default='999: Leerer Datensatz')
	pegel_html_zeitstempel = models.DateTimeField(blank=True)
	
	def __str__(self):
		return self.pegel_html_titel
	