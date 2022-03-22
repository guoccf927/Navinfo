# -*- coding: utf-8 -*-
# @Time      :2022/2/16 10:29
# @Author    :guocongcong7572@navinfo.com

from TestHdms.Base.basefunc_test import *

NO_END_TIME_ERROR_LOG = """"oem_data_additions":[{"attr_id":"C1/ccEEtEey3Idie8zwxiw==","attribute_errors":[{"error_code":"EC-HCC-DC-time","error_msg":"Invalid end time due to the field missing , empty or its invalid value."}]},{"attr_id":"A8/ccEEtEey3Idie8zwxiw==","attribute_errors":[{"error_code":"EC-HCC-DC-time","error_msg":"Invalid end time due to the field missing , empty or its invalid value."}]}]"""
FILE_LIST_DIR = r'E:/03 HDMS/98 测试文件/04 hcc-prod-int'
LOOP_NUM = 10
TIME_SLEEP = 3


class BaseClear(TestBaseFunc):
    """
    删除脚本要用给的所有attr_id
    hcc删除：以attr_id为目标，当脚本中有一个attr_id不存在，则删除任务整个抛弃
    """
    def __init__(self, catalog_id, layer_id, file_name):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param file_name: 本次要用的json文件
        """
        # 读取指定文件
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.file_name = file_name
        with open(f'{FILE_LIST_DIR}/{self.file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取provider_id和attr_id
        provider_id = json_file['volatile_provider_id']
        for i in range(len(json_file['volatile_location_changes'])):
            for j in range(len(json_file['volatile_location_changes'][i]['oem_data_additions'])):
                attr_id = json_file['volatile_location_changes'][i]['oem_data_additions'][j]['attr_id']

                # 读取hcc-04-delete-attr_ids.json文件，并替换其中的attr_id和provider_id
                del_file_name = 'hcc-04-delete-attr_ids.json'
                with open(f'{FILE_LIST_DIR}/{del_file_name}', 'r', encoding='utf-8') as fp:
                    del_json_file = json.load(fp)
                del_json_file['volatile_location_changes'][0]['oem_data_deletions'][0] = attr_id
                del_json_file['volatile_provider_id'] = provider_id
                with open(f'{FILE_LIST_DIR}/{del_file_name}', 'w+', encoding='utf-8') as dump_f:
                    json.dump(del_json_file, dump_f)

                # 删除attr_id
                self.get_trace_id(self.catalog_id, self.layer_id, del_json_file)

        # 执行完删除操作后，等待3s
        time.sleep(TIME_SLEEP)
        time_now = datetime.datetime.now()
        time_now = time_now.strftime("%Y/%m/%d %H:%M:%S")
        print(time_now)


class BasePublish(TestBaseFunc):
    """
    hcc 发布验证：tile时间更新
    """
    def __init__(self, catalog_id, layer_id, catalog_out_id, layer_out_id, hcc_prod_flag=True):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param catalog_out_id: hdms平台oso输出catalog
        :param layer_out_id: hdms平台oso输出layer
        :param hcc_prod_flag: hcc默认正式线
        """
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.catalog_out_id = catalog_out_id
        self.layer_out_id = layer_out_id
        self.hcc_prod_flag = hcc_prod_flag

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

        # 查看当前utc时间，为了比较tile更新的时间
        utc_time = utc_now.strftime("%Y/%m/%d %H:%M:%S")
        print(utc_time)

        # 读取指定文件
        file_name = 'hcc-01-publish-557038792.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 获取provider_id和attr_list
        provider_id = json_file['volatile_provider_id']
        attr_list = []
        for i in range(len(json_file['volatile_location_changes'])):
            for j in range(len(json_file['volatile_location_changes'][i]['oem_data_additions'])):
                attr_id = json_file['volatile_location_changes'][i]['oem_data_additions'][j]['attr_id']
                attr_list.append(attr_id)
        print(attr_list)

        # 发布tile-hcc
        self.get_trace_id(self.catalog_id, self.layer_id, json_file)

        # 查看hdms上出现tile时间更新
        tile = '557038792'
        for i in range(LOOP_NUM):
            res_time = self.get_tile_info([tile], self.catalog_out_id, self.layer_out_id, timestamp_flag=True)
            if res_time[0] > utc_time:
                break
            time.sleep(TIME_SLEEP)
            print(f'{self.catalog_out_id}/{self.layer_out_id}/{tile}发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > utc_time, f'{self.catalog_out_id}/{self.layer_out_id}/{tile}发布失败'

        if ENV_FLAG:
            # 测试环境可进一步检查数据库,attr_id入库
            if hcc_prod_flag:
                daimler_hcc = 'daimler02'
            if not hcc_prod_flag:
                daimler_hcc = 'daimler_int'
            sql_statement = f"SELECT attr_id FROM {daimler_hcc}.hcc_attributes WHERE tile = '{tile}' " \
                            f"AND provider_id = '{provider_id}';"
            ret_sql = self.get_pgsql(sql_statement)
            attr_id_flag = True
            for attr_id in attr_list:
                if (attr_id,) not in ret_sql:
                    attr_id_flag = False
            assert attr_id_flag, f'{self.catalog_out_id}/{self.layer_out_id}/{tile} attr_id入库失败'


class BaseUpdate(TestBaseFunc):
    """
    hcc 更新验证：更新的end_time 一个比之前的早，一个比之前的晚，最终redis中写入更早的end_time时间
    备注：已知问题，删除end_time较早attr_id时，redis中的过期时间不更新
    链接：http://zentaoimp.navinfo.com/zentao/bug-view-27921.html
    """
    def __init__(self, catalog_id, layer_id, catalog_out_id, layer_out_id, prod_flag=True):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param catalog_out_id: hdms平台oso输出catalog
        :param layer_out_id: hdms平台oso输出layer
        :param prod_flag: 默认正式线
        """
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.catalog_out_id = catalog_out_id
        self.layer_out_id = layer_out_id
        self.prod_flag = prod_flag

        # 查看当前utc时间，为了比较tile更新的时间
        utc_now = datetime.datetime.utcnow()
        utc_time = utc_now.strftime("%Y/%m/%d %H:%M:%S")
        print(utc_time)

        # 读取指定文件
        file_name = 'hcc-02-updata-557038792.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)

        # 替换'F0/ccEEtEey3Idie8zwxiw=='过期时间为当前时间17min后，并写回文件
        utc_now = datetime.datetime.utcnow()
        utc_17_after = (utc_now + datetime.timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%S")
        print(f'{self.catalog_out_id}/{self.layer_out_id} "F0/ccEEtEey3Idie8zwxiw=="的过期时间：{utc_17_after}')
        json_file['volatile_location_changes'][0]['oem_data_additions'][0]['end_time'] = utc_17_after
        with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)

        # 发布tile-hcc
        self.get_trace_id(self.catalog_id, self.layer_id, json_file)

        # 查看hdms上出现tile时间更新
        tile = '557038792'
        for i in range(LOOP_NUM):
            res_time = self.get_tile_info([tile], self.catalog_out_id, self.layer_out_id, timestamp_flag=True)
            if res_time[0] > utc_time:
                break
            time.sleep(TIME_SLEEP)
            print(f'{self.catalog_out_id}/{self.layer_out_id}/{tile}发布失败，等待{str(TIME_SLEEP)}s * {i + 1}')
        assert res_time[0] > utc_time, f'{self.catalog_out_id}/{self.layer_out_id}/{tile}发布失败'

        if ENV_FLAG:
            # 测试环境可进一步检查redis——oso:cloud_test:hcc:expires101，过期时间更新为最早的end_time
            for i in range(LOOP_NUM):
                res_expire = self.get_tile_expire(tile, zset_key='hcc:expires101', prod_flag=self.prod_flag)
                if res_expire == utc_17_after:
                    break
                time.sleep(TIME_SLEEP)
                print(f'{self.catalog_out_id}/{self.layer_out_id}/{tile} redis_expire更新，等待{str(TIME_SLEEP)}s * {i + 1}')
            # 存在bug，无法校验
            # assert res_expire == utc_17_after, f'{self.catalog_out_id}/{self.layer_out_id}/{tile}redis_expire 更新失败'


class BaseErrorLog(TestBaseFunc):
    def __init__(self, catalog_id, layer_id, error_layer_id):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param error_layer_id: 错误日志所在的layer
        """
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.error_layer_id = error_layer_id

        # 读取文件
        file_name = 'hcc-03-no-多个end_time.json'
        with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)
        trace_id = self.get_trace_id(self.catalog_id, self.layer_id, json_file)

        # 循环等待日志出现，并打印结果
        for j in range(LOOP_NUM):
            res_err = self.get_errorlog(self.catalog_id, self.error_layer_id)
            if trace_id in res_err:
                print(f'日志正常生成，内容如下：\n{res_err}\n')
                break
            time.sleep(TIME_SLEEP)
            print(f"循环{j + 1}*{str(TIME_SLEEP)}s, 还没找到对应的日志")
        assert NO_END_TIME_ERROR_LOG in res_err, f'{self.catalog_out_id}/{self.layer_out_id} 错误日志上报失败'


