# -*- coding: utf-8 -*-
# @Time        :2022/3/21 16:48
# @Author      :guocongcong7572@navinfo.com
# @Description :字段缺失校验,其中"msg_id"字段缺失不报错
import re

import pytest

from TestHdms.Base.basefunc_test import *

LOOP_NUM = 10
TIME_SLEEP = 3
DATA_CHECK_FILE_DIR = '../TestFiles/03 data check'


class Base(TestBaseFunc):
    def __init__(self, catalog_id, layer_id, error_layer_id, file_dir, error_log_list):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param error_layer_id: 错误日志所在的layer
        :param file_dir: 本地构造文件的路劲
        :param error_log_list: errorlog预期结果
        """
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.error_layer_id = error_layer_id
        self.file_dir = file_dir
        self.error_log_list = error_log_list

        file_list = os.listdir(self.file_dir)
        print(file_list)
        for i in range(len(file_list)):
            if ".json" in file_list[i]:
                print(f'文件名称为： {file_list[i]}')
                with open(f'{self.file_dir}/{file_list[i]}', 'r', encoding='utf-8') as fp:
                    json_file = json.load(fp)
                trace_id = self.get_trace_id(self.catalog_id, self.layer_id, json_file)

                if 'clear' in file_list[i]:
                    # clear文件用来清理数据
                    time.sleep(TIME_SLEEP)
                    print('\n')

                if 'clear' not in file_list[i]:
                    # 循环等待日志出现，并打印结果
                    for j in range(LOOP_NUM):
                        res_err = self.get_errorlog(self.catalog_id, self.error_layer_id)
                        if trace_id in res_err:
                            # 22Q3SP1需求10839要求输出attr_id和location_id
                            attr_id1 = re.findall(r'"attr_id":(.*?),', res_err)
                            attr_id2 = re.findall(r'"attr_id":(.*?)}', res_err)
                            attr_id = attr_id1 if len(attr_id1) > 0 else attr_id2
                            if len(attr_id) == 0:
                                print('attr_id 不存在')
                            elif attr_id[0] == 'null':
                                print('attr_id 为null')
                            elif attr_id[0] == '""':
                                print('attr_id 为""')
                            volatile_location_id1 = re.findall(r'"volatile_location_id":(.*?),', res_err)
                            volatile_location_id2 = re.findall(r'"volatile_location_id":(.*?)}', res_err)
                            volatile_location_id = volatile_location_id1 if len(volatile_location_id1) > 0 else volatile_location_id2
                            if len(volatile_location_id) == 0:
                                print('volatile_location_id 不存在')
                            elif volatile_location_id[0] == 'null':
                                print('volatile_location_id 为null')
                            elif volatile_location_id[0] == '""':
                                print('volatile_location_id 为""')
                            print('\n')
                            break
                        time.sleep(TIME_SLEEP)
                        print(f"循环{j + 1}*{str(TIME_SLEEP)}s,还没找到对应的日志")
                    assert self.error_log_list[i - 1] in res_err, f'{file_list[i]} 日志错误'


class TestDataCheckMiss:
    """
    取出rcsint|rcsext|hcc|hci 正式线|测试线 字段缺失时的errorlog
    """

    def test_rcsint_prod_01(self):
        """
        rcsint 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/int'
        Base(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, ERROR_LAYER_RCSINT, file_dir, MISS_FIELD_RCSINT_ERRORLOG_LIST)

    def test_rcsext_prod_02(self):
        """
        rcsext 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/ext'
        Base(CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, ERROR_LAYER_RCSEXT, file_dir, MISS_FIELD_RCSEXT_ERRORLOG_LIST)

    # @pytest.mark.skip()
    def test_hcc_prod_03(self):
        """
        hcc 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hcc'
        Base(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, MISS_FIELD_HCC_ERRORLOG_LIST)

    # @pytest.mark.skip()
    def test_hci_prod_04(self):
        """
        hci 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hci'
        Base(CATALOG_HCC_HCI, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, MISS_FIELD_HCI_ERRORLOG_LIST)

    def test_rcsint_int_05(self):
        """
        rcsint 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/int'
        Base(CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, ERROR_LAYER_RCSINT, file_dir, MISS_FIELD_RCSINT_ERRORLOG_LIST)

    def test_rcsext_int_06(self):
        """
        rcsext 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/ext'
        Base(CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, ERROR_LAYER_RCSEXT, file_dir, MISS_FIELD_RCSEXT_ERRORLOG_LIST)

    # @pytest.mark.skip()
    def test_hcc_int_07(self):
        """
        hcc 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hcc'
        Base(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, MISS_FIELD_HCC_ERRORLOG_LIST)

    # @pytest.mark.skip()
    def test_hci_int_08(self):
        """
        hci 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hci'
        Base(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, MISS_FIELD_HCI_ERRORLOG_LIST)
