# Milove Backend

Milove 网站后端，提供了 `Dockerfile`，跑的时候需要指定 django 和 gunicorn 的配置文件，前者由 `DJANGO_SETTINGS_MODULE` 环境变量指定（一般为 `milove/settings_prod.py`），后者固定为项目根目录下的 `gunicorn_config.py` 文件。

API 相关的所有东西，将来会从 Postman 导出。

目前在尝试使用 NextCloud 私有云，将来 `Product` 需要改动，把 `ImageField` 改成和 `SellRequest` 类似的，自动读取指定目录下的所有图片，以和 NextCloud 整合。

后端还差一个提现没有写，打算最后再说。
