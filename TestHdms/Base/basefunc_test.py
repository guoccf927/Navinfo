# -*- coding: utf-8 -*-
# @Author    :guocongcong7572@navinfo.com
import hashlib
import math
import os
import subprocess
import sys
import time

import requests
import json
import psycopg2
import redis
import datetime

from crcmod.predefined import PredefinedCrc
from Navinfo.TestHdms.Base.test_field import *

# 存取变量
GLOBAL_VALUE = {}


class TestBaseFunc:

    def add_global_variable(self, key, value):
        if key is None:
            pass
        elif isinstance(key, str):
            GLOBAL_VALUE[key] = value
            return GLOBAL_VALUE
        else:
            for i, j in zip(key, value):
                GLOBAL_VALUE[i] = j
        return GLOBAL_VALUE

    def get_global_variable(self, get_key):
        if get_key is None:
            pass
        return GLOBAL_VALUE[get_key]

    def get_trace_id(self, catalog_type, layer_type, json_file, domain=DOMAIN):
        """
        :param catalog_type:
        :param layer_type:
        :param json_file:
        :param domain:
        :return: TraceID
        """

        url = f"{domain}/ingest/v1/catalogs/{catalog_type}/layers/{layer_type}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': AUTHORIZATION_NOEXPIRE
        }
        res = requests.post(url, json=json_file, headers=headers)
        res_test = json.loads(res.text)
        print(res_test)
        trace_id = res_test["TraceID"]
        print(f"trace_id: {trace_id}")
        return trace_id

    def get_pgsql(self, sql_statement):
        """
        :param sql_statement:
        :return: sql语句执行结果
        """
        # 创建连接对象
        pg_conf = {
            "database": "id_editor",
            "user": "idpg",
            "password": "b7QQzZoUyId1hEfI",
            "host": "10.60.156.253",
            "port": 5432
        }
        conn = psycopg2.connect(**pg_conf)
        cur = conn.cursor()

        # 执行sql语句
        cur.execute(sql_statement)
        if 'select' in sql_statement or 'SELECT' in sql_statement:
            sql_res = cur.fetchall()
            print(sql_res)

        # 关闭连接
        conn.commit()
        cur.close()
        conn.close()

        # 返回sql执行结果
        if 'select' in sql_statement or 'SELECT' in sql_statement:
            return sql_res

    def get_tile_expire(self, tile_id, zset_key, prod_flag=True, redis_env_key=REDIS_ENV_KEY, redis_conf=REDIS_CONF):
        """
        :param tile_id:目标tile
        :param zset_key:例如，"oso:cloud_test:rcs:expires:103"中"rcs:expires:103"
        :param prod_flag:正式线|测试线 标志位，默认正式线
        :param redis_env_key:环境切换，统一维护
        :param redis_conf:环境redis连接信息，统一维护
        :return: 返回tile_id对应的过期时间UTC格式 or 不存在
        """

        # 创建redis连接对象,实现一个连接池
        pool = redis.ConnectionPool(**redis_conf)
        r = redis.Redis(connection_pool=pool)
        # r = redis.Redis(**redis_conf) # 耗资源

        # 正式线 | 测试线
        if prod_flag:
            redis_env_key = redis_env_key
        if not prod_flag:
            redis_env_key = f'{redis_env_key}_int'

        # 查看ZSET-tile的过期时间
        re_expire = f"oso:{redis_env_key}:{zset_key}"
        tiles_with_scores = r.zrange(re_expire, 0, -1, withscores=True)
        print(tiles_with_scores)

        # 取出指定tile_id的过期时间并转UTC格式，不存在则返回False
        for elem in tiles_with_scores:
            if tile_id in elem:
                timestamp = int(elem[1]) / 1000
                expires_time = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")
                print(f"{re_expire}/{tile_id} 过期时间: {expires_time}")
                return expires_time
        else:
            now_time = datetime.datetime.now()
            print(now_time)
            print(f"{tile_id} 不存在")
            return 'false'

    def get_redis_rcs_attrid(self, attr_list=[], del_flag=False, rcsint_flag=True, rcs_prod_flag=True,
                             redis_env_key=REDIS_ENV_KEY, redis_conf=REDIS_CONF):
        """
        :param redis_key: redis查看的key
        :param attr_list: 默认空，在校验attr_id时传参
        :param del_flag: 默认不删除，在需要删除时置位为TRUE
        :param rcsint_flag: 默认查看rcsint, False查看rcsext
        :param rcs_prod_flag: 默认查看正式线，False查看测试线
        :param redis_conf: redis连接信息
        :param redis_env_key: redis目录，根据环境不同进行改变
        :return: 校验结果
        """
        # 创建redis连接对象,实现一个连接池
        pool = redis.ConnectionPool(**redis_conf)
        r = redis.Redis(connection_pool=pool)

        # 正式线 | 测试线
        if rcs_prod_flag:
            redis_env_key = redis_env_key
        if not rcs_prod_flag:
            redis_env_key = f'{redis_env_key}_int'

        # rcsint |rcsext
        if rcsint_flag:
            re_attr = f"oso:{redis_env_key}:rcs:attrids:103_*ey3Idie8zwxiw=="
        if not rcsint_flag:
            re_attr = f"oso:{redis_env_key}:rcs:attrids:108_*ey3Idie8zwxiw=="

        # 查看attr_id列表
        list_keys = r.keys(re_attr)
        print(list_keys)

        # 共用标志位
        attr_flag = True

        # 查看STRING-attr是否存在
        if not del_flag:
            for attr in attr_list:
                if f'{re_attr[:-16]}{attr}' not in list_keys:
                    attr_flag = False
            return attr_flag

        if del_flag:
            # 进行attr_id删除操作
            if len(list_keys) == 0:
                return attr_flag

            if len(list_keys) != 0:
                for key in list_keys:
                    r.delete(key)
                return self.get_redis_rcs_attrid()

    def get_redis_rcs_expire(self, tile_list, rcsint_flag=True, rcs_prod_flag=True, redis_env_key=REDIS_ENV_KEY,
                             redis_conf=REDIS_CONF):
        """
        :param tile_list:
        :param rcs_prod_flag: 默认正式线， False测试线
        :param rcsint_flag: 默认查看rcsint；False则查看rcsext
        :param redis_env_key: 默认查看正式线(测试环境)
        :param redis_conf: 默认测试环境
        :功能: 查看redis "oso:*:rcs:expires:103|8"
        """

        # 创建redis连接对象,实现一个连接池
        pool = redis.ConnectionPool(**redis_conf)
        r = redis.Redis(connection_pool=pool)
        # r = redis.Redis(**redis_conf) # 耗资源

        # 正式线 | 测试线
        if rcs_prod_flag:
            redis_env_key = redis_env_key
        if not rcs_prod_flag:
            redis_env_key = f'{redis_env_key}_int'

        # 查看ZSET-tile的过期时间
        if rcsint_flag:
            re_expire = f"oso:{redis_env_key}:rcs:expires:103"
        if not rcsint_flag:
            re_expire = f"oso:{redis_env_key}:rcs:expires:108"
        tiles_with_scores = r.zrange(re_expire, 0, -1, withscores=True)
        print(tiles_with_scores)

        # 取出tile
        tiles_redis = []
        for elem in tiles_with_scores:
            tiles_redis.append(elem[0])
        print(tiles_redis)
        # 查看tile是否都存在，存在不存在的情况则为False
        expire_flag = True
        for tile in tile_list:
            if str(tile) not in tiles_redis:
                expire_flag = False

        return expire_flag

    def get_redis_rcs_tile(self, tile_list, rcsint_flag=True, rcs_prod_flag=True, redis_env_key=REDIS_ENV_KEY,
                           redis_conf=REDIS_CONF):
        """
        :param tile_list:
        :param rcs_prod_flag: 默认正式线， False测试线
        :param rcsint_flag: 默认查看rcsint；False则查看rcsext
        :param redis_env_key: 默认查看正式线(测试环境)
        :param redis_conf: 默认测试环境
        :功能: 查看redis3个key的内容"oso:cloud_test:rcs:expires:103"
        """

        # 创建redis连接对象,实现一个连接池
        pool = redis.ConnectionPool(**redis_conf)
        r = redis.Redis(connection_pool=pool)
        # r = redis.Redis(**redis_conf) # 耗资源

        # 正式线 | 测试线
        if rcs_prod_flag:
            redis_env_key = redis_env_key
        if not rcs_prod_flag:
            redis_env_key = f'{redis_env_key}_int'

        # 查看HASH-tile
        if rcsint_flag:
            re_tile = f"oso:{redis_env_key}:rcs:tiles:103"
        if not rcsint_flag:
            re_tile = f"oso:{redis_env_key}:rcs:tiles:108"
        tile_flag = True
        for tile in tile_list:
            tile_with_time_str = r.hget(re_tile, tile)
            print(tile_with_time_str)
            if tile_with_time_str is None:
                tile_flag = False

        return tile_flag

    def get_redis_rcs_tile_info(self, tile_id, rcsint_flag=True, rcs_prod_flag=True, redis_env_key=REDIS_ENV_KEY,
                                redis_conf=REDIS_CONF):
        """
        :param tile_id:
        :param rcsint_flag:
        :param rcs_prod_flag:
        :param redis_env_key:
        :param redis_conf:
        :return: 返回整个value，json格式
        """
        # 创建redis连接对象,实现一个连接池
        pool = redis.ConnectionPool(**redis_conf)
        r = redis.Redis(connection_pool=pool)
        # r = redis.Redis(**redis_conf) # 耗资源

        # 正式线 | 测试线
        if rcs_prod_flag:
            redis_env_key = redis_env_key
        if not rcs_prod_flag:
            redis_env_key = f'{redis_env_key}_int'

        # 查看HASH-tile
        if rcsint_flag:
            re_tile = f"oso:{redis_env_key}:rcs:tiles:103"
        if not rcsint_flag:
            re_tile = f"oso:{redis_env_key}:rcs:tiles:108"

        tile_with_time_str = r.hget(re_tile, tile_id)
        tile_with_time_json = json.loads(tile_with_time_str)
        print(tile_with_time_json)
        return tile_with_time_json

    def get_tile_info(self, tile_list, catalog_type, layer_type, timestamp_flag=False, domain=DOMAIN):
        """
        :param tile_list:
        :param catalog_type:hdms平台输出的catalog
        :param layer_type:hdms平台输出的layer
        :param timestamp_flag: 默认不查看tile的更新时间；True则查看更新时间，不查看tile个数
        :param domain: 环境信息
        :return: 默认返回tile个数，timestamp_flag=TRUE时返回tile的更新时间
        """
        url = f"{domain}/hadauth/api/catalog/{catalog_type}/layer/{layer_type}/partitions"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': AUTHORIZATION_NOEXPIRE
        }

        num_list = []
        timestamp_list = []
        for tile_id in tile_list:
            payload = {
                "partition": "%s" % tile_id,
                "orderBy": "DESC",
                "page": 1,
                "pageSize": 10
            }
            res = requests.post(url, json=payload, headers=headers)
            res_test = json.loads(res.text)
            total_num = res_test["data"]["total"]
            num_list.append(total_num)
            print(f'{catalog_type}/{layer_type}/{tile_id}/total_num: {total_num}')
            if timestamp_flag:
                timestamp = res_test['data']['rows'][0]['timeStamp']
                print(timestamp)
                timestamp_list.append(timestamp)
        if timestamp_flag:
            print(timestamp_list)
            return timestamp_list
        print(num_list)
        return num_list

    def get_tile_list(self, catalog_type, layer_type, domain=DOMAIN):
        """
        :param catalog_type:hdms上输出的catalog id
        :param layer_type:hdms上输出的layer id
        :param domain: 环境信息
        :return: 返回tile list
        """
        url = f"{domain}/hadauth/api/catalog/{catalog_type}/layer/{layer_type}/partitions"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': AUTHORIZATION_NOEXPIRE
        }

        tile_list = []
        payload = {
            "partition": "",
            "orderBy": "DESC",
            "page": 1,
            "pageSize": 10
        }
        res = requests.post(url, json=payload, headers=headers)
        res_test = json.loads(res.text)
        total_num = res_test["data"]["total"]
        print(f'tile total_num:{total_num}')
        loop_num = math.ceil(total_num / 10)
        for i in range(loop_num):
            page = i + 1
            payload = {
                "partition": "",
                "orderBy": "DESC",
                "page": page,
                "pageSize": 10
            }
            res = requests.post(url, json=payload, headers=headers)
            res_test = json.loads(res.text)
            for j in range(len(res_test['data']['rows'])):
                partition = res_test['data']['rows'][j]['partition']
                tile_list.append(partition)

        print(f'{catalog_type}/{layer_type} is: {tile_list}')
        return tile_list

    def get_tile_checksum_crc(self, tile_list, catalog_id, layer_id, domain=DOMAIN):
        """
        从hdms平台下载下来的tile文件，读取其中的checksum和crc
        :param tile_list:
        :param catalog_id:hdms平台oso输出的catalog
        :param layer_id:hdms平台oso输出catalog下的layer
        :param domain: 环境信息
        :return: 返回list = [tile, checksum, crc]
        """

        checksum_crc_list = []

        for tile in tile_list:
            url = f"{domain}/hadauth/api/download/v1/catalogs/{catalog_id}/layers/{layer_id}/data/{tile}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': AUTHORIZATION_NOEXPIRE
            }
            res = requests.get(url, headers=headers)
            content = res.content
            # 下载的tile文件是byte类型，进行解码取出checksum和crc
            # 获取checksum
            sha1func = hashlib.sha256()
            sha1func.update(content)
            sha256 = str(sha1func.hexdigest())
            checksum = sha256.upper()
            # 获取crc
            hasher = PredefinedCrc('crc-32c')
            hasher.update(content)
            crc32c = hasher.digest()
            crc32c = int.from_bytes(crc32c, byteorder='big', signed=False)
            crc32c = str("%X" % (crc32c & 0xffffffff)).lower()
            if len(crc32c) < 8:
                for i in range(8):
                    prefix = '0' * i
                    crc32c_new = f'{prefix}{crc32c}'
                    if len(crc32c_new) == 8:
                        break
                crc32c = crc32c_new
            res_list = [tile, checksum, crc32c]
            checksum_crc_list.append(res_list)
        print(f'hdms/{catalog_id}/{layer_id} is:\n{checksum_crc_list}')
        return checksum_crc_list

    def query_tile_checksum_crc(self, catalog_id, layer_id, domain=DOMAIN):
        """
        从hdms平台下载下来的tile文件，读取其中的checksum和crc
        :param catalog_id:hdms平台oso输出的catalog
        :param layer_id:hdms平台oso输出catalog下的layer
        :param domain: 环境信息
        :return: 返回list = [tile, checksum, crc]
        """

        headers = {
            'Content-Type': 'application/json',
            'Authorization': AUTHORIZATION_NOEXPIRE
        }

        # # 获取当前catalog下layer的version-20220304
        # url = f'{domain}/hadauth/api/catalog/{catalog_id}/layer/{layer_id}'
        # res = requests.get(url, headers=headers)
        # res_test = json.loads(res.text)
        # version = res_test['data']['version']

        # 获取当前catalog的version-20220307
        url = f'{domain}/hadauth/api/catalog/{catalog_id}'
        res = requests.get(url, headers=headers)
        res_test = json.loads(res.text)
        version = res_test['data']['version']

        # 调用开发提供的接口-徐淑凤-10738
        url = f"{domain}/query/v2/catalogs/{catalog_id}/layers/{layer_id}/partitions"
        params = {"version": version}
        res = requests.get(url, params=params, headers=headers)
        res_test = json.loads(res.text)

        checksum_crc_list = []
        # 开发提供的接口取出tile、checksum和crc
        for i in range(len(res_test['partitions'])):
            # 获取tile
            tile = res_test['partitions'][i]['partition']
            # 获取checksum
            checksum = res_test['partitions'][i]['checksum']
            # 获取crc
            crc32c = res_test['partitions'][i]['crc']
            res_list = [tile, checksum, crc32c]
            checksum_crc_list.append(res_list)
        print(f'interface/{catalog_id}/{layer_id} is:\n{checksum_crc_list}')
        return checksum_crc_list

    def get_errorlog(self, catalog_type, layer_type, domain=DOMAIN):
        """
        :param catalog_type: 输出errorlog的catalog
        :param layer_type:输出errorlog的layer
        :param domain:
        :return:
        """

        # 找到第一个日志的datahandle
        url = f"{domain}/hadauth/api/catalog/{catalog_type}/layer/{layer_type}/partitions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': AUTHORIZATION_NOEXPIRE
        }
        payload = {"partition": "", "orderBy": "DESC", "page": 1, "pageSize": 10}
        res = requests.post(url, json=payload, headers=headers)
        res_test = json.loads(res.text)
        print(res_test)
        data_handle = res_test['data']['rows'][0]['dataHandle']
        print(f'dataHandle: {data_handle}')

        # 查看第一个日志内容
        url = f'{domain}/hadauth/api/download/v1/catalogs/{catalog_type}/layers/{layer_type}/data/{data_handle}'
        res = requests.get(url, headers=headers)
        # res_test = json.loads(res.text)
        # print(res_test)
        print(res.text)
        return res.text

    def run_cmd(self, cmd):
        """
        该类用于在一个新的进程中执行一个子程序。
        即允许你去创建一个新的进程让其执行另外的程序，并与它进行通信，获取标准的输入、标准输出、标准错误以及返回码等。
        :param cmd: cmd命令
        :return: res[1] 获得输出
        """

        # shell = True表示直接在解释器中运行，即不会弹出黑的命令行
        print(cmd)
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # 该方法和子进程交互，返回一个包含 输出和错误的元组，如果对应参数没有设置的，则无法返回
        sout, serr = res.communicate()

        # 可获得返回码、输出、错误、进程号；
        return res.returncode, sout, serr, res.pid

    def output_log_begin(self):
        """
        执行结果输出
        :return:outputfile
        """
        # 为避免log文件被覆盖，增加时间戳来分开记录
        log_day = time.strftime("%Y-%m-%d", time.localtime())
        path = f'D:\\PycharmProjects\\result\\log\\{log_day}\\'
        folder = os.path.exists(path)

        # 判断是否存在文件夹如果不存在则创建为文件夹
        if not folder:
            # makedirs 创建文件时如果路径不存在会创建这个路径
            os.makedirs(path)

        log_time = time.time()
        full_path = f'{path}log_{log_time}.txt'
        outputfile = open(full_path, 'w')
        sys.stdout = outputfile
        return outputfile

    def output_log_end(self, outputfile):
        """
        :param outputfile: output_log_begin的返回值
        """
        print(file=outputfile)
        # close后才能看到写入的数据
        outputfile.close()
