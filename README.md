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

# 命令行配置说明
```shell
usage: main.py [-h] [--mode {task,backup,unpack,info}] [--disable_enc DISABLE_ENC] [--disable_gzip DISABLE_GZIP] [--cache_dir CACHE_DIR]
               [--password PASSWORD] [--cloud_path CLOUD_PATH] [--config_path CONFIG_PATH] [--cron_expression CRON_EXPRESSION]
               [--max_copy_count MAX_COPY_COUNT] [-v VERBOSE]
               [file]

一个自动的周期性的把文件备份到阿里云的工具

positional arguments:
  file                  存放备份文件的文件夹路径或者备份文件之一

optional arguments:
  -h, --help            show this help message and exit
  --mode {task,backup,unpack,info}, -m {task,backup,unpack,info}
                        运行模式，task 为执行定时备份，decrypt 为解密，backup为即可执行一次备份，info用于查看已有的包信息
  --disable_enc DISABLE_ENC, -e DISABLE_ENC
                        是否加密
  --disable_gzip DISABLE_GZIP, -g DISABLE_GZIP
                        是否压缩
  --cache_dir CACHE_DIR
                        缓存文件路径
  --password PASSWORD   加密用的密钥，妥善保存，解密需要用到
  --cloud_path CLOUD_PATH
                        阿里云用于备份的文件路径
  --config_path CONFIG_PATH
                        配置文件存储路径
  --cron_expression CRON_EXPRESSION
                        定时任务表达式
  --max_copy_count MAX_COPY_COUNT
                        云端保存的最大备份数量
  -v VERBOSE, --verbose VERBOSE
                        展示更详细的执行过程
```
# 待完成事项

1. docker支持
2. 受排除文件的通配符匹配
3. 支持从文件读取密码
