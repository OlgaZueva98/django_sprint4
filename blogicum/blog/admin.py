from django.contrib import admin

from .models import Category, Location, Post, Comment

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
    )
    list_filter = ('is_published', 'post')


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    list_display_links = ('title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comment, CommentAdmin)
