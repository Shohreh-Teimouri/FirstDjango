from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListAPIView.as_view(), name='post_list_api'),
    path('<int:pk>/', views.PostDetailAPIView.as_view(),
         name='post_detail_api'),
    path('create/', views.PostCreateAPIView.as_view(),
         name='Post_Create_api'),
    path('<int:pk>/edit', views.PostEditAPIView.as_view(),
         name='post_edit_api'),
    path('<int:pk>/delete', views.RemovePostAPIView.as_view(),
         name='post_delete_api'),
    path('draft/', views.PostDraftListAPIView.as_view(),
         name='post_draft_api'),    
    path('draft/<int:pk>/publish', views.PostPublishAPIView.as_view(),
         name='post_publish_api'),
    path('<int:pk>/addcomment/', views.AddCommentAPIView.as_view(),
         name='add_comment_api'),    
    path('comment/<int:pk>/approve/', views.ApproveCommentAPIView.as_view(),
         name='approve_comment_api'),    
    path('comment/<int:pk>/delete/', views.RemoveCommentAPIView.as_view(),
         name='remove_comment_api'),
    path('about-us/', views.AboutUsPageAPIView.as_view(),
         name='about_us'),
####################################################################################aditional#######
    
    path('<int:pk>/comments/', views.CommentListAPIView.as_view(),
         name='list_comments'),
]
