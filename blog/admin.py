from django.contrib import admin
from .models import Post, Comment, SiteAbout, PostView, PostCategory, PostTag

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'auther', 'categories', 'published_date',]

    class Meta:
        model = Post


class CommentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'auther', 'approved_comment', 'post']

    class Meta:
        model = Post

class PostViewAdmin(admin.ModelAdmin):
    list_display = ['post', 'user']

    class Meta:
        model = PostView


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SiteAbout)
admin.site.register(PostView, PostViewAdmin)
admin.site.register(PostCategory)
admin.site.register(PostTag)
