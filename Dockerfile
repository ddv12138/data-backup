FROM python:3.8-slim-bookworm
WORKDIR /app
COPY src requirements.txt  /app/
USER root
RUN apt-get update && apt-get install -y p7zip-full && rm -rf /var/lib/apt/lists/* \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && mkdir /.aligo \
    && chown -R 1001:1001 /.aligo \
    && chown -R 1001:1001 /app \
    && chmod -R 755 /app \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone

ENTRYPOINT ["python", "main.py"]
CMD ["task","--progress"]

