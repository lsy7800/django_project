from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
# Create your views here.

# 文章列表视图
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 用户搜索逻辑
    if search:
        if order == 'total_views':
            # 用Q对象进行联合搜索
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        # 将search参数设置为空
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    # 每页显示三篇文章
    paginator = Paginator(article_list,3)
    # 获取url中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码传回给articles
    articles = paginator.get_page(page)
    context = {'articles':articles, 'order':order, 'search':search}
    return render(request,'article/list.html',context)

# 文章详情视图
def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)

    comments = Comment.objects.filter(article=id)
    # 浏览量+1
    article.total_views +=1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 目录
        'markdown.extensions.toc'
    ])

    article.body = md.convert(article.body)

    context = {'article':article,'toc':md.toc,'comments':comments}
    return render(request,'article/detail.html',context)

# 创建文章
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到实例表单当中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否符合模型要求
        if article_post_form.is_valid():
            # 保存数据但是暂时不提交到数据库
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = request.user
            # 将新文章保存到数据库
            new_article.save()
            # 完成后返回文章列表
            return redirect('article:article_list')
        else:
            return HttpResponse("您输入的信息有误，请重新输入")
    # 如果用户请求获取数据
    else:
        # 创建表单实例
        article_post_form = ArticlePostForm()
        # 赋值上下文
        context = {'article_post_form':article_post_form}
        # 返回模板
        return render(request,'article/create.html',context)

# 删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request,id):
    if request.method == "POST":
        # 根据id获取需要删除的文章
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect('article:article_list')
    else:
        return HttpResponse('经允许post请求')

# 修改文章
@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            # 保存新写入的title，body
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()

            return redirect('article:article_detail',id=id)

    else:
        article_post_form = ArticlePostForm()
        context = {'article':article,'article_post_form':article_post_form}
        return render(request,'article/update.html',context)