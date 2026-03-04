from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from skills.models import CustomUser, Skill, Profile, SwapRequest, Rating, Notification, Lesson


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'date_joined')
    list_filter = ('role', 'date_joined', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name',)
    ordering = ('category', 'name')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_skills_offered', 'get_skills_wanted', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'bio')
    filter_horizontal = ('skills_offered', 'skills_wanted')
    readonly_fields = ('created_at', 'updated_at')

    def get_skills_offered(self, obj):
        return ', '.join([skill.name for skill in obj.skills_offered.all()]) or 'None'
    get_skills_offered.short_description = 'Skills Offered'

    def get_skills_wanted(self, obj):
        return ', '.join([skill.name for skill in obj.skills_wanted.all()]) or 'None'
    get_skills_wanted.short_description = 'Skills Wanted'


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'skill_offering', 'skill_wanting', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('sender__username', 'receiver__username', 'skill_offering__name', 'skill_wanting__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Participants', {
            'fields': ('sender', 'receiver')
        }),
        ('Skills', {
            'fields': ('skill_offering', 'skill_wanting')
        }),
        ('Request Details', {
            'fields': ('message', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SwapRequest, SwapRequestAdmin)


class RatingAdmin(admin.ModelAdmin):
    list_display = ('swap', 'rater', 'ratee', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('rater__username', 'ratee__username', 'swap__sender__username', 'swap__receiver__username')


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'tutor', 'skill', 'scheduled_time', 'status')
    list_filter = ('status', 'scheduled_time', 'skill')
    search_fields = ('title', 'tutor__username', 'skill__name')
    filter_horizontal = ('learners',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')

admin.site.register(Rating, RatingAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Lesson, LessonAdmin)
