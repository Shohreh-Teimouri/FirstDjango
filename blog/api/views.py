from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .permissions import (IsOwnerOrReadOnly,
                          DeletePostOrComment, 
                          UpdatePostOrComment,
                          publishPostOrComment,)
from blog.models import Post, PostView, Comment, SiteAbout
from .serializers import (PostSerializer,
                          PostDetailSerializer,
                          CreatePostSerializer,
                          PostEditSerializer,
                          PostDeleteSerializer,
                          PostDraftSerializer,
                          PostPublishSerializer,
                          AddCommentToPostSerializer, 
                          ApproveComment, 
                          RemoveComment, 
                          AboutUsSerializer, CommentSerializer)

from rest_framework.pagination import BasePagination


class PostListAPIView(APIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request):
        ordering = request.GET.get('ordering', 'newer')
        sort = '-published_date' if ordering == 'newer' else 'published_date'
        types = request.GET.get('types', 'published')
        page = self.validate_integers(request.GET.get('page', 1))
        #defult: you have to create per_page and set value for it alaways by yourself 
        per_page = self.validate_integers(request.GET.get('per_page', 5))
        start=(page-1)*per_page
        end=page*per_page
        posts = Post.objects.annotate(num_views=Count('post_views')).all()
        # posts[:5]
        # posts[5:]
        # posts[-1] choun data slice should nemishe filter or order anjam besh beinkater start and end akharin ja
        #ke query mireh gozashteh mishe na--> .all()[start:end]

        if types == 'published':
            posts = posts.filter(published_date__isnull=False)
        else:
            posts = posts.filter(published_date__isnull=True)

        serializer = self.serializer_class(
            posts.order_by(sort)[start:end], many=True)
        return Response(serializer.data, status=200)

    def validate_integers(self,value):
        try:
            return int(value)
        except ValueError as e:
            raise ValidationError('it should be integer')  

class PostDetailAPIView(APIView):
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk):
        try:
            post = Post.objects.prefetch_related("comments").get(pk=pk)  # extract quey:post --> comment/select_related(reverse prefetch)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        obj, created = PostView.objects.get_or_create(
            post_id=pk, user_id=request.user.id)
        serializer = self.serializer_class(post, many=False, context={"user_id":request.user.id}) #pass context in line 65 serlializer
        return Response(serializer.data)


class PostCreateAPIView(APIView):
    serializer_class = CreatePostSerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(auther=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostEditAPIView(APIView):
    serializer_class = PostEditSerializer
    permission_classes = [IsAuthenticated, UpdatePostOrComment]


    def options(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        obj, created = PostView.objects.get_or_create(
            post_id=pk, user_id=request.user.id)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)
        
    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PostEditSerializer(data=request.data, instance=post)
        if serializer.is_valid():
            serializer.save(auther=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete (self, request, pk):
    #     return Response(status=200)

class RemovePostAPIView(APIView):
    permission_classes = [IsAuthenticated, DeletePostOrComment]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response("This post was deleted!")


class PostDraftListAPIView(APIView):
    serializer_class = PostDraftSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(
            published_date__isnull=True).order_by('-created_date')
        serializer = self.serializer_class(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PostPublishAPIView(APIView):
    serializer_class = PostPublishSerializer
    permission_classes = [IsAdminUser, publishPostOrComment]

    def get(self,request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post.publish()
        serializer = self.serializer_class(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

########################################################################comment#############################


class AddCommentAPIView(APIView):
    serializer_class = AddCommentToPostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.post = post
            serializer.save(auther=request.user, post=post, approved_comment=False) # this approch needs admin for approving
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApproveCommentAPIView(APIView):
    serializer_class = ApproveComment
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        comment.approve()
        serializer = self.serializer_class(comment)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveCommentAPIView(APIView):
    serializer_class = RemoveComment
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(request, comment)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response('your comment was removed!!')
########################################################################aboutus#############################


class AboutUsPageAPIView(APIView):
    serializer_class = AboutUsSerializer
    permission_classes = [IsAuthenticated,]
    def get(self, request):
        site_data = SiteAbout.objects.all()
        serializer = self.serializer_class(site_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

########################################################################additional#############################


class CommentListAPIView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, pk):
        post = Post.objects.get(pk=pk)
        comments = Comment.objects.filter(post=post)
        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)