from django.contrib import admin
from .models import LateArrival


@admin.register(LateArrival)
class LateArrivalAdmin(admin.ModelAdmin):
    list_display   = ("employee", "fecha", "hora_llegada", "minutos_tarde", "descuento", "period")
    list_filter    = ("period", "fecha")
    search_fields  = ("employee__name",)
    date_hierarchy = "fecha"
    readonly_fields = ("minutos_tarde", "descuento", "period", "created_at")