class BaseBackup(TestBaseFunc):
    """
    hcc 备份验证
    """
    def __init__(self, catalog_out_id, layer_out_id):
        """
        :param catalog_out_id: 备份路径与hdms平台oso 输出catalog一致
        :param layer_out_id: 备份路径与hdms平台oso 输出layer一致
        """
        self.catalog_out_id = catalog_out_id
        self.layer_out_id = layer_out_id

        # 涉及发布的tile
        tile = '557038792'

        # 打印存起来的时间
        print(GLOBAL_VALUE)

        # 查看当前utc时间，20220317/9
        utc_now = datetime.datetime.utcnow()
        time_utc = utc_now.strftime("%Y%m%d/%H")
        if time_utc[-2] == '0':
            time_utc = f'{time_utc[:-2]}{time_utc[-1]}'
        print(time_utc)
        time_now = (utc_now + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        print(time_now)

        # 存放此次发布的oso数据
        backup_list = []

        # 避免时间跨小时，一致时则自动去重
        time_set = {GLOBAL_VALUE['begin_utc'], time_utc}
        for time_str in time_set:
            # 查看对应环境s3目录
            s3_dir = f'{S3_ENV}/OSO_backup/{self.catalog_out_id}/{self.layer_out_id}/{time_str}/{tile}/'
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
            assert len(backup_list) == 2, f'{self.catalog_out_id}/{self.layer_out_id}/{tile} 备份个数错误'


class TestHccSmoke:
    """
    hcc冒烟
    """

    def test_hcc_clear_attr_id_00(self):
        """
        清除attr_id，hcc部分珊瑚会走编译，导致hcc备份个数不准确
        :return:
        """
        file_list = ['hcc-01-publish-557038792.json', 'hcc-02-updata-557038792.json']
        for file_name in file_list:
            BaseClear(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, file_name)
            BaseClear(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, file_name)
        time.sleep(TIME_SLEEP*LOOP_NUM)

    def test_hcc_prod_publish_01(self):
        """
        hcc正式线发布
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BasePublish(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, CATALOG_OUT, TILE_LAYER_HCCHCI)

    def test_hcc_prod_update_02(self):
        """
        hcc正式线更新end_time
        缺陷：不能连续执行，因为一个已知bug
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseUpdate(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, CATALOG_OUT, TILE_LAYER_HCCHCI)

    def test_hcc_prod_error_log_03(self):
        """
        hcc正式线错误日志上报
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseErrorLog(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, ERROR_LAYER_HCC)

    def test_hcc_prod_backup_04(self):
        """
        hcc 正式线备份
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseBackup(CATALOG_OUT, TILE_LAYER_HCCHCI)

    def test_hcc_int_publish_05(self):
        """
        hcc测试线发布
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BasePublish(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, CATALOG_OUT_TEST, TILE_LAYER_HCCHCI, hcc_prod_flag=False)

    def test_hcc_int_update_06(self):
        """
        hcc测试线更新end_time
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseUpdate(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, CATALOG_OUT_TEST, TILE_LAYER_HCCHCI, prod_flag=False)

    def test_hcc_int_error_log_07(self):
        """
        hcc测试线错误日志上报
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseErrorLog(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, ERROR_LAYER_HCC)

    def test_hcc_int_backup_08(self):
        """
        hcc 测试线备份
        """
        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        BaseBackup(CATALOG_OUT_TEST, TILE_LAYER_HCCHCI)
