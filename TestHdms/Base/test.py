import hashlib
import os
import re
from natsort import ns, natsorted
from crcmod.predefined import PredefinedCrc
from TestHdms.Base.basefunc_test import *

# filepath = r"D:\Download\557027723-trfregs-正式线-0308-不一致"
# filepath = r"D:\Download\null (8)"
#
# def getsha256(filepath):
#     file = open(filepath, 'rb')
#     sha1func = hashlib.sha256()
#     sha1func.update(file.read())
#     sha256 = str(sha1func.hexdigest())
#     return sha256.upper()
#
#
# def getcrc32c(filepath):
#     file = open(filepath, 'rb')
#     hasher = PredefinedCrc('crc-32c')
#     hasher.update(file.read())
#     crc32c = hasher.digest()
#     crc32c = int.from_bytes(crc32c, byteorder='big', signed=False)
#     return "%X" % (crc32c & 0xffffffff)
#
#
# print("checksum:%s" % getsha256(filepath))
# print("crc:%s" % getcrc32c(filepath).lower())


# FILE_LIST_DIR = r'E:/03 HDMS/98 测试文件/data check/01 rcs-字段校验/ext'

# 替换目录下的所有目标json文件volatile_provider_id-108，并写回文件
# file_list = os.listdir(FILE_LIST_DIR)
# print(file_list)
# for i in range(len(file_list)):
#     if ".json" in file_list[i]:
#         print(f'文件名称为： {file_list[i]}')
#         with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'r', encoding='utf-8') as fp:
#             json_file = json.load(fp)
#         if 'volatile_provider_id' not in file_list[i]:
#             json_file["volatile_provider_id"] = 108
#             # json_file["volatile_provider_id"] = 117
#         with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
#             json.dump(json_file, dump_f)
#         os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/rcsext{file_list[i][6:]}')
        # os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/hci{file_list[i][3:]}')


# 替换rcsint 正式线 557038792过期时间为当前时间17min后，并写回文件
# 读取目标json文件-103
# file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
# with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
#     json_file = json.load(fp)
# utc_now = datetime.datetime.utcnow()
# utc_17_after = (utc_now + datetime.timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%S")
# json_file['tile_replacements'][1]['end_time'] = utc_17_after
# with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
#     json.dump(json_file, dump_f)

# 排序问题：os.listdir()结果不一定和Windows系统名称排序一致;;;files_1 = natsorted(files,alg=ns.PATH) 加上alg=ns.PATH参数才和windows系统名称排序一致
# 未生效 和Windows顺序依旧不一致
# DATA_CHECK_FILE_DIR = '../TestFiles/03 data check'
# file_dir = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/int'
# file_dir1 = f'{DATA_CHECK_FILE_DIR}/01 rcs-字段校验/ext'
# file_dir2 = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/int'
# file_dir3 = f'{DATA_CHECK_FILE_DIR}/02 rcs-字段缺失/ext'
# file_dir3 = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hcc'
# file_dir4 = f'{DATA_CHECK_FILE_DIR}/03 hcc-字段缺失/hci'
# file_dir5 = f'{DATA_CHECK_FILE_DIR}/04 hcc-字段校验'
# file_list = os.listdir(file_dir5)
# file_list1 = natsorted(file_list, alg=ns.PATH)
# print(file_list)
# print(file_list1)
# assert file_list == file_list1

func = TestBaseFunc()

# with open('E:\\03 HDMS\\98 测试文件\\00 迭代\\22Q3SP1\\10839\\rcsint-01-payload为null，attr_id不能decode.json', 'r', encoding='utf-8') as fp:
#     json_file = json.load(fp)
#
# # 发送json文件
# trace_id = func.get_trace_id(CATALOG_RCSINT, TRACEID_LAYER_RCSINT, json_file)
#
# # 循环等待日志出现，并打印结果
# for j in range(10):
#     res_err = func.get_errorlog(CATALOG_RCSINT, ERROR_LAYER_RCSINT)
#
#     if trace_id in res_err:
#         attr_id = re.findall('"attr_id":(.*?),', res_err, re.S)[0]
#         volatile_location_id = re.findall('"volatile_location_id":(.*?),', res_err, re.S)[0]
#         print(attr_id)
#         print(volatile_location_id)
#         break
#     time.sleep(3)
#     print(f"循环{j + 1}*3s,还没找到对应的日志")


# res_err = '''{"error_timestamp":"2022-04-08T09:25:41","upload_id":"dff9b4f1-544c-4c51-954c-6ae994a9f9d5","msg_id":null,"msg_type":null,"volatile_provider_id":null,"map_version":null,"inuse_map_version":null,"basic_info_errors":[{"error_code":"EC-RCSEXT-DC-msgType","error_msg":"The following fields(msg_type) could not be resolve successfully, please check the field value."}],"tile_replacements":null}'''

