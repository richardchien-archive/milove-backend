# Milove Backend

Milove 网站后端，提供了 `Dockerfile`，跑的时候需要指定 django 和 gunicorn 的配置文件，前者由 `DJANGO_SETTINGS_MODULE` 环境变量指定（一般为 `milove/settings_prod.py`），后者固定为项目根目录下的 `gunicorn_config.py` 文件。
