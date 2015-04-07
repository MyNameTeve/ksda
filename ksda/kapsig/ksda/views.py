from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import Http404

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

from ksda.models import *
from ksda.forms import *
from ksda.s3 import *

# Import all other views to this main file.
from views_profile import *
from views_waitsession import *
from views_worksession import *
from views_ec import *
from views_brotherRoll import *
from views_forum import *
from views_threads import *
from views_documents import *
from views_finances import *
from views_calendar import *

"""
Only called when DB is empty. First brother will get EC powers.
"""
@transaction.atomic
def initializeBrotherhood(brother):
    """
    ec = Group.objects.create(name='ec')
    ec.save()

    membership = Membership(person=brother,group=ec)
    membership.save()
    """

    admin = Role(name='Admin',
                 finePower=True,
                 worksessionPower=True,
                 waitsessionPower=True,
                 ecPower=True,
                 brother=brother)
    admin.save()
    
    """
    Note: To remove this membership later, 
    m = Membership.objects.get(person=brother,group=ec)
    m.delete()
    """

    # Used for pre-populating database with roles.
    initializeRoles()
    
    # Used for pre-populating database with already existing documents.
    documents = initializeDocuments()



    for document in documents:
        filename = document.name
        url = document.generate_url(expires_in=0, query_auth=False)
        new_document = Document(user=brother.user,
                                filename=filename,
                                url=url)
        new_document.save()

    #add the work sessions to the data bases
    initializeWorksessions()

@transaction.atomic
def register(request):
    context = {}
    
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'ksda/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form
    
    # Validate the form.
    if not form.is_valid():
        return render(request, 'ksda/register.html', context)

    # At this point, the form data is valid. Register the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    #TODO figure out default work/wait sesh units
    new_waitsessioninfo = WaitsessionBrotherInfo()
    new_worksessioninfo = WorksessionBrotherInfo()
    
    new_waitsessioninfo.save()
    new_worksessioninfo.save()

    new_brother = Brother(user=new_user,
                          worksessionbrotherinfo=new_worksessioninfo,
                          waitsessionbrotherinfo=new_waitsessioninfo,
                          email=form.cleaned_data['email'],
                          venmoID=form.cleaned_data['venmoID'])
    new_brother.save()

    # First brother in the brotherhood - no email confirmation required.
    if Brother.objects.count() == 1:
        tid = TID(currentID = 0)
        tid.save()
        initializeBrotherhood(new_brother)
        #TODO This isn't displayed 
        context['infoMessage'] = 'Congratulations on creating a new brotherhood!'

        new_user.is_active = True
        new_user.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
        login(request, new_user)
        return redirect('/ksda/')
            
    else:
        # Generate a one-time use token and an email message body
        token = default_token_generator.make_token(new_user)

        email_body = """
    
            A new user, %s %s, has attempted to register for Kappa Sigma Delta-Alpha. Please click the link below to confirm their registration.
            http://%s%s
        """ % (new_user.first_name,
               new_user.last_name,
               request.get_host(),
               reverse('confirm', args=(new_user.username, token)))

        #FIX THIS TO GET EC EMAILS.
        ec = Role.objects.filter(ecPower=True)
        ec_member_emails = []
        for member in ec:
            try:
                ec_member_emails.append(member.brother.email)
            except:
                continue
    
        #Send email to admin for approval.
        send_mail(subject="New Registration Requires Your Approval",
                  message=email_body,
                  from_email="kappasigmadeltaalpha@gmail.com",
                  recipient_list=ec_member_emails)
    
        return render(request, 'ksda/needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    #Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    #Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    email_body = """
    
    Welcome to the Kappa Sigma Delta-Alpha. The admin has approved your registration. Please click on the link below to login.
    
    http://%s%s
    """ % (request.get_host(), reverse('login'))

    brother = Brother.objects.get(user=user)
    
    send_mail(subject="Your Request Has Been Approved",
              message=email_body,
              from_email="kappasigmadeltaalpha@gmail.com",
              recipient_list=[brother.email])

    return render(request, 'ksda/confirmed.html', {})

def doLogin(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            print 'logging in'
            login(request, user)
            return profilePage(request)
        else:
            print 'not active'
    else:
        print 'no user'

def showMain(request):
    context = {}
    return render(request, 'ksda/index.html', context)
