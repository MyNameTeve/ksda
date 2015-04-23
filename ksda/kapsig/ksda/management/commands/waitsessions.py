from django.core.management.base import BaseCommand, CommandError
from ksda.models import *
import datetime

class Command(BaseCommand):

	args = '<>'
	def handle(self, *args, **options):
		#filter by free that day and active then order by units and order
		monday = Brother.objects.all().filter(active=True, waitsessionbrotherinfo__freeM = True).order_by("waitsessionbrotherinfo__units","-order")
		tuesday = Brother.objects.all().filter(active=True, waitsessionbrotherinfo__freeT = True).order_by("waitsessionbrotherinfo__units","-order")
		wednesday = Brother.objects.all().filter(active=True, waitsessionbrotherinfo__freeW = True).order_by("waitsessionbrotherinfo__units","-order")
		thursday = Brother.objects.all().filter(active=True, waitsessionbrotherinfo__freeH = True).order_by("waitsessionbrotherinfo__units","-order")
		friday = Brother.objects.all().filter(active=True, waitsessionbrotherinfo__freeF = True).order_by("waitsessionbrotherinfo__units","-order")
		
		# m = []
		# t = []
		# w = []
		# h = []
		# f = []
		# for b in monday:
		# 	m.append(b)
		# for b in tuesday:
		# 	t.append(b)
		# for b in wednesday:
		# 	w.append(b)
		# for b in thursday:
		# 	h.append(b)
		# for b in friday:
		# 	f.append(b)
		# days = [m,t,w,h,f]
		# days.sort()

		count = -1	
		today = datetime.date.today()
		#set an offset to add tot he current day to get to the closest sunday then add to 
		#get the desired day
		offset =  6 - datetime.date.today().weekday()
		#determine the date of the week for the different wait session days
		m = today + datetime.timedelta(days=(offset+1))
		t = today + datetime.timedelta(days=(offset+2))
		w = today + datetime.timedelta(days=(offset+3))
		h = today + datetime.timedelta(days=(offset+4))
		f = today + datetime.timedelta(days=(offset+5))
		#loop through all the brothers available for the given day and give them that waitsession
		#once 3 are assigned break out of the loop
		for b in monday:
			count += 1
			if (count >= 3):
				break
			else:
				new_waitsession = Waitsession.objects.create(date=m, brotherinfo=b.waitsessionbrotherinfo)
    			new_waitsession.save()
  
    	
			count = -1
	    	for b in tuesday:
				count += 1
				if (count >= 3):
					
					break
				else:
					new_waitsession = Waitsession.objects.create(date=t, brotherinfo=b.waitsessionbrotherinfo)
	    			new_waitsession.save()
	    	count = -1			
	    	for b in wednesday:
				count += 1
				if (count >= 3):
					
					break
				else:
					new_waitsession = Waitsession.objects.create(date=w,
	                                    brotherinfo=b.waitsessionbrotherinfo)
	    			new_waitsession.save()
	    	count = -1
	    	for b in thursday:
				count += 1
				if (count >= 3):
					
					break
				else:
					new_waitsession = Waitsession.objects.create(date=h,
	                                    brotherinfo=b.waitsessionbrotherinfo)
	    			new_waitsession.save()
	    	count = -1
	    	for b in friday:
				count += 1
				if (count >= 3):
					
					break
				else:
					new_waitsession = Waitsession.objects.create(date=f,
	                                    brotherinfo=b.waitsessionbrotherinfo)
	    			new_waitsession.save()
    	

    	
    	
    	


    		

		