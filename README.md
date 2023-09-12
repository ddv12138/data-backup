# 使用说明
## 一般使用
### step1 安装依赖
```shell
pip install requirements.txt
```
### step2 修改配置
1. 修改 [config.py](src/config.py) 或者直接在命令行指定，命令行说明见下方
2. 修改邮箱配置，用于发送阿里云盘登陆二维码，将 [email_config_example.py](email_config_example.py)重命名为 `email_config.py` 之后修改其中的配置

### step3 运行并查看帮助
```
python main.py -h
```
## 容器部署

### 拉取镜像
```
docker push ddv12138/data-backup
```

### 运行定时任务进行备份
1. 参考配置文件内的说明，编写配置文件 ```config.py```，重点在于
   - exclude_list：排除清单，备份过程中需要排除的文件或者文件夹
   - password：加密用的密码
   - cloud_path: 备份在阿里云盘的存放位置，程序不会自动创建，需要手动提前创建好
   - cron_expression： 任务执行周期的cron表达式，具体参见 [croniter表达式说明](https://pypi.org/project/croniter/)
   - max_copy_count: 同时保存的最大备份数量，过期的将移入回收站
2. 如果使用邮箱接收二维码进行登陆验证```(推荐)```,还需要修改配置文件 [email_config_example.py](email_config_example.py)，重命名为 ```email_config.py```
3. 准备好以上配置文件以后，假设```config.py```中include_list为默认的只有一个 ```backup```,docker启动命令如下
```
docker run -itd --restart \
-v <folder_need_backup_1>:/app/backup/<folder_need_backup_1> \
-v <folder_need_backup_2>:/app/backup/<folder_need_backup_2> \
-v <file_need_backup_1>:/app/backup/<file_need_backup_1> \
-v <file_need_backup_2>:/app/backup/<file_need_backup_2> \
-v <your_config.py>:/app/config.py \
-v <your_email_config.py>:/app/email_config.py \
ddv12138/data-backup
```
docker-compose.yml

```shell
version: '3.3'
services:
    data-backup:
    image: ddv12138/data-backup
    restart: unless-stopped
    volumes:
     - '<folder_need_backup_1>:/app/backup/<folder_need_backup_1>'
     - '<folder_need_backup_2>:/app/backup/<folder_need_backup_2>'
     - '<file_need_backup_1>:/app/backup/<file_need_backup_1>'
     - '<file_need_backup_2>:/app/backup/<file_need_backup_2>'
     - '<your_config.py>:/app/config.py'
     - '<your_email_config.py>:/app/email_config.py'
     - '<your_cache_dir>:/app/cache'
```

其中```folder_need_backup_1```和```folder_need_backup_2```为需要备份的文件夹举例，映射到容器目录/app/backup下，需要备份的文件```file_need_backup_1```、```file_need_backup_2```类似，此外需要的配置文件也分别映射到容器对应位置

以上只是一种配置情况举例，实际可以根据实际情况，自由调整配置文件以及容器的目录映射

### 立即执行一次备份
参考[运行定时任务进行备份](#运行定时任务进行备份)中的1、2、3步编辑好配置文件以后，运行以下命令可立即执行一次备份
```shell
docker run --rm ddv12138/data-backup python main.py backup
```

### 查看上一次备份成功以后的打包信息
参考[运行定时任务进行备份](#运行定时任务进行备份)中的1、2、3步编辑好配置文件以后，首先需要知道缓存文件存放位置，也就是配置文件中的 ```cache_dir```，然后取缓存文件路径，有分包的情况下，指定任意分包即可
```shell
docker run --rm ddv12138/data-backup python main.py info -i cache/xxxx-xx-xx_xx.xx.xx/package.x.ddv
```

### 使用其他配置
如果需要自定义是否使用加密，是否使用压缩，日志级别，进度条开关等，可以通过修改config.py，也可以通过命令行参数指定，查看具体的命令行参数可以使用如下命令
```shell
docker run --rm ddv12138/data-backup python main.py -h
```

