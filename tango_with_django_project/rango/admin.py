from django.contrib import admin
from rango.models import Category, Page

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,         {'fields': ['name', 'slug']}),
        ('Popularity', {'fields': ['likes', 'views'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'likes', 'views')
    #list_filter = ['likes']    #Adds filter to category admin page.
    search_fields = ['name']    #Adds search bar for name field.
    prepopulated_fields = {'slug':('name',)} #pre-populates field as you type name.

class PageAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Page Information', {'fields': ['title', 'category', 'url']}),
        ('Popularity',       {'fields': ['views'], 'classes': ['collapse']}),
    ]
    list_display = ('title', 'category', 'views')
    search_fields = ['title', 'url']
        

# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)