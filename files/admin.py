from django.contrib import admin
from .models import FileRecord, DownloadRecord, DownloadableFile

@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'file_size', 'uploaded_at', 'employee_code')
    list_filter = ('uploaded_at', 'employee_code')
    search_fields = ('original_filename', 'employee_code')
    readonly_fields = ('file_size', 'uploaded_at')
    date_hierarchy = 'uploaded_at'

@admin.register(DownloadableFile)
class DownloadableFileAdmin(admin.ModelAdmin):
    list_display = ('filename', 'file_size', 'last_modified', 'is_downloaded', 'last_downloaded_at')
    list_filter = ('is_downloaded', 'last_modified')
    search_fields = ('filename',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'last_modified'

@admin.register(DownloadRecord)
class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ('file', 'employee_code', 'downloaded_at')
    list_filter = ('downloaded_at', 'employee_code')
    search_fields = ('employee_code',)
    date_hierarchy = 'downloaded_at'
    readonly_fields = ('downloaded_at',)
