from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin
from vendor.models import Vendor

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class CustomProfileAdmin(UserAdmin):
    list_display = ('user','address', 'prof')
    ordering = ('-created_at',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    def prof(self,obj):
        # p = UserProfile.objects.filter(user=obj.pk,userprofile__is_approved=True)
        p = Vendor.objects.filter(user_profile=obj.pk, is_approved=True)
        return list(p)


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, CustomProfileAdmin)