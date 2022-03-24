# Navinfo
自动化脚本实现
## TestHdms
HDMS项目相关业务
### 1、Base
公共部分
#### basefunc_test.py
公共方法
#### test_field.py
公共字段，包含环境信息维护
### 2、TestBug
迭代过程中可实现自动化的Bug，以禅道Bug编号区分
### 3、TestCases
通用脚本
#### test_datacheck.py
功能：各个字段校验  
范围：hcc|hci|rcsint|rcsext 正式线|测试线  
未覆盖场景：  
（1）msg_id：该字段不在代码校验范围内  
（2）字段重复：pycharm调用字段重复的json文件时，返回结果未上报错误日志，postman调用正常返回错误日志
#### test_datacheck_miss.py
功能：各个字段缺失校验  
范围：hcc|hci|rcsint|rcsext 正式线|测试线  
未覆盖场景：msg_id字段缺失时自动补充为null，不上报错误日志
#### test_smoke_hcc.py
功能：冒烟测试  
范围：hcc|hci 正式线|测试线  
覆盖场景：更新、部分删除、备份校验、错误日志上报、过期删除attr_id（手工查看）  
未覆盖场景：全部删除
#### test_smoke_rcs.py
功能：冒烟测试  
范围：rcsint|rcsext 正式线|测试线  
覆盖场景：发布、更新、删除、备份、错误日志上报、过期删除（手工查看）
