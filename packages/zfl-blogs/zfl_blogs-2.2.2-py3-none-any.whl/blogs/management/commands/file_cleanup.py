import glob
import os
import re

from django.conf import settings  # type: ignore
from django.core.management.base import BaseCommand  # type: ignore

from blogs.models import Blog


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        markdownxで蓄積した画像ファイルを整理

        $ python3 manage.py file_cleanup
        """
        img_list = []
        sum_deletes = 0
        blogs = Blog.objects.all()
        for blog in blogs:
            img_datas = re.findall(
                r"(?<=\!\[\]\(/)\w+/\w+/\w+-\w+-\w+-\w+-\w+.\w+", blog.text
            )
            img_datas_2 = re.findall(
                r'(?<=\<img src\="/)\w+/\w+/\w+-\w+-\w+-\w+-\w+.\w+', blog.text
            )
            if img_datas:
                img_list += img_datas
            if img_datas_2:
                img_list += img_datas_2
        if settings.DEBUG:
            candidates_delete = glob.glob("media/markdownx/*.*")
        else:
            img_list = [re.sub(r"^", "/var/www/", img) for img in img_list]
            candidates_delete = glob.glob("/var/www/media/markdownx/*.*")
        for candidate in candidates_delete:
            if candidate not in img_list:
                self.stdout.write(self.style.SUCCESS(f"削除 => {candidate}"))
                os.remove(candidate)
                sum_deletes += 1
        self.stdout.write(self.style.SUCCESS(f"記事中ファイル合計: {len(img_list)}"))
        self.stdout.write(self.style.SUCCESS(f"メディアファイル合計: {len(candidates_delete)}"))
        self.stdout.write(self.style.SUCCESS(f"削除したファイル合計: {sum_deletes}"))
        self.stdout.write(self.style.SUCCESS("クリーンアップ完了"))
