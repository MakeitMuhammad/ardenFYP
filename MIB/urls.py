
from django.urls import path, include
from MIB import views as view
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #index page
    path('', view.index, name='index'),

#about page
    path('about/', view.about, name='about'),


    #contact page
    path('contact/', view.contact, name='contact'),

    #dashboard page
    path('dashboard/', view.dashboard, name='dashboard'),
    #--profile update
    path('profile/update/', views.update_profile, name='update_profile'),
    #--profile pic
     path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
     #--profile socials
     path('profile/update-social/', views.update_social_link, name='update_social_link'),
     #--profile tasks
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),

#--expert dashboard
    path('expert_dashboard/', view.expert_dashboard, name='expert_dashboard'),
    #--tags
    path('add_skills/', views.add_skills, name='add_skills'),
    




    #aibuddy page
    path('aibuddy/', view.aibuddy, name='aibuddy'),
    path('aibuddy-api/', views.aibuddy_api, name='aibuddy_api'),  # AJAX handler

    #signup page
    path('signup/', view.signup, name='signup'),

    #login page
    path('login/', view.login, name='login'),

    #logout 
      path('logout/', views.logout_view, name='logout'),


    #project
     path('projects/', views.projects, name='projects'),
    #new project
     path('newproject/', views.newproject, name='newproject'),
     #project detail
     path('projects/<int:project_id>/tasks/', views.project_tasks, name='project_tasks'),


    #search
     path('search/', views.user_search, name='user_search'),
    # profile view
    path('profile/<int:user_id>/', views.profile_view, name='profile_view'),

    #message
     path('message/<int:user_id>/', views.message_view, name='message_view'),
    path('message/send/', views.send_message, name='send_message'),

    #noifications
    path('notifications/', views.notification_list, name='notification_list'),

    #all chats
    path('allchats/', view.all_chats, name='all_chats'),

    #return
    path('returns/', view.returns, name='returns'),

   


    

    #base template
    # path('base_template/', view.base, name='base_template'),

    #delete logic
     path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),

    
    
]
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

