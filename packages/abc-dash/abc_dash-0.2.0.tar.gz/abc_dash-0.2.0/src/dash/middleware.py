class RealIpMiddleware:
    """
    ソケットモードのgunicornでIPを補完する

    ポートではなくソケットでgunicornを稼働させる場合、REMOTE_ADDR が空になってしまう。
    nginxをproxy_paramsで正しく設定していれば閲覧者のIP(つまりnginxから見た$remote_addr)がX-Real-IPにセットされる。
    これをgunicornに渡すミドルウェア。

    X-Forwarded-Forとは全く異なる概念なので混同しないこと。
    """
    HEADER_KEY = "HTTP_X_REAL_IP"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.HEADER_KEY in request.META:
            remote_addr = request.META.get(self.HEADER_KEY)
            request.META["REMOTE_ADDR"] = remote_addr
        return self.get_response(request)
