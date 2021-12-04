# 该后端为飞书课表录入的后端

由uwsgi + nginx + django架构实现

目前可以进行华南理工大学以及广东工业大学的课表录入

# 主要接口

/api中主要为调用接口

/api/scut

/api/gdut

/backstage/views.py

主要为简单的url通信以及飞书登录权限获取

# 前端文件

/static文件夹中有前端HTML、js、css源码以及图片

# 网页url

backstage.easypus.com/feishu
