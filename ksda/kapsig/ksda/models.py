from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import datetime

class WaitsessionBrotherInfo(models.Model):
    units = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    freeM = models.BooleanField(default=True)
    freeT = models.BooleanField(default=True)
    freeW = models.BooleanField(default=True)
    freeH = models.BooleanField(default=True)
    freeF = models.BooleanField(default=True)

    def displayFreeDays(self):
        return ('M ' if self.freeM else '_ ') + \
        ('T ' if self.freeT else '_ ') + \
        ('W ' if self.freeW else '_ ') + \
        ('Th ' if self.freeH else '_ ') + \
        ('F ' if self.freeF else '_ ')

    def __str__(self):
        return self.brother.getName() + ': ' + str(self.units) + \
               ', Free on: ' + self.displayFreeDays()
    
    def displayInfo(self):
        return [self.brother.order, self.brother.getName(), str(self.units), self.displayFreeDays()]

class WorksessionBrotherInfo(models.Model):
    units = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    freeThisWeekend = models.BooleanField(default=True)

    def __str__(self):
        return str(self.units) + ', ' + str(freeThisWeekend)
    
    def displayInfo(self):
        return [self.brother.order, self.brother.getName(), str(self.units), self.freeThisWeekend]

class Fine(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=128)
    brother = models.ForeignKey('Brother', related_name='assignee')
    assignedBy = models.ForeignKey('Brother', related_name='assigner')
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    chair = models.ForeignKey('Role',related_name='chair')
    
    def __str__(self):
        return '[' + str(self.created.strftime("%b %d, %Y")) + '] ' + \
               '$' + str(self.amount) + ' to ' + self.brother.getName() + ' from ' + self.assignedBy.getName() + \
               ' because ' + str(reason)

class Role(models.Model):
    name = models.CharField(max_length=128)
    finePower = models.BooleanField(default=False)
    worksessionPower = models.BooleanField(default=False)
    waitsessionPower = models.BooleanField(default=False)
    ecPower = models.BooleanField(default=False)
    brother = models.ForeignKey('Brother', null=True)

    def __str__(self):
        return str(self.name)

class Brother(models.Model):
    user = models.OneToOneField(User)
    active = models.BooleanField(default=True)
    pledge = models.BooleanField(default=False)
    order = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    email = models.EmailField(max_length=200)
    number = models.CharField(max_length=30,default='555-555-5555')
    waitsessionbrotherinfo = models.OneToOneField(WaitsessionBrotherInfo)
    worksessionbrotherinfo = models.OneToOneField(WorksessionBrotherInfo)
    venmoID = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

    def getName(self):
        return str(self.user.first_name + ' ' + self.user.last_name)

    def brotherRollInfo(self):
        return [self.order, 
                reverse('ksda.views.profilePageObserved', None, [str(self.user.username)]), 
                self.getName(), 
                self.email, 
                self.number, 
                self.getRolesPretty()]
    
    def pledgeRollInfo(self):
        return [reverse('ksda.views.profilePageObserved', None, [str(self.user.username)]),
                self.getName(),
                self.email,
                self.number]

    def getRoles(self):
        roles = Role.objects.filter(brother=self)
        return roles

    def getRolesPretty(self):
        roles = self.getRoles()
        rolesPretty = ''
        for i in xrange(len(roles)):
            sep = ' ' 
            if i < len(roles) - 1:
                sep = ', '
            rolesPretty += str(roles[i]) + sep
        return rolesPretty
        

    def hasPower(self, power):
        roles = self.getRoles()
        for role in roles:
            if getattr(role, power):
                return True
        return False

    def hasFiningPower(self):
        return self.hasPower('finePower')
    def hasWorksessionPower(self):
        return self.hasPower('worksessionPower')
    def hasWaitsessionPower(self):
        return self.hasPower('waitsessionPower')
    def hasEcPower(self):
        return self.hasPower('ecPower')

class Waitsession(models.Model):
    date = models.DateField()
    completed = models.BooleanField(default=False)
    brotherinfo = models.ForeignKey('WaitsessionBrotherInfo')

    def __str__(self):
        return '[' + str(self.date.strftime("%b %d")) + \
                '] : ' + str(self.brotherinfo.brother.getName())

    def isActive(self):
        return datetime.date.today() <= self.date

    def isComplete(self):
        return self.completed

    def toggleComplete(self):
        self.completed = not self.completed
        self.brotherinfo.units += 1 if self.completed else -1

class WorksessionTask(models.Model):
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Worksession(models.Model):
    date = models.DateField()
    completed = models.BooleanField(default=False)
    brotherinfo = models.ForeignKey('WorksessionBrotherInfo')
    task = models.ForeignKey('WorksessionTask')

    def __str__(self):
        return '[' + str(self.date.strftime("%b %d")) + \
                '] : ' + str(self.brotherinfo.brother.getName()) + \
                ' -- ' + str(self.task)

    def isActive(self):
        return datetime.date.today() <= self.date

    def isComplete(self):
        return self.completed

    def toggleComplete(self):
        self.completed = not self.completed
        self.brotherinfo.units += 1 if self.completed else -1

class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Brother, through='Membership')

    def __str__(self):
        return self.name

class Membership(models.Model):
    person = models.ForeignKey(Brother)
    group = models.ForeignKey(Group)

class Comment(models.Model):
    text = models.CharField(max_length=160)
    brother = models.ForeignKey('Brother', null=True)
    dateTime = models.DateTimeField()
    def __unicode__(self):
        return self.text

class Item(models.Model):
    text = models.CharField(max_length=160)
    brother = models.ForeignKey('Brother', null=True)
    dateTime = models.DateTimeField()
    comments = models.ManyToManyField(Comment)
    def __unicode__(self):
        return self.text

class Thread(models.Model):
    title = models.CharField(max_length = 100)
    brother = models.ForeignKey('Brother', null = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    threadID = models.IntegerField(default=0)
    content = models.CharField(max_length = 1000)
    url = models.CharField(blank=True, max_length=256)
    responses = models.ManyToManyField(Item)
    def __unicode__(self):
        return self.title


class TID(models.Model):
    currentID = models.IntegerField(default=0)
    def __unicode__(self):
        return self.title

class Document(models.Model):
    user = models.ForeignKey(User)
    filename = models.CharField(max_length=128)
    url = models.CharField(blank=True, max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.filename


