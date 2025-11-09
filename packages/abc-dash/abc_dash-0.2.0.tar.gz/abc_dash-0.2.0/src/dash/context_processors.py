from django.conf import settings

TITLES = {
    "django_registration_register": "新規会員登録",
    "django_registration_complete": "仮登録が完了いたしました。",
    "django_registration_activation_complete": "会員登録の受付が完了いたしました。",
    "django_registration_activate": "既に会員登録が完了しているか、無効なURLです。",  # completeに飛ばないときはエラー
    "django_registration_disallowed": "ただいま会員登録はご利用いただけません。",
    "login": "ログイン"
}


def add_title(request):
    matcher_key = request.resolver_match.url_name
    if matcher_key and request.resolver_match.namespace:
        matcher_key = request.resolver_match.namespace + ":" + matcher_key

    if hasattr(settings, "TITLES"):
        project_titles = settings.TITLES
    else:
        project_titles = {}

    title = project_titles.get(matcher_key, "")

    if not title:
        title = TITLES.get(matcher_key, "")

    return {
        "title": title,
    }
