# -*- coding: utf-8 -*-
# @Time        :2022/1/19 14:44
# @Author      :guocongcong7572@navinfo.com
# @Description : rcs冒烟测试

import os
import sys
import time
from Navinfo.TestHdms.Base.basefunc_test import *
import pytest

FILE_LIST_DIR = r'E:/03 HDMS/98 测试文件/02 rcs-prod-int'
NO_END_TIME_ERR_LIST = [
    """"tile_replacements":[{"nds_packed_tile_id":"557017790","tileId_timestamp_errors":[{"error_code":"EC-RCSINT-DC-time","error_msg":"Invalid end time due to the field missing , empty or its invalid value."}],"oem_data_additions":null}]""",
    """"tile_replacements":[{"nds_packed_tile_id":"557017790","tileId_timestamp_errors":[{"error_code":"EC-RCSEXT-DC-time","error_msg":"Invalid end time due to the field missing , empty or its invalid value."}],"oem_data_additions":null}]""",
]
LOOP_NUM = 20
TIME_SLEEP = 3


class TestRcsSmoke(TestBaseFunc):

    # @pytest.mark.skip
    def test_rcsint_init(self):
        """
        范围：正式线|测试线 rcsint
        功能：删除相关 attr_id 和 tile
        "tile_deletions": [557017790, 557042475, 557038792]
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-01-int-删除.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)
        # 删除tile-正式线|测试线 rcsint
        self.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)
        self.get_trace_id(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, json_file)
        time.sleep(5)
        # 校验是否删除成功, hdms对应的tile不可见
        tile_list = [557017790, 557042475, 557038792]
        ret_del = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSINT)
        ret_del_int = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSINT)
        assert 1 not in ret_del, 'rcsint 正式线tile删除失败'
        assert 1 not in ret_del_int, 'rcsint 测试线tile删除失败'

        if ENV_FLAG:
            # 预生产时无法查看redis
            # 删除attr_id-正式线|测试线、rcsint
            ret_pro = self.get_redis_rcs_attrid(del_flag=True)
            ret_int = self.get_redis_rcs_attrid(del_flag=True, rcs_prod_flag=False)
            # 校验是否删除成功, redis中对应的attr_id为空
            assert ret_pro, 'rcsint 正式线attr_id删除失败'
            assert ret_int, 'rcsint 测试线attr_id删除失败'

    def test_rcsint_prod_01_publish(self):
        """
        功能：rcsint 正式线 发布不存在的tile成功
        校验：
        1、hdms平台发布成功
        2、redis attr_id、expire、tile存在
        tile：557042475,557038792,557017790
        其中，557038792过期时间为当前时间17min后，验证过期删除；其他过期时间为2025年
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 备份数据，可能存在跨小时的情况，需要查下开始发布时的时间，包含utc和北京时间
        utc_now = datetime.datetime.utcnow()
        begin_utc = utc_now.strftime("%Y%m%d/%H")
        if begin_utc[-2] == '0':
            begin_utc = f'{begin_utc[:-2]}{begin_utc[-1]}'
        print(begin_utc)
        begin_time = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(begin_time)
        backup_time = self.add_global_variable(['begin_utc', 'begin_time'], [begin_utc, begin_time])
        print(backup_time)

        # 读取目标json文件-103
        file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list和tile_list
        attr_list = []
        tile_list = []
        for i in range(len(json_file['tile_replacements'])):
            tile_id = json_file['tile_replacements'][i]['nds_packed_tile_id']
            tile_list.append(tile_id)
            for j in range(len(json_file['tile_replacements'][i]['oem_data_additions'])):
                attr_id = json_file['tile_replacements'][i]['oem_data_additions'][j]['attr_id']
                attr_list.append(attr_id)
        print(tile_list)
        print(attr_list)

        # 替换rcsint 正式线 557038792过期时间为当前时间17min后，并写回文件
        utc_now = datetime.datetime.utcnow()
        utc_17_after = (utc_now + datetime.timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%S")
        print(f'rcsint 正式线 {tile_list[1]}的过期时间：{utc_17_after}')
        json_file['tile_replacements'][1]['end_time'] = utc_17_after
        with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)

        # 发布tile-正式线 rcsint
        self.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看hdms上出现3个tile
        for i in range(LOOP_NUM):
            ret_publish = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSINT)
            if 0 not in ret_publish:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsint 正式线tile存在发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 0 not in ret_publish, 'rcsint 正式线tile存在发布失败'

        # 测试环境校验redis内容，预发环境不校验
        if ENV_FLAG:
            # 2、查看redis:tile
            for i in range(LOOP_NUM):
                res_tile = self.get_redis_rcs_tile(tile_list)
                print(res_tile)
                if res_tile:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 正式线redis_tile校验失败，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_tile, 'rcsint 正式线redis_tile校验失败'

            # 3、查看redis:attr_id、expire
            res_attr = self.get_redis_rcs_attrid(attr_list)
            print(res_attr)
            assert res_attr, 'rcsint 正式线redis_attr校验失败'
            res_expire = self.get_redis_rcs_expire(tile_list)
            print(res_expire)
            assert res_expire, 'rcsint 正式线redis_expire校验失败'

    def test_rcsint_prod_02_update(self):
        """
        功能：rcsint 正式线更新557042475 - 更新新的link
        校验：
        1、hdms平台，557042475时间更新，比case01中的时间大
        2、redis中attr_id、expire、tile更新
        ps：字符串可比较大小，迭代对象
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-03-557042475-更新新的link.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 更新tile-557042475
        self.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、hdms平台，557042475时间更新
        for i in range(LOOP_NUM):
            tile_list = ['557042475', '557017790']
            res_time = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSINT, timestamp_flag=True)
            if res_time[0] > res_time[1]:
                break
            time.sleep(TIME_SLEEP)
            print(f'hdms平台 rcsint 正式线-557042475 时间更新失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > res_time[1], 'hdms平台 rcsint 正式线-557042475 时间更新失败'

        if ENV_FLAG:
            """
            22Q2SP2迭代-32618，解决redis中多余的attrids——20220302
            # 2、redis中tile的attr_id更新
            for i in range(LOOP_NUM):
                tile_json = self.get_redis_rcs_tile_info(tile_list[0])
                if attr_list == tile_json['attrids']:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 正式线redis_tile下attrids更新失败，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert attr_list == tile_json['attrids'], 'rcsint 正式线redis_tile下attrids更新失败'
            """

            # 3、redis中expire时间更新
            for i in range(LOOP_NUM):
                end_time = json_file['tile_replacements'][0]['end_time']
                res_expire = self.get_tile_expire(tile_list[0], zset_key='rcs:expires:103')
                if res_expire == end_time:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 正式线redis_expire更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_expire == end_time, 'rcsint 正式线redis_expire 更新失败'

            # 4、redis中attr_id更新
            res_attr = self.get_redis_rcs_attrid(attr_list)
            print(res_attr)
            assert res_attr, 'rcsint 正式线redis_attr校验失败'

    def test_rcsint_prod_03_errorlog(self):
        """
        功能：rcsint 正式线错误日志正常发布到hdms
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取文件
        file_name = 'rcs-04-no-end_time.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 发布end_time不存在的json文件
        trace_id = self.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看日志，日志内容正确
        for i in range(LOOP_NUM):
            res_err = self.get_errorlog(CATALOG_RCSINT, ERROR_LAYER_RCSINT)
            if trace_id in res_err:
                break
            time.sleep(TIME_SLEEP)
            print(f"还没找到对应的日志，等待{i + 1}*3s")
        # 取出对应的日志，校验错误日志内容和位置
        assert NO_END_TIME_ERR_LIST[0] in res_err, 'rcsint 正式线 错误日志内容和位置错误'

        if ENV_FLAG:
            # 2、redis attr_id不存在
            res_attr = self.get_redis_rcs_attrid(attr_list)
            print(res_attr)
            assert not res_attr, 'rcsint 正式线redis_attr datacheck失败时进入redis'

    def test_rcsint_prod_04_delete(self):
        """
        功能：rcsint 正式线删除
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-05-删除557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 删除tile-正式线 rcsint
        self.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)
        # time.sleep(5)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 校验是否删除成功, hdms对应的tile不可见
        for i in range(LOOP_NUM):
            tile_list = [557017790]
            ret_del = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSINT)
            if 1 not in ret_del:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsint 正式线tile删除失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 1 not in ret_del, 'rcsint 正式线tile删除失败'

    def test_rcsint_prod_05_backup(self):
        """
        功能：rcsint 正式线 备份
        :return:
        """
        # 查看当前utc时间，20220129/2
        print(GLOBAL_VALUE)

        utc_now = datetime.datetime.utcnow()
        time_utc = utc_now.strftime("%Y%m%d/%H")
        if time_utc[-2] == '0':
            time_utc = f'{time_utc[:-2]}{time_utc[-1]}'
        print(time_utc)
        time_now = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(time_now)

        # 涉及发布的tile
        tile_list = ['557017790', '557042475', '557038792']
        # 存放此次发布的oso数据
        backup_list = []
        # 避免时间跨小时，一致时则自动去重
        time_set = {GLOBAL_VALUE['begin_utc'], time_utc}
        for time_str in time_set:
            for tile in tile_list:
                # 查看对应环境s3目录
                s3_dir = f'{S3_ENV}/OSO_backup/{CATALOG_OUT}/{TILE_LAYER_RCSINT}/{time_str}/{tile}/'
                s3_cmd = f'aws s3 ls s3://{s3_dir}'
                if ENV_FLAG:
                    ret = self.run_cmd(s3_cmd)
                    # 返回值类型为bytes，转为list形式
                    ret_list = str(ret[1])[2:-1].strip('').split(r'\r\n')
                    for i in range(len(ret_list)):
                        if GLOBAL_VALUE['begin_time'] <= ret_list[i][:19] <= time_now:
                            backup_list.append(ret_list[i])
                else:
                    print(s3_dir)
        print(backup_list)

        if ENV_FLAG:
            # 校验每个tile备份个数是否正确
            list_7790 = []
            list_2475 = []
            list_8792 = []
            for backup in backup_list:
                if '557017790' in backup:
                    list_7790.append(backup)
                if '557042475' in backup:
                    list_2475.append(backup)
                if '557038792' in backup:
                    list_8792.append(backup)
            assert len(list_7790) == 1, '557017790 rcsint 正式线备份个数错误'
            assert len(list_2475) == 2, '557042475 rcsint 正式线备份个数错误'
            assert len(list_8792) == 1, '557038792 rcsint 正式线备份个数错误'

    def test_rcsint_int_01_publish(self):
        """
        功能：rcsint 测试线 发布不存在的tile成功
        校验：
        1、hdms平台发布成功
        2、redis attr_id、expire、tile存在
        tile：557042475,557038792,557017790
        其中，557038792过期时间为当前时间20min后，验证过期删除；其他过期时间为2025年
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list和tile_list
        attr_list = []
        tile_list = []
        for i in range(len(json_file['tile_replacements'])):
            tile_id = json_file['tile_replacements'][i]['nds_packed_tile_id']
            tile_list.append(tile_id)
            for j in range(len(json_file['tile_replacements'][i]['oem_data_additions'])):
                attr_id = json_file['tile_replacements'][i]['oem_data_additions'][j]['attr_id']
                attr_list.append(attr_id)
        print(tile_list)
        print(attr_list)

        # 替换rcsint 测试线 557038792过期时间为当前时间20min后，并写回文件
        utc_now = datetime.datetime.utcnow()
        utc_20_after = (utc_now + datetime.timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%S")
        print(f'rcsint 测试线 {tile_list[1]}的过期时间：{utc_20_after}')
        json_file['tile_replacements'][1]['end_time'] = utc_20_after
        with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)

        # 备份数据，可能存在跨小时的情况，需要查下开始发布时的时间，包含utc和北京时间
        utc_now = datetime.datetime.utcnow()
        begin_utc = utc_now.strftime("%Y%m%d/%H")
        if begin_utc[-2] == '0':
            begin_utc = f'{begin_utc[:-2]}{begin_utc[-1]}'
        print(begin_utc)
        begin_time = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(begin_time)
        backup_time = self.add_global_variable(['begin_utc', 'begin_time'], [begin_utc, begin_time])
        print(backup_time)

        # 发布tile-测试线 rcsint
        self.get_trace_id(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看hdms上出现3个tile
        for i in range(LOOP_NUM):
            ret_publish = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSINT)
            if 0 not in ret_publish:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsint 测试线tile存在发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 0 not in ret_publish, 'rcsint 测试线tile存在发布失败'

        if ENV_FLAG:
            # 因环境快慢因素，加循环，循环20次，一次3s
            # 2、查看redis:tile
            for i in range(LOOP_NUM):
                res_tile = self.get_redis_rcs_tile(tile_list, rcs_prod_flag=False)
                print(res_tile)
                if res_tile:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 测试线redis_tile校验失败，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_tile, 'rcsint 测试线redis_tile校验失败'

            # 3、查看redis:attrids、expire
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False)
            print(res_attr)
            assert res_attr, 'rcsint 测试线redis_attr校验失败'
            res_expire = self.get_redis_rcs_expire(tile_list, rcs_prod_flag=False)
            print(res_expire)
            assert res_expire, 'rcsint 测试线redis_expire校验失败'

    def test_rcsint_int_02_update(self):
        """
        功能：rcsint 测试线更新557042475 - 更新新的link
        校验：
        1、hdms平台，557042475时间更新，比case01中的时间大
        2、redis中attr_id、expire、tile更新
        ps：字符串可比较大小，迭代对象
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-03-557042475-更新新的link.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 更新tile-557042475
        self.get_trace_id(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、hdms平台，557042475时间更新
        for i in range(LOOP_NUM):
            tile_list = ['557042475', '557017790']
            res_time = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSINT, timestamp_flag=True)
            if res_time[0] > res_time[1]:
                break
            time.sleep(TIME_SLEEP)
            print(f'hdms平台 rcsint 测试线-557042475 时间更新失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > res_time[1], 'hdms平台 rcsint 测试线-557042475 时间更新失败'

        if ENV_FLAG:
            """
            22Q2SP2迭代-32618，解决redis中多余的attrids——20220302
            # 2、redis中tile的attr_id更新
            for i in range(LOOP_NUM):
                tile_json = self.get_redis_rcs_tile_info(tile_list[0], rcs_prod_flag=False)
                if attr_list == tile_json['attrids']:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 测试线redis_tile下attrids更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert attr_list == tile_json['attrids'], 'rcsint 测试线redis_tile下attrids更新'
            """

            # 3、redis中expire时间更新
            for i in range(LOOP_NUM):
                end_time = json_file['tile_replacements'][0]['end_time']
                res_expire = self.get_tile_expire(tile_list[0], zset_key='rcs:expires:103', prod_flag=False)
                if res_expire == end_time:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsint 测试线redis_expire更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_expire == end_time, 'rcsint 测试线redis_expire 更新失败'

            # 4、redis中attr_id更新
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False)
            print(res_attr)
            assert res_attr, 'rcsint 测试线redis_attr校验失败'

    def test_rcsint_int_03_errorlog(self):
        """
        功能：rcsint 测试线错误日志正常发布到hdms
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取文件
        file_name = 'rcs-04-no-end_time.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 发布end_time不存在的json文件
        trace_id = self.get_trace_id(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看日志，日志内容正确
        for i in range(LOOP_NUM):
            res_err = self.get_errorlog(CATALOG_RCSINT_TEST, ERROR_LAYER_RCSINT)
            if trace_id in res_err:
                break
            time.sleep(TIME_SLEEP)
            print(f"还没找到对应的日志，等待{i + 1}*3s")
        # 取出对应的日志，校验错误日志内容和位置
        assert NO_END_TIME_ERR_LIST[0] in res_err, 'rcsint 测试线 错误日志内容和位置错误'

        if ENV_FLAG:
            # 2、redis attr_id不存在
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False)
            print(res_attr)
            assert not res_attr, 'rcsint 测试线redis_attr datacheck失败时进入redis'

    def test_rcsint_int_04_delete(self):
        """
        功能：rcsint 测试线 删除
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-05-删除557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 删除tile-测试线 rcsint
        self.get_trace_id(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 校验是否删除成功, hdms对应的tile不可见
        for i in range(LOOP_NUM):
            tile_list = [557017790]
            ret_del = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSINT)
            if 1 not in ret_del:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsint 测试线tile删除失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 1 not in ret_del, 'rcsint 测试线tile删除失败'

    def test_rcsint_int_05_backup(self):
        """
        功能：rcsint 测试线 备份
        :return:
        """
        # 查看当前utc时间，20220129/2
        print(GLOBAL_VALUE)

        utc_now = datetime.datetime.utcnow()
        time_utc = utc_now.strftime("%Y%m%d/%H")
        if time_utc[-2] == '0':
            time_utc = f'{time_utc[:-2]}{time_utc[-1]}'
        print(time_utc)
        time_now = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(time_now)

        # 涉及发布的tile
        tile_list = ['557017790', '557042475', '557038792']
        # 存放此次发布的oso数据
        backup_list = []
        # 避免时间跨小时，一致时则自动去重
        time_set = {GLOBAL_VALUE['begin_utc'], time_utc}
        for time_str in time_set:
            for tile in tile_list:
                # 查看对应环境s3目录
                s3_dir = f'{S3_ENV}/OSO_backup/{CATALOG_OUT_TEST}/{TILE_LAYER_RCSINT}/{time_str}/{tile}/'
                s3_cmd = f'aws s3 ls s3://{s3_dir}'
                if ENV_FLAG:
                    ret = self.run_cmd(s3_cmd)
                    # 返回值类型为bytes，转为list形式
                    ret_list = str(ret[1])[2:-1].strip('').split(r'\r\n')
                    for i in range(len(ret_list)):
                        if GLOBAL_VALUE['begin_time'] <= ret_list[i][:19] <= time_now:
                            backup_list.append(ret_list[i])
                else:
                    print(s3_dir)
        print(backup_list)

        if ENV_FLAG:
            # 校验每个tile备份个数是否正确
            list_7790 = []
            list_2475 = []
            list_8792 = []
            for backup in backup_list:
                if '557017790' in backup:
                    list_7790.append(backup)
                if '557042475' in backup:
                    list_2475.append(backup)
                if '557038792' in backup:
                    list_8792.append(backup)
            assert len(list_7790) == 1, '557017790 rcsint 测试线备份个数错误'
            assert len(list_2475) == 2, '557042475 rcsint 测试线备份个数错误'
            assert len(list_8792) == 1, '557038792 rcsint 测试线备份个数错误'

    def test_rcsext_init(self):
        """
        范围：正式线|测试线 rcsext
        功能：
        1、替换文件volatile_provider_id=108
        2、删除相关 attr_id 和 tile
        3、"tile_deletions": [557017790, 557042475, 557038792, 557025753]
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 替换目录下的所有目标json文件volatile_provider_id-108，并写回文件
        file_list = os.listdir(FILE_LIST_DIR)
        print(file_list)
        for i in range(len(file_list)):
            if ".json" in file_list[i]:
                print(f'文件名称为： {file_list[i]}')
                with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'r', encoding='utf-8') as fp:
                    json_file = json.load(fp)
                json_file["volatile_provider_id"] = 108
                # json_file["volatile_provider_id"] = 117
                with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
                    json.dump(json_file, dump_f)
                # os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/rcs{file_list[i][6:]}')
                # os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/hci{file_list[i][3:]}')

        # 读取修改后的文件
        file_name = 'rcs-01-int-删除.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 删除tile-正式线|测试线 rcsext
        self.get_trace_id(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, json_file)
        self.get_trace_id(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, json_file)
        time.sleep(5)

        # 校验是否删除成功, hdms对应的tile不可见
        tile_list = [557017790, 557042475, 557038792]
        ret_del = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSEXT)
        ret_del_int = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
        assert 1 not in ret_del, 'rcsext 正式线tile删除失败'
        assert 1 not in ret_del_int, 'rcsext 测试线tile删除失败'

        if ENV_FLAG:
            # 删除attr_id-正式线|测试线、rcsext
            ret_pro = self.get_redis_rcs_attrid(del_flag=True, rcsint_flag=False)
            ret_int = self.get_redis_rcs_attrid(del_flag=True, rcsint_flag=False, rcs_prod_flag=False)
            # 校验是否删除成功, redis中对应的attr_id为空
            assert ret_pro, 'rcsext 正式线attr_id删除失败'
            assert ret_int, 'rcsext 测试线attr_id删除失败'

    def test_rcsext_prod_01_publish(self):
        """
        功能：rcsext 正式线 发布不存在的tile成功
        校验：
        1、hdms平台发布成功
        2、redis attr_id、expire、tile存在
        tile：557042475,557038792,557017790
        其中，557038792过期时间为当前时间17min后，验证过期删除；其他过期时间为2025年
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list和tile_list
        attr_list = []
        tile_list = []
        for i in range(len(json_file['tile_replacements'])):
            tile_id = json_file['tile_replacements'][i]['nds_packed_tile_id']
            tile_list.append(tile_id)
            for j in range(len(json_file['tile_replacements'][i]['oem_data_additions'])):
                attr_id = json_file['tile_replacements'][i]['oem_data_additions'][j]['attr_id']
                attr_list.append(attr_id)
        print(tile_list)
        print(attr_list)

        # 替换rcsext 正式线 557038792过期时间为当前时间17min后，并写回文件
        utc_now = datetime.datetime.utcnow()
        utc_17_after = (utc_now + datetime.timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%S")
        print(f'rcsext 正式线 {tile_list[1]}的过期时间：{utc_17_after}')
        json_file['tile_replacements'][1]['end_time'] = utc_17_after
        with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)

        # 备份数据，可能存在跨小时的情况，需要查下开始发布时的时间，包含utc和北京时间
        utc_now = datetime.datetime.utcnow()
        begin_utc = utc_now.strftime("%Y%m%d/%H")
        if begin_utc[-2] == '0':
            begin_utc = f'{begin_utc[:-2]}{begin_utc[-1]}'
        print(begin_utc)
        begin_time = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(begin_time)
        backup_time = self.add_global_variable(['begin_utc', 'begin_time'], [begin_utc, begin_time])
        print(backup_time)

        # 发布tile-正式线 rcsext
        self.get_trace_id(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看hdms上出现3个tile
        for i in range(LOOP_NUM):
            ret_publish = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSEXT)
            if 0 not in ret_publish:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsext 正式线tile存在发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 0 not in ret_publish, 'rcsext 正式线tile存在发布失败'

        if ENV_FLAG:
            # 因环境快慢因素，加循环，循环20次，一次3s
            # 2、查看redis:tile
            for i in range(LOOP_NUM):
                res_tile = self.get_redis_rcs_tile(tile_list, rcsint_flag=False)
                print(res_tile)
                if res_tile:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 正式线redis_tile校验失败，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_tile, 'rcsext 正式线redis_tile校验失败'

            # 3、查看redis:attrids、expire
            res_attr = self.get_redis_rcs_attrid(attr_list, rcsint_flag=False)
            print(res_attr)
            assert res_attr, 'rcsext 正式线redis_attr校验失败'
            res_expire = self.get_redis_rcs_expire(tile_list, rcsint_flag=False)
            print(res_expire)
            assert res_expire, 'rcsext 正式线redis_expire校验失败'

    def test_rcsext_prod_02_update(self):
        """
        功能：rcsext 正式线更新557042475 - 更新新的link
        校验：
        1、hdms平台，557042475时间更新，比case01中的时间大
        2、redis中attr_id、expire、tile更新
        ps：字符串可比较大小，迭代对象
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-03-557042475-更新新的link.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 更新tile-557042475
        self.get_trace_id(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、hdms平台，557042475时间更新
        for i in range(LOOP_NUM):
            tile_list = ['557042475', '557017790']
            res_time = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSEXT, timestamp_flag=True)
            if res_time[0] > res_time[1]:
                break
            time.sleep(TIME_SLEEP)
            print(f'hdms平台 rcsext 正式线-557042475 时间更新失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > res_time[1], 'hdms平台 rcsext 正式线-557042475 时间更新失败'

        if ENV_FLAG:
            """
            22Q2SP2迭代-32618，解决redis中多余的attrids——20220302
            # 2、redis中tile的attr_id更新
            for i in range(LOOP_NUM):
                tile_json = self.get_redis_rcs_tile_info(tile_list[0], rcsint_flag=False)
                if attr_list == tile_json['attrids']:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 正式线redis_tile下attrids更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert attr_list == tile_json['attrids'], 'rcsext 正式线redis_tile下attrids更新'
            """

            # 3、redis中expire时间更新
            for i in range(LOOP_NUM):
                end_time = json_file['tile_replacements'][0]['end_time']
                res_expire = self.get_tile_expire(tile_list[0], zset_key='rcs:expires:108')
                if res_expire == end_time:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 测试线redis_expire更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_expire == end_time, 'rcsext 正式线redis_expire 更新失败'

            # 4、redis中attr_id更新
            res_attr = self.get_redis_rcs_attrid(attr_list, rcsint_flag=False)
            print(res_attr)
            assert res_attr, 'rcsext 正式线redis_attr校验失败'

    def test_rcsext_prod_03_errorlog(self):
        """
        功能：rcsext 正式线错误日志正常发布到hdms
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取文件
        file_name = 'rcs-04-no-end_time.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 发布end_time不存在的json文件
        trace_id = self.get_trace_id(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, json_file)
        # time.sleep(5)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看日志，日志内容正确
        for i in range(LOOP_NUM):
            res_err = self.get_errorlog(CATALOG_RCSEXT, ERROR_LAYER_RCSEXT)
            if trace_id in res_err:
                break
            time.sleep(TIME_SLEEP)
            print(f"还没找到对应的日志，等待{i + 1}*3s")
        # 取出对应的日志，校验错误日志内容和位置
        assert NO_END_TIME_ERR_LIST[1] in res_err, 'rcsext 正式线 错误日志内容和位置错误'

        if ENV_FLAG:
            # 2、redis attr_id不存在
            res_attr = self.get_redis_rcs_attrid(attr_list, rcsint_flag=False)
            print(res_attr)
            assert not res_attr, 'rcsext 正式线redis_attr datacheck失败时进入redis'

    def test_rcsext_prod_04_delete(self):
        """
        功能：rcsext 正式线 删除
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        file_name = 'rcs-05-删除557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 删除tile-正式线 rcsext
        self.get_trace_id(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 校验是否删除成功, hdms对应的tile不可见
        for i in range(LOOP_NUM):
            tile_list = [557017790]
            ret_del = self.get_tile_info(tile_list, CATALOG_OUT, TILE_LAYER_RCSEXT)
            if 1 not in ret_del:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsext 测试线tile删除失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 1 not in ret_del, 'rcsext 正式线tile删除失败'

    def test_rcsext_prod_05_backup(self):
        """
        功能：rcsext 正式线 备份
        :return:
        """
        # 查看当前utc时间，20220129/2
        print(GLOBAL_VALUE)

        utc_now = datetime.datetime.utcnow()
        time_utc = utc_now.strftime("%Y%m%d/%H")
        if time_utc[-2] == '0':
            time_utc = f'{time_utc[:-2]}{time_utc[-1]}'
        print(time_utc)
        time_now = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(time_now)

        # 涉及发布的tile
        tile_list = ['557017790', '557042475', '557038792']
        # 存放此次发布的oso数据
        backup_list = []
        # 避免时间跨小时，一致时则自动去重
        time_set = {GLOBAL_VALUE['begin_utc'], time_utc}
        for time_str in time_set:
            for tile in tile_list:
                # 查看对应环境s3目录
                s3_dir = f'{S3_ENV}/OSO_backup/{CATALOG_OUT}/{TILE_LAYER_RCSEXT}/{time_str}/{tile}/'
                s3_cmd = f'aws s3 ls s3://{s3_dir}'
                if ENV_FLAG:
                    ret = self.run_cmd(s3_cmd)
                    # 返回值类型为bytes，转为list形式
                    ret_list = str(ret[1])[2:-1].strip('').split(r'\r\n')
                    for i in range(len(ret_list)):
                        if GLOBAL_VALUE['begin_time'] <= ret_list[i][:19] <= time_now:
                            backup_list.append(ret_list[i])
                else:
                    print(s3_dir)
        print(backup_list)

        if ENV_FLAG:
            # 校验每个tile备份个数是否正确
            list_7790 = []
            list_2475 = []
            list_8792 = []
            for backup in backup_list:
                if '557017790' in backup:
                    list_7790.append(backup)
                if '557042475' in backup:
                    list_2475.append(backup)
                if '557038792' in backup:
                    list_8792.append(backup)
            assert len(list_7790) == 1, '557017790 rcsext 正式线备份个数错误'
            assert len(list_2475) == 2, '557042475 rcsext 正式线备份个数错误'
            assert len(list_8792) == 1, '557038792 rcsext 正式线备份个数错误'

    def test_rcsext_int_01_publish(self):
        """
        功能：rcsext 测试线 发布不存在的tile成功
        校验：
        1、hdms平台发布成功
        2、redis attr_id、expire、tile存在
        tile：557042475,557038792,557017790
        其中，557038792过期时间为当前时间20min后，验证过期删除；其他过期时间为2025年
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-108
        file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list和tile_list
        attr_list = []
        tile_list = []
        for i in range(len(json_file['tile_replacements'])):
            tile_id = json_file['tile_replacements'][i]['nds_packed_tile_id']
            tile_list.append(tile_id)
            for j in range(len(json_file['tile_replacements'][i]['oem_data_additions'])):
                attr_id = json_file['tile_replacements'][i]['oem_data_additions'][j]['attr_id']
                attr_list.append(attr_id)
        print(tile_list)
        print(attr_list)

        # 替换rcsext 测试线 557038792过期时间为当前时间20min后，并写回文件
        utc_now = datetime.datetime.utcnow()
        utc_20_after = (utc_now + datetime.timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%S")
        print(f'rcsint 正式线 {tile_list[1]}的过期时间：{utc_20_after}')
        json_file['tile_replacements'][1]['end_time'] = utc_20_after
        with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)

        # 备份数据，可能存在跨小时的情况，需要查下开始发布时的时间，包含utc和北京时间
        utc_now = datetime.datetime.utcnow()
        begin_utc = utc_now.strftime("%Y%m%d/%H")
        if begin_utc[-2] == '0':
            begin_utc = f'{begin_utc[:-2]}{begin_utc[-1]}'
        print(begin_utc)
        begin_time = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(begin_time)
        backup_time = self.add_global_variable(['begin_utc', 'begin_time'], [begin_utc, begin_time])
        print(backup_time)

        # 发布tile-测试线 rcsint
        self.get_trace_id(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看hdms上出现3个tile
        for i in range(LOOP_NUM):
            ret_publish = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
            if 0 not in ret_publish:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsext 测试线tile存在发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 0 not in ret_publish, 'rcsext 测试线tile存在发布失败'

        if ENV_FLAG:
            # 2、查看redis:tile
            for i in range(LOOP_NUM):
                res_tile = self.get_redis_rcs_tile(tile_list, rcs_prod_flag=False, rcsint_flag=False)
                print(res_tile)
                if res_tile:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 测试线redis_tile校验失败，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_tile, 'rcsext 测试线redis_tile校验失败'

            # 3、查看redis:attrids、expire
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False, rcsint_flag=False)
            print(res_attr)
            assert res_attr, 'rcsext 测试线redis_attr校验失败'
            res_expire = self.get_redis_rcs_expire(tile_list, rcs_prod_flag=False, rcsint_flag=False)
            print(res_expire)
            assert res_expire, 'rcsext 测试线redis_expire校验失败'

    def test_rcsext_int_02_update(self):
        """
        功能：rcsext 测试线更新557042475 - 更新新的link
        校验：
        1、hdms平台，557042475时间更新，比case01中的时间大
        2、redis中attr_id、expire、tile更新
        ps：字符串可比较大小，迭代对象
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取目标json文件-103
        file_name = 'rcs-03-557042475-更新新的link.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 更新tile-557042475
        self.get_trace_id(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、hdms平台，557042475时间更新
        for i in range(LOOP_NUM):
            tile_list = ['557042475', '557017790']
            res_time = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSEXT, timestamp_flag=True)
            if res_time[0] > res_time[1]:
                break
            time.sleep(TIME_SLEEP)
            print(f'hdms平台 rcsext 测试线-557042475 时间更新失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > res_time[1], 'hdms平台 rcsext 测试线-557042475 时间更新失败'

        if ENV_FLAG:
            """
            22Q2SP2迭代-32618，解决redis中多余的attrids——20220302
            # 2、redis中tile的attr_id更新
            for i in range(LOOP_NUM):
                tile_json = self.get_redis_rcs_tile_info(tile_list[0], rcs_prod_flag=False, rcsint_flag=False)
                if attr_list == tile_json['attrids']:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 测试线redis_tile下attrids更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert attr_list == tile_json['attrids'], 'rcsext 测试线redis_tile下attrids更新'
            """

            # 3、redis中expire时间更新
            for i in range(LOOP_NUM):
                end_time = json_file['tile_replacements'][0]['end_time']
                res_expire = self.get_tile_expire(tile_list[0], zset_key='rcs:expires:108', prod_flag=False)
                if res_expire == end_time:
                    break
                time.sleep(TIME_SLEEP)
                print(f'rcsext 测试线redis_expire更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            assert res_expire == end_time, 'rcsext 测试线redis_expire 更新失败'

            # 4、redis中attr_id更新
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False, rcsint_flag=False)
            print(res_attr)
            assert res_attr, 'rcsext 测试线redis_attr校验失败'

    def test_rcsext_int_03_errorlog(self):
        """
        功能：rcsext 测试线错误日志正常发布到hdms
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        # 读取文件
        file_name = 'rcs-04-no-end_time.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取attr_list
        attr_list = []
        for j in range(len(json_file['tile_replacements'][0]['oem_data_additions'])):
            attr_id = json_file['tile_replacements'][0]['oem_data_additions'][j]['attr_id']
            attr_list.append(attr_id)
        print(attr_list)

        # 发布end_time不存在的json文件
        trace_id = self.get_trace_id(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, json_file)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 1、查看日志，日志内容正确
        for i in range(10):
            res_err = self.get_errorlog(CATALOG_RCSEXT_TEST, ERROR_LAYER_RCSEXT)
            if trace_id in res_err:
                break
            time.sleep(TIME_SLEEP)
            print(f"还没找到对应的日志，等待{i + 1}*3s")
        # 取出对应的日志，校验错误日志内容和位置
        assert NO_END_TIME_ERR_LIST[1] in res_err, 'rcsext 测试线 错误日志内容和位置错误'

        if ENV_FLAG:
            # 2、redis attr_id不存在
            res_attr = self.get_redis_rcs_attrid(attr_list, rcs_prod_flag=False, rcsint_flag=False)
            print(res_attr)
            assert not res_attr, 'rcsext 测试线redis_attr datacheck失败时进入redis'

    def test_rcsext_int_04_delete(self):
        """
        功能：rcsext 测试线 删除
        1、存在的tile
        2、不存在的tile不报错
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        file_name = 'rcs-05-删除557017790.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 删除tile-测试线 rcsext
        self.get_trace_id(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, json_file)
        # time.sleep(5)

        # 因环境快慢因素，加循环，循环20次，一次3s
        # 校验是否删除成功, hdms对应的tile不可见
        for i in range(LOOP_NUM):
            tile_list = [557017790]
            ret_del = self.get_tile_info(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
            if 1 not in ret_del:
                break
            time.sleep(TIME_SLEEP)
            print(f'rcsext 测试线tile删除失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert 1 not in ret_del, 'rcsext 测试线tile删除失败'

    def test_rcsext_int_05_backup(self):
        """
        功能：rcsext 测试线 备份
        :return:
        """
        # 查看当前utc时间，20220129/2
        print(GLOBAL_VALUE)

        utc_now = datetime.datetime.utcnow()
        time_utc = utc_now.strftime("%Y%m%d/%H")
        if time_utc[-2] == '0':
            time_utc = f'{time_utc[:-2]}{time_utc[-1]}'
        print(time_utc)
        time_now = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(time_now)

        # 涉及发布的tile
        tile_list = ['557017790', '557042475', '557038792']
        # 存放此次发布的oso数据
        backup_list = []
        # 避免时间跨小时，一致时则自动去重
        time_set = {GLOBAL_VALUE['begin_utc'], time_utc}
        for time_str in time_set:
            for tile in tile_list:
                # 查看对应环境s3目录
                s3_dir = f'{S3_ENV}/OSO_backup/{CATALOG_OUT_TEST}/{TILE_LAYER_RCSEXT}/{time_str}/{tile}/'
                s3_cmd = f'aws s3 ls s3://{s3_dir}'
                if ENV_FLAG:
                    ret = self.run_cmd(s3_cmd)
                    # 返回值类型为bytes，转为list形式
                    ret_list = str(ret[1])[2:-1].strip('').split(r'\r\n')
                    for i in range(len(ret_list)):
                        if GLOBAL_VALUE['begin_time'] <= ret_list[i][:19] <= time_now:
                            backup_list.append(ret_list[i])
                else:
                    print(s3_dir)
        print(backup_list)

        if ENV_FLAG:
            # 校验每个tile备份个数是否正确
            list_7790 = []
            list_2475 = []
            list_8792 = []
            for backup in backup_list:
                if '557017790' in backup:
                    list_7790.append(backup)
                if '557042475' in backup:
                    list_2475.append(backup)
                if '557038792' in backup:
                    list_8792.append(backup)
            assert len(list_7790) == 1, '557017790 rcsext 测试线备份个数错误'
            assert len(list_2475) == 2, '557042475 rcsext 测试线备份个数错误'
            assert len(list_8792) == 1, '557038792 rcsext 测试线备份个数错误'

    def test_rcs_clear(self):
        """
        1、删除attr_id：rcsint|ext 正式线|测试线
        2、恢复文件：volatile_provider_id-103
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)

        if ENV_FLAG:
            # 删除attr_id
            self.get_redis_rcs_attrid(del_flag=True)
            self.get_redis_rcs_attrid(del_flag=True, rcs_prod_flag=False)
            self.get_redis_rcs_attrid(del_flag=True, rcsint_flag=False)
            self.get_redis_rcs_attrid(del_flag=True, rcsint_flag=False, rcs_prod_flag=False)

        # 替换目录下的所有目标json文件volatile_provider_id-103，并写回文件
        file_list = os.listdir(FILE_LIST_DIR)
        print(file_list)
        for i in range(len(file_list)):
            if ".json" in file_list[i]:
                print(f'文件名称为： {file_list[i]}')
                with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'r', encoding='utf-8') as fp:
                    json_file = json.load(fp)
                json_file["volatile_provider_id"] = 103
                with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
                    json.dump(json_file, dump_f)
