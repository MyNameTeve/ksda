from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

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
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'ksda/register.html', context)
    
    form = RegistrationForm(request.POST)
    context['form'] = form
    
    if not form.is_valid():
        return render(request, 'ksda/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'])
    new_user.first_name = form.cleaned_data['first_name']
    new_user.last_name = form.cleaned_data['last_name']
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

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect('/ksda/')

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

def showMain(request):
    print 'showMain'
    context = {}
    return render(request, 'ksda/index.html', context)
