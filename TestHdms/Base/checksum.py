import hashlib
import os

from crcmod.predefined import PredefinedCrc
from TestHdms.Base.basefunc_test import *

# filepath = r"D:\Download\557027723-trfregs-正式线-0308-不一致"
filepath = r"D:\Download\null (8)"
# filepath = r"D:\Download\557038792"


def getsha256(filepath):
    file = open(filepath, 'rb')
    sha1func = hashlib.sha256()
    sha1func.update(file.read())
    sha256 = str(sha1func.hexdigest())
    return sha256.upper()


def getcrc32c(filepath):
    file = open(filepath, 'rb')
    hasher = PredefinedCrc('crc-32c')
    hasher.update(file.read())
    crc32c = hasher.digest()
    crc32c = int.from_bytes(crc32c, byteorder='big', signed=False)
    return "%X" % (crc32c & 0xffffffff)


print("checksum:%s" % getsha256(filepath))
print("crc:%s" % getcrc32c(filepath).lower())


FILE_LIST_DIR = r'E:/03 HDMS/98 测试文件/data check/01 rcs-字段校验/ext'

# 替换目录下的所有目标json文件volatile_provider_id-108，并写回文件
file_list = os.listdir(FILE_LIST_DIR)
print(file_list)
for i in range(len(file_list)):
    if ".json" in file_list[i]:
        print(f'文件名称为： {file_list[i]}')
        with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'r', encoding='utf-8') as fp:
            json_file = json.load(fp)
        if 'volatile_provider_id' not in file_list[i]:
            json_file["volatile_provider_id"] = 108
            # json_file["volatile_provider_id"] = 117
        with open(f'{FILE_LIST_DIR}/{file_list[i]}', 'w+', encoding='utf-8') as dump_f:
            json.dump(json_file, dump_f)
        os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/rcsext{file_list[i][6:]}')
        # os.rename(f'{FILE_LIST_DIR}/{file_list[i]}', f'{FILE_LIST_DIR}/hci{file_list[i][3:]}')


# 替换rcsint 正式线 557038792过期时间为当前时间17min后，并写回文件
# 读取目标json文件-103
file_name = 'rcs-02-3个tile发布-557042475-557038792-557017790.json'
with open(f'{FILE_LIST_DIR}/{file_name}', 'r', encoding='utf-8') as fp:
    json_file = json.load(fp)
utc_now = datetime.datetime.utcnow()
utc_17_after = (utc_now + datetime.timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%S")
json_file['tile_replacements'][1]['end_time'] = utc_17_after
with open(f'{FILE_LIST_DIR}/{file_name}', 'w+', encoding='utf-8') as dump_f:
    json.dump(json_file, dump_f)
