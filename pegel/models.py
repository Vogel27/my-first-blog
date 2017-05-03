from django.db import models

class Pegel(models.Model):
	comment = models.CharField(max_length=140)
	#hier müsste dann ein Nummernfeld folgen??
	pegelstand = models.TextField()
	date = models.DateTimeField()
	
	def __str__(self):
		return self.comment

class PegelZeit(models.Model):
	Uhrzeit = models.DateTimeField()
	Pegelstand = models.IntegerField()
	Notation = models.CharField(max_length=15)
	Kommentar = models.TextField()
	downloadzeitpunkt = models.DateTimeField()
	
	def __str__(self):
		return self.Uhrzeit
	
