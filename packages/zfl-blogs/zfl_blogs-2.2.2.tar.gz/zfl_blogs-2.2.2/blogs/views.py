from distutils.util import strtobool

from django.contrib import messages  # type: ignore
from django.http import HttpResponse  # type: ignore
from django.shortcuts import get_object_or_404, redirect  # type: ignore
from django.urls import reverse_lazy  # type:ignore
from django.views.generic import CreateView, DetailView, ListView, UpdateView  # type: ignore

from .forms import BlogForm
from .models import Blog, Category, Advertisement, Anchorlink


class IndexView(ListView):
    template_name = "blogs/index.html"
    context_object_name = "blogs"
    paginate_by = 12

    def get_queryset(self):
        """ブログ記事が公開且つIDの古い順にデータを取得"""
        # ↓の方法でBlogオブジェクトを取得する
        # category = get_object_or_404(Category, title=self.kwargs["category"])
        queryset = Blog.objects.filter(is_publick=True).order_by("-id")
        return queryset


class CategoryView(ListView):
    template_name = "blogs/index.html"
    context_object_name = "blogs"
    paginate_by = 12

    def get_queryset(self):
        """カテゴリー別でブログ記事が公開且つIDの古い順にデータを取得"""
        # 404エラーを使用した方法
        category = get_object_or_404(Category, title=self.kwargs["category"])
        queryset = Blog.objects.filter(is_publick=True, category=category).order_by("-id")
        messages.success(self.request, category)
        return queryset

    def get_context_data(self, **kwargs):
        """テンプレートへ渡す新着記事のインスタンスの作成"""
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, title=self.kwargs["category"])
        return context


class BlogDetailView(DetailView):
    model = Blog
    template_name = "blogs/detail.html"
    context_object_name = "blog"

    def get_context_data(self, **kwargs):
        """テンプレートへ渡す新着記事のインスタンスの作成"""
        context = super().get_context_data(**kwargs)
        context["blog"] = get_object_or_404(Blog, id=self.kwargs["pk"], is_publick=True)
        context["new_articls"] = self.model.objects.filter(is_publick=True).order_by(
            "-id"
        )[:5]
        context["advertisement"] = Advertisement.objects.all().order_by("-id")[:1]
        return context


class PrivateIndexView(ListView):
    queryset = Blog.objects.filter(is_publick=False).order_by("-id")
    template_name = "blogs/private_index.html"
    context_object_name = "private_blog"

    def get(self, request):
        """管理人以外のアクセスはHTMLページでコメントを返す"""
        if not request.user.is_authenticated:
            return HttpResponse("<h1>権限がありません。</h1>")
        return super().get(request)


class PrivateDetailView(DetailView):
    model = Blog
    template_name = "blogs/private_detail.html"
    context_object_name = "private_blog"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["private_blog"] = get_object_or_404(
            Blog, id=self.kwargs["pk"], is_publick=False
        )
        return context

    def get(self, request, pk):
        """管理人以外のアクセスはHTMLページでコメントを返す"""
        if not request.user.is_authenticated:
            return HttpResponse("<h1>権限がありません。</h1>")
        return super().get(request, pk)


class BlogFormView(CreateView):
    model = Blog
    form_class = BlogForm
    template_name = "blogs/create.html"
    success_url = reverse_lazy("blogs:index")
    get_object_name = "blog"

    def form_valid(self, form):
        """保存前の検証フェーズ"""
        # is_publickによってリダイレクト先を変更する
        if bool(strtobool(form.data["is_publick"])):
            self.success_url = reverse_lazy("blogs:index")
        else:
            self.success_url = reverse_lazy("blogs:private_index")

        # メッセージを表示する
        messages.success(self.request, "新規作成完了")
        return super().form_valid(form)

    def get(self, request):
        """管理人以外のアクセスはHTMLページでコメントを返す"""
        if not request.user.is_authenticated:
            return HttpResponse("<h1>権限がありません。</h1>")
        return super().get(request)


class EditBlogFormView(UpdateView):
    """更新用フォーム"""

    model = Blog
    form_class = BlogForm
    template_name = "blogs/edit.html"
    success_url = reverse_lazy("blogs:index")
    get_object_name = "blog"

    def form_valid(self, form):
        """保存前の検証フェーズ"""
        # is_publickによってリダイレクト先を変更する
        if bool(strtobool(form.data["is_publick"])):
            self.success_url = reverse_lazy("blogs:index")
        else:
            self.success_url = reverse_lazy("blogs:private_index")

        # 検証完了のメッセージを設定
        messages.success(self.request, "更新完了")

        return super().form_valid(form)

    def get(self, request, pk):
        """管理人以外のアクセスはHTMLページでコメントを返す"""
        if not request.user.is_authenticated:
            return HttpResponse("<h1>権限がありません。</h1>")
        return super().get(request, pk)


def release(request, pk):
    """Blog公開用"""
    if request.user.is_authenticated:
        blog_release = get_object_or_404(Blog, id=pk, is_publick=False)
        blog_release.to_release()
        return redirect("blogs:index")
    return HttpResponse("<h1>権限がありません。</h1>")


def private(request, pk):
    """Blog非公開用"""
    if request.user.is_authenticated:
        blog_private = get_object_or_404(Blog, id=pk, is_publick=True)
        blog_private.to_private()
        return redirect("blogs:private_index")
    return HttpResponse("<h1>権限がありません。</h1>")
