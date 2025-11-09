# zfl-blogs

[![PyPI - Version](https://img.shields.io/pypi/v/zfl-blogs.svg)](https://pypi.org/project/zfl-blogs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zfl-blogs.svg)](https://pypi.org/project/zfl-blogs)

![Videotogif (1)](https://github.com/kenno-warise/zfl-blogs/assets/51676019/40e84ba8-6da0-47eb-b8f9-a82f84b034d5)

-----

**目次**

- [詳細](#詳細)
- [インストール](#インストール)
- [設定](#設定)
- [実行](#実行)
- [License](#license)

## 詳細

zfl-blogs

## インストール

```console
$ pip install --upgrade pip

$ pip --version
pip 21.3.1

$ pip install zfl-blogs
```

## 設定

`settings.py`の編集

```python
INSTALLED_APPS = [
    ...
    'django.forms',
    'django_cleanup',  # ファイルを自動的に削除するサードパーティ
    'markdownx',       # Django用に構築されたMarkdownエディタ
    'blogs',           # zfl-blogsアプリ
]

# マークダウンプレビューで必要な定義
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

...

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # プロジェクト直下でのtemplatesディレクトリを有効にする
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'blogs.context.common',  # context.pyのcommon関数をテンプレートで使えるようにする
            ],
            # カスタムテンプレートタグ
            'libraries': {
                'mark': 'blogs.templatetags.mark',
            }
        },
    },
]

...

STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MARKDOWNX_IMAGE_MAX_SIZE = {'size': (800, 500), 'quality': 100}

MARKDOWNX_UPLOAD_MAX_SIZE = 1000 * 1024 # 最大1MBまで可能

MARKDOWNX_UPLOAD_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']

MARKDOWNX_MARKDOWN_EXTENSIONS = [
        'extra',  # Markdownの拡張機能
        'admonition', # 訓戒・忠告
        'sane_lists', # 正常なリスト
        'toc',    # 目次
        'nl2br',  # 改行
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
        'toc': {
            'title': '目次',
            'permalink': True
        }
}

```

`urls.py`の編集

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('markdownx/', include("markdownx.urls")),
    path('blogs/', include("blogs.urls")),
]

# 開発環境での設定
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`settings.py`の`FORM_RENDERER`で`django.forms.renderers.TemplatesSetting`に設定しているので、プロジェクト直下に`templates`ディレクトリを作成し、`blogs`アプリの`templates`ディレクトリから`markdownx`ディレクトリをコピーしてきます。

そうすることで、記事を書く際のマークダウンプレビューを横並びにすることができます。

- [django-markdownx プレビュー](https://pypi.org/project/django-markdownx/3.0.1/)

プロジェクト直下に「templates」ディレクトリを作成します。

```console
$ mkdir templates
```

zfl-blogsパッケージ内にある「markdownx/widget.html」をプロジェクト直下の「templates」ディレクトリにコピーします。

以下のようにして目的のディレクトリの在り処を確認できます。

```console
$ python3 -c "import blogs; print(blogs.__path__[0])"
.../lib/python3.6/site-packages/blogs
```

linuxコマンドの「xargs」を使って一行でコピーしてしまいます。

```console
$ python3 -c "import blogs; print(blogs.__path__[0]+'/templates/markdownx')" | xargs -I % -t cp -r % templates/.
cp -r /../lib/python3.6/site-packages/blogs/templates/markdownx templates.
```

プロジェクト直下のディレクトリを確認

```console
$ls templates
markdownx
```

プロジェクト直下のtemplatesディレクトリ内にある「base.html」をエクステンドしているので、「base.html」には「title」・「blogs-style」のブロックタグを設定します。

デザインはCSSフレームワークのBootstrap5.3.0を使用しています。

```html
<html lang="ja" prefix="og: http://ogp.me/ns#">
  <head>

    <!-- Webサイトタイトル -->
    <title>{% block title %}Blog{% endblock title %}</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
    <!-- Bootstrap ICON -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">

    <!-- OginalApp Style -->
    {% block blogs-style %}{% endblock blogs-style %}

  </head>
  <body>

    {% block content %}
    {% endblock %}

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
  </body>
</html>
```

## 実行

データベースの作成

```console
$ python3 manage.py migrate
```

スーパーユーザーの作成

```console
$ python3 manage.py createsuperuser
```

起動

```console
$ python3 manage.py runserver
```

## その他

markdownxで保存された画像は自動的に削除されないので、file_cleanupコマンドを実行して手動削除する必要があります。

```console
$ python3 manage.py file_cleanup
```

## License

`zfl-blogs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
