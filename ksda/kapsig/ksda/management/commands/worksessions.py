from django.core.management.base import BaseCommand, CommandError
from ksda.models import *
import datetime

class Command(BaseCommand):

	args = '<>'
	def handle(self, *args, **options):
		brothers = Brother.objects.all().filter(active=True,worksessionbrotherinfo__freeThisWeekend=True).order_by("worksessionbrotherinfo__units","-order")
		tasks = WorksessionTask.objects.all().filter(active=True)

		wb = []
		wsl = []

		count = -1	
		today = datetime.date.today()
		#set the day=3 so that today is thursday and it will assign the worksessions for sunday
		#if you change the day that the system assigns worksessions then change the days offset
		date = today + datetime.timedelta(days=3)

		for task in tasks:
			wsl.append(task)

		for b in brothers:
			count += 1
			if (count >= len(wsl)):
				break
			else:
				new_worksession = Worksession.objects.create(date=date,
                                    brotherinfo=b.worksessionbrotherinfo,
                                    task=wsl[count])
    			new_worksession.save()
    	
    	worksessions = Worksession.objects.all()
    	


    		

		