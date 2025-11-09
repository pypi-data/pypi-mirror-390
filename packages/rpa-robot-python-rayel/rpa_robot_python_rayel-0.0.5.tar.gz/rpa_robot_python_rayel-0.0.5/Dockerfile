FROM python:3.9-alpine3.20

WORKDIR /app

# 把代码添加到工作目录
ADD main.py demo_job.py ./

# 安装 snail-job-python 依赖
RUN pip install -v snail-job-python -i https://mirrors.aliyun.com/pypi/simple/

ENTRYPOINT [ "python", "main.py" ]
