# Extend the official Rasa SDK image
FROM python:3.8.5

# Use subdirectory as working directory
WORKDIR /app

# Copy actions folder to working directory
COPY src requirements.txt  /app/
# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && mkdir /.aligo \
    && chown -R 1001:1001 /.aligo \
    && chown -R 1001:1001 /app \
    && chmod -R 755 /app \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone
# By best practices, don't run the code with root user
USER 1001

# Start the action server
#ENTRYPOINT ["python", "main.py"]
#CMD ["--mode task"]
CMD ["ls"]
