import markdown
from django.db import models  # type: ignore
from django.utils import timezone  # type: ignore
from django.utils.text import slugify  # type: ignore
from markdownx.models import MarkdownxField  # type: ignore
from markdownx.settings import MARKDOWNX_MARKDOWN_EXTENSIONS as EXTENSIONS  # type: ignore


class Category(models.Model):
    """カテゴリーモデル"""

    # カラーリスト
    COLORS = [
        ["gray", "gray"],
        ["crimson", "crimson"],
        ["royalblue", "royalblue"],
        ["darkgreen", "darkgreen"],
        ["darkolivegreen", "darkolivegreen"],
        ["darkorange", "darkorange"],
        ["darkviolet", "darkviolet"],
    ]
    title = models.CharField("カテゴリー", max_length=20)
    thumbnail = models.ImageField(
        "サムネイル（空欄可）",
        upload_to="blogs/category/thumbnail",
        null=True,
        blank=True,
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    overview = models.CharField("概要", null=True, blank=True, max_length=256)
    slug = models.SlugField(null=True, blank=True, unique=True)
    color = models.CharField(default=COLORS[0][0], choices=COLORS, max_length=50)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # slug変数が空だった場合、title変数のデータをslug変数に代入する
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ブログカテゴリーリスト"
        verbose_name_plural = "ブログカテゴリーリスト"


class Blog(models.Model):
    """記事作成モデル"""

    title = models.CharField("タイトル", max_length=150)
    text = MarkdownxField("テキスト", help_text="Markdown形式で書いてください。")
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_publick = models.BooleanField(
        "選択",
        choices=(
            (True, "公開"),
            (False, "非公開"),
        ),
    )
    release_date = models.DateField(null=True, blank=True)
    thumbnail = models.ImageField(
        "サムネイル（空欄可）",
        upload_to="blogs/blog/thumbnail",
        null=True,
        blank=True,
    )

    def to_release(self):
        self.is_publick = True
        self.save()

    def to_private(self):
        self.is_publick = False
        self.save()

    def get_toc(self):
        md = markdown.Markdown(extensions=EXTENSIONS)
        html = md.convert(self.text)
        return md.toc  # type: ignore

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_publick and not self.release_date:
            self.release_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "ブログリスト"
        verbose_name_plural = "ブログリスト"


class Advertisement(models.Model):
    advertiser_name = models.CharField("広告主", max_length=200)
    image = models.ImageField("広告画像", blank=True)
    image_color = models.CharField("イメージカラー", max_length=7, default="#ecf0f1")
    start_date = models.DateTimeField("開始日時")
    end_date = models.DateTimeField("終了日時")

    def __str__(self):
        return self.advertiser_name

    class Meta:
        verbose_name = "広告主リスト"
        verbose_name_plural = "広告主リスト"


class Anchorlink(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    anchor = models.CharField("アンカー", max_length=200)
    url = models.URLField("URL")

    def __str__(self):
        return self.anchor


# class Popular(models.Model):
#     """
#     GoogleAnalytics APIモデル
#     blogsアプリで使用しているので、後にblogsアプリに移行
#
#     """
#     title = models.CharField('人気記事', max_length=100)
#     path = models.CharField('URL', max_length=100)
#     view = models.IntegerField('閲覧数')
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = '人気記事リスト'
#         verbose_name_plural = '人気記事リスト'
