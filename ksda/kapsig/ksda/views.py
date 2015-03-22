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

# Import all other views to this main file.
from views_profile import *
from views_waitsession import *
from views_worksession import *
from views_ec import *
from views_brotherRoll import *

"""
Only called when DB is empty. First brother will get EC powers.
"""
@transaction.atomic
def initializeBrotherhood(brother):
    print 'FOUNDING BROTHERHOOD'
    print 'CREATING ADMIN'
    
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
                                        last_name=form.cleaned_data['last_name'],
                                        email=form.cleaned_data['email'])

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
                          waitsessionbrotherinfo=new_waitsessioninfo)
    new_brother.save()

    if Brother.objects.count() == 1:
        initializeBrotherhood(new_brother)
        #TODO This isn't displayed 
        context['infoMessage'] = 'Congratulations on creating a new brotherhood!'

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
    
        Welcome to the Kappa Sigma Delta-Alpha. Please click the link below to
        verify your email address and complete the registration of your account:
    
        http://%s%s
    """ % (request.get_host(),
           reverse('confirm', args=(new_user.username, token)))

    #TODO change from_email
    send_mail(subject="Verfiy your email address",
              message=email_body,
              from_email="rnved@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    
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
    return render(request, 'ksda/confirmed.html', {})

def doLogin(request):
    print 'doLogin'
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

@login_required
def financesPage(request):
    print 'financesPage'
    context = {}
    return render(request, 'ksda/finances.html', context) 
@login_required
def forumPage(request):
    print 'forumPage'
    context = {}
    return render(request, 'ksda/forum.html', context) 
@login_required
def documentsPage(request):
    print 'documentsPage'
    context = {}
    return render(request, 'ksda/documents.html', context) 

@login_required
def calendarPage(request):
    print 'calendarPage'
    context = {}
    return render(request, 'ksda/calendar.html', context) 

def showMain(request):
    print 'showMain'
    context = {}
    return render(request, 'ksda/index.html', context)
