from django.contrib.auth.models import User  # type: ignore
from django.test import TestCase  # type: ignore
from django.urls import reverse  # type: ignore

from .models import Category


class IndexViewTests(TestCase):
    """IndexViewのテスト"""

    def test_zero_blog(self):
        """ブログ記事存在しない場合のindex"""
        response = self.client.get(reverse("blogs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["blogs"], [])

    def test_up_blog_private(self):
        """非公開ブログ記事存在する場合のindex"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        response = self.client.get(reverse("blogs:index"))
        self.assertQuerysetEqual(response.context["blogs"], [])

    def test_up_blog_publick(self):
        """公開ブログ記事存在する場合のindexページの見え方"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=True)
        response = self.client.get(reverse("blogs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["blogs"], ["<Blog: タイトル>"])
        # QuerySetを使用した判定の場合
        # queryset = category.blog_set.filter(is_publick=True).order_by('-id')
        # self.assertQuerysetEqual(
        #         response.context["blogs"],
        #         queryset,
        #         transform=lambda x: x, # デフォルトではtransform=repr()が使用されているためエラーとなるので変更。
        # )


class CategoryViewTests(TestCase):
    """CategoryViewのテスト"""

    def test_zero_category(self):
        """ブログカテゴリーの値が存在しない場合に/blogs/category/***にアクセスした際の判定"""
        url = reverse("blogs:category", args=("カテゴリー１",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_up_category(self):
        """ブログカテゴリーの値が存在する場合の/blogs/category/***にアクセスした際の判定"""
        category = Category.objects.create(title="カテゴリー１")
        url = reverse("blogs:category", args=("カテゴリー１",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, category.title)
        self.assertQuerysetEqual(response.context["blogs"], [])

    def test_up_blog_in_category(self):
        """ブログ記事が存在する場合の/blogs/category/***にアクセスした際の判定"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=True)
        url = reverse("blogs:category", args=("カテゴリー１",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, category.title)
        self.assertQuerysetEqual(response.context["blogs"], ["<Blog: タイトル>"])
        # QuerySetを使用した判定の場合
        # queryset = Blog.objects.filter(is_publick=True, category=category).order_by("-id")
        # self.assertQuerysetEqual(
        #         response.context["blogs"],
        #         queryset,
        #         transform=lambda x: x, # デフォルトではtransform=repr()が使用されているためエラーとなるので変更。
        # )


class BlogDetailViewTests(TestCase):
    """BlogDetailViewのテスト"""

    def test_detail_result(self):
        """ブログ記事の詳細ページの結果"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=True)
        blog = category.blog_set.get(title="タイトル")
        url = reverse("blogs:detail", args=(blog.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)


class PrivateIndexViewTests(TestCase):
    """PrivateIndexViewクラスのテスト"""

    def test_no_account_result(self):
        """権限の無い状態からアクセスした場合"""
        response = self.client.get(reverse("blogs:private_index"))
        self.assertContains(response, "権限がありません。")

    def test_login_user_result(self):
        """権限があり、非公開ブログ記事が存在する場合"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        queryset = category.blog_set.filter(is_publick=False).order_by("-id")
        self.client.force_login(User.objects.create_user("tester"))
        response = self.client.get(reverse("blogs:private_index"))
        self.assertQuerysetEqual(
            response.context["private_blog"], queryset, transform=lambda x: x
        )


class PrivateDetailViewTests(TestCase):
    """PrivateDetailViewのテスト"""

    def test_no_account_result(self):
        """権限の無い状態からアクセスした場合"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        blog = category.blog_set.get(is_publick=False)
        url = reverse("blogs:private_detail", args=(blog.id,))
        response = self.client.get(url)
        self.assertContains(response, "権限がありません。")

    def test_login_user_private_detail_result(self):
        """非公開ブログ記事の詳細ページの結果"""
        category = Category.objects.create(title="カテゴリー１")
        category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        blog = category.blog_set.get(is_publick=False)
        self.client.force_login(User.objects.create_user("tester"))
        url = reverse("blogs:private_detail", args=(blog.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)


class BlogFormViewTests(TestCase):
    """BlogFormViewのテスト"""

    def test_blog_post_redirect(self):
        """ブログが保存され、リダイレクト先へ遷移するテスト"""
        Category.objects.create(title="カテゴリー１")
        response = self.client.post(
            path=reverse("blogs:new_blog"),
            data={"category": 1, "title": "タイトル", "text": "テキスト", "is_publick": True},
        )
        redirect_url = reverse("blogs:index")
        self.assertRedirects(response, redirect_url)

    def test_no_account_new_blog_access(self):
        """権限の無い状態からブログ作成ページにアクセスした場合"""
        response = self.client.get(reverse("blogs:new_blog"))
        self.assertContains(response, "権限がありません。")

    def test_login_user_new_blog_access(self):
        """ログインユーザーがブログ作成ページにアクセスした結果"""
        self.client.force_login(User.objects.create_user("tester"))
        response = self.client.get(reverse("blogs:new_blog"))
        self.assertContains(response, "戻る")


class EditBlogFormViewTests(TestCase):
    """EditBlogFormViewのテスト"""

    def test_blog_edit_redirect(self):
        """ブログが更新され、リダイレクト先へ遷移するテスト"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        url = reverse("blogs:edit", args=(blog.id,))
        redirect_url = reverse("blogs:index")
        response = self.client.post(
            path=url,
            data={"category": 1, "title": "タイトル", "text": "テキスト", "is_publick": True},
        )
        self.assertRedirects(response, redirect_url)

    def test_from_no_account_editblog_access(self):
        """権限の無い状態からブログ更新ページにアクセスした場合"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        url = reverse("blogs:edit", args=(blog.id,))
        response = self.client.get(url)
        self.assertContains(response, "権限がありません。")

    def test_from_login_user_editblog_access(self):
        """ログインユーザーがブログ更新ページにアクセスした結果"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        self.client.force_login(User.objects.create_user("tester"))
        url = reverse("blogs:edit", args=(blog.id,))
        response = self.client.get(url)
        self.assertContains(response, "戻る")


class ReleaseTests(TestCase):
    """release関数のテスト"""

    def test_blog_release_redirect(self):
        """特定のブログ記事が公開にアクセスされた際のリダイレクト先へ遷移するテスト"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        self.client.force_login(User.objects.create_user("tester"))
        url = reverse("blogs:release", args=(blog.id,))
        redirect_url = reverse("blogs:index")
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_no_account_blog_release_access(self):
        """権限の無い状態から特定のブログ記事の公開にアクセスされた際のHttpResponse"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        url = reverse("blogs:release", args=(blog.id,))
        response = self.client.get(url)
        self.assertContains(response, "権限がありません。")


class PrivateTests(TestCase):
    """private関数のテスト"""

    def test_blog_private_redirect(self):
        """特定のブログ記事が非公開にアクセスされた際のリダイレクト先へ遷移するテスト"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=True)
        self.client.force_login(User.objects.create_user("tester"))
        url = reverse("blogs:private", args=(blog.id,))
        redirect_url = reverse("blogs:private_index")
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_no_account_blog_private_access(self):
        """権限の無い状態から特定のブログ記事の非公開にアクセスされた際のHttpResponse"""
        category = Category.objects.create(title="カテゴリー１")
        blog = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        url = reverse("blogs:private", args=(blog.id,))
        response = self.client.get(url)
        self.assertContains(response, "権限がありません。")
