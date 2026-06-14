from django.contrib import admin
from django.utils.html import format_html
from .models import ProcessedImage


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'original_thumbnail', 'processed_thumbnail', 'prediction_label', 'prediction_confidence', 'uploaded_at')
    list_filter = ('user', 'uploaded_at')
    search_fields = ('user__username', 'user__email', 'prediction_label')
    readonly_fields = ('uploaded_at', 'original_thumbnail', 'processed_thumbnail')
    ordering = ('-uploaded_at',)

    def original_thumbnail(self, obj):
        if obj.original_image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.original_image.url
            )
        return '—'
    original_thumbnail.short_description = 'Original'

    def processed_thumbnail(self, obj):
        if obj.processed_image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;background:#ddd;" />',
                obj.processed_image.url
            )
        return '—'
    processed_thumbnail.short_description = 'Processed'
