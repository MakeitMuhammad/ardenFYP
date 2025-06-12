from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, SocialLink, Project, ProjectTask, Tag, Message, Notification

#-------------------------------------------------
# Profile Inline
#-------------------------------------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

#-------------------------------------------------
# User Admin
#-------------------------------------------------
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'full_name', 'account_type', 'is_staff', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'account_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'account_type', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Register the CustomUser model with CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

#-------------------------------------------------
# User sociallinks
#-------------------------------------------------
@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'website', 'github', 'twitter', 'instagram', 'facebook']

#-------------------------------------------------
#  Project
#-------------------------------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username', 'user__full_name')  # customize per your user model
    list_filter = ('created_at',)

#-------------------------------------------------
# prject task
#-------------------------------------------------
@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'task', 'status')
    search_fields = ('task',)
    list_filter = ('status',)

#-------------------------------------------------
#tags
#-------------------------------------------------



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')
    search_fields = ('name',)


#-------------------------------------------------
#  message
#-------------------------------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'read')
    list_filter = ('read', 'timestamp')
    search_fields = ('sender__username', 'recipient__username', 'content')
    ordering = ('-timestamp',)
#-------------------------------------------------
# notifs
#-------------------------------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'timestamp', 'is_read', 'link')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('recipient__username', 'sender__username', 'message')
    ordering = ('-timestamp',)