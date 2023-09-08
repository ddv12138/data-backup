# 使用说明
## step1 安装依赖
```shell
pip install requirements.txt
```
## step2 修改配置
1. 修改 [config.py](config.py) 或者直接在命令行指定，命令行说明见下方
2. 修改邮箱配置，用于发送阿里云盘登陆二维码，将 [email_config_example.py](email_config_example.py)重命名为 `email_config.py` 之后修改其中的配置

## step3 运行并查看帮助
```
python main.py -h
```

# 待完成事项

1. docker支持
2. 受排除文件的通配符匹配
3. 支持从文件读取密码
