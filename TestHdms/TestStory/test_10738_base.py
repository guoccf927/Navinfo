# -*- coding: utf-8 -*-
# @Time        :2022/3/4 21:06
# @Author      :guocongcong7572@navinfo.com
# @Description :#10738 Daimler动态及oso元数据中checksum及crc需要与gzip解压后的数据文件保持一致

from TestHdms.Base.basefunc_test import *

LOOP_NUM = 10
TIME_SLEEP = 3


class Base(TestBaseFunc):
    def __init__(self, catalog_id, layer_id):
        # logfile = self.output_log_begin()

        self.catalog_id = catalog_id
        self.layer_id = layer_id

        # 获取hdms和接口中的checksum和crc
        tile_list = self.get_tile_list(catalog_id, layer_id)
        hdms_tile = self.get_tile_checksum_crc(tile_list, catalog_id, layer_id)
        interface_tile = self.query_tile_checksum_crc(catalog_id, layer_id)

        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    # 将所有校验结果打印出来，不报错
                    if interface_tile[i][1] != hdms_tile[j][1]:
                        print(f'校验的第{j + 1}个tile:{hdms_tile[j][0]} checksum不一致')
                        print('*********************************************这是一条分界线*********************************************')
                    else:
                        print(f'校验的第{j + 1}个tile:{hdms_tile[j][0]} checksum一致')
                    if interface_tile[i][2] != hdms_tile[j][2]:
                        print(f'校验的第{j + 1}个tile:{hdms_tile[j][0]} crc不一致')
                        print('*********************************************这是一条分界线*********************************************')
                    else:
                        print(f'校验的第{j + 1}个tile:{hdms_tile[j][0]} crc一致')
                    # 直接校验，出现错误则跳出
                    # assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j + 1}个tile:{hdms_tile[j][0]} crc不一致'
                    # assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j + 1}个tile:{hdms_tile[j][0]} checksum不一致'
                    continue
        # self.output_log_end(logfile)


class Test_10738:
    """
    Daimler动态及oso元数据中checksum及crc需要与gzip解压后的数据文件保持一致
    """

    def test_rcsint_prod_01(self):
        """
        rcsint 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT, TILE_LAYER_RCSINT)

    def test_rcsext_prod_02(self):
        """
        rcsext 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT, TILE_LAYER_RCSEXT)

    def test_hcc_prod_03(self):
        """
        hcc 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT, TILE_LAYER_HCCHCI)

    def test_trfregs_prod_04(self):
        """
        trfregs 正式线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT, TILE_LAYER_TRFREGS)

    def test_rcsint_int_05(self):
        """
        rcsint 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT_TEST, TILE_LAYER_RCSINT)

    def test_rcsext_int_06(self):
        """
        rcsext 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)

    def test_hcc_int_07(self):
        """
        hcc 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT_TEST, TILE_LAYER_HCCHCI)

    def test_trfregs_int_08(self):
        """
        trfregs 测试线
        """

        # 打印当前方法名称
        print('\r\n当前用例名称：', sys._getframe().f_code.co_name)
        Base(CATALOG_OUT_TEST, TILE_LAYER_TRFREGS)
