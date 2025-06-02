from django.contrib import admin

from publications.models import Publication, Commentary

# Register your models here.

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_free', 'author', 'created_at')
    list_filter = ('is_free', 'created_at', 'author')
    search_fields = ('title', 'author')


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'publication', 'author', 'created_at')
    list_filter = ('created_at', 'author', 'publication')
    search_fields = ('first_name', 'last_name')
