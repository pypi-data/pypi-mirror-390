from .models import Category


def common(request):
    """
    カテゴリーのインスタンスを取得

    """
    context = {
        "category_list": Category.objects.all(),
    }
    return context
