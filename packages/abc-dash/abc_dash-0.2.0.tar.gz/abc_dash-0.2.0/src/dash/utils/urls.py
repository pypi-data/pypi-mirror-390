from django.http import QueryDict
from django.urls import path


def append_param(base_url, params, current_params=None):
    if current_params:
        new_params = current_params.copy()
    else:
        new_params = QueryDict(mutable=True)

    new_params.update(params)

    return base_url + "?" + new_params.urlencode()


def resources(singular, cls, views, prefix=None, name_base=None, pk_expr="<int:pk>"):
    """
    Generate CRUD urls.

    On each generation, try to find relavant view class. If not exists, just ignore.

    | path                         | view       | name              |
    | /{singular}/                 | ListView   | {singular}_list   |
    | /{singular}/add              | CreateView | {singular}_add    |
    | /{singular}/<int:pk>/        | DetailView | {singular}_detail |
    | /{singular}/<int:pk>/change  | UpdateView | {singular}_change |
    | /{singular}/<int:pk>/delete  | DelteView  | {singular}_delete |
    """
    patterns = []
    base = "{}".format(singular)

    if not name_base:
        name_base = singular
    if prefix:
        base = "{}/{}".format(prefix, base)
        name_base = "{}_{}".format(prefix, name_base)

    try:
        patterns.append(
            path(
                "{}/".format(base),
                getattr(views, "{}ListView".format(cls)).as_view(),
                name="{}_list".format(name_base)
            )
        )
    except AttributeError:
        pass

    try:
        patterns.append(
            path(
                "{}/add".format(base),
                getattr(views, "{}CreateView".format(cls)).as_view(),
                name="{}_add".format(name_base)
            )
        )
    except AttributeError:
        pass

    try:
        patterns.append(
            path(
                "{}/{}/".format(base, pk_expr),
                getattr(views, "{}DetailView".format(cls)).as_view(),
                name="{}_detail".format(name_base)
            )
        )
    except AttributeError:
        pass

    try:
        patterns.append(
            path(
                "{}/{}/change".format(base, pk_expr),
                getattr(views, "{}UpdateView".format(cls)).as_view(),
                name="{}_change".format(name_base)
            )
        )
    except AttributeError:
        pass

    try:
        patterns.append(
            path(
                "{}/{}/delete".format(base, pk_expr),
                getattr(views, "{}DeleteView".format(cls)).as_view(),
                name="{}_delete".format(name_base)
            )
        )
    except AttributeError:
        pass

    return patterns


def filterset_as_query_dict(filterset):
    """
    フィルターとして動作するクエリパラメータだけをdictとして返す

    動作しないパラメータ例: page, submit
    """
    if not filterset.is_bound:
        return {}

    # 1. 有効なパラメータ名を列挙
    valid_keys = set()
    for name in filterset.filters.keys():
        field = filterset.form.fields.get(name)
        if field is None:
            continue
        widget = field.widget
        # SuffixedMultiWidget系
        suffixes = getattr(widget, "suffixes", None)
        if suffixes:
            for suffix in suffixes:
                valid_keys.add(f"{name}_{suffix}")
        # 基底名も有効
        valid_keys.add(name)

    # 2. dataから有効なものだけ抽出
    q = {}
    for k, v in filterset.data.items():
        if v in [None, ""]:
            continue
        if k in valid_keys:
            q[k] = v
    return q
