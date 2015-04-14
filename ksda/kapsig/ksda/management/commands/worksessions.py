from django.core.management.base import BaseCommand, CommandError
from ksda.models import *
import datetime

from django.core.mail import send_mail

class Command(BaseCommand):

	args = '<>'
	def handle(self, *args, **options):
		brothers = Brother.objects.all().filter(active=True,worksessionbrotherinfo__freeThisWeekend=True).order_by("worksessionbrotherinfo__units","-order")
		tasks = WorksessionTask.objects.all().filter(active=True)

		wb = []
		wsl = []

		count = -1	
		#use offset to find the number of days till sunday
		offset =  6 - datetime.date.today().weekday()
		today = datetime.date.today()
		# then offset the current day to get the date of the next sunday
		date = today + datetime.timedelta(days=offset)
		

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
    			email = [b.email]
    			email_body = """
            	You have been assigned the worksession %s for %s
        		""" % (wsl[count], date)

       
        
    
    			#send the email to the person who got that worksession
    			send_mail(subject="New Worksession Assignment",
                	message=email_body,
                	from_email="kappasigmadeltaalpha@gmail.com",
                	recipient_list=email)
    	
    	worksessions = Worksession.objects.all()
    	


    		

		