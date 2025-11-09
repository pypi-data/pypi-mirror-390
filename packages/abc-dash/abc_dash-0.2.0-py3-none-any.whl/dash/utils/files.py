import unicodedata
import uuid

import pathvalidate


def sanitize_filename(val, normalize=True):
    """
    ファイル名をサーバー上(unix系)で安全に扱えるようにする。

    upload_to で直接アップロード元のファイルを使う際や、ユーザーが入力した名称をファイル名として使う際に。
    """
    if normalize:
        val = unicodedata.normalize("NFC", val)
    return pathvalidate.sanitize_filename(
        val, replacement_text="-", platform="universal"
    )


def per_model_path(instance, filename):
    """
    ファイル名をランダムに生成し、インスタンスのクラス名に基づきフォルダ分けをする。

    upload_to に直接設定できる。
    ユーザーがアップした名前は重要ではなく、重複なく安全に保存したい際に。
    """
    return "{}/{}".format(instance._meta.db_table, get_random_filename(filename, True))


def get_random_filename(filename, organize=False):
    ext = filename.rsplit(".", 1)
    ext = "." + ext[1] if ext else ""
    new_filename = "{}{}".format(uuid.uuid4().hex, ext)
    if not organize:
        return new_filename
    return "{}/{}".format(new_filename[0:2], new_filename)