# res_err = """{"error_timestamp":"2022-04-08T09:26:08","upload_id":"4cffa4e6-0dee-4891-9076-7c6bfd77d7da","msg_id":"nYeldssxEemBrBheDxK4cA==","msg_type":"REPLACE_TILES","volatile_provider_id":108,"map_version":"123","inuse_map_version":"nrn:navinfo:data:::HDMap-NDS-2.5.4-China-Daimler;86","basic_info_errors":null,"tile_replacements":[{"nds_packed_tile_id":"557042475","tileId_timestamp_errors":[{"error_code":"EC-RCSEXT-DC-time","error_msg":"Invalid create_time (null) due to the wrong/expired schema or value."}],"oem_data_additions":[{"attr_id":"A1/ccEEtEey3Idie8zwxiw==","volatile_location_id":10019068,"attribute_errors":null},{"attr_id":"A2/ccEEtEey3Idie8zwxiw==","volatile_location_id":10019067,"attribute_errors":null}]}]}"""
# res_err = """{"error_timestamp":"2022-04-08T09:26:46","upload_id":"52d5369e-5e8f-46ae-91f7-90f43d68b042","msg_id":"nYeldssxEemBrBheDxK4cA==","msg_type":"REPLACE_TILES","volatile_provider_id":108,"map_version":"123","inuse_map_version":"nrn:navinfo:data:::HDMap-NDS-2.5.4-China-Daimler;86","basic_info_errors":null,"tile_replacements":[{"nds_packed_tile_id":"557042475","tileId_timestamp_errors":null,"oem_data_additions":[{"attr_id":null,"volatile_location_id":10096790,"attribute_errors":[{"error_code":"EC-RCSEXT-DC-field","error_msg":"The following fields are missing or empty:attr_id"}]}]}]}"""

# res_err = """{"error_timestamp":"2022-04-08T09:26:50","upload_id":"f65f183b-1524-4ccf-9327-09d9991d92f6","msg_id":"nYeldssxEemBrBheDxK4cA==","msg_type":"REPLACE_TILES","volatile_provider_id":108,"map_version":"123","inuse_map_version":"nrn:navinfo:data:::HDMap-NDS-2.5.4-China-Daimler;86","basic_info_errors":null,"tile_replacements":[{"nds_packed_tile_id":"557042475","tileId_timestamp_errors":null,"oem_data_additions":[{"attr_id":"","volatile_location_id":10096790,"attribute_errors":[{"error_code":"EC-RCSEXT-DC-field","error_msg":"The following fields are missing or empty:attr_id"}]}]}]}"""
res_err = """{"volatile_location_id":116,"volatile_location_id_errors":null,"oem_data_additions":null,"oem_data_deletions":[{"error_code":"EC-HCC-DC-noData","error_msg":"Invalid input file due to no change defined on the OEM data layer.","attr_id":null}]}]}"""
attr_id = re.findall(r'"attr_id":(.*?),', res_err)
volatile_location_id = re.findall(r'"volatile_location_id":(.*?),', res_err)
# if len(attr_id) == 0:
#     attr_id = re.findall(r'"attr_id":(.*?)}', res_err)
#     if len(attr_id) == 0:
#         print('attr_id 不存在')
#     elif attr_id[0] == 'null':
#         print('attr_id 为null')
#     elif attr_id[0] == '""':
#         print('attr_id 为""')
# elif attr_id[0] == 'null':
#     print('attr_id 为null')
# elif attr_id[0] == '""':
#     print('attr_id 为""')
# if len(volatile_location_id) == 0:
#     volatile_location_id = re.findall(r'"volatile_location_id":(.*?)}', res_err)
#     if len(volatile_location_id) == 0:
#         print('volatile_location_id 不存在')
#     elif volatile_location_id[0] == 'null':
#         print('volatile_location_id 为null')
#     elif volatile_location_id[0] == '""':
#         print('volatile_location_id 为""')
# elif volatile_location_id[0] == 'null':
#     print('volatile_location_id 为null')
# elif volatile_location_id[0] == '""':
#     print('volatile_location_id 为""')

attr_id1 = re.findall(r'"attr_id":(.*?),', res_err)
attr_id2 = re.findall(r'"attr_id":(.*?)}', res_err)

attr_id = attr_id1 if len(attr_id1) > 0 else attr_id2
if len(attr_id) == 0:
    print('attr_id 不存在')
elif attr_id[0] == 'null':
    print('attr_id 为null')
elif attr_id[0] == '""':
    print('attr_id 为""')

