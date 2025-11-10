from django.test import TestCase  # type: ignore

from blogs.templatetags.mark import markdown_to_html

from .models import Blog, Category


class MarkTests(TestCase):
    """blogs/templatetags/mark.py"""

    def test_markdown_to_html(self):
        """マークダウンからHTMLへ変換"""
        text = "*Hello*"
        html = markdown_to_html(text)
        self.assertEqual(html, "<p><em>Hello</em></p>")


class CategoryModelTests(TestCase):
    """Categoryモデルのテスト"""

    def test_category_title_result(self):
        """__str__メソッド"""
        result = Category(title="カテゴリー１")
        self.assertIsInstance(result.__str__(), str)


class BlogModelTests(TestCase):
    """Blogモデルのテスト"""

    def test_blog_to_release_result(self):
        """to_releaseメソッド"""
        category = Category.objects.create(title="カテゴリー１")
        result = category.blog_set.create(title="タイトル", text="テキスト", is_publick=False)
        result.to_release()
        self.assertIs(result.is_publick, True)

    def test_blog_to_private_result(self):
        """to_privateメソッド"""
        category = Category.objects.create(title="カテゴリー１")
        result = category.blog_set.create(title="タイトル", text="テキスト", is_publick=True)
        result.to_private()
        self.assertIs(result.is_publick, False)

    def test_blog_get_toc_result(self):
        """get_tocメソッド"""
        category = Category.objects.create(title="カテゴリー１")
        text = """[TOC]\n## Hello"""
        blog = category.blog_set.create(
            title="タイトル", text="[TOC]\n## Hello", is_publick=True
        )
        text = """<div class="toc">\n<ul>\n<li><a href="#hello">Hello</a></li>\n</ul>\n</div>\n"""
        self.assertEqual(blog.get_toc(), text)

    def test_blog_title_result(self):
        """__str__メソッド"""
        result = Blog(title="タイトル")
        self.assertIsInstance(result.__str__(), str)
