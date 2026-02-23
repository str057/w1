from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'action',
        'user',
        'time',
        'place',
        'is_pleasant',
        'periodicity',
        'is_public',
        'created_at'
    ]
    list_filter = [
        'is_pleasant',
        'is_public',
        'periodicity',
        'created_at',
        'user'
    ]
    search_fields = [
        'action',
        'place',
        'reward',
        'user__email',
        'user__username'
    ]
    readonly_fields = ['created_at']
    list_display_links = ['id', 'action']
    list_per_page = 20

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Характеристики привычки', {
            'fields': ('is_pleasant', 'periodicity', 'time_to_complete')
        }),
        ('Связи и награды', {
            'fields': ('related_habit', 'reward')
        }),
        ('Дополнительно', {
            'fields': ('is_public', 'created_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'related_habit')