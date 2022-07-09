from urllib import request
from rest_framework import serializers
from blog.models import Post, Comment, SiteAbout



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostDetailSerializer(serializers.ModelSerializer):
    # comments = CommentSerializer(many=True)
    comments=serializers.SerializerMethodField()


    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'auther'] + ['comments']

    def get_comments(self, obj): #obj=post
        # user_id=self.context["user_id"]
        # user inja int boud ama obj.auther object boud amd byad yeksan bashan be in khater ba id car kardim.
        # using _ is better way to optimize the code instead of . becAUSE auter is forgein key in post model
        if self.context["user_id"] == obj.auther_id:
            approve_comments = obj.comments.all()

        else:
            approve_comments = obj.comments.filter(approved_comment=True)
        
        return CommentSerializer(approve_comments, many=True).data



class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        # exclude = ['published_date']


class PostEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ['published_date', 'created_date', 'auther']


class PostDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        


class PostPublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
###########################################################################


class AddCommentToPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text',)

class ApproveComment(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
class RemoveComment(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

###########################################################################


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteAbout
        fields = '__all__'

###########################################################################aditional###

