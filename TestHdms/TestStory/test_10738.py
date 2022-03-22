# -*- coding: utf-8 -*-
# @Time        :2022/3/4 16:04
# @Author      :guocongcong7572@navinfo.com
# @Description :22Q2SP2迭代10738需求

from TestHdms.Base.basefunc_test import *


class Test_10738(TestBaseFunc):
    """
    Daimler动态及oso元数据中checksum及crc需要与gzip解压后的数据文件保持一致
    """

    def test_rcsint_prod_01(self):
        """
        rcsint 正式线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT, TILE_LAYER_RCSINT)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT, TILE_LAYER_RCSINT)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT, TILE_LAYER_RCSINT)

        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_rcsext_prod_02(self):
        """
        rcsext 正式线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT, TILE_LAYER_RCSEXT)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT, TILE_LAYER_RCSEXT)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT, TILE_LAYER_RCSEXT)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_hcc_prod_03(self):
        """
        hcc 正式线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT, TILE_LAYER_HCCHCI)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT, TILE_LAYER_HCCHCI)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT, TILE_LAYER_HCCHCI)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_trfregs_prod_04(self):
        """
        trfregs 正式线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT, TILE_LAYER_TRFREGS)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT, TILE_LAYER_TRFREGS)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT, TILE_LAYER_TRFREGS)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_rcsint_int_05(self):
        """
        rcsint 测试线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        # 打印当前方法名称
        print('\n当前用例名称：', sys._getframe().f_code.co_name)
        tile_list = self.get_tile_list(CATALOG_OUT_TEST, TILE_LAYER_RCSINT)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSINT)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT_TEST, TILE_LAYER_RCSINT)

        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_rcsext_int_06(self):
        """
        rcsext 测试线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT_TEST, TILE_LAYER_RCSEXT)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_hcc_int_07(self):
        """
        hcc 测试线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT_TEST, TILE_LAYER_HCCHCI)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT_TEST, TILE_LAYER_HCCHCI)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT_TEST, TILE_LAYER_HCCHCI)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'

    def test_trfregs_int_08(self):
        """
        trfregs 测试线
        """

        # 打印当前方法名称
        print('当前用例名称：', sys._getframe().f_code.co_name)

        tile_list = self.get_tile_list(CATALOG_OUT_TEST, TILE_LAYER_TRFREGS)
        hdms_tile = self.get_tile_checksum_crc(tile_list, CATALOG_OUT_TEST, TILE_LAYER_TRFREGS)
        interface_tile = self.query_tile_checksum_crc(CATALOG_OUT_TEST, TILE_LAYER_TRFREGS)
        for j in range(len(hdms_tile)):
            for i in range(len(interface_tile)):
                if hdms_tile[j][0] == interface_tile[i][0]:
                    assert interface_tile[i][1] == hdms_tile[j][1], f'校验的第{j+1}个tile:{hdms_tile[j][0]} checksum不一致'
                    assert interface_tile[i][2] == hdms_tile[j][2], f'校验的第{j+1}个tile:{hdms_tile[j][0]} crc不一致'
