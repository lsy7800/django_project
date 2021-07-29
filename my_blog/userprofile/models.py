from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
# Create your models here.

class Profile(models.Model):
    # 与user模型构成1对1关系
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    # 电话号码字段
    phone = models.CharField(max_length=20,blank=True)
    # 头像
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/',blank=True)
    # 个人简介
    bio = models.TextField(max_length=500,blank=True)

    def __str__(self):
        return 'user:{}'.format(self.user.username)

# # 信号接受函数，每当新建立User时自动调用函数
# @receiver(post_save,sender=User)
# def create_user_profile(sender,instance,created,**kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
# # 信号接受函数，每当更新User时走动调用函数
# @receiver(post_save,sender=User)
# def save_user_profile(sender,instance,**kwargs):
#     instance.profile.save()
@login_required(login_url='/userprofile/login/')
def profile_edit(request,id):
    user = User.objects.get(id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)