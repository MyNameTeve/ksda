from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^$', 'ksda.views.profilePage'),
    
    url(r'^profile$', 'ksda.views.profilePage', name='profile'),
    url(r'^profile/(?P<observedUserName>\w+)/$', 'ksda.views.profilePageObserved', name='profilePageObserved'),
    url(r'^changePassword$', 'ksda.views.changePassword', name='changePassword'),
    url(r'^updateProfileStandard$', 'ksda.views.updateProfileStandard', name='updateProfileStandard'),
    url(r'^updateProfileAdvanced$', 'ksda.views.updateProfileAdvanced', name='updateProfileAdvanced'),

    url(r'^worksessions$', 'ksda.views.worksessionsPage', name='worksessions'),
    url(r'^newWorksession$', 'ksda.views.addWorksession', name='newWorksession'),
    url(r'^newWorksessionTask$', 'ksda.views.addWorksessionTask', name='newWorksessionTask'),
    url(r'^newWorkunit$', 'ksda.views.addWorkunit', name='newWorkunit'),
    url(r'^toggleWorksessionComplete$', 'ksda.views.toggleWorksessionComplete', name='toggleWorksessionComplete'),
    url(r'^deleteWorksession$', 'ksda.views.deleteWorksession', name='deleteWorksession'),
    url(r'^deleteWorksessionTask$', 'ksda.views.deleteWorksessionTask', name='deleteWorksessionTask'),
    url(r'^getWorksessionInfo$', 'ksda.views.getWorksessionInfo', name='getWorksessionInfo'),

    url(r'^waitsessions$', 'ksda.views.waitsessionsPage', name='waitsessions'),
    url(r'^newWaitsession$', 'ksda.views.addWaitsession', name='newWaitsession'),
    url(r'^newWaitunit$', 'ksda.views.addWaitunit', name='newWaitunit'),
    url(r'^toggleWaitsessionComplete$', 'ksda.views.toggleWaitsessionComplete', name='toggleWaitsessionComplete'),
    url(r'^deleteWaitsession$', 'ksda.views.deleteWaitsession', name='deleteWaitsession'),
    url(r'^getWaitsessionInfo$', 'ksda.views.getWaitsessionInfo', name='getWaitsessionInfo'),

    url(r'^finances$', 'ksda.views.financesPage', name='finances'),
    
    url(r'^forum$', 'ksda.views.forumPage', name='forum'),
    
    url(r'^documents$', 'ksda.views.documentsPage', name='documents'),

    url(r'^brotherRoll$', 'ksda.views.brotherRoll', name='brotherRoll'),
    url(r'^assignRole$', 'ksda.views.assignRole', name='assignRole'),
    url(r'^newRole$', 'ksda.views.newRole', name='newRole'),
    url(r'^deleteRole$', 'ksda.views.deleteRole', name='deleteRole'),

    url(r'^ec$', 'ksda.views.ecPage', name='ec'),
    url(r'^sendEmail$', 'ksda.views.sendEmail', name='sendEmail'),
    
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'ksda/login.html'}, name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register$', 'ksda.views.register', name='register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'ksda.views.confirm_registration', name='confirm'),
)
