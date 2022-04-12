# -*- coding: utf-8 -*-
# @Time        :2022/3/21 14:56
# @Author      :guocongcong7572@navinfo.com
# @Description :datacheck 字段校验,其中"msg_id"字段缺失不报错;;;未覆盖场景——文件不是json格式、字段重复(使用postman正常报错);;;
# @backup      :由于日志较多，使用当前console输出的话会导致之前的日志丢失，使用文件写入的方式；base类中有日志写入操作，之后再进行文件写入会出现问题
import re

from TestHdms.Base.basefunc_test import *
import pytest

LOOP_NUM = 10
TIME_SLEEP = 3
DATA_CHECK_FILE_DIR = '../TestFiles/03 data check'


class Base(TestBaseFunc):
    def __init__(self, case_name, catalog_id, layer_id, error_layer_id, file_dir, error_log_list):
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
        self.case_name = case_name
        # 日志输出到本地
        logfile = self.output_log_begin(self.case_name)

        file_list = os.listdir(self.file_dir)
        print(file_list)
        for i in range(len(file_list)):
            print(f'文件名称为： {file_list[i]}')
            with open(f'{self.file_dir}/{file_list[i]}', 'r', encoding='utf-8') as fp:
                json_file = json.load(fp)

            # 替换end_time为当前时间10min后
            if 'end_time小于当前时间+15min.' in file_list[i]:
                utc_now = datetime.datetime.utcnow()
                utc_10_after = (utc_now + datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
                if 'rcs' in file_list[i]:
                    json_file['tile_replacements'][0]['end_time'] = utc_10_after
                if 'hcc' in file_list[i]:
                    json_file['volatile_location_changes'][0]['oem_data_additions'][0]['end_time'] = utc_10_after
                with open(f'{self.file_dir}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
                    json.dump(json_file, dump_f)

            # 发送json文件
            trace_id = self.get_trace_id(self.catalog_id, self.layer_id, json_file)

            if 'clear' not in file_list[i]:
                # 循环等待日志出现，并打印结果
                for j in range(LOOP_NUM):
                    res_err = self.get_errorlog(self.catalog_id, self.error_layer_id)
                    if trace_id in res_err:
                        attr_id = re.findall(r'"attr_id":(.*?),', res_err)
                        volatile_location_id = re.findall(r'"volatile_location_id":(.*?),', res_err)
                        if len(attr_id) == 0:
                            print(f'10839字段校验：{file_list[i]} attr_id 不存在')
                        if len(attr_id) != 0:
                            if attr_id[0] == 'null':
                                print(f'10839字段校验：{file_list[i]} attr_id 为null')
                            if attr_id[0] == '""':
                                print(f'10839字段校验：{file_list[i]} attr_id 为""')
                        if len(volatile_location_id) == 0:
                            print(f'10839字段校验：{file_list[i]} volatile_location_id 不存在')
                        if len(volatile_location_id) != 0:
                            if volatile_location_id[0] == 'null':
                                print(f'10839字段校验：{file_list[i]} volatile_location_id 为null')
                            if volatile_location_id[0] == '""':
                                print(f'10839字段校验：{file_list[i]} volatile_location_id 为""')
                        print('\n')
                        break
                    time.sleep(TIME_SLEEP)
                    print(f"循环{j + 1}*{str(TIME_SLEEP)}s,还没找到对应的日志")
                # assert self.error_log_list[i - 1] in res_err, f'{file_list[i]} 日志错误'
        self.output_log_end(logfile)


class BaseClearHCC(TestBaseFunc):
    """
    清理hcc的attr_id
    """
    def __init__(self, catalog_id, layer_id, file_dir):
        """
        :param catalog_id: ingest接口中catalog
        :param layer_id: ingest接口中layer
        :param file_dir: 本地构造文件的路劲
        """
        self.catalog_id = catalog_id
        self.layer_id = layer_id
        self.file_dir = file_dir

        # 需要删除的attr_id，避免attr_id重复影响下一步字段的校验
        attr_id_list = [
            "Z1/ccEEtEey3Idie8zwxiw==",
            "Z2/ccEEtEey3Idie8zwxiw==",
            "Z3/ccEEtEey3Idie8zwxiw==",
            "Z4/ccEEtEey3Idie8zwxiw==",
            "Y0/ccEEtEey3Idie8zwxiw=="
        ]
        # 读取文件
        file_name = 'hcc-00-clear-attr_id.json'
        with open(f'{self.file_dir}/{file_name}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)
        # 替换attr_id
        for attr_id in attr_id_list:
            json_file['volatile_location_changes'][0]['oem_data_deletions'][0] = attr_id
            with open(f'{self.file_dir}/{file_name}', 'w+', encoding='utf-8') as dump_f:
                json.dump(json_file, dump_f)
            # 发送json文件
            self.get_trace_id(self.catalog_id, self.layer_id, json_file)
        time.sleep(TIME_SLEEP)


class BaseChangeProviderId(TestBaseFunc):
    """
    替换volatile_provider_id
    """
    def __init__(self, file_dir, volatile_provider_id):
        """
        :param file_dir: 本地构造文件的路劲
        :param volatile_provider_id: hcc-102|116|118，hci-101|117
        """
        self.file_dir = file_dir
        self.volatile_provider_id = volatile_provider_id
        file_list = os.listdir(self.file_dir)
        print(file_list)
        for i in range(len(file_list)):
            if 'volatile_provider_id' not in file_list[i]:
                print(f'文件名称为： {file_list[i]}')
                with open(f'{self.file_dir}/{file_list[i]}', 'r', encoding='utf-8') as fp:
                    json_file = json.load(fp)

                # 替换volatile_provider_id
                json_file['volatile_provider_id'] = self.volatile_provider_id
                with open(f'{self.file_dir}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
                    json.dump(json_file, dump_f)


class TestDataCheck:
    """
    取出rcsint|rcsext|hcc|hci 正式线|测试线 字段校验
    """

    # @pytest.mark.skip()
    def test_rcsint_prod_01(self):
        """
        rcsint 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/int'
        Base(case_name, CATALOG_RCSINT, TRACEID_LAYER_RCSINT, ERROR_LAYER_RCSINT, file_dir, CHECK_FIELD_RCSINT_ERRORLOG_LIST)

    def test_rcsext_prod_02(self):
        """
        rcsext 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/ext'
        Base(case_name, CATALOG_RCSEXT, TRACEID_LAYER_RCSEXT, ERROR_LAYER_RCSEXT, file_dir, CHECK_FIELD_RCSEXT_ERRORLOG_LIST)

    def test_hcc_102_prod_03(self):
        """
        hcc 102 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 102
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hcc_116_prod_04(self):
        """
        hcc 116 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 116
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hcc_118_prod_05(self):
        """
        hcc 118 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 118
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hci_101_prod_06(self):
        """
        hci 101 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 101
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI, TRACEID_LAYER_HCI, file_dir)
        Base(case_name, CATALOG_HCC_HCI, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, CHECK_FIELD_HCI_ERRORLOG_LIST)

    def test_hci_117_prod_07(self):
        """
        hci 117 正式线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 117
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI, TRACEID_LAYER_HCI, file_dir)
        Base(case_name, CATALOG_HCC_HCI, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, CHECK_FIELD_HCI_ERRORLOG_LIST)

    def test_rcsint_int_08(self):
        """
        rcsint 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/int'
        Base(case_name, CATALOG_RCSINT_TEST, TRACEID_LAYER_RCSINT, ERROR_LAYER_RCSINT, file_dir, CHECK_FIELD_RCSINT_ERRORLOG_LIST)

    def test_rcsext_int_09(self):
        """
        rcsext 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/ext'
        Base(case_name, CATALOG_RCSEXT_TEST, TRACEID_LAYER_RCSEXT, ERROR_LAYER_RCSEXT, file_dir, CHECK_FIELD_RCSEXT_ERRORLOG_LIST)

    def test_hcc_102_int_10(self):
        """
        hcc 102 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 102
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hcc_116_int_11(self):
        """
        hcc 116 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 116
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hcc_118_int_12(self):
        """
        hcc 118 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 118
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, file_dir)
        Base(case_name, CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCC, ERROR_LAYER_HCC, file_dir, CHECK_FIELD_HCC_ERRORLOG_LIST)

    def test_hci_101_int_13(self):
        """
        hci 101 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 101
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCI, file_dir)
        Base(case_name, CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, CHECK_FIELD_HCI_ERRORLOG_LIST)

    def test_hci_117_int_14(self):
        """
        hci 117 测试线
        """

        # 打印当前方法名称
        case_name = sys._getframe().f_code.co_name
        print('\r\n当前用例名称：', case_name)
        file_dir = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
        volatile_provider_id = 117
        BaseChangeProviderId(file_dir, volatile_provider_id)
        BaseClearHCC(CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCI, file_dir)
        Base(case_name, CATALOG_HCC_HCI_TEST, TRACEID_LAYER_HCI, ERROR_LAYER_HCI, file_dir, CHECK_FIELD_HCI_ERRORLOG_LIST)
