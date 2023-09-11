# Extend the official Rasa SDK image
FROM python:3.8.5

# Use subdirectory as working directory
WORKDIR /app

# Copy actions folder to working directory
COPY ./BytesChain /app/BytesChain
COPY ./ddv /app/ddv
COPY ./AligoUtil.py /app/AligoUtil.py
COPY ./config.py /app/config.py
COPY ./EncUtil.py /app/EncUtil.py
COPY ./FilePack.py /app/FilePack.py
COPY ./LogUtil.py /app/LogUtil.py
COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt
# Change back to root user to install dependencies
USER root

# Install extra requirements for actions code, if necessary (uncomment next line)
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# By best practices, don't run the code with root user
USER 1001

# Start the action server
ENTRYPOINT ["python", "main.py"]
CMD ["--mode task"]