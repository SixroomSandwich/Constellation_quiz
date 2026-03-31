from django.contrib import admin
from .models import Constellation

@admin.register(Constellation)
class ConstellationAdmin(admin.ModelAdmin):
    list_display = ['name_ru', 'name_la', 'created_at']
    search_fields = ['name_ru', 'name_la']