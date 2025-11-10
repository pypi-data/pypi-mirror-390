import filecmp
import glob
import gzip
import hashlib
import io
import json
import logging
import math
import shutil
import string
import sys
import tarfile
import urllib
import warnings
from datetime import datetime
import codecs
from os import PathLike
from typing import Union

import jsonlines

import yaml
import types
import wave
import multiprocessing as mp
from colorama import Fore, Style


from ..thread.my_thread import *
from .utils_file_2 import *
from .utils_file_3 import *


# ------------------个性化 logging 相关------------------
#  ==========basic============
NO_PRINT = False
LOG_FILE = None
LOG_FILE_WRITE_F = None

def do_set_no_print(flag):
    global NO_PRINT
    NO_PRINT = flag

def do_set_log_file(file_path, mode='a'):
    global LOG_FILE
    LOG_FILE = file_path
    global LOG_FILE_WRITE_F
    LOG_FILE_WRITE_F = open(LOG_FILE, mode=mode, encoding='utf-8', buffering=1)
    LOG_FILE_WRITE_F.write("============DRAGON-LOG-START=================\n")

def _dragon_print(string_temp, flush=True):
    if NO_PRINT:
        return
    print(string_temp, flush=flush)
    if LOG_FILE_WRITE_F is not None:
        LOG_FILE_WRITE_F.write(string_temp + '\n')

def logging_print(*args):
    if NO_PRINT:
        return
    string_temp = " ".join([str(arg) for arg in args])
    time_str = datetime.now().strftime(f'%Y-%m-%d %H:%M:%S DRAGON-PRINT ')
    string_temp = time_str + ' ' + string_temp
    _dragon_print(string_temp, flush=True)

def logging_info(*args):
    if NO_PRINT:
        return
    string_temp = " ".join([str(arg) for arg in args])
    time_str = datetime.now().strftime(f'%Y-%m-%d %H:%M:%S DRAGON-INFO ')
    string_temp = time_str + ' ' + string_temp
    _dragon_print(Fore.GREEN + string_temp + Style.RESET_ALL, flush=True)

def logging_warning(*args):
    if NO_PRINT:
        return
    string_temp = " ".join([str(arg) for arg in args])
    time_str = datetime.now().strftime(f'%Y-%m-%d %H:%M:%S DRAGON-WARNING ')
    string_temp = time_str + ' ' + string_temp
    _dragon_print(Fore.YELLOW + string_temp + Style.RESET_ALL, flush=True)

def logging_error(*args):
    if NO_PRINT:
        return
    string_temp = " ".join([str(arg) for arg in args])
    time_str = datetime.now().strftime(f'%Y-%m-%d %H:%M:%S DRAGON-ERROR ')
    string_temp = time_str + ' ' + string_temp
    _dragon_print(Fore.RED + string_temp + Style.RESET_ALL, flush=True)

class LimitPrinter:
    def __init__(self):
        self.max = 30
        self.now = 0

    def print(self, *args):
        text = ' '.join([str(x) for x in args])
        if self.now < self.max:
            logging_info("LIMIT_PRINT: ", text)
            self.now += 1

    def set_max(self, max_in):
        self.max = max_in

    def reset(self):
        self.now = 0

global_limit_printer = LimitPrinter()

def logging_limit_print(*text):
    global global_limit_printer
    global_limit_printer.print(*text)

# ========basic , info, warning error, limit_print, set_no_print, set_log_file============


def print_list(data: list):
    logging_info('_________print_list_start_______________')
    for item in data:
        logging_info(item)
    logging_info('_________print_list_end____total:%d' % len(data))

def print_dict(data: dict):
    logging_info('_________print_dict_start_______________')
    for k, v in data.items():
        logging_info(f'{k} :\t{v}')
    logging_info('_________print_dict_end____total:%d' % len(data))

def print_checkpoint_dict(checkpoint_dict_or_path):
    if not isinstance(checkpoint_dict_or_path, dict):
        assert isinstance(checkpoint_dict_or_path, str)
        checkpoint = torch.load(checkpoint_dict_or_path, map_location='cpu')
    logging_info('_________print_checkpoint_start_______________')
    for k, v in checkpoint.items():
        logging_info(f'{k} :\t{v.shape}')
    logging_info('_________print_checkpoint_end____total:%d' % len(checkpoint))

def hello_gxl():
    """"""
    logging_info("我是耿雪龙")
def do_print_model_dtype(model):
    dtype_name = ""
    for name, param in model.named_parameters():
        dtype_name = param.dtype
        break
    logging_info(f"模型数据类型：{dtype_name}")
# ------------------个性化 logging 相关-------------end











# -----------------时间相关-------------------------
def do_get_now_time_by_second():
    """单位为秒, 通常和do_get_elapsed_time合并使用计算时间差值"""
    return time.time()

def do_get_elapsed_time(last_time_by_second):
    """回复数字, 单位秒"""
    return time.time() - last_time_by_second


def get_now_format_str(the_format='%Y-%m-%d_%H_%M_%S'):
    """
    获取当前日期和时间, 以字符串的形式返回
    :param the_format:
    :return:
    """
    current_datetime = datetime.now()
    # 格式化日期为字符串
    formatted_date = current_datetime.strftime(the_format)
    return formatted_date

class GxlTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start()

    def start(self):
        """Start the timer."""
        self.start_time = time.time()

    def stop(self):
        """Stop the timer."""
        self.end_time = time.time()

    def start_halfway(self):
        self.start()

    def stop_halfway_and_return(self, is_sec=True):
        self.stop()
        elapsed_time = self.elapsed_time()
        self.start()
        if is_sec:
            return elapsed_time / 1000
        return elapsed_time

    def stop_halfway(self,is_sec = True):
        self.stop()
        elapsed_time = self.elapsed_time()
        self.start()
        if is_sec:
            elapsed_time = elapsed_time
            return elapsed_time
        return elapsed_time * 1000

    def stop_halfway_and_print(self, print_str="任务完成", is_sec=True):
        self.stop()
        elapsed_time = self.elapsed_time()
        self.start()
        if is_sec:
            elapsed_time = elapsed_time
            logging_info(f"{print_str} 用时:{elapsed_time}秒")
            return elapsed_time
        logging_info(f"{print_str} 用时:{elapsed_time * 1000}毫秒")
        return elapsed_time * 1000

    def elapsed_time(self):
        """Return the elapsed time in seconds."""
        if self.start_time is None:
            raise ValueError("Timer has not been started")
        if self.end_time is None:
            raise ValueError("Timer has not been stopped")
        return self.end_time - self.start_time
global_timer = GxlTimer()
# --------------------时间相关, now, elapsed, timer--------------------------------end









# --------------------------file size 相关-------------------------------
def get_dir_size(dir_path: str):
    """
    单位:MB
    """
    size = 0
    for root, dirs, files in os.walk(dir_path):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size / (1024 ** 2)

def do_get_dir_size(dir_path: str):
    """
    单位:MB
    :param dir_path:
    :return:
    """
    return get_dir_size(dir_path)

def get_file_size(file_path):
    """单位：MB"""
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path) / (1024 ** 2)

def do_get_file_size(file_path):
    """单位：MB"""
    return get_file_size(file_path)
# --------------------------file size 相关-------------------------------end






# -----------------------数据加载相关----------------------------------------------
def load_list_file_clean(path: str):
    """
    得到不包含换行符的str_list
    :param path: 文件路径
    :return: 不包含换行符的字符串列表
    """
    logging_info(f"load_list_file_clean() - 开始加载文件: {path}")
    global_timer.start_halfway()

    if not os.path.exists(path):
        logging_info(f'load_list_file_clean() - 错误: 文件不存在: {path}')
        return []

    try:
        with codecs.open(path, 'r', encoding='utf-8') as f:
            cat_to_name: list = f.read().splitlines()  # 不包括换行符
            logging_info(f"load_list_file_clean() - 加载成功, 数据总条数为: {len(cat_to_name)}, 加载文件: {path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f'load_list_file_clean() - 错误: 加载文件时出错: {path}, 错误信息: {str(e)}')
        return []
    return cat_to_name

def load_first_row_clean(path: str):
    """
    得到不包含换行符的第一行, 如果文件为空，则返回“”
    :param path: 文件路径
    :return: 第一行字符串（去除换行符）
    """
    logging_info(f"load_first_row_clean() - 开始加载文件: {path}")
    global_timer.start_halfway()

    if not os.path.exists(path):
        logging_info(f'load_first_row_clean() - 错误: 文件不存在: {path}')
        return ""

    try:
        with codecs.open(path, 'r', encoding='utf-8') as f:
            cat_to_name: str = f.readline().strip()  # 获取第一行并去掉换行符
            logging_info(f"load_first_row_clean() - 加载成功, 第一行数据: {cat_to_name}, 加载文件: {path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f'load_first_row_clean() - 错误: 加载文件时出错: {path}, 错误信息: {str(e)}')
        return ""
    return cat_to_name

def load_list_file_unclean(path: str):
    """
    得到包含换行符的str_list
    :param path: 文件路径
    :return: 包含换行符的字符串列表
    """
    logging_info(f"load_list_file_unclean() - 开始加载文件: {path}")

    try:
        with codecs.open(path, 'r', encoding='utf-8') as f:
            cat_to_name: list = f.readlines()  # 包含换行符
            logging_info(f"load_list_file_unclean() - 加载成功, 数据总条数为: {len(cat_to_name)}, 加载文件: {path}")
    except Exception as e:
        logging_info(f'load_list_file_unclean() - 错误: 加载文件时出错: {path}, 错误信息: {str(e)}')
        return []
    return cat_to_name

def load_dict_from_json(path) -> dict:
    """
    从JSON文件中加载字典
    :param path: JSON文件路径
    :return: 加载的字典数据
    """
    logging_info(f"load_dict_from_json() - 开始加载文件: {path}")
    global_timer.start_halfway()

    try:
        with codecs.open(path, 'r', encoding='utf-8') as f:
            cat_to_name: dict = json.load(f)
            logging_info(f"load_dict_from_json() - 加载成功, 数据总条数为: {len(cat_to_name)}, 加载文件: {path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f'load_dict_from_json() - 错误: 加载文件时出错: {path}, 错误信息: {str(e)}')
        return {}
    return cat_to_name

def load_dict_list_from_jsonl(jsonl_file_path) -> list:
    """
    从JSONL文件中加载字典列表
    :param jsonl_file_path: JSONL文件路径
    :return: 字典列表
    """
    logging_info(f"load_dict_list_from_jsonl() - 开始加载文件: {jsonl_file_path}")

    lines_res = []
    global_timer.start_halfway()
    try:
        with codecs.open(jsonl_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    line = json.loads(line)
                    lines_res.append(line)
                except Exception as e:
                    logging_info(f"load_dict_list_from_jsonl() - 错误: 解析行时出错: {line}, 错误信息: {str(e)}")
                    continue
            logging_info(
                f"load_dict_list_from_jsonl() - 加载成功, 数据总条数为: {len(lines_res)}, 加载文件: {jsonl_file_path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f"load_dict_list_from_jsonl() - 错误: 加载文件时出错: {jsonl_file_path}, 错误信息: {str(e)}")
    return lines_res

def load_dict_from_scp(label_scp_file: str, silence: bool = False) -> dict:
    """
    得到scp文件的内容,要求key value以空格分割，第一个为key,剩下的都是value
    :param label_scp_file: SCP文件路径
    :param silence: 是否静默输出（默认False）
    :return: 字典数据
    """
    logging_info(f"load_dict_from_scp() - 开始加载文件: {label_scp_file}")

    res = {}
    global_timer.start_halfway()
    try:
        with codecs.open(label_scp_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                items = line.split()
                if len(items) < 2:
                    if not silence:
                        logging_info(f'load_dict_from_scp() - 警告: 行数据不符合scp规范, 跳过: {line}')
                    continue
                elif len(items) == 2:
                    res[items[0].strip()] = items[1].strip()
                else:
                    res[items[0].strip()] = ' '.join(items[1:]).strip()
        logging_info(f"load_dict_from_scp() - 加载成功, 数据总条数为: {len(res)}, 加载文件: {label_scp_file}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f"load_dict_from_scp() - 错误: 加载文件时出错: {label_scp_file}, 错误信息: {str(e)}")
        return {}
    return res

def do_load_item_list_from_scp(input_scp_path):
    """
    得到scp文件的内容,要求key value以空格分割，第一个为key,剩下的都是value
    :param input_scp_path: SCP文件路径
    :return: 包含key-value元组的列表
    """
    logging_info(f"do_load_item_list_from_scp() - 开始加载文件: {input_scp_path}")

    item_list = []
    try:
        with codecs.open(input_scp_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                items = line.split()
                if len(items) < 2:
                    logging_info(f'load_dict_from_scp() - 警告: 行数据不符合scp规范, 跳过: {line}')
                    continue
                elif len(items) == 2:
                    item_list.append((items[0].strip(), items[1].strip()))
                else:
                    item_list.append((items[0].strip(), ' '.join(items[1:]).strip()))
        logging_info(
            f"do_load_item_list_from_scp() - 加载成功, 数据总条数为: {len(item_list)}, 加载文件: {input_scp_path}")
    except Exception as e:
        logging_info(f"do_load_item_list_from_scp() - 错误: 加载文件时出错: {input_scp_path}, 错误信息: {str(e)}")
        return []
    return item_list

def load_item_list_from_scp(input_scp_path):
    """
    包装函数，用于加载scp文件中的key-value元组
    :param input_scp_path: SCP文件路径
    :return: 包含key-value元组的列表
    """
    logging_info(f"load_item_list_from_scp() - 调用包装函数 do_load_item_list_from_scp, 文件: {input_scp_path}")
    return do_load_item_list_from_scp(input_scp_path)

def load_tuple_list_from_scp(label_scp_file: str) -> list:
    """
    从scp文件中加载元组列表
    :param label_scp_file: SCP文件路径
    :return: 元组列表
    """
    logging_info(f"load_tuple_list_from_scp() - 开始加载文件: {label_scp_file}")

    res = []
    try:
        with codecs.open(label_scp_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                items = line.split()
                if len(items) < 2:
                    logging_info(f'load_tuple_list_from_scp() - 警告: 行数据不符合scp规范, 跳过: {line}')
                    continue
                elif len(items) == 2:
                    res.append((items[0].strip(), items[1].strip()))
                else:
                    logging_info(f'load_tuple_list_from_scp() - 警告: 行数据不符合scp规范, 不跳过: {line}')
                    res.append((items[0].strip(), ' '.join(items[1:]).strip()))
        logging_info(f"load_tuple_list_from_scp() - 加载成功, 数据总条数为: {len(res)}, 加载文件: {label_scp_file}")
    except Exception as e:
        logging_info(f"load_tuple_list_from_scp() - 错误: 加载文件时出错: {label_scp_file}, 错误信息: {str(e)}")
    return res
def load_data_from_xlsx(file_path, return_cols=True, table_index=0):
    """"""
    try:
        import pandas as pd
    except:
        logging_info('pandas 未安装，请先安装 pandas; pip install pandas')
        return
    logging_info('load_data_from_xlsx: {}'.format(file_path))
    xls = pd.ExcelFile(file_path)
    res = {}
    sheet1 = pd.read_excel(xls, sheet_name=xls.sheet_names[table_index])
    if return_cols:
        col_num = len(sheet1.columns)
        logging_info(f'按列读取，读取出每一列的数据，列数：{col_num}')
        for i in range(col_num):
            column_sheet_i = sheet1.iloc[:, i]
            name_i = column_sheet_i.name
            values_list= list(column_sheet_i)
            res[name_i] = values_list
    else:
        header_list = sheet1.columns.tolist()
        name_i = header_list[0]
        res[name_i] = header_list[1:]
        row_num = len(sheet1.index)
        logging_info(f'按行读取，读取出每一行的数据，行数：{row_num+1}')
        for i in range(row_num):
            row_sheet_i = sheet1.iloc[i, :]
            values_list= list(row_sheet_i)
            name_i = values_list[0]
            values_list = values_list[1:]
            res[name_i] = values_list
    return res

def write_dict_to_xlsx(data_dict, output_file, cols_pattern=True):
    try:
        import pandas as pd
    except:
        logging_info('pandas 未安装，请先安装 pandas; pip install pandas')
        return
    makedir_for_file(output_file)
    if cols_pattern:
        logging_info(f'按列写入: {output_file}')
        # 创建一个DataFrame对象
        df = pd.DataFrame(data_dict)
        # 将DataFrame写入xlsx文件
        df.to_excel(output_file, index=False)
    else:
        logging_info(f'按行写入: {output_file}')
        # 创建一个DataFrame对象
        df = pd.DataFrame.from_dict(data_dict, orient='index').reset_index()
        # 将DataFrame写入Excel文件
        df.to_excel(output_file, index=False, header=False)

# -----------------------数据加载相关----------------------------------------------end










# -----------------------数据保存相关----------------------------------------------start
def write_list_to_file(data_list: list, path: str, is_append: bool = False):
    """
    要求data_list中每个元素(str)末尾没有换行, 该写入程序为每个item生成一个结尾的换行符
    :param data_list: 数据列表
    :param path: 文件路径
    :param is_append: 是否追加写入
    :return: None
    """
    global_timer.start_halfway()
    logging_info(f"write_list_to_file() - 开始写入文件: {path}, 数据总条数为: {len(data_list)}")
    makedir_for_file(path)

    try:
        with codecs.open(path, 'w' if not is_append else 'a', encoding='utf-8') as f:
            for data in data_list:
                f.write(data + '\n')
        logging_info(f"write_list_to_file() - 写入成功, 数据总条数为: {len(data_list)}, 写入文件: {path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f"write_list_to_file() - 错误: 写入文件时出错: {path}, 错误信息: {str(e)}")


def write_dict_to_json(dic, json_file_path):
    """
    将字典写入JSON文件
    :param dic: 字典数据
    :param json_file_path: JSON文件路径
    :return: None
    """
    logging_info(f"write_dict_to_json() - 开始写入文件: {json_file_path}, 数据总条数为: {len(dic)}")

    if "/" not in json_file_path:
        json_file_path = "./" + json_file_path
    makedir_for_file(json_file_path)

    try:
        with codecs.open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(dic, f, ensure_ascii=False, indent=4)
        logging_info(f"write_dict_to_json() - 写入成功, 数据总条数为: {len(dic)}, 写入文件: {json_file_path}")
    except Exception as e:
        logging_info(f"write_dict_to_json() - 错误: 写入文件时出错: {json_file_path}, 错误信息: {str(e)}")


def write_dict_list_to_jsonl(dict_list, jsonl_file_path, is_append: bool = False):
    """
    将字典列表写入JSONL文件
    :param dict_list: 字典列表
    :param jsonl_file_path: JSONL文件路径
    :param is_append: 是否追加写入
    :return: None
    """
    global_timer.start_halfway()
    logging_info(f"write_dict_list_to_jsonl() - 开始写入文件: {jsonl_file_path}, 数据总条数为: {len(dict_list)}")

    if not is_append:
        if os.path.exists(jsonl_file_path):
            os.remove(jsonl_file_path)

    makedir_for_file(jsonl_file_path)

    try:
        if not is_append:
            with jsonlines.open(jsonl_file_path, mode='w') as f:
                f.write_all(dict_list)
        else:
            with jsonlines.open(jsonl_file_path, mode='a') as f:
                f.write_all(dict_list)
        logging_info(
            f"write_dict_list_to_jsonl() - 写入成功, 数据总条数为: {len(dict_list)}, 写入文件: {jsonl_file_path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f"write_dict_list_to_jsonl() - 错误: 写入文件时出错: {jsonl_file_path}, 错误信息: {str(e)}")


def write_single_dict_to_jsonl(dic, jsonl_file_path):
    """
    将单个字典写入JSONL文件
    :param dic: 字典数据
    :param jsonl_file_path: JSONL文件路径
    :return: None
    """
    logging_info(f"write_single_dict_to_jsonl() - 开始写入文件: {jsonl_file_path}")

    try:
        with jsonlines.open(jsonl_file_path, mode='a') as f:
            f.write(dic)
        logging_info(f"write_single_dict_to_jsonl() - 写入成功, 写入文件: {jsonl_file_path}")
    except Exception as e:
        logging_info(f"write_single_dict_to_jsonl() - 错误: 写入文件时出错: {jsonl_file_path}, 错误信息: {str(e)}")


def write_dict_to_scp(dic: dict, scp_file_path: str):
    """
    将字典数据写入SCP文件
    :param dic: 字典数据
    :param scp_file_path: SCP文件路径
    :return: None
    """
    logging_info(f"write_dict_to_scp() - 开始写入文件: {scp_file_path}, 数据总条数为: {len(dic)}")
    global_timer.start_halfway()

    makedir_for_file(scp_file_path)

    try:
        with codecs.open(scp_file_path, 'w', encoding='utf-8') as f:
            for k, v in dic.items():
                f.write(f"{k} {v}\n")
        logging_info(f"write_dict_to_scp() - 写入成功, 数据总条数为: {len(dic)}, 写入文件: {scp_file_path}, 耗时: {global_timer.stop_halfway()}s")
    except Exception as e:
        logging_info(f"write_dict_to_scp() - 错误: 写入文件时出错: {scp_file_path}, 错误信息: {str(e)}")

# -----------------------数据保存相关----------------------------------------------end











# ---------------------------dir and path 相关----------------------------------------start
def do_remove_last_slash(file_path):
    """
    去掉路径末尾的斜杠
    :param file_path:
    :return:
    """
    if file_path[-1] == '/':
        file_path = file_path[:-1]
    return file_path

def makedir(path):
    if isinstance(path, str):
        path = Path(path)
        # os.makedirs(path)
    if not path.exists():
        logging_info(f'路径{path.absolute()}不存在,现创建')
        path.mkdir(parents=True, exist_ok=True)
    else:
        logging_info(f'路径{path.absolute()}已存在,不用创建')

def makedir_sil(path):
    os.makedirs(str(path), exist_ok=True)

def makedir_for_file(filepath):
    dirpath = os.path.dirname(filepath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def makedir_for_file_or_dir(filepath):
    def ends_with_dot_and_non_slash_backslash(text):
        pattern = r'\.[^/\\]+$'
        return re.search(pattern, text) is not None
    # dirpath = os.path.dirname(filepath)
    if ends_with_dot_and_non_slash_backslash(filepath):
        makedir_for_file(filepath)
    else:
        makedir_sil(filepath)

def _join_path(path1, path2):
    if path1 is None or path2 is None or len(path1) == 0 or len(path2) == 0:
        return ""
    while path1[-1] == '/' or path1[-1] == '\\':
        path1 = path1[:-1]
    while path2[0] == '/' or path2[0] == '\\':
        path2 = path2[1:]
    return f'{path1}/{path2}'

def join_path(*args):
    """
    安全拼接若干路径, 再也不用担心分路径结尾和开头的分隔符的困扰了
    """
    lens = len(args)
    if lens == 0:
        return ""
    path = args[0]
    for i in range(1, lens):
        path = _join_path(path, args[i])
    return path

def get_file_pure_name_from_path(path: str):
    """
    得到单纯的文件名，没有后缀和目录名
    不论名字有多少个点， 只吧最后一个点的右侧删去，保留左侧的内容，不保留最后一个点。
    """
    return os.path.splitext(os.path.basename(path))[0]

def do_get_file_pure_name_from_path(path: str):
    """
    得到单纯的文件名，没有后缀和目录名
    不论名字有多少个点， 只吧最后一个点的右侧删去，保留左侧的内容，不保留最后一个点。
    """
    return os.path.splitext(os.path.basename(path))[0]

def do_get_suffix_from_path(path: str):
    return os.path.splitext(os.path.basename(path))[1]
def get_other_file_in_same_dir(old_file, new_file_name):
    dirname = os.path.dirname(old_file)
    return os.path.join(dirname, new_file_name)

def get_clean_filename(filename: str):
    """
    将一个字符串转为一个可以作为文件名的形式, 将非法字符替换为-,保留25个字符
    """
    # # 移除非法字符
    # filename = filename.replace(' ', '')
    # cleaned_filename = re.sub(r'[\/:*?"<>|]', '-', filename)
    # # 截断文件名，以确保它在不同系统下都有效, 本来是255, 但实验表明在windows下还是因为长度报错了,所有索性改为25
    # cleaned_filename = cleaned_filename[:25]
    # return cleaned_filename
    A = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", filename)
    return A[:25]
def remove_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
def do_remove_file(file_path: str):
    remove_file(file_path)
def do_delete_file(file_path: str):
    remove_file(file_path)
def do_replace_dir(input_path, new_dir):
    """
    将一个路径的parent dir替换为一个新的路径， 可以是dir 也可以是file
    :param input_path:
    :param new_dir:
    :return:
    """
    base_name = os.path.basename(input_path)
    new_path = os.path.join(new_dir, base_name)
    return new_path
def do_replace_name(input_path, new_name):
    """
    将一个路径的parent dir替换为一个新的路径， 可以是dir 也可以是file
    :param input_path:
    :param new_dir:
    :return:
    """
    # base_name = os.path.basename(input_path)
    base_dir = os.path.dirname(input_path)
    new_path = os.path.join(base_dir, new_name)
    return new_path
def remove_dir(directory_to_delete):
    """递归删除一整个目录"""
    logging_info('remove_dir():开始删除目录:%s' % directory_to_delete)
    shutil.rmtree(directory_to_delete)
    logging_info('remove_dir():目录结束删除:%s' % directory_to_delete)
# ---------------------------dir and path 相关----------------------------------------end 






# -------------------------------加载文件路径集合----------------------------------------start
def get_scp_for_wav_dir(wav_dir: str, wav_scp_file_path: str = None, suffix: str = '.wav', recursive=False):
    """
    生成wav.scp文件，或者返回包含wav文件路径的字典。
    :param wav_dir: 包含wav文件的目录路径
    :param wav_scp_file_path: 生成的scp文件的存储路径，如果为None，则直接返回包含wav文件路径的字典
    :param suffix: wav文件的后缀，默认为'.wav'
    :param recursive: 是否递归查找子目录中的wav文件，默认为False
    :return: 如果wav_scp_file_path为None，返回包含wav文件路径的字典；否则返回None
    """
    logging_info('开始执行函数：get_scp_for_wav_dir()')
    global_timer.start_halfway()
    if suffix[0] != '.':
        suffix = '.' + suffix
    if recursive:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'**/*{suffix}'), recursive=True)
    else:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'*{suffix}'))
    if wav_scp_file_path is None:
        logging_info('存储地址为None，就直接返回dict')
        res_dict = {}
        for wav_path in tqdm(wav_path_list, total=len(wav_path_list)):
            res_dict[get_file_pure_name_from_path(wav_path)] = wav_path
        global_timer.stop_halfway_and_print('结束执行函数：get_scp_for_wav_dir()')
        return res_dict
    else:
        makedir_for_file(wav_scp_file_path)
        res_dict = {}
        for wav_path in tqdm(wav_path_list, total=len(wav_path_list)):
            res_dict[get_file_pure_name_from_path(wav_path)] = wav_path
        write_dict_to_scp(res_dict, wav_scp_file_path)
        global_timer.stop_halfway_and_print('结束执行函数：get_scp_for_wav_dir()')
        return None


def get_list_for_wav_dir(wav_dir: str, wav_list_file_path: str = None, suffix: str = '.wav', recursive=False):
    """
    获取指定目录下所有wav文件的列表，可以选择是否递归查找子目录，并可将结果保存到文件中。
    如果wav_list_file_path为None，则直接返回列表。

    :param wav_dir: 包含wav文件的目录路径
    :param wav_list_file_path: 可选参数，如果提供则将wav文件列表保存到该路径的文件中
    :param suffix: 可选参数，wav文件的后缀名，默认为'.wav'
    :param recursive: 可选参数，是否递归查找子目录，默认为False
    :return: wav文件的列表或None（如果结果已保存到文件）
    """
    logging_info('开始执行函数：get_list_for_wav_dir()')
    global_timer.start_halfway()
    if suffix[0] != '.':
        suffix = '.' + suffix
    if recursive:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'**/*{suffix}'), recursive=True)
    else:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'*{suffix}'))
    if wav_list_file_path is None:
        logging_info('存储地址为None，就直接返回list')
        global_timer.stop_halfway_and_print('结束执行函数：get_scp_for_wav_dir()')
        return wav_path_list
    else:
        write_list_to_file(wav_path_list, wav_list_file_path)
        global_timer.stop_halfway_and_print('结束执行函数：get_scp_for_wav_dir()')
        return None

def do_get_list_for_wav_dir(wav_dir: str, wav_list_file_path: str = None, suffix: str = '.wav', recursive=False):
    """
    获取指定目录下所有wav文件的列表，可以选择是否递归查找子目录，并可将结果保存到文件中。
    如果wav_list_file_path为None，则直接返回列表。

    :param wav_dir: 包含wav文件的目录路径
    :param wav_list_file_path: 可选参数，如果提供则将wav文件列表保存到该路径的文件中
    :param suffix: 可选参数，wav文件的后缀名，默认为'.wav'
    :param recursive: 可选参数，是否递归查找子目录，默认为False
    :return: wav文件的列表或None（如果结果已保存到文件）
    """
    return get_list_for_wav_dir(wav_dir, wav_list_file_path, suffix, recursive)
def do_get_scp_for_wav_dir(wav_dir: str, wav_scp_file_path: str = None, suffix: str = '.wav', recursive=False):
    """
    生成wav.scp文件，或者返回包含wav文件路径的字典。
    :param wav_dir: 包含wav文件的目录路径
    :param wav_scp_file_path: 生成的scp文件的存储路径，如果为None，则直接返回包含wav文件路径的字典
    :param suffix: wav文件的后缀，默认为'.wav'
    :param recursive: 是否递归查找子目录中的wav文件，默认为False
    :return: 如果wav_scp_file_path为None，返回包含wav文件路径的字典；否则返回None
    """
    return get_scp_for_wav_dir(wav_dir, wav_scp_file_path, suffix, recursive)


def get_file_path_list_for_wav_dir(wav_dir: str, wav_list_file_path: str = None, suffix: str = '.wav', recursive=False):
    """
    生成wav_path list
    :param wav_dir:
    :param wav_list_file_path:
    :param suffix:
    :param recursive:
    :return:
    """
    logging_info('开始执行函数：get_file_path_list_for_wav_dir()')
    global_timer.start_halfway()
    if suffix[0] != '.':
        suffix = '.' + suffix
    if recursive:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'**/*{suffix}'), recursive=True)
    else:
        wav_path_list = glob.glob(os.path.join(wav_dir, f'*{suffix}'))
    if wav_list_file_path is None:
        logging_info('get_file_path_list_for_wav_dir(): 存储地址为None，就直接返回list')
        global_timer.stop_halfway_and_print('结束执行函数：get_file_path_list_for_wav_dir()')
        return wav_path_list
    else:
        logging_info('get_file_path_list_for_wav_dir(): 存储地址为{}'.format(wav_list_file_path))
        makedir_for_file(wav_list_file_path)
        write_list_to_file(wav_path_list, wav_list_file_path)
    global_timer.stop_halfway_and_print('结束执行函数：get_file_path_list_for_wav_dir()')
    return None
# -------------------------------加载文件路径集合----------------------------------------end













# ----------------------------------文件复制----------------------------------------start
def copy_file(source_path, destination_path, buffer_size=1024 * 6, use_shell=False, visualization=True, is_jump=False):
    assert isinstance(destination_path, str)
    if is_jump:
        if os.path.exists(destination_path):
            if get_file_size(destination_path) == get_file_size(source_path):
                logging_info(f"文件已经存在,跳过复制操作：{destination_path}")
                return
    makedir_for_file(destination_path)
    if use_shell:
        _copy_file_shell(source_path, destination_path)
    else:
        if visualization:
            #  6 * 1024 较佳， 750-800MB/s的传输速度, 但没有shell快，略逊于shell(6*1024)
            _copy_file_visualization(source_path, destination_path, buffer_size)
        else:
            _copy_file_no_visualization(source_path, destination_path)

def _copy_file_shell(source_path, destination_path):
    command_line = f"cp {source_path} {destination_path}"
    os.system(command_line)


def _copy_file_visualization(source_path, destination_path, buffer_size=64):
    buffer_size = buffer_size * 1024
    logging_info(f'正在复制文件...从 {source_path} 到 {destination_path}')
    try:
        """"""
        with open(source_path, 'rb') as source_file, open(destination_path, 'wb') as destination_file:
            # 获取源文件的总大小，用于进度条的设置
            source_size = os.path.getsize(source_path)
            # 创建进度条
            with tqdm(total=source_size, unit='B', unit_scale=True, desc=f"正在复制") as pbar:
                # 流式复制文件内容，同时更新进度条
                while True:
                    # 读取缓冲区大小的内容
                    content = source_file.read(buffer_size)
                    if not content:
                        break
                    # 写入到目标文件
                    destination_file.write(content)
                    # 更新进度条
                    pbar.update(len(content))
        print(f"文件 {source_path} 已成功复制到 {destination_path}")
    except Exception as e:
        print(f"复制文件时发生错误：{e}")


def _copy_file_no_visualization(source_path, destination_path):
    makedir_sil(os.path.dirname(destination_path))
    logging_info(f'正在复制文件...从 {source_path} 到 {destination_path}')
    try:
        with open(source_path, 'rb') as source_file:
            content = source_file.read()

        with open(destination_path, 'wb') as destination_file:
            destination_file.write(content)

        print(f"文件 {source_path} 已成功复制到 {destination_path}")
    except Exception as e:
        print(f"复制文件时发生错误：{e}")


def copy_file2(source_path, target_dir, is_jump=False, is_log=True):
    if is_log:
        logging_info(f"copy_file2：{source_path} {target_dir} {is_jump}")
    makedir_sil(target_dir)
    # 获取源文件的文件名
    file_name = os.path.basename(source_path)
    # 拼接目标文件的完整路径
    destination_file = os.path.join(target_dir, file_name)
    if is_jump:
        if os.path.exists(destination_file):
            if get_file_size(destination_file) == get_file_size(source_path):
                logging_info(f"is_jump=True，{destination_file} 已经存在，跳过复制")
                return destination_file
    # 复制文件到目标目录
    _copy_file_shell(source_path, destination_file)
    # shutil.copy(source_path, destination_file) //有很大问题, 在多线程下不起作用
    return destination_file

def copy_file_to_dir(source_path, destination_dir, is_jump=False, is_log=False):
    copy_file2(source_path, destination_dir, is_jump=is_jump, is_log=is_log)
# -------------------------------文件复制----------------------------------------end

def do_convert_str_to_float_list(str_list: str):
    """
    将字符串转换为float列表
    :param str_list:
    :return:
    """
    import ast
    # 使用ast.literal_eval将字符串转换为Python列表
    list_obj = ast.literal_eval(str_list)
    return list_obj



def do_get_commandline_param(param_num: int, param_description_list: list = None):
    """
    从命令行里得到参数
    :param param_num:
    :param param_description_list:
    :return:
    """
    help_str = "Usage: python the_python_script_file.py"
    if param_description_list is None:
        for i in range(1, param_num + 1):
            help_str = help_str + " " + "param_{}".format(i)
    else:
        assert len(param_description_list) == param_num
        for i in range(1, param_num + 1):
            help_str = help_str + " " + param_description_list[i - 1]
    arg_num = len(sys.argv)
    if arg_num < param_num + 1:
        print(help_str)
        exit(1)
    argv_1 = sys.argv[1]
    if argv_1 == "--help" or argv_1 == "-h":
        print(help_str)
        exit(1)
    param_list = []
    for i in range(1, param_num+1):
        param_list.append(sys.argv[i])
    return param_list





def do_convert_wav_text_scp_to_jsonl(wav_scp_file_path: str,
                                     text_scp_file_path: str,
                                     target_jsonl_file_path: str = None):
    """
    convert wav text scp to jsonl,
    如果target_josnl_file为None， 则直接返回dict_list
    """
    wav_dic = load_dict_from_scp(wav_scp_file_path)
    text_dic = load_dict_from_scp(text_scp_file_path)
    if len(wav_dic) != len(text_dic):
        logging_info("warning: wav_scp文件和text_scp文件长度不一致")
    if target_jsonl_file_path is not None:
        makedir_for_file(target_jsonl_file_path)
        if os.path.exists(target_jsonl_file_path):
            os.remove(target_jsonl_file_path)
        res_dict_list = []
        for k, v in tqdm(wav_dic.items(), desc='do_convert_wav_text_scp_to_jsonl', total=len(wav_dic)):
            if k not in text_dic:
                logging_info('warning: {} not in text_dic'.format(k))
                continue
            text = text_dic[k]
            res_dict_list.append({'key': k, 'wav': v, 'txt': text})
        write_dict_list_to_jsonl(res_dict_list, target_jsonl_file_path)
    else:
        res_list = []
        for k, v in wav_dic.items():
            if k not in text_dic:
                logging_info('warning: {} not in text_dic'.format(k))
                continue
            text = text_dic[k]
            res_list.append({'key': k, 'wav': v, 'txt': text})
        return res_list


def do_convert_wav_text_scp_to_json(wav_scp_file_path: str, text_scp_file_path, target_json_file_path: str):
    """
    convert wav text scp to json
    """
    makedir_for_file(target_json_file_path)
    wav_dic = load_dict_from_scp(wav_scp_file_path)
    text_dic = load_dict_from_scp(text_scp_file_path)
    if len(wav_dic) != len(text_dic):
        logging_info("warning: wav_scp文件和text_scp文件长度不一致")
    os.remove(target_json_file_path)
    res_dic = {}
    for k, v in wav_dic.items():
        if k not in text_dic:
            logging_info('warning: {} not in text_dic'.format(k))
            continue
        text = text_dic[k]
        res_dic[k] = {'wav': v, 'txt': text}
    write_dict_to_json(res_dic, target_json_file_path)







class GxlDownloader_Encrypt:
    encrypted_hash_file_name = 'encrypted_hash.json'
    encrypted_dict = {}

    def __init__(self, root_dir: str):
        """
        使用urllib库对链接进行下载
        :param root_dir:
        """
        makedir_sil(root_dir)
        self.root = root_dir
        self.suffix = 'gxlfile'
        # self.file_lock = threading.Lock()
        if os.path.exists(os.path.join(self.root, self.encrypted_hash_file_name)):
            self.encrypted_dict = load_dict_from_json(os.path.join(self.root, self.encrypted_hash_file_name))

    def __del__(self):
        logging_info(f"Object {self} is being destroyed")
        write_dict_to_json(self.encrypted_dict, os.path.join(self.root, self.encrypted_hash_file_name))

    @classmethod
    def generate_hash(cls, input_file, hash_algorithm='sha256'):
        """
        读取一个文件的数据， 并生成其对应的hash值
        """
        # 读取文件的字节数据
        if isinstance(input_file, str):
            with codecs.open(input_file, 'rb') as file:
                data = file.read()
        else:
            data = input_file
        # 使用指定哈希算法计算哈希值
        hash_function = hashlib.new(hash_algorithm)
        hash_function.update(data)
        hash_value = hash_function.hexdigest()

        return hash_value

    def get_expected_encrypted_for_filename(self, filename):
        """"""
        return self.encrypted_dict.get(filename, None)

    def add_encrypted_hash_item(self, filename: str):
        """"""
        self.encrypted_dict[filename] = self.generate_hash(os.path.join(self.root, filename))

    def set_suffix(self, suffix: str):
        self.suffix = suffix

    def download(self, url: str, suffix: str = None, filename: str = None):
        if filename is None:
            filename = get_clean_filename(os.path.basename(url))
        if suffix is None:
            suffix = self.suffix
        filename = filename + "." + suffix
        logging_info(f'开始下载:{filename},url:{url}')
        download_target = os.path.join(self.root, filename)
        expected_sha256 = self.get_expected_encrypted_for_filename(filename)
        if os.path.exists(download_target) and os.path.isfile(download_target):
            if self.generate_hash(download_target) == expected_sha256:
                logging_info('文件已经存在')
                return download_target
            else:
                warnings.warn(
                    f"{download_target} exists, but the SHA256 checksum does not match; re-downloading the file"
                )

        with urllib.request.urlopen(url) as source, codecs.open(download_target, "wb") as output:
            with tqdm(
                    total=int(source.info().get("Content-Length", -1)),
                    ncols=80,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
            ) as loop:
                while True:
                    buffer = source.read(8192)
                    if not buffer:
                        break
                    output.write(buffer)
                    loop.update(len(buffer))
        self.add_encrypted_hash_item(filename)
        logging_info(f'下载完成:{filename},url:{url}')
        return download_target


class GxlDownloader:
    def __init__(self, root_dir: str = None):
        """
        使用urllib库对链接进行下载
        :param root_dir:
        """
        if root_dir is None:
            root_dir = './output/'
        makedir_sil(root_dir)
        self.root = root_dir
        self.suffix = 'wav'

    def set_suffix(self, suffix: str):
        self.suffix = suffix

    def download(self, url: str, target_dir: str = None, filename: str = None, suffix: str = None, ):
        if filename is None:
            filename = get_clean_filename(os.path.basename(url))
        if suffix is None:
            suffix = self.suffix
        if target_dir is None:
            target_dir = self.root
        if suffix.startswith('.'):
            suffix = suffix[1:]
        filename = filename + "." + suffix
        makedir_sil(target_dir)
        logging_info(f'开始下载:{filename},url:{url}')
        download_target = os.path.join(target_dir, filename)
        if os.path.exists(download_target) and os.path.isfile(download_target):
            warnings.warn(
                f"{download_target} exists, don't download again"
            )
            return

        with urllib.request.urlopen(url) as source, codecs.open(download_target, "wb") as output:
            with tqdm(
                    total=int(source.info().get("Content-Length", -1)),
                    ncols=80,
                    unit="iB",
                    unit_scale=True,
                    unit_divisor=1024,
            ) as loop:
                while True:
                    buffer = source.read(8192)
                    if not buffer:
                        break
                    output.write(buffer)
                    loop.update(len(buffer))
        logging_info(f'下载完成:{filename},url:{url}')
        return download_target


def download_file(url: str, target_dir: str = None, filename: str = None, suffix: str = None, ):
    if filename is None:
        filename = get_clean_filename(os.path.basename(url))
    if suffix is None:
        suffix = 'wav'
    if target_dir is None:
        target_dir = './output/'
    makedir_sil(target_dir)
    if suffix.startswith('.'):
        suffix = suffix[1:]
    filename = filename + "." + suffix
    download_target = os.path.join(target_dir, filename)
    logging_info(f'开始下载: {filename} , url: {url} , target: {download_target}')
    if os.path.exists(download_target) and os.path.isfile(download_target):
        logging.debug(
            f"{download_target} exists, don't download again"
        )
        return

    with urllib.request.urlopen(url) as source, codecs.open(download_target, "wb") as output:
        with tqdm(
                total=int(source.info().get("Content-Length", -1)),
                ncols=80,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
        ) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break
                output.write(buffer)
                loop.update(len(buffer))
    logging_info(f'下载完成:{filename},url:{url},target:{download_target}')
    return download_target


def download_file_by_request(url: str, target_dir: str = None, filename: str = None, suffix: str = None, ):
    import requests
    if filename is None:
        filename = get_clean_filename(os.path.basename(url))
    if suffix is None:
        suffix = 'wav'
    if target_dir is None:
        target_dir = './output/'
    makedir_sil(target_dir)
    if suffix.startswith('.'):
        suffix = suffix[1:]
    filename = filename + "." + suffix
    download_target = os.path.join(target_dir, filename)
    logging_info(f'开始下载: {filename} , url: {url} , target: {download_target}')
    if os.path.exists(download_target) and os.path.isfile(download_target):
        logging.debug(
            f"{download_target} exists, don't download again"
        )
        return

    response = requests.get(url, stream=True)
    # 获取文件大小
    total_size = int(response.headers.get('content-length', 0))
    chunk_size = 128
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
    with open(download_target, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            progress_bar.update(len(chunk))




def do_split_dict(original_dict, num_subsets):
    """
    将字典尽量平均地切成 num_subsets 份，前 r 份多 1 个键。
    返回一个由子字典组成的列表。
    """
    if num_subsets <= 0:
        raise ValueError("num_subsets must be positive")

    n = len(original_dict)
    q, r = divmod(n, num_subsets)   # q: 基础块大小；r: 需要+1的块数

    keys = list(original_dict.keys())  # 保持插入顺序
    subsets = []
    start = 0
    for i in range(num_subsets):
        size = q + (1 if i < r else 0)
        end = start + size
        subset_keys = keys[start:end]
        subset_dict = {k: original_dict[k] for k in subset_keys}
        subsets.append(subset_dict)
        start = end
    return subsets



def do_merge_scp(input_dir, output_scp_file):
    """

    :param input_dir:
    :param output_scp_file:
    :return:
    """
    little_scp_list = glob.glob(os.path.join(input_dir, '*.scp'))
    res_dict = {}
    for little_scp_path in little_scp_list:
        little_dict = load_dict_from_scp(little_scp_path)
        res_dict.update(little_dict)
    write_dict_to_scp(res_dict, output_scp_file)


def normal_path(path: str):
    return path.replace('\\', '/')


def load_dict_from_yaml(file_path: str):
    with open(file_path, 'rt', encoding='utf-8') as f:
        dict_1 = yaml.load(f, Loader=yaml.FullLoader)
    return dict_1


def write_dict_to_yaml(dic: dict, file_path: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(dic, f, default_flow_style=False, allow_unicode=True)


def do_dict2simpleNamespaceObj(dict_obj: dict):
    """
    将一个字典转换为命名空间对象,
    命名空间对象可以修改key对应的value值
    可以通过.的方式调用键值对用的value值,如果调用没设置的键值,则直接报错,
    :param dict_obj:
    :return:
    """
    return types.SimpleNamespace(**dict_obj)


def do_add_dir_to_path(dir_path: str):
    sys.path.append(dir_path)


def set_seed(seed):
    # 设置Python随机数生成器的种子
    random.seed(seed)

    # 设置NumPy的随机数生成器的种子
    np.random.seed(seed)

    # 设置PyTorch的随机数生成器的种子
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # 以下是为了确保CuDNN在训练过程中的确定性，但可能会影响性能
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def convert_namespaceObj_to_dict(obj):
    return vars(obj)


class AslpDataset:
    def __init__(self):
        self.save_path = join_path(os.path.expanduser("~"), ".aslp", "aslp_dataset.json")
        self.scp_root_dir = '/home/work_nfs5_ssd/hfxue/data/data4w/source_1'
        self.raw_list_dir = '/home/work_nfs6/xlgeng/data/asr_data_shard_list'
        self.shard_list_dir = '/home/work_nfs6/xlgeng/data/asr_data_raw_list'
        self.key_dict = {}
        self.index_dict = {}
        makedir_for_file_or_dir(self.save_path)
        if not os.path.exists(self.save_path):
            all_key = os.listdir(self.scp_root_dir)
            for i, key in enumerate(all_key):
                the_key = key.lower()
                self.key_dict[the_key] = dict(
                    wav_scp=os.path.join(self.scp_root_dir, key, 'wav.scp'),
                    text=os.path.join(self.scp_root_dir, key, 'text'),
                    shard_list=os.path.join(self.shard_list_dir, key, "shard_list.txt"),
                    datyamla_list=os.path.join(self.raw_list_dir, key, "data.list"),
                )
            write_dict_to_json(self.key_dict, self.save_path)
        else:
            self.key_dict = load_dict_from_json(self.save_path)
        for i, key in enumerate(self.key_dict.keys()):
            the_key = key.lower()
            self.index_dict[the_key] = i

    def print_all_keys(self):
        """
        打印出所有数据集的名称。
        :return:
        """
        print_dict(self.index_dict)
        logging_info('该函数打印出了所有数据集的名称和其对应的id。')
        logging_info('使用get_path_info_by_key_or_id（）函数和key或id可获取对应的路径信息，以字典形式返回。')

    def print_all_data(self):
        print_dict(self.key_dict)

    def get_path_info_by_key_or_id(self, key):
        key = key if isinstance(key, str) else self.index_dict.get(key, "未找到对应的key")
        info = self.key_dict.get(key, "未找到对应的key")
        if info == "未找到对应的key":
            logging_info(f"未找到对应的key:{key}")
            return None
        return info

    def download_file(self, output_dir: str):
        makedir_sil(output_dir)
        output_path = join_path(output_dir, "aslp_dataset.json")
        copy_file(self.save_path, output_path)

    def search(self, keyword: str):
        right_dict = {}
        keyword = keyword.lower()
        for key, i in self.index_dict.items():
            if keyword in key:
                right_dict[key] = i
        print_dict(right_dict)




def do_change_file_suffix(file_path, suffix):
    """
    将一个文件的后缀名替换为另一个后缀名
    :param file_path:
    :param suffix:
    :return:
    """
    str_1 = file_path.split('.')[:-1]
    return '.'.join(str_1) + '.' + suffix


def print_model_size(model):
    """
    打印模型的大小， 单位为M（1024*1024）
    :param model:
    :return:
    """
    num_params = sum(p.numel() for p in model.parameters())
    logging_info('the number of model params: {:,f}M'.format(num_params / 1024 / 1024))
    #  打印有梯度的参数
    num_grad_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logging_info('the number of model grad params: {:,f}M'.format(num_grad_params / 1024 / 1024))
    # 打印没有梯度的参数
    num_no_grad_params = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    logging_info('the number of model no grad params: {:,f}M'.format(num_no_grad_params / 1024 / 1024))


def do_set_cuda_env(gpu_ids: str = '0,1,2,3'):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_ids


def do_get_scp_from_mono_wav_txt(wav_dir: str, output_dir=None):
    """
    处理场景:
    一个目录中零散分布着wav文件和针对单个wav文件的txt文件
    :param wav_dir:
    :return:
    """
    logging_info("开始处理,处理场景:一个目录中零散分布着wav文件和针对单个wav文件的txt文件")
    wav_path_list = glob.glob(f'{wav_dir}/**/*.wav', recursive=True)
    txt_path_list = glob.glob(f'{wav_dir}/**/*.txt', recursive=True)
    wav_dict = {}
    txt_dict = {}
    for wav_path in wav_path_list:
        key = os.path.basename(wav_path).split('.')[0]
        wav_dict[key] = wav_path
    for txt_path in txt_path_list:
        key = os.path.basename(txt_path).split('.')[0]
        txt_dict[key] = txt_path
    if output_dir is not None:
        makedir_sil(output_dir)
        write_dict_to_scp(wav_dict, os.path.join(output_dir, 'wav.scp'))
        write_dict_to_scp(txt_dict, os.path.join(output_dir, 'text'))
        return
    return wav_dict, txt_dict


def write_to_tar_file(data_list: list[tuple], tar_file_path: str, resample=16000, i=-1):
    """
    将数据写入tar文件，
    data_list: item: (key, text.txt, wav_path)
    """
    import torchaudio
    print(f'开始处理第{i}个shard')
    AUDIO_FORMAT_SETS = {'flac', 'mp3', 'm4a', 'ogg', 'opus', 'wav', 'wma'}
    makedir_for_file(tar_file_path)
    finished_path = do_change_file_suffix(tar_file_path, 'finished')
    with tarfile.open(tar_file_path, "w") as tar:
        for item in tqdm(data_list, total=len(data_list), desc=f"shard_{i}"):
            key, txt, wav = item
            suffix = wav.split('.')[-1]
            assert suffix in AUDIO_FORMAT_SETS, f"不支持的音频格式{suffix},仅支持{AUDIO_FORMAT_SETS}"
            # read & resample
            audio, sample_rate = torchaudio.load(wav, normalize=False)
            if sample_rate != resample:
                audio = torchaudio.transforms.Resample(
                    sample_rate, resample)(audio.float())
                audio = audio.to(torch.int16)
            # change format to wav
            f = io.BytesIO()
            torchaudio.save(f, audio, resample, format="wav", bits_per_sample=16)
            suffix = "wav"
            f.seek(0)
            data = f.read()
            assert isinstance(txt, str), f"txt必须是str类型"
            txt_file_name = key + '.txt'
            txt = txt.encode('utf8')
            txt_data = io.BytesIO(txt)
            txt_info = tarfile.TarInfo(txt_file_name)
            txt_info.size = len(txt)
            tar.addfile(txt_info, txt_data)

            wav_file = key + '.' + suffix
            wav_data = io.BytesIO(data)
            wav_info = tarfile.TarInfo(wav_file)
            wav_info.size = len(data)
            tar.addfile(wav_info, wav_data)
    print(f'第{i}个shard处理完成')
    with open(finished_path, 'w') as f:
        pass


def write_wtn_to_tar_file(data_list: list[tuple], tar_file_path: str, resample=16000, i=-1):
    """
    将数据写入tar文件，
    data_list: item: (key, text.txt, wav_path, npy_path)
    """
    import torchaudio
    print(f'开始处理第{i}个shard')
    AUDIO_FORMAT_SETS = {'flac', 'mp3', 'm4a', 'ogg', 'opus', 'wav', 'wma'}
    makedir_for_file(tar_file_path)
    finished_path = do_change_file_suffix(tar_file_path, 'finished')
    with tarfile.open(tar_file_path, "w") as tar:
        for item in tqdm(data_list, total=len(data_list), desc=f"shard_{i}"):
            key, txt, wav, npy = item
            suffix = wav.split('.')[-1]
            assert suffix in AUDIO_FORMAT_SETS, f"不支持的音频格式{suffix},仅支持{AUDIO_FORMAT_SETS}"
            # read & resample
            audio, sample_rate = torchaudio.load(wav, normalize=False)
            if sample_rate != resample:
                audio = torchaudio.transforms.Resample(
                    sample_rate, resample)(audio.float())
                audio = audio.to(torch.int16)
            # change format to wav
            f = io.BytesIO()
            torchaudio.save(f, audio, resample, format="wav", bits_per_sample=16)
            suffix = "wav"
            f.seek(0)
            data = f.read()

            assert isinstance(txt, str), f"txt必须是str类型"
            txt_file_name = key + '.txt'
            txt = txt.encode('utf8')
            txt_data = io.BytesIO(txt)
            txt_info = tarfile.TarInfo(txt_file_name)
            txt_info.size = len(txt)
            tar.addfile(txt_info, txt_data)

            wav_file = key + '.' + suffix
            wav_data = io.BytesIO(data)
            wav_info = tarfile.TarInfo(wav_file)
            wav_info.size = len(data)
            tar.addfile(wav_info, wav_data)
            tar.add(npy, arcname=key + '.npy')
    print(f'第{i}个shard处理完成')
    with open(finished_path, 'w') as f:
        pass


def do_make_shard_file4wtn(jsonl_path, output_dir: str, num_utt_per_shard: int = 1000,
                           num_threads=32, prefix_for_tar_file: str = "shard", resample: int = 16000,
                           ):
    """
    得到一个shard文件组成的目录, logger must is not None
    """
    logging_info('开始打shard for ' + prefix_for_tar_file)
    logging_info(f'prefix_for_tar_file: {prefix_for_tar_file}')
    logging_info(f'jsonl_path: {jsonl_path}')
    logging_info(f'output_dir: {output_dir}')
    logging_info(f'num_utt_per_shard: {num_utt_per_shard}')
    logging_info(f'num_threads: {num_threads}')
    logging_info(f'resample: {resample}')
    data = []
    dict_list = load_dict_list_from_jsonl(jsonl_path)
    for dict_i in dict_list:
        key = dict_i['key']
        wav = dict_i['wav']
        txt = dict_i['txt']
        npy = dict_i['npy']
        data.append((key, txt, wav, npy))
    logging_info(f"共有{len(data)}个utt")
    chunks = [data[i:i + num_utt_per_shard] for i in range(0, len(data), num_utt_per_shard)]
    os.makedirs(output_dir, exist_ok=True)
    logging_info(f"共有{len(chunks)}个shard")
    # Using thread pool to speedup
    pool = multiprocessing.Pool(processes=num_threads)
    shards_list = []
    for i, chunk in enumerate(chunks):
        tar_file_path = os.path.join(output_dir,
                                     '{}_{:09d}.tar'.format(prefix_for_tar_file, i))
        shards_list.append(tar_file_path)
        finished_file_path = do_change_file_suffix(tar_file_path, 'finished')
        if os.path.exists(finished_file_path):
            continue
        pool.apply_async(
            write_to_tar_file,
            (chunk, tar_file_path, resample, i))

    pool.close()
    pool.join()
    logging_info('打shard结束, 保存shard列表')
    with open(os.path.join(output_dir, 'shards_list.txt'), 'w', encoding='utf8') as fout:
        for name in shards_list:
            fout.write(name + '\n')
    logging_info('打shard完全结束')
    # copy_file(wav_scp_file_path, os.path.join(output_dir, 'wav.scp'))
    # copy_file(text_scp_file_path, os.path.join(output_dir, 'text'))
    copy_file(jsonl_path, os.path.join(output_dir, 'data.list'))


def do_make_shard_file(wav_scp_file_path: str, text_scp_file_path: str, output_dir: str, num_utt_per_shard: int = 1000,
                       num_threads=32, prefix_for_tar_file: str = "shard", resample: int = 16000,
                       ):
    """
    得到一个shard文件组成的目录, logger must is not None
    """
    logging_info('开始打shard for ' + prefix_for_tar_file)
    logging_info('wav_scp: ' + wav_scp_file_path)
    logging_info('text_scp: ' + text_scp_file_path)
    wav_dic = load_dict_from_scp(wav_scp_file_path)
    data = []
    text_dic = load_dict_from_scp(text_scp_file_path)
    for k, text in text_dic.items():
        if k not in wav_dic:
            logging_info(f"warning: {k}不在wav_scp文件中")
            continue
        data.append((k, text, wav_dic[k]))
    logging_info(f"共有{len(data)}个utt")
    chunks = [data[i:i + num_utt_per_shard] for i in range(0, len(data), num_utt_per_shard)]
    os.makedirs(output_dir, exist_ok=True)
    logging_info(f"共有{len(chunks)}个shard")
    # Using thread pool to speedup
    pool = multiprocessing.Pool(processes=num_threads)
    shards_list = []
    for i, chunk in enumerate(chunks):
        tar_file_path = os.path.join(output_dir,
                                     '{}_{:09d}.tar'.format(prefix_for_tar_file, i))
        shards_list.append(tar_file_path)
        finished_file_path = do_change_file_suffix(tar_file_path, 'finished')
        if os.path.exists(finished_file_path):
            continue
        pool.apply_async(
            write_to_tar_file,
            (chunk, tar_file_path, resample, i))

    pool.close()
    pool.join()
    logging_info('打shard结束, 保存shard列表')
    with open(os.path.join(output_dir, 'shards_list.txt'), 'w', encoding='utf8') as fout:
        for name in shards_list:
            fout.write(name + '\n')
    logging_info('打shard完全结束')
    copy_file(wav_scp_file_path, os.path.join(output_dir, 'wav.scp'))
    copy_file(text_scp_file_path, os.path.join(output_dir, 'text'))


def get_random_subdict(source_dict: dict, num_value: int):
    keys = list(source_dict.keys())
    random.shuffle(keys)
    return {key: source_dict[key] for key in keys[:num_value]}


def do_get_random_subdict(source_dict: dict, num_value: int):
    keys = list(source_dict.keys())
    random.shuffle(keys)
    return {key: source_dict[key] for key in keys[:num_value]}


def get_subdict(source_dict: dict, start_i, end_i):
    return {key: source_dict[key] for key in list(source_dict.keys())[start_i:end_i]}


def do_convert_jsonl_to_wav_text_scp(jsonl_path, scp_path=None, text_path=None):
    """
    将jsonl文件转换为wav和text的scp文件
    :param jsonl_path:
    :param scp_path:
    :param text_path:
    :return:
    """

    dict_list = load_dict_list_from_jsonl(jsonl_path)
    wav_dict = {}
    text_dict = {}
    for item in dict_list:
        wav_dict[item['key']] = item['wav']
        text_dict[item['key']] = item['txt']
    if scp_path is not None:
        write_dict_to_scp(wav_dict, scp_path)
    if text_path is not None:
        write_dict_to_scp(text_dict, text_path)
    return wav_dict, text_dict

def do_split_list(source_list, num_subsets):
    """
    将列表按顺序尽量平均地切成 num_subsets 份。
    各子集大小之差 <= 1，前 r 个子集比后面的多 1 个元素。
    """
    if num_subsets <= 0:
        raise ValueError("num_subsets must be positive")

    n = len(source_list)
    q, r = divmod(n, num_subsets)  # q: 基础块大小；r: 前 r 块各多 1 个

    subsets = []
    start = 0
    for i in range(num_subsets):
        size = q + (1 if i < r else 0)
        end = start + size
        subsets.append(source_list[start:end])
        start = end
    return subsets


def do_extract_audio_segment(input_path, output_path, start_sample, end_sample):
    # logging_info(
    #     f'do_extract_audio_segment():开始截取{input_path}，从{start_sample}到{end_sample},输出到:{output_path}')
    with wave.open(input_path, 'rb') as input_wave:
        # 获取音频参数
        params = input_wave.getparams()
        output_params = (params[0], params[1], params[2], params[3], params[4], params[5])
        # 设置输出音频参数
        output_params = (params[0], params[1], params[2], end_sample - start_sample, params[4], params[5])
        # 打开输出音频文件
        with wave.open(output_path, 'wb') as output_wave:
            output_wave.setparams(output_params)
            # 移动到指定的开始采样点
            input_wave.setpos(start_sample)
            # 读取指定范围的采样点数据
            data = input_wave.readframes(end_sample - start_sample)
            # 写入输出文件
            output_wave.writeframes(data)
def do_get_sample_rate(input_wav_path):

    with wave.open(input_wav_path, 'rb') as audio_file:
        sample_rate = audio_file.getframerate()
    return int(sample_rate)


def do_decompression_tar(tar_path, output_dir):
    """
    解压tar,到指定目录
    :param tar_path:
    :param output_dir:
    :return:
    """
    with tarfile.open(tar_path, 'r') as tar:
        tar.extractall(output_dir)


def do_clean_wav(input_file_path, output_file_path):
    """
    使用ffmpeg工具,
    将音频整理成标准格式， 16K采样， 单通道，补齐音频头
    :param input_file_path:
    :param output_file_path:
    :return:
    """
    os.system(f"ffmpeg -i '{input_file_path}' -ac 1 -ar 16000 -vn {output_file_path}")


def is_windows_system():
    if sys.platform.startswith('win'):
        return True
    else:
        return False


def is_linux_system():
    if sys.platform.startswith('linux'):
        return True
    else:
        return False


def do_remove_punctuation(text):
    """使用正则表达式去除标点符号，只保留汉字、英文和数字"""
    # 使用正则表达式去除标点符号，只保留汉字、英文和数字
    return re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)


def do_filter(text, only_zn=False, only_en=False, only_num=False):
    """使用正则表达式去除标点符号，只保留汉字、英文和数字"""
    if only_zn:
        return re.sub(r'[\u4e00-\u9fa5]', '', text)
    if only_en:
        return re.sub(r'[a-zA-Z]', '', text)
    if only_num:
        return re.sub(r'[0-9]', '', text)
    return re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text)


def do_convert_text2chars_dict(text_scp_path, dict_file_path, blank_sym='<blank>'):
    """
    仅仅为中文服务
    :param text_scp_path:
    :param dict_file_path:
    :return:
    """
    logging_info(f'开始遍历{text_scp_path}中的所有句子，提取chars_dictionary')
    makedir_for_file(dict_file_path)
    text_dict = load_dict_from_scp(text_scp_path)
    chars_set = set()
    for value in tqdm(text_dict.values(), total=len(text_dict), desc='提取chars_dictionary'):
        for char_i in value:
            chars_set.add(char_i)
    with codecs.open(dict_file_path, 'w', encoding='utf-8') as f:
        f.write(f'{blank_sym} 0\n')
        f.write('<unk> 1\n')
        f.write('<sos> 2\n')
        f.write('<eos> 2\n')
        for i, char in enumerate(sorted(chars_set)):
            f.write(f'{char} {i + 3}\n')


def get_sample_count(audio_file_path: str):
    """
    得到路径所指音频的采样点数
    output->
    sample_count: 采样点数
    sample_rate: 采样率
    """
    return _get_sample_count_wave(audio_file_path)


def _get_sample_count_wave(file_path):
    """比较快"""
    with wave.open(file_path, 'rb') as audio_file:
        sample_count = audio_file.getnframes()
        sample_rate = audio_file.getframerate()
    return sample_count, sample_rate


def _get_sample_count_torchaudio(file_path):
    """比较慢"""
    import torchaudio
    waveform, sr = torchaudio.load(file_path)
    return len(waveform[0]), sr

def do_get_sample_count(audio_file_path: str):
    """
    得到路径所指音频的采样点数
    output->
    sample_count: 采样点数
    sample_rate: 采样率
    """
    return get_sample_count(audio_file_path)

def do_get_wav_duration(audio_file_path: str):
    cout, rate = get_sample_count(audio_file_path)
    return cout / rate

def get_tsv_from_wav_scp(wav_scp_path, output_tsv_path, num_thread=32):
    """"""
    print_str = "dict,不予展示"
    logging_info(
        f"get_tsv_from_wav_scp:开始处理如下wav_scp: {wav_scp_path if isinstance(wav_scp_path, str) else print_str}, tsv_path: {output_tsv_path}")
    makedir_sil(output_tsv_path)
    if isinstance(wav_scp_path, str):
        wav_dict = load_dict_from_scp(wav_scp_path)
    elif isinstance(wav_scp_path, dict):
        wav_dict = wav_scp_path
    else:
        raise ValueError("get_tsv_from_wav_scp: wav_scp_path must be str or dict")
    res_list = ["/"]
    wav_list = list(wav_dict.values())
    list_list = do_split_list(wav_list, num_thread)
    runner = GxlDynamicThreadPool()
    for list_i in list_list:
        """"""
        runner.add_task(little_fun4get_tsv_from_wav_scp, [res_list, list_i])
    runner.start()
    write_list_to_file(res_list, "./all_data_with_sample.tsv")


def little_fun4get_tsv_from_wav_scp(res_list, wav_path_list):
    temp_list = []
    for wav_path in tqdm(wav_path_list, total=len(wav_path_list)):
        """"""
        from gxl_ai_utils.utils.utils_data import get_sample_count
        samples, _ = get_sample_count(wav_path)
        temp_list.append(f"{wav_path}\t{samples}")
    res_list.extend(temp_list)




def do_compress_file_by_gzip(input_file, output_file=None):
    if output_file is None:
        output_file = input_file + '.gz'

    logging_info(f'开始使用gzip压缩文件：{input_file},压缩到:{output_file}')
    with open(input_file, 'rb') as f_in:
        with gzip.open(output_file, 'wb') as f_out:
            f_out.writelines(f_in)
    logging_info(f'完成使用gzip压缩文件：{input_file},压缩到:{output_file}')


def do_merge_file(*input_file_list):
    """
    最后一个参数为输出
    :param input_file_list:
    :return:
    """
    if len(input_file_list) == 1:
        logging_info('只有一个文件，直接返回')
        return input_file_list[0]
    if len(input_file_list) == 0:
        logging_info('没有文件，直接返回')
        return None
    output_file = input_file_list[-1]
    input_file_list = input_file_list[:-1]
    logging_info(f'开始合并文件：{input_file_list},输出到：{output_file}')
    with open(output_file, 'wb') as f_out:
        for input_file in input_file_list:
            with open(input_file, 'rb') as f_in:
                f_out.writelines(f_in)
    logging_info(f'完成合并文件：{input_file_list},输出到：{output_file}')


def do_get_random_sublist(input_list, num):
    """"""
    if num >= len(input_list):
        return input_list
    return [input_list[i] for i in sorted(random.sample(range(len(input_list)), num))]


def _do_compute_fbank4icefall(
        num_mel_bins: int = 80,
        perturb_speed: bool = False,
        whisper_fbank: bool = False,
        fbank_dir: str = "data/fbank",
        manifests_dir: str = "data/manifests",
        prefix: str = "gxldata",
        partition: str = "train",  # train dev test
        num_jobs: int = 8,
):
    """
    需要设置pytorch单进程。
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    :param num_mel_bins:
    :param perturb_speed:
    :param whisper_fbank:
    :param fbank_dir:
    :param manifests_dir:
    :param prefix:
    :param partition:
    :return:
    """
    try:
        from lhotse import (
            CutSet,
            Fbank,
            FbankConfig,
            LilcomChunkyWriter,
            WhisperFbank,
            WhisperFbankConfig,
        )
        from lhotse.recipes.utils import read_manifests_if_cached
        from icefall.utils import get_executor, str2bool
    except ImportError:
        pass

    # torch.set_num_threads(1)
    # torch.set_num_interop_threads(1)
    makedir_sil(fbank_dir)
    src_dir = Path(manifests_dir)
    output_dir = Path(fbank_dir)
    num_jobs = min(num_jobs, os.cpu_count())
    dataset_parts = (
        f"{partition}",
    )
    prefix = prefix
    suffix = "jsonl.gz"
    manifests = read_manifests_if_cached(
        dataset_parts=dataset_parts,
        output_dir=src_dir,
        prefix=prefix,
        suffix=suffix,
    )
    assert manifests is not None

    assert len(manifests) == len(dataset_parts), (
        len(manifests),
        len(dataset_parts),
        list(manifests.keys()),
        dataset_parts,
    )
    if whisper_fbank:
        extractor = WhisperFbank(
            WhisperFbankConfig(num_filters=num_mel_bins, device="cuda")
        )
    else:
        extractor = Fbank(FbankConfig(num_mel_bins=num_mel_bins))
    with get_executor() as ex:  # Initialize the executor only once.
        for partition, m in manifests.items():
            if (output_dir / f"{prefix}_cuts_{partition}.{suffix}").is_file():
                logging.info(f"{partition} already exists - skipping.")
                continue
            logging.info(f"Processing {partition}")
            cut_set = CutSet.from_manifests(
                recordings=m["recordings"],
                supervisions=m["supervisions"],
            )
            if "train" in partition and perturb_speed:
                logging.info("Doing speed perturb")
                cut_set = (
                        cut_set + cut_set.perturb_speed(0.9) + cut_set.perturb_speed(1.1)
                )
            cut_set = cut_set.compute_and_store_features(
                extractor=extractor,
                storage_path=f"{output_dir}/{prefix}_feats_{partition}",
                # when an executor is specified, make more partitions
                num_jobs=num_jobs if ex is None else 80,
                executor=ex,
                storage_type=LilcomChunkyWriter,
            )
            cut_set.to_file(output_dir / f"{prefix}_cuts_{partition}.{suffix}")
            do_extract_gz(output_dir / f"{prefix}_cuts_{partition}.{suffix}", output_dir)



def _do_convert_scp_to_manifest4icefall(wav_scp_path, text_scp_path, wav_manifest_path, text_manifest_path,
                                        num_thread=8):
    def build_wav_dict_for_icefall(key, input_wav_path):
        sample_num, sample_rate = get_sample_count(input_wav_path)
        # file_name = get_file_pure_name_from_path(input_wav_path)
        duration = sample_num / sample_rate
        res_dict = {}
        res_dict['id'] = key
        res_dict['sources'] = [dict(
            type='file',
            channels=[0],
            source=input_wav_path,
        )]
        res_dict['sampling_rate'] = sample_rate
        res_dict['num_samples'] = sample_num
        res_dict['duration'] = duration
        res_dict['channel_ids'] = [0]
        return res_dict

    def build_text_dict_for_icefall(key, input_text_str, duration_dict):
        if key not in duration_dict:
            # logging_info('key not in duration dict,也就是text中有的key wav.scp没有: ' + key)
            return {}
        res_dict = {}
        res_dict['id'] = key
        res_dict['recording_id'] = key
        res_dict['start'] = 0.0
        res_dict['duration'] = duration_dict[key]
        res_dict['channel'] = 0
        res_dict['text'] = input_text_str
        res_dict['language'] = 'Chinese'
        res_dict['speaker'] = 'S0901'
        return res_dict

    def little_func4wav_convert(res_list, wav_dict):
        temp_list = []
        for key, wav_path in tqdm(wav_dict.items(), total=len(wav_dict)):
            temp_list.append(build_wav_dict_for_icefall(key, wav_path))
        res_list.extend(temp_list)

    def little_func4text_convert(res_list, wav_dict, duration_dict):
        temp_list = []
        for key, wav_path in tqdm(wav_dict.items(), total=len(wav_dict)):
            temp_dict = build_text_dict_for_icefall(key, wav_path, duration_dict)
            if len(temp_dict) > 0:
                temp_list.append(temp_dict)
        res_list.extend(temp_list)

    logging_info('开始 do_convert_scp_to_manifest4icefall')
    makedir_for_file(wav_manifest_path)
    makedir_for_file(text_manifest_path)
    if os.path.exists(wav_manifest_path) and os.path.exists(text_manifest_path):
        logging_info(f'{wav_manifest_path}and{text_manifest_path}文件已经存在，直接返回')
        return
    else:
        logging_info(f'{wav_manifest_path}and{text_manifest_path}文件不存在，开始生成')
    wav_dict = load_dict_from_scp(wav_scp_path)
    text_dict = load_dict_from_scp(text_scp_path)
    new_wav_dict = {}
    new_text_dict = {}
    for key, wav_path in wav_dict.items():
        if key not in text_dict:
            continue
        if len(text_dict[key]) < 2:
            continue
        new_wav_dict[key] = wav_path
        new_text_dict[key] = text_dict[key]
    logging_info('do_convert_scp_to_manifest():filter前wav_dict和text_dict的数量: ' + str(len(wav_dict)) + ' ' + str(
        len(text_dict)))
    wav_dict = new_wav_dict
    text_dict = new_text_dict
    logging_info('do_convert_scp_to_manifest():filter后wav_dict和text_dict的数量: ' + str(len(wav_dict)) + ' ' + str(
        len(text_dict)))



    res_wav_dict_list = []
    runner = GxlDynamicThreadPool()
    wav_dict_list = do_split_dict(wav_dict, num_thread)
    for wav_dict_i in wav_dict_list:
        runner.add_task(little_func4wav_convert, [res_wav_dict_list, wav_dict_i])
    logging_info('do_convert_scp_to_manifest():开始执行为wav生成manifest')
    runner.start()
    write_dict_list_to_jsonl(res_wav_dict_list, wav_manifest_path)
    wav_manifest_path_gz = wav_manifest_path + '.gz'
    do_compress_file_by_gzip(wav_manifest_path, wav_manifest_path_gz)
    # res_wav_dict_list = load_dict_list_from_jsonl(wav_manifest_path)

    # 得到duration信息的字典
    logging_info('do_convert_scp_to_manifest():开始生成duration字典')
    duration_dict = {}
    for dict_i in tqdm(res_wav_dict_list, total=len(res_wav_dict_list)):
        id = dict_i['id']
        duration = dict_i['duration']
        duration_dict[id] = duration
    logging_info('do_convert_scp_to_manifest():生成duration字典完成')

    res_text_dict_list = []
    text_dict = load_dict_from_scp(text_scp_path)
    runner = GxlDynamicThreadPool()
    text_dict_list = do_split_dict(text_dict, 32)
    for text_dict_i in text_dict_list:
        runner.add_task(little_func4text_convert, [res_text_dict_list, text_dict_i, duration_dict])
    logging_info('do_convert_scp_to_manifest():开始执行为text生成manifest')
    runner.start()
    write_dict_list_to_jsonl(res_text_dict_list, text_manifest_path)
    text_manifest_path_gz = text_manifest_path + '.gz'
    do_compress_file_by_gzip(text_manifest_path, text_manifest_path_gz)


def get_jsonl_filename4icefall(prefix: str = 'gxldata', partition: str = 'train'):
    return f'{prefix}_recordings_{partition}.jsonl', f'{prefix}_supervisions_{partition}.jsonl'


def do_make_data4icefall(wav_scp_path,
                         text_scp_path,
                         manifest_dir=None,
                         fbank_dir=None,
                         parent_dir=None,
                         partition: str = 'train',
                         prefix: str = 'gxldata',
                         only_manifest: bool = False,
                         only_fbank: bool = False,
                         num_thread_manifest=1):
    """

    :param wav_scp_path:
    :param text_scp_path:
    :param manifest_dir:
    :param fbank_dir:
    :param parent_dir: 如果设置了parent_dir,则manifest_dir 和 fbank_dir无效, 使用parent_dir和默认的目录名
    :param partition:
    :param prefix:
    :return:
    """
    logging_info('开始处理{}的数据'.format(partition))
    if parent_dir is not None:
        manifest_dir = os.path.join(parent_dir, 'manifest')
        fbank_dir = os.path.join(parent_dir, 'fbank')
    makedir_sil(manifest_dir)
    makedir_sil(fbank_dir)
    if not only_fbank:
        logging_info('首先得到manifest,文件为.jsonl.gz')
        manifest_wav_filename, manifest_text_filename = get_jsonl_filename4icefall(prefix, partition)
        manifest_wav_path = os.path.join(manifest_dir, manifest_wav_filename)
        manifest_text_path = os.path.join(manifest_dir, manifest_text_filename)
        _do_convert_scp_to_manifest4icefall(wav_scp_path, text_scp_path, manifest_wav_path, manifest_text_path,num_thread=num_thread_manifest)
        logging_info('得到manifest完成')
    else:
        logging_info(f'only_fbank={only_fbank}')
        return
    if not only_manifest:
        logging_info('开始生成fbank')
        _do_compute_fbank4icefall(
            manifests_dir=manifest_dir,
            fbank_dir=fbank_dir,
            partition=partition,
            prefix=prefix,
            perturb_speed=(partition == 'train')
        )
        logging_info('生成fbank完成')
    else:
        logging_info(f'only_manifest={only_manifest}')
        return


def do_extract_gz(file_path, output_dir=None):
    # 创建目标目录（如果不存在）
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)

    # 打开.gz文件并解压到目标目录
    with gzip.open(file_path, 'rb') as f_in:
        file_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_dir, os.path.splitext(file_name)[0])
        with open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)




def _do_copy_files_by_manifest_scp(manifest_path, output_dir, num_thread=32, is_jump=False):
    def litttle_fuc(input_dict_i, output_dir, res_dict):
        for key, file_path in tqdm(input_dict_i.items(), total=len(input_dict_i)):
            new_path = do_replace_dir(file_path, output_dir)
            copy_file(file_path, new_path, use_shell=True, visualization=False, is_jump=is_jump)
            res_dict[key] = new_path

    timer = GxlTimer()
    logging_info('开始执行：_do_copy_files_by_manifest_scp()')
    input_dict = load_dict_from_scp(manifest_path)
    res_dict = {}
    dict_list = do_split_dict(input_dict, num_thread)
    runner = GxlDynamicProcessPool()
    for dict_ in dict_list:
        runner.add_task(litttle_fuc, [dict_, output_dir, res_dict])
    runner.start()
    sec_num = timer.stop_halfway_and_return()
    logging_info('结束执行：_do_copy_files_by_manifest_scp(), 用时：' + str(sec_num) + '秒')
    return res_dict

def __litttle_fuc_4_copy_files_by_manifest_list(input_list_i, output_dir_i, is_jump_i=False):
    """
    multi process 不能使用函数内的子函数
    """
    for file_path in tqdm(input_list_i, total=len(input_list_i)):
        new_path = do_replace_dir(file_path, output_dir_i)
        copy_file(file_path, new_path, use_shell=True, visualization=False, is_jump=is_jump_i)
def _do_copy_files_by_manifest_list(manifest_path, output_dir, num_thread=32, is_jump=False):

    timer = GxlTimer()
    logging_info('开始执行：_do_copy_files_by_manifest_list()')
    input_file_list = load_list_file_clean(manifest_path)
    res_list = []
    dict_list = do_split_list(input_file_list, num_thread)
    runner = GxlDynamicProcessPool()
    for dict_ in dict_list:
        runner.add_task(__litttle_fuc_4_copy_files_by_manifest_list, [dict_, output_dir, is_jump])
    runner.start()
    sec_num = timer.stop_halfway_and_return()
    logging_info('结束执行：_do_copy_files_by_manifest_list(), 用时：' + str(sec_num) + '秒')
    return res_list


def _do_copy_files_by_manifest_jsonl(manifest_path, output_dir, num_thread=32, is_jump=False):
    pass


def do_copy_files_by_manifest(manifest_path, output_dir, manifest_type='scp', num_thread=32,is_jump=False):
    """

    :param manifest_path:
    :param output_dir:
    :param manifest_type:  scp, list, jsonl
    :return:
    """
    if manifest_type == 'scp':
        return _do_copy_files_by_manifest_scp(manifest_path, output_dir, num_thread=num_thread,is_jump=is_jump)
    elif manifest_type == 'list':
        return _do_copy_files_by_manifest_list(manifest_path, output_dir, num_thread=num_thread,is_jump=is_jump)
    elif manifest_type == 'jsonl':
        return _do_copy_files_by_manifest_jsonl(manifest_path, output_dir, num_thread=num_thread, is_jump=is_jump)
    else:
        raise ValueError(f'manifest_type={manifest_type}不支持')





def do_get_fake_dir():
    temp_path = f'/home/xlgeng/.cache/.temp/{random.randint(10000, 99999)}'
    makedir_sil(temp_path)
    return temp_path
def do_get_fake_file():
    temp_path = f'/home/xlgeng/.cache/.temp/{random.randint(10000, 99999)}.txt'
    makedir_for_file(temp_path)
    return temp_path
def do_get_fake_file_from_list(my_list):
    temp_path = f'/home/xlgeng/.cache/.temp/{random.randint(10000, 99999)}.txt'
    write_list_to_file(my_list, temp_path)
    return temp_path


def do_split_list_with_scale(source_list, num_subsets, scale_list):
    """
    最后一个块包含多余的余数
    :param source_list:
    :param num_subsets:
    :return:
    """
    total_len = len(source_list)
    # 按比例分割列表
    subsets = []
    start_idx = 0
    for scale in scale_list:
        end_idx = start_idx + math.ceil(scale * total_len)
        subsets.append(source_list[start_idx:end_idx])
        start_idx = end_idx

    return subsets


def do_inference_paraformer(input_wav_scp, output_dir, true_text_path=None, gpuid=None):
    from modelscope.pipelines import pipeline
    from modelscope.utils.constant import Tasks
    if gpuid is not None:
        os.environ['CUDA_VISIBLE_DEVICES'] = f'{gpuid}'
    inference_pipeline = pipeline(
        task=Tasks.auto_speech_recognition,
        model='iic/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
        model_revision="v2.0.4")
    makedir_sil(output_dir)

    if isinstance(input_wav_scp, dict):
        wav_dict = input_wav_scp
    else:
        wav_dict = load_dict_from_scp(input_wav_scp)
    res_text_list = []
    for key, path in tqdm(wav_dict.items(), total=len(wav_dict)):
        logging_info(key, path)
        if not os.path.exists(path):
            continue
        try:
            text_res = inference_pipeline(path)
            logging_info(f'{key} {text_res[0]["text"]}')
            res_text_list.append(f'{key} {text_res[0]["text"]}')
        except Exception as e:
            print(e)
            continue
    write_list_to_file(res_text_list, os.path.join(output_dir, 'text'))
    if true_text_path is not None:
        do_compute_wer(true_text_path, os.path.join(output_dir, 'text'), output_dir)



def do_say_hello_to_gxl():
    logging_info("Hello, GXL!")


def do_padding_ids_by_lens(y: torch.Tensor, lengths: torch.Tensor, padding_id):
    assert len(y) == len(lengths), "The lengths of y and lengths"
    assert y.ndim == 2, f'y.ndim={y.ndim}, 只能是2'
    assert lengths.ndim == 1, f'lengths.ndim={lengths}'
    mask = torch.arange(y.size(1), device=y.device, dtype=y.dtype).expand(y.size(0), y.size(1))
    mask = mask < lengths.unsqueeze(1)
    mask = mask.to(y.device)
    y_res = torch.full_like(y, padding_id, dtype=y.dtype, device=y.device)
    y_res[mask] = y[mask]
    return y_res


def do_padding_embeds_by_lens(y: torch.Tensor, lengths: torch.Tensor, padding_num):
    assert len(y) == len(lengths), "The lengths of y and lengths are not equal."
    assert y.ndim == 3, f'y.ndim={y.ndim}, 只能是3'
    assert lengths.ndim == 1, f'lengths.ndim={lengths}'
    batch_size, max_len, embed_size = y.shape
    # 创建一个新的填充张量
    padded_y = torch.full((batch_size, max_len, embed_size), padding_num, device=y.device, dtype=y.dtype)
    # 创建一个mask
    mask = torch.arange(max_len, device=y.device).expand(len(lengths), max_len) < lengths.unsqueeze(1)
    # 使用mask将y的值复制到新的填充张量中
    padded_y[mask] = y[mask]
    return padded_y


def do_execute_shell_command(command_line):
    """

    :param command_line: 可以是str,也可以是str_list
    :return:
    """
    timer = GxlTimer()
    command_list = []
    if isinstance(command_line, list):

        command_line = ' '.join(command_line)
        command_list.append(command_line)
    logging_info('执行命令：' + command_line)
    result = subprocess.run(command_line, shell=True, stdout=subprocess.PIPE, text=True)
    res = result.stdout
    timer.stop_halfway_and_print("do_execute_shell_command():命令执行完成")
    return res


def do_get_file_rows_num_shell(file_path):
    command_line = f'wc -l {file_path}'
    res = do_execute_shell_command(command_line)
    return int(res.split(' ')[0])


def do_print_param_num_all(model, print_str=""):
    param_num = 0
    for param in model.parameters():
        param_num += param.numel()
    param_num = param_num / 1024 / 1024
    logging_info(f'{print_str} all param num: ', param_num, "MB")


def do_print_param_num_trained(model, print_str=""):
    param_num = 0
    for param in model.parameters():
        if param.requires_grad:
            param_num += param.numel()
    param_num = param_num / 1024 / 1024
    logging_info(f'{print_str} trained param num: ', param_num, "MB")


def do_print_param_num_untrained(model, print_str=""):
    param_num = 0
    for param in model.parameters():
        if not param.requires_grad:
            param_num += param.numel()
    param_num = param_num / 1024 / 1024
    logging_info(f'{print_str} untrained param num: ', param_num, "MB")


def do_fire_all_params(model, print_str=""):
    logging_info(f'fire {print_str} all params')
    for param in model.parameters():
        param.requires_grad = True


def do_freeze_all_params(model, print_str=""):
    logging_info(f'freeze {print_str} all params')
    for param in model.parameters():
        param.requires_grad = False


def do_uncompress_shard(shard_path_list, output_dir, wav_path=None, text_path=None, num_thread=8):
    """
    将一个shards list 解压到目标目录，且会按shard 名字创建子目录
    :param shard_path_list: str or list
    :param output_dir:
    :param wav_path:
    :param text_path:
    :param num_thread:
    :return:
    """
    runner = GxlDynamicThreadPool()
    if isinstance(shard_path_list, str):
        shard_path_list = load_list_file_clean(shard_path_list)
    list_list = do_split_list(shard_path_list, num_thread)

    def little_func(little_list, output_dir):
        for shard_path in tqdm(little_list, total=len(little_list)):
            do_uncompress_shard4one(shard_path, output_dir)

    for list_i in list_list:
        runner.add_task(little_func, [list_i, output_dir])
    runner.start()
    wav_dict = do_get_scp_for_wav_dir(output_dir, suffix='.wav')
    text_path_dict = do_get_scp_for_wav_dir(output_dir, suffix='.txt')
    text_dict = {key: load_first_row_clean(text_path_dict[key]) for key in text_path_dict}
    if wav_path is None or text_path is None:
        return wav_dict, text_dict
    write_dict_to_scp(wav_dict, wav_path)
    write_dict_to_scp(text_dict, text_path)


def do_uncompress_shard4one(shard_path, output_dir):
    shard_name = get_file_pure_name_from_path(shard_path)
    output_tmp = f'{output_dir}/{shard_name}'
    makedir_sil(output_tmp)
    shell_str = f'tar -xvf {shard_path} -C {output_tmp}'
    do_execute_shell_command(shell_str)


def do_generate_random_num2(num_digit):
    # 生成一个0到10的num次方-1之间的随机数
    random_num = random.randint(0, 10 ** num_digit - 1)

    # 将数字转换为字符串，并使用zfill方法补齐到num位
    random_num_str = str(random_num).zfill(num_digit)

    return random_num_str
def do_generate_random_num(num_digit):
    res = ""
    for i in range(num_digit):
        # 生成一个0到9之间的随机数
        random_num = random.randint(0, 10)
        res += str(random_num)
    return res


def plot_lines(data_dict, x_labels=None, y_step=0.01, nbins=50):
    try:
        import matplotlib.ticker.MultipleLocator as MultipleLocator
        import matplotlib.pyplot as plt
    except:
        logging_info('matplotlib 未安装，请先安装 matplotlib; pip install matplotlib')
        return
    # 创建一个图形对象
    fig, ax = plt.subplots(figsize=(10, 8))
    if x_labels is None:
        x_labels = [str(i) for i in range(len(list(data_dict.values())[0]))]

    # 绘制每条线
    for key, values in data_dict.items():
        ax.plot(values, label=key)

    # 设置X轴标签
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_title('Simple Line Plot')
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    # 自定义网格线样式
    ax.grid(color='gray', linestyle='--', linewidth=0.5)

    # 设置Y轴步长
    # ax.set_yticks(range(int(min(min(data_dict.values()))), int(max(max(data_dict.values())))+1, y_step))
    ax.yaxis.set_major_locator(MultipleLocator(y_step))
    # 设置Y轴的标签显示频率
    # ax.yaxis.set_major_locator(MaxNLocator(prune='both', nbins=nbins))  # nbins控制显示的标签数量

    # 添加图例
    ax.legend()

    # 显示图形
    plt.show()





def do_listdir(directory_path, return_path = True):
    """
    遍历指定目录下的所有文件和子目录，
    返回一级目录下的目录路径列表和文件路径列表。

    :param directory_path: 指定目录的路径
    :return: 一个元组，包含两个列表：(dir_path_list, file_path_list)
    """
    dir_path_list = []
    file_path_list = []

    # 遍历指定目录下的所有项
    for item in os.listdir(directory_path):
        # 构建完整的路径
        full_path = os.path.join(directory_path, item)

        # 判断是文件还是目录
        if os.path.isdir(full_path):
            # 如果是目录，添加到目录列表中
            if return_path:
                dir_path_list.append(full_path)
            else:
                dir_path_list.append(item)
        elif os.path.isfile(full_path):
            # 如果是文件，添加到文件列表中
            if return_path:
                file_path_list.append(full_path)
            else:
                file_path_list.append(item)

            # 返回结果
    return dir_path_list, file_path_list



def get_wer_from_wer_file(filepath):
    # 假设文件名为 "data.txt"，并且文件内容中包含了类似 "Mandarin -> 3.20 % N=" 的句子
    # 读取文件内容
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # 定义正则表达式来匹配 "Mandarin -> " 后跟数字（可能包含小数点）和百分比符号
    # 注意：这个正则表达式假设了 "Mandarin -> " 是固定的，并且之后直接跟着数字、小数点、数字、百分比符号和可能的空格及 "N="
    pattern = r'Mandarin -> (\d+\.\d+) %\s*N='
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, content)
    if len(matches) == 0:
        logging_info(f'no find wer num in {filepath}')
        return -1
    return float(matches[0])

def do_get_wer_from_wer_file4mandarin(filepath):
    # 假设文件名为 "data.txt"，并且文件内容中包含了类似 "Mandarin -> 3.20 % N=" 的句子
    # 读取文件内容
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # 定义正则表达式来匹配 "Mandarin -> " 后跟数字（可能包含小数点）和百分比符号
    # 注意：这个正则表达式假设了 "Mandarin -> " 是固定的，并且之后直接跟着数字、小数点、数字、百分比符号和可能的空格及 "N="
    pattern = r'Mandarin -> (\d+\.\d+) %\s*N='
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, content)
    if len(matches) == 0:
        logging_info(f'no find wer num in {filepath}')
        return -1
    return float(matches[0])

def do_get_wer_from_wer_file4english(filepath):
    # 假设文件名为 "data.txt"，并且文件内容中包含了类似 "Mandarin -> 3.20 % N=" 的句子
    # 读取文件内容
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # 定义正则表达式来匹配 "Mandarin -> " 后跟数字（可能包含小数点）和百分比符号
    # 注意：这个正则表达式假设了 "Mandarin -> " 是固定的，并且之后直接跟着数字、小数点、数字、百分比符号和可能的空格及 "N="
    pattern = r'English -> (\d+\.\d+) %\s*N='
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, content)
    if len(matches) == 0:
        logging_info(f'no find wer num in {filepath}')
        return -1
    return float(matches[0])


def do_get_wer_from_wer_file4all(filepath):
    # 假设文件名为 "data.txt"，并且文件内容中包含了类似 "Mandarin -> 3.20 % N=" 的句子
    # 读取文件内容
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # 定义正则表达式来匹配 "Mandarin -> " 后跟数字（可能包含小数点）和百分比符号
    # 注意：这个正则表达式假设了 "Mandarin -> " 是固定的，并且之后直接跟着数字、小数点、数字、百分比符号和可能的空格及 "N="
    pattern = r'Overall -> (\d+\.\d+) %\s*N='
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, content)
    if len(matches) == 0:
        logging_info(f'no find wer num in {filepath}')
        return -1
    return float(matches[0])

def get_wer_all_from_wer_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    # 使用正则表达式匹配你需要的数字
    matches = re.search(r'Mandarin -> (\d+\.?\d*) %.*S=(\d+) D=(\d+) I=(\d+)', content)

    # 如果匹配成功，将匹配到的结果放入一个列表中
    if matches:
        numbers = [float(matches.group(i)) for i in range(1, 5)]
        return numbers
    else:
        logging_info(f'no find wer num in {filepath}')
        return -1

import os
import subprocess

def convert_webm_to_wav(webm_file, wav_file):
    command = ['ffmpeg', '-i', webm_file, wav_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def do_download_from_play_url(input_url, output_dir, wav_type='mp3', wav_name='loaded_audio', keep_title=False, is_list=False):
    """"""
    now = do_get_now_time_by_second()
    makedir_sil(output_dir)
    template_dir = os.path.join(output_dir, wav_name)
    if keep_title:
        template_dir = f"{template_dir}_%(title)s.%(ext)s"
        template_dir = template_dir + "_%(title)s"
    if is_list:
        template_dir = template_dir + '_%(id)s'
    template_dir = template_dir + ".%(ext)s"
    if wav_type.startswith('.'):
        wav_type = wav_type[1:]
    command = [
        'yt-dlp',
        '-x',  # 仅提取音频
        '--audio-format', wav_type,  # 设置音频格式为wav,mp3等
        '--output', template_dir,  # 设置输出文件名模板
        input_url  # YouTube视频URL
    ]
    logging_info(f'开始下载, link: {input_url}')
    res = subprocess.run(command, capture_output=True, text=True)
    res = str(res)[-100:]
    logging_info(f"下载完成,耗时：{do_get_elapsed_time(now)}s，link: {input_url}\n res:", res)


def do_normalization(input_file, output_wav):
    subprocess.run(['ffmpeg', '-i', input_file, '-ac', '1', '-ar', '16000', output_wav])


def do_convert_dict_to_scp_str_list(res_dict):
    """"""
    res_list = []
    for key, value in res_dict.items():
        res_list.append(f"{key} {value}")
    return res_list



def do_filter_for_encn(input_str):
    """"""
    # 将英文字母转换为大写
    text = input_str.upper()
    # 英文单词之间如果存在_ ▁则使用空格代替
    text = re.sub(r'([a-zA-Z])_([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])▁([a-zA-Z])', r'\1 \2', text)
    # 去除汉字之间的空格
    text = re.sub(r'\s+([\u4e00-\u9fa5])', r'\1', text)
    # 汉字与英文单词之间使用空格隔开
    text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])([\u4e00-\u9fa5])', r'\1 \2', text)
    return text

def do_compute_wer_return_wer(true_text, hpy_text):
    fake_dir = do_get_fake_dir()
    do_compute_wer(true_text, hpy_text, fake_dir)
    temp_path = os.path.join(fake_dir, 'wer')
    wer_float = get_wer_from_wer_file(temp_path)
    remove_dir(fake_dir)
    return wer_float

def do_inference_paraformer_return_wer(input_wav_scp, true_text_path=None, gpuid=None):
    fake_dir = do_get_fake_dir()
    do_inference_paraformer(input_wav_scp,fake_dir, true_text_path, gpuid)
    temp_wer_path = os.path.join(fake_dir, 'wer')
    wer_float = get_wer_from_wer_file(temp_wer_path)
    return wer_float


def do_extract_first_number(s):
    # 使用正则表达式查找字符串中的第一个数字
    match = re.search(r'\d+\.\d+|\d+', s)
    if match:
        # 将找到的数字转换为float类型
        return float(match.group())
    else:
        # 如果没有找到数字，返回None
        return None

def do_compress_directory_to_tar_gz(dir_path):
    logging_info(f'Compressing {dir_path} to {dir_path}.tar.gz')
    now = do_get_now_time_by_second()
    # 创建一个.tar.gz文件的路径
    tar_path = dir_path + '.tar.gz'
    # 创建一个tar文件
    with tarfile.open(tar_path, 'w:gz') as tar:
        # 添加目录到tar文件
        tar.add(dir_path, arcname=os.path.basename(dir_path))
    duration = do_get_elapsed_time(now)
    print(f'Compress finish,consume  time :{duration}s,  {dir_path} to {tar_path}')

def compress_directory_to_tar_gz_with_bur(dir_path):
    logging_info(f'Compressing {dir_path} to {dir_path}.tar.gz')
    now = do_get_now_time_by_second()
    # 创建一个.tar.gz文件的路径
    tar_path = dir_path + '.tar.gz'

    # 获取所有文件和子目录
    all_files = [os.path.join(dir_path, file_name) for file_name in os.listdir(dir_path)]

    # 创建一个进度条
    progress = tqdm(total=len(all_files), desc=f'Compressing {dir_path}')

    # 创建一个tar文件
    with tarfile.open(tar_path, 'w:gz') as tar:
        for file in all_files:
            # 添加文件到tar文件
            tar.add(file, arcname=os.path.relpath(file, dir_path))
            # 更新进度条
            progress.update()

    progress.close()
    duration = do_get_elapsed_time(now)
    print(f'Compressed ,consume  time :{duration}s, {dir_path} to {tar_path}')


def do_convert_str_to_obj_by_ast(str):
    """
    将list tuple dict等字符串形式的内容转成list tuple dict对象
    :param str:
    :return:
    """
    import ast
    converted_list = ast.literal_eval(str)
    return converted_list


def do_copy_directory_only_codefile_with_true_suffix(source_dir, destination_dir,true_suffix_tuple: tuple,  make_same_name_of_source=False):
    """
    如果不想设置true_tuple，就传入（）， 程序自动设置为('.py','.yaml','.sh', 'json)
    默认make_same_name_of_source为false,也就是source_dir 和 target_dir都是需要一样的最后一级别的目录名
    :param source_dir:
    :param destination_dir:
    :param true_suffix_tuple:
    :param make_same_name_of_source:
    :return:
    """
    # 创建目标目录
    if make_same_name_of_source:
        destination_path = os.path.join(destination_dir, os.path.basename(source_dir))
    else:
        destination_path = destination_dir
    os.makedirs(destination_path, exist_ok=True)
    if len(true_suffix_tuple)<1:
        true_suffix_tuple = ('.py','.yaml','.sh', 'json')

    # 遍历源目录中的文件和子目录
    for item in tqdm(os.listdir(source_dir), desc='copy_directory_only_codefile', total=len(os.listdir(source_dir))):
        if item in ['.git', '.idea', '__pycache__', 'exp']:
            print(f'skip {item}')
            continue
        item_path = os.path.join(source_dir, item)
        destination_item_path = os.path.join(destination_path, item)

        # 如果是文件
        if os.path.isfile(item_path):
            # 判断文件后缀是否符合要求
            if item.endswith(true_suffix_tuple):
                # print(f'copy file: {item_path} to {destination_item_path}')
                _copy_file_shell(item_path, destination_item_path)
        # 如果是子目录
        elif os.path.isdir(item_path):
            # 递归复制子目录
            do_copy_directory_only_codefile_with_true_suffix(item_path, destination_item_path, true_suffix_tuple, make_same_name_of_source=make_same_name_of_source)


def do_copy_directory_only_codefile_with_false_suffix(source_dir, destination_dir,false_suffix_tuple: tuple, make_same_name_of_source=False):
    """

    :param make_same_name_of_source:
    :param source_dir:
    :param destination_dir:
    :param false_suffix_tuple:
    :return:
    """
    # 创建目标目录
    if make_same_name_of_source:
        destination_path = os.path.join(destination_dir, os.path.basename(source_dir))
    else:
        destination_path = destination_dir
    os.makedirs(destination_path, exist_ok=True)
    if len(false_suffix_tuple)<1:
        false_suffix_tuple = ('.pt', '.tar', '.gz', '.scp','.list','.jsonl','.txt')

    # 遍历源目录中的文件和子目录
    for item in tqdm(os.listdir(source_dir), desc='copy_directory_only_codefile', total=len(os.listdir(source_dir))):
        item_path = os.path.join(source_dir, item)
        destination_item_path = os.path.join(destination_path, item)

        # 如果是文件
        if os.path.isfile(item_path):
            # 判断文件后缀是否符合要求
            if not item.endswith(false_suffix_tuple):
                _copy_file_shell(item_path, destination_item_path)
        # 如果是子目录
        elif os.path.isdir(item_path):
            # 递归复制子目录
            do_copy_directory_only_codefile_with_false_suffix(item_path, destination_item_path, false_suffix_tuple, make_same_name_of_source=make_same_name_of_source)

def load_dict_from_tsv(input_tsv_path, if_relpath:bool=False):
    """"""
    total_list = load_list_file_clean(input_tsv_path)
    root_dir = total_list[0]
    left_list = total_list[1:]
    res_dict = {}
    for line in left_list:
        line_list = line.strip().split()
        assert len(line_list) == 2  # tsv的格式硬性要求
        if if_relpath:
            res_dict[line_list[0]] = os.path.join(root_dir, line_list[1])
        else:
            res_dict[line_list[0]] = line_list[1]
    return res_dict


def do_get_formatted_datalist_for_asr_task(input_wav, input_text, dataset_name):
    """
    这个函是为了给实验室理解大模型任务中要用到的数据生成标准格式的data.list
    标准格式:
      {
  "task": task_tag, # 如 "<TRANSCRIBE>"
  "key":  utt_id, # 如 "IC0001W0007"
  "wav": wav_path, # 如 "/home/backup_nfs/data-ASR/AIShell2/AISHELL-2/iOS/data/wav/C0001/IC0001W0007.wav"
  "txt": text, # 如 "天安门"
  "lang": language, # 如 "<CN>"
  "speaker": speaker_tag, # 如 "spk001"
  "emotion": emotion等分类标签 # 如 "<HAPPY>"
  "gender": 性别标签 # 如 "<MALE>"
  "extra":{class:"label", "duration": wav_length# 单位s，如2.05125，表示2.05秒}
  }

    :param input_text:
    :param input_wav:
    :return:
    """
    if not isinstance(input_wav, dict):
        assert isinstance(input_wav, str)
        input_wav = load_dict_from_scp(input_wav)
    if not isinstance(input_text, dict):
        assert isinstance(input_text, str)
        input_text = load_dict_from_scp(input_text)
    task_tag = "<TRANSCRIBE>"
    lang = "<CN>" if "librispeech" not in dataset_name else "<EN>"
    speaker = "<NONE>"
    emotion  = "NEUTRAL"
    gender = "<NONE>"
    res_list = []
    for key, wav_path in tqdm(input_wav.items(), desc="Generating formatted data.list for ASR task", total=len(input_wav)):
        # txt = input_text[key]  # 别忘了key值的对应性
        if key not in input_text:
            logging_warning("Warning: {} not in input_text".format(key))
            continue
        txt = input_text[key]
        duration = 0
        try:
            duration = do_get_wav_duration(wav_path)
        except:
            try:
                samples, rt = _get_sample_count_torchaudio(wav_path)
                duration = samples / rt
            except:
                # utils_file.logging_info('Error in getting duration of wav file: {}'.format(wav_path))
                duration = 0
        extra = {"duration": duration, "dataset": dataset_name}
        item_dict = {"task": task_tag, "key": key, "wav": wav_path,"txt": txt, "lang": lang, "speaker": speaker, "emotion": emotion, "gender": gender, "extra": extra}
        res_list.append(item_dict)
    return res_list


def do_get_formatted_datalist_for_all_task(input_wav, input_text, dataset_name, task_tag, fake_duration=True):
    """
    这个函是为了给实验室理解大模型任务中要用到的数据生成标准格式的data.list
    标准格式:
      {
  "task": task_tag, # 如 "<TRANSCRIBE>"
  "key":  utt_id, # 如 "IC0001W0007"
  "wav": wav_path, # 如 "/home/backup_nfs/data-ASR/AIShell2/AISHELL-2/iOS/data/wav/C0001/IC0001W0007.wav"
  "txt": text, # 如 "天安门"
  "lang": language, # 如 "<CN>"
  "speaker": speaker_tag, # 如 "spk001"
  "emotion": emotion等分类标签 # 如 "<HAPPY>"
  "gender": 性别标签 # 如 "<MALE>"
  "extra":{class:"label", "duration": wav_length# 单位s，如2.05125，表示2.05秒}
  }

    :param input_text:
    :param input_wav:
    :return:
    """
    if not isinstance(input_wav, dict):
        assert isinstance(input_wav, str)
        input_wav = load_dict_from_scp(input_wav)
    if not isinstance(input_text, dict):
        assert isinstance(input_text, str)
        input_text = load_dict_from_scp(input_text)
    # task_tag = "<TRANSCRIBE>"
    lang = "<CN>" if "librispeech" not in dataset_name else "<EN>"
    speaker = "<NONE>"
    emotion  = "NEUTRAL"
    gender = "<NONE>"
    res_list = []
    for key, wav_path in tqdm(input_wav.items(), desc="Generating formatted data.list for ASR task", total=len(input_wav)):
        # txt = input_text[key]  # 别忘了key值的对应性
        if key not in input_text:
            logging_warning("Warning: {} not in input_text".format(key))
            continue
        txt = input_text[key]
        duration = 0
        if fake_duration:
            duration = -1
        else:
            try:
                duration = do_get_wav_duration(wav_path)
            except:
                try:
                    samples, rt = _get_sample_count_torchaudio(wav_path)
                    duration = samples / rt
                except:
                    # utils_file.logging_info('Error in getting duration of wav file: {}'.format(wav_path))
                    duration = 0
        extra = {"duration": duration, "dataset": dataset_name}
        item_dict = {"task": task_tag, "key": key, "wav": wav_path,"txt": txt, "lang": lang, "speaker": speaker, "emotion": emotion, "gender": gender, "extra": extra}
        res_list.append(item_dict)
    return res_list



def little_func_for_cp_from_dict(input_wav_dict, output_dir, index ):
    """
    这个函数是为了多进程的同时复制文件. 只在index=0的进程展示进度条
    :param input_wav_dict:
    :param output_dir:
    :param index:
    :return:
    """
    if index == 0:
        for key, wav_path in tqdm(input_wav_dict.items(), total=len(input_wav_dict), desc='复制文件'):
            copy_file2(wav_path, output_dir, is_jump=True, is_log=False)
    else:
        for key, wav_path in input_wav_dict.items():
            copy_file2(wav_path, output_dir, is_jump=True, is_log=False)

def do_little_func_for_cp_from_dict(input_wav_dict, output_dir, index):
    little_func_for_cp_from_dict(input_wav_dict, output_dir, index)
def little_func_for_cp_from_list(input_wav_list, output_dir, index ):
    """
    这个函数是为了多进程的同时复制文件. 只在index=0的进程展示进度条
    :param input_wav_list:
    :param output_dir:
    :param index:
    :return:
    """
    if index == 0:
        for  wav_path in tqdm(input_wav_list.items(), total=len(input_wav_list), desc='复制文件'):
            copy_file2(wav_path, output_dir, is_jump=True, is_log=False)
    else:
        for wav_path in input_wav_list.items():
            copy_file2(wav_path, output_dir, is_jump=True, is_log=False)

def do_little_func_for_cp_from_list(input_wav_list, output_dir, index):
    little_func_for_cp_from_list(input_wav_list, output_dir, index)

def do_sort_dict_by_value(my_dict, asc=True):
    """
    对字典按照value排序,默认升序,升序代表这最开始的是小值
    """
    if asc:
        return dict(sorted(my_dict.items(), key=lambda x: x[1]))
    else:
        return dict(sorted(my_dict.items(), key=lambda x: x[1], reverse=True))
def do_get_vocab_dict_from_text_scp_by_char_fn(text_scp_path, output_vocab_path=None):
    """
    从一个text.scp中得到一个token.txt, 按照wenet u2++需要的格式
    """
    token_dict = {}
    text_dict = load_dict_from_scp(text_scp_path)
    for key, text in tqdm(text_dict.items(), desc='get vocab', total=len(text_dict)):
        for char in text:
            if char in [' ','','\n','\t']:
                continue
            if char not in token_dict:
                token_dict[char] = 0
            else:
                token_dict[char] += 1
    sort_dict = do_sort_dict_by_value(token_dict)
    res_dict = {}
    res_dict['<blank>'] = 0
    res_dict['<unk>'] = 1
    res_dict['<sos/eos>'] = 2
    for key, value in sort_dict.items():
        res_dict[key] = len(res_dict)
    if output_vocab_path:
        write_dict_to_scp(res_dict, output_vocab_path)
    else:
        return res_dict

def load_dict_from_scp_for_symbol_table(symbol_table_path:Union[str, PathLike]):
    tmp_dict = load_dict_from_scp(symbol_table_path)
    return {k:int(v) for k,v in tmp_dict.items()}


def do_ctc_greedy_decode(ctc_output, blank_index)-> List[List[int]]:
    """
    Perform greedy search decoding on CTC output.

    Args:
        ctc_output (torch.Tensor): CTC output tensor of shape (batch_size, T, vocab_size).
        blank_index (int): Index of the blank character in the vocabulary.

    Returns:
        List of decoded sequences.
    """
    batch_size, T, vocab_size = ctc_output.shape
    decoded_sequences = []

    for batch in range(batch_size):
        # Get the most probable index at each time step
        max_indices = ctc_output[batch].argmax(dim=1).tolist()

        # Decode the sequence
        decoded_sequence = []
        prev_char = None

        for char_index in max_indices:
            if char_index != blank_index:
                # If the current character is not blank and not the same as the previous character
                if char_index != prev_char:
                    decoded_sequence.append(char_index)
                prev_char = char_index

                # Convert list of indices to the final decoded sequence
        decoded_sequences.append(decoded_sequence)

    return decoded_sequences


def do_replace_str_to_file(source_str, target_str, input_file, output_file):
    """
    将 input_file 文件中的所有 source_str 替换为 target_str，并将结果写入 output_file。

    :param source_str: 要被替换的字符串
    :param target_str: 用于替换的目标字符串
    :param input_file: 源文件路径
    :param output_file: 输出文件路径
    :return: None
    """
    try:
        # 读取输入文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换指定字符串
        updated_content = content.replace(source_str, target_str)

        # 将替换后的内容写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        logging_info(f"替换完成，结果已保存到 {output_file}")

    except FileNotFoundError:
        logging_error(f"错误: 输入文件 '{input_file}' 未找到")
    except IOError as e:
        logging_error(f"IO 错误: {e}")
    except Exception as e:
        logging_error(f"发生了未知错误: {e}")


def do_replace_str_to_file_and_return_list(source_str, target_str, input_file):
    """
    将 input_file 文件中的所有 source_str 替换为 target_str，并将结果以 list 的形式返回。

    :param source_str: 要被替换的字符串
    :param target_str: 用于替换的目标字符串
    :param input_file: 源文件路径
    :return: 包含替换后内容的列表，每个元素是一行替换后的字符串
    """
    try:
        # 读取输入文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换指定字符串
        updated_content = content.replace(source_str, target_str)

        # 将替换后的内容按行拆分成列表
        result_list = updated_content.splitlines()

        return result_list

    except FileNotFoundError:
        print(f"错误: 输入文件 '{input_file}' 未找到")
        return []
    except IOError as e:
        print(f"IO 错误: {e}")
        return []
    except Exception as e:
        print(f"发生了未知错误: {e}")
        return []


def do_convert_file_list_to_dict(input_list):
    """
    将文件list转成dict,key为文件的纯名字（不要后缀）
    :param input_list:
    :return:
    """
    return {get_file_pure_name_from_path(i): i for i in input_list}


def do_sync_files(file_list_path, password, username, remote_host, local_directory,remote_dir='/'):
    """
    使用 rsync 命令从远程主机下载文件，并支持断点续传(-P决定)。
    remote_dir使用的场景： 如果一个shards_list.txt文件中的pure文件名字不是唯一的， 则需要相对于某一个根目录，保留这个
    目录下面的子目录的结构，这样就不会出现覆盖文件的情况了。
    sync比scp更好用，功能相似的前体下sync支持断点续传
    :param file_list_path: 包含文件列表的文件路径
    :param password: 远程主机的 SSH 密码
    :param username: 远程主机的用户名
    :param remote_host: 远程主机的 IP 地址或主机名
    :param local_directory: 本地存储文件的目标目录
    :param remote_dir: 远程目录起始位置
    :return:
    """
    remote_dir = remote_dir if remote_dir.endswith('/') else remote_dir+'/'
    if len(remote_dir) !=1:
        do_replace_str_to_file(remote_dir, '/', file_list_path, './tmp.list')
        file_list_path = './tmp.list'
        # 构造 rsync 命令
        rsync_command = [
            'sshpass', '-p', password,  # 使用 sshpass 提供密码
            'rsync', '-avrP',  # rsync 参数：-a（归档），-v（详细），-r（递归），-P（部分传输和进度）
            # '--no-relative',  # 去掉远程目录的层级结构
            f'--files-from={file_list_path}',  # 从文件列表中读取文件路径
            f'{username}@{remote_host}:{remote_dir}',  # 远程源路径
            local_directory  # 本地目标目录
        ]
    elif remote_dir=='/':
        # 构造 rsync 命令
        rsync_command = [
            'sshpass', '-p', password,  # 使用 sshpass 提供密码
            'rsync', '-avrP',  # rsync 参数：-a（归档），-v（详细），-r（递归），-P（部分传输和进度）
            '--no-relative',  # 去掉远程目录的层级结构
            f'--files-from={file_list_path}',  # 从文件列表中读取文件路径
            f'{username}@{remote_host}:{remote_dir}',  # 远程源路径
            local_directory  # 本地目标目录
        ]
    else:
        logging_warning('remote dir格式不正确')
        return

    # 执行 rsync 命令
    try:
        subprocess.run(rsync_command, check=True)
        print("文件同步完成！")
        do_remove_file('./tmp.list')
    except subprocess.CalledProcessError as e:
        print(f"rsync 命令执行失败: {e}")
    except FileNotFoundError as e:
        print(f"命令未找到: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
def do_mkdir_p_remote(output_dir, password, username, remote_host):
    mkdir_command = [
        'sshpass', '-p', password,  # 使用 sshpass 提供密码
        'ssh',
        f'{username}@{remote_host}',
        'mkdir', '-p',
        output_dir
    ]
    try:
        subprocess.run(mkdir_command, check=True)
        print("目录创建完成！")
    except subprocess.CalledProcessError as e:
        print(f"mkdir 命令执行失败: {e}")
    except FileNotFoundError as e:
        print(f"命令未找到: {e}")

def do_sync_copy_dir_upload(loacal_dir_path, output_root_dir, password, username, remote_host):
    """
    rsync -avrP ....
    将本地的目录A上传到云端的Broot目录，创建A的叶子目录
    :param input_file_path:
    :param output_file_path:
    :param password:
    :param username:
    :param remote_host:
    :return:
    """
    rsync_command = [
        'sshpass', '-p', password,  # 使用 sshpass 提供密码
        'rsync', '-avrP',  # rsync 参数：-a（归档），-v（详细），-r（递归），-P（部分传输和进度）
        f'{loacal_dir_path}',
        f'{username}@{remote_host}:{output_root_dir}',  # 远程源路径
    ]
    # 执行 rsync 命令
    try:
        subprocess.run(rsync_command, check=True)
        print("文件同步完成！")
    except subprocess.CalledProcessError as e:
        print(f"rsync 命令执行失败: {e}")
    except FileNotFoundError as e:
        print(f"命令未找到: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
def do_sync_copy_file_upload(input_file_path, output_file_path, password, username, remote_host):
    """
    rsync -avrP ....
    :param input_file_path:
    :param output_file_path:
    :param password:
    :param username:
    :param remote_host:
    :return:
    """
    output_dir = os.path.dirname(output_file_path)
    mkdir_command = [
        'sshpass', '-p', password,  # 使用 sshpass 提供密码
        'ssh',
        f'{username}@{remote_host}',
        'mkdir', '-p',
        output_dir
    ]
    rsync_command = [
        'sshpass', '-p', password,  # 使用 sshpass 提供密码
        'rsync', '-avrP',  # rsync 参数：-a（归档），-v（详细），-r（递归），-P（部分传输和进度）
        f'{input_file_path}',
        f'{username}@{remote_host}:{output_file_path}',  # 远程源路径
    ]
    # 执行 rsync 命令
    try:
        subprocess.run(mkdir_command, check=True)
        subprocess.run(rsync_command, check=True)
        print("文件同步完成！")
    except subprocess.CalledProcessError as e:
        print(f"rsync 命令执行失败: {e}")
    except FileNotFoundError as e:
        print(f"命令未找到: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def do_sync_files_download_data_multi_thread(file_list_path, password, username, remote_host,local_directory,remote_dir='/', num_thread=10):
    runner = GxlDynamicProcessPool()
    file_list = load_list_file_clean(file_list_path)
    file_list_list = do_split_list(file_list, num_subsets=num_thread)
    for file_list_i in file_list_list:
        fake_file = do_get_fake_file()
        write_list_to_file(file_list_i, fake_file)
        runner.add_task(do_sync_files, [fake_file, password, username, remote_host,local_directory,remote_dir])
    runner.start()

def do_sync_files_upload_data(file_list_path, password, username, remote_host,remote_dir):
    """
    sync比scp更好用，功能相似的前体下sync支持断点续传
    :param file_list_path: 包含文件列表的文件路径
    :param password: 远程主机的 SSH 密码
    :param username: 远程主机的用户名
    :param remote_host: 远程主机的 IP 地址或主机名
    :param local_directory: 本地存储文件的目标目录
    :param remote_dir: 远程目录起始位置
    :return:
    """
    # 构造 rsync 命令
    rsync_command = [
        'sshpass', '-p', password,  # 使用 sshpass 提供密码
        'rsync', '-avrP',  # rsync 参数：-a（归档），-v（详细），-r（递归），-P（部分传输和进度）
        '--no-relative',  # 去掉远程目录的层级结构
        # f'--parallel={num_thread}',  # 添加多线程参数，同时启动4个线程进行操作
        f'--files-from={file_list_path}',  # 从文件列表中读取文件路径
        "/",
        f'{username}@{remote_host}:{remote_dir}',  # 远程源路径
    ]
    # 执行 rsync 命令
    try:
        logging_info(f'开始执行：{" ".join(rsync_command)}')
        subprocess.run(rsync_command, check=True)
        logging_info("文件同步完成！")
    except subprocess.CalledProcessError as e:
        logging_info(f"rsync 命令执行失败: {e}")
    except FileNotFoundError as e:
        logging_info(f"命令未找到: {e}")
    except Exception as e:
        logging_info(f"发生错误: {e}")

def do_sync_files_upload_data_multi_thread(file_list_path, password, username, remote_host,remote_dir, num_thread=10):
    do_mkdir_p_remote(remote_dir, password, username, remote_host)
    runner = GxlDynamicProcessPool()
    file_list = load_list_file_clean(file_list_path)
    file_list_list = do_split_list(file_list, num_subsets=num_thread)
    for file_list_i in file_list_list:
        fake_file = do_get_fake_file()
        write_list_to_file(file_list_i, fake_file)
        runner.add_task(do_sync_files_upload_data, [fake_file, password, username, remote_host,remote_dir])
    runner.start()



def _do_get_files_dict(directory):
    result_dict = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_abs_path = os.path.join(root, file)
            file_name_without_extension = os.path.splitext(file)[0]
            if file_name_without_extension not in result_dict:
                result_dict[file_name_without_extension] = []
            result_dict[file_name_without_extension].append(file_abs_path)
    return result_dict

def do_convert_shards2raw(shards_path, raw_data_list_path, output_wav_dir_path):
    """
    将shards_path中的数据转换为raw数据，并将原始wav保存到output_wav_dir_path中
    """
    if shards_path is not None:
        shards_list = load_list_file_clean(shards_path)
        # remove_dir(output_wav_dir_path)
        # makedir_sil(output_wav_dir_path)
        for shard_path_i in shards_list:
            do_decompression_tar(shard_path_i, output_wav_dir_path)
    file_path_res_dict = _do_get_files_dict(output_wav_dir_path)
    dict_list_res = []
    for key, value in tqdm(file_path_res_dict.items(), desc="convert shards to raw", total=len(file_path_res_dict)):
        dict_i = {'key': key}
        for sub_file_path in value:
            suffix = sub_file_path.split('.')[-1]
            if suffix == 'wav':
                dict_i['wav'] = sub_file_path
            elif suffix == 'extra':
                dict_i[suffix] = json.loads(load_list_file_clean(sub_file_path)[0])
            else:
                dict_i[suffix] = load_list_file_clean(sub_file_path)[0] if len(load_list_file_clean(sub_file_path))>0 else ""
        dict_list_res.append(dict_i)
    write_dict_list_to_jsonl(dict_list_res, raw_data_list_path)

def do_showing_confusion_matrix(labels, matrix,title='', output_fig_path: str=None):
    """
    可视化混淆矩阵的函数
    :param labels: 标签序列，类型为列表等可迭代对象
    :param matrix: 代表混淆矩阵的二维列表，元素为整数，形状应为(len(labels), len(labels))
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except:
        logging_info("请安装matplotlib和numpy, 使用pip install matplotlib numpy")
        return
    num_classes = len(labels)
    fig, ax = plt.subplots()
    # 使用imshow来绘制热力图展示混淆矩阵
    im = ax.imshow(np.array(matrix), cmap=plt.cm.Blues)

    # 设置x轴和y轴的刻度以及对应的标签
    ax.set_xticks(np.arange(num_classes))
    ax.set_yticks(np.arange(num_classes))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    # 旋转x轴刻度标签，让其更美观显示
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # 添加每个方格中的数值标签
    for i in range(num_classes):
        for j in range(num_classes):
            text = ax.text(j, i, matrix[i][j],
                           ha="center", va="center", color="black")

    ax.set_title(f"{title} Confusion Matrix")
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')
    fig.tight_layout()
    if output_fig_path is not None:
        plt.savefig(output_fig_path)
    else:
        plt.show()


def do_replace_str_for_file_and_return_new_file(input_shards_path, str1, str2):
    """
    将input_file文件中的str1都替换为str2,并存入file_path2
    :param input_shards_path:
    :param str1:
    :param str2:
    :return:
    """
    file_path2 = do_get_fake_file()
    with open(input_shards_path, 'r', encoding='utf-8') as file:
        content = file.read()
        content = content.replace(str1, str2)
    with open(file_path2, 'w', encoding='utf-8') as file:
        file.write(content)
    return file_path2


def do_get_first_tag_from_str(input_str, upper=True):
    """
    得到第一个<>标签的内容，并将其转为大写
    >>> input : "<tag1>content1<tag2>content2<tag3>content3"
    >>> output: "<TAG1>"
    :param upper: if false, return the lower case of the tag
    :param input_str:
    :return:
    """
    # 使用正则表达式提取所有 <> 中的内容
    matches = re.findall(r'<.*?>', input_str)
    # 输出结果
    if len(matches)==0:
        return '<--no_tag-->'
    if upper:
        return matches[0].upper()
    else:
        return matches[0].lower()



def do_split_file(input_file, num_parts, output_dir):
    """

    Args:
        input_file:
        num_parts:
        output_dir:

    Returns:

    """
    # utils_file.makedir_sil(output_dir)
    with open(input_file, 'rb') as f:
        f.seek(0, 2)  # 将文件指针移动到文件末尾
        file_size = f.tell()  # 获取文件大小
        chunk_size = file_size // num_parts  # 计算每一份的大小
        logging_info(f'chunk_size:{chunk_size}')
        f.seek(0)  # 将文件指针移回文件开头
        for i in range(num_parts):
            part_file = f"{output_dir}/{input_file.split('/')[-1]}_{i}.gxl_part"
            logging_info(f'part_file:{part_file}')
            with open(part_file, 'wb') as part:
                if i == num_parts - 1:  # 最后一部分可能会大一些，处理文件大小不能整除的情况
                    data = f.read()
                else:
                    data = f.read(chunk_size)
                part.write(data)


def do_combine_files(output_file, split_files_dir, old_file_name, num_parts):
    """

    Args:
        output_file:
        split_files_dir:
        old_file_name:  **.* eg: 001.tar
        num_parts: int ,

    Returns:

    """
    with open(output_file, 'wb') as out:
        for i in range(num_parts):
            part_file = f"{split_files_dir}/{old_file_name}_{i}.gxl_part"
            print(part_file)
            with open(part_file, 'rb') as part:
                data = part.read()
                out.write(data)


def do_download_parts(split_files_dir, old_input_name, parts_num, output_dir, num_thread):
    """
    下载分片文件到本地
    Args:
        split_files_dir:
        old_input_name: ***.* eg: 001.tar
        parts_num:
        output_dir:
        num_thread:

    Returns:

    """
    file_list = []
    for i in range(parts_num):
        file_list.append(f"{split_files_dir}/{old_input_name}_{i}.gxl_part")
    fake_path = do_get_fake_file()
    random.shuffle(file_list)
    write_list_to_file(file_list, fake_path)
    do_sync_files_download_data_multi_thread(
        file_list_path=fake_path,
        username="root",
        password="Fy!mATB@QE",
        remote_host="139.210.101.41",
        local_directory=output_dir,
        num_thread=num_thread
    )

def do_filter_list_delete_if_contain_str(input_list, str_to_filter):
    return list(filter(lambda x: str_to_filter not in x, input_list))

from functools import partial
class GXLMultiprocessingWithReturn:
    def __init__(self, num_processes):
        self.num_processes = num_processes
        self.ctx = multiprocessing.get_context('spawn')

    def run(self, func, big_dict_or_list, **kwargs):
        assert big_dict_or_list is not None, "big_dict_or_list 不能为空！"
        assert callable(func), "func 必须是一个可调用对象！"
        assert isinstance(big_dict_or_list, (dict, list)), "big_dict_or_list 必须是一个字典或列表！"
        if isinstance(big_dict_or_list, dict):
            split_list =do_split_dict(big_dict_or_list, self.num_processes)
        else:
            split_list =do_split_list(big_dict_or_list, self.num_processes)
        logging_info(f'开始多进程处理，共有 {len(split_list)} 个子任务。')
        time_start = time.time()
        wrapped_func = partial(func, **kwargs)
        results_from_all_processes = []
        with multiprocessing.Pool(self.num_processes) as pool:
            results_from_all_processes = pool.map(wrapped_func, split_list)
        end_time = time.time()
        print(f"--- 所有进程处理完毕，耗时: {end_time - time_start:.2f} 秒 ---")
        return results_from_all_processes


class GXLMultiprocessingWithReturnWithProcessID:
    def __init__(self, num_processes):
        """
        要求函数的param要有两个,第一个是切分的list, 第二个是进程id,这样函数可以在处理的时候根据进程id来做一些处理,,进程Id从0开始,依次累计

        :param num_processes: 进程数量
        """
        self.num_processes = num_processes
        self.ctx = mp.get_context('spawn')

    def run(self, func, big_dict_or_list, **kwargs):
        assert big_dict_or_list is not None, "big_dict_or_list 不能为空！"
        assert callable(func), "func 必须是一个可调用对象！"
        assert isinstance(big_dict_or_list, (dict, list)), "big_dict_or_list 必须是一个字典或列表！"
        if isinstance(big_dict_or_list, dict):
            split_list = do_split_dict(big_dict_or_list, self.num_processes)
        else:
            split_list = do_split_list(big_dict_or_list, self.num_processes)
        logging_info(f'开始多进程处理，共有 {len(split_list)} 个子任务。')
        tasks = [(little_dict_list, index_id) for index_id, little_dict_list in enumerate(split_list)]
        time_start = time.time()
        results_from_all_processes = []
        wrapped_func = partial(func, **kwargs)
        with mp.Pool(self.num_processes) as pool:
            results_from_all_processes = pool.starmap(wrapped_func, tasks)
        end_time = time.time()
        print(f"--- 所有进程处理完毕，耗时: {end_time - time_start:.2f} 秒 ---")
        return results_from_all_processes


def do_make_pad_mask(lengths: torch.Tensor, max_len: int = 0) -> torch.Tensor:
    """Make mask tensor containing indices of padded part.

    See description of make_non_pad_mask.

    Args:
        lengths (torch.Tensor): Batch of lengths (B,).
    Returns:
        torch.Tensor: Mask tensor containing indices of padded part.

    Examples:
        >>> lengths = [5, 3, 2]
        >>> make_pad_mask(lengths)
        masks = [[0, 0, 0, 0 ,0],
                 [0, 0, 0, 1, 1],
                 [0, 0, 1, 1, 1]]
    """
    batch_size = lengths.size(0)
    max_len = max_len if max_len > 0 else lengths.max().item()
    seq_range = torch.arange(0,
                             max_len,
                             dtype=torch.int64,
                             device=lengths.device)
    seq_range_expand = seq_range.unsqueeze(0).expand(batch_size, max_len)
    seq_length_expand = lengths.unsqueeze(-1)
    mask = seq_range_expand >= seq_length_expand
    return mask

def do_make_seq_mask(lengths: torch.Tensor, max_len: int = 0) -> torch.Tensor:
    """Make mask tensor containing indices of padded part.

    See description of make_non_pad_mask.

    Args:
        lengths (torch.Tensor): Batch of lengths (B,).
    Returns:
        torch.Tensor: Mask tensor containing indices of padded part.

    Examples:
        >>> lengths = [5, 3, 2]
        >>> make_pad_mask(lengths)
        masks = [[1, 1, 1, 1 ,1],
                 [1, 1, 1, 0, 0],
                 [1, 1, 0, 0, 0]]
                 ]
    """
    return ~do_make_pad_mask(lengths, max_len)

def do_remove_brackets_content(s):
    """
    删除字符串中的 <> []标签内容
    :param s:
    :return:
    """
    # 正则模式：匹配 <...> 或 [...] 格式的内容（包括括号）
    # <.*?> 匹配 < 开头、> 结尾的任意字符（非贪婪模式，避免跨多个括号匹配）
    # \[.*?\] 匹配 [ 开头、] 结尾的任意字符（注意 [ ] 是特殊字符，需转义）
    pattern = r'<.*?>|\[.*?\]'
    # 替换匹配到的内容为空字符串
    return re.sub(pattern, '', s)

def do_remove_spaces_between_chinese(text):
    """
    强硬匹配， 把汉字两边的空格都去掉，保证干净
    :param text:
    :return:
    """
    return remove_spaces_between_chinese(text)

def remove_spaces_between_chinese(text):
    """
    强硬匹配， 把汉字两边的空格都去掉，保证干净
    :param text:
    :return:
    """
    # 正则模式：匹配“汉字 + 任意多空格 + 汉字”
    # \u4e00-\u9fa5 匹配所有汉字
    # \s+ 匹配一个或多个空格（包括空格、制表符等空白字符，若仅需空格可改为 ' +'）
    # pattern = r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])'
    # # 替换为：第一个汉字 + 第二个汉字（去掉中间的空格）
    # return re.sub(pattern, r'\1\2', s)
    text = re.sub(r'\s*([\u4e00-\u9fff])\s*', r'\1', text)
    return text


def do_remove_punctuation_keep_quote(s: str, character_upper=True) -> str:
    """
    移除所有标点，但是保留英文的单引号，以防止类似it's这样的词语被销毁
    :param s:
    :param character_upper:
    :return:
    """
    return remove_punctuation_keep_quote(s, character_upper)

def remove_punctuation_keep_quote(s: str, character_upper=True) -> str:
    """
    移除所有标点，但是保留英文的单引号，以防止类似it's这样的词语被销毁
    :param s:
    :param character_upper:
    :return:
    """
    if character_upper:
        s = s.upper()
    # 1. 定义需要去除的英语标点（排除单引号'）
    en_punct_to_remove = string.punctuation.replace("'", "")

    # 2. 定义需要去除的中文标点（可根据需求补充）
    zh_punct_to_remove = "，。！？；：“”‘’（）《》【】『』「」……—～、｜·"

    # 3. 合并所有待移除的标点
    all_punct_to_remove = en_punct_to_remove + zh_punct_to_remove

    # 4. 创建翻译表：将所有待移除标点映射为空白（即删除）
    translator = str.maketrans("", "", all_punct_to_remove)

    # 5. 应用翻译表去除标点
    return s.translate(translator)


def do_get_random_str_only_characters(length=16):
    """
    Generate a random string of given length.
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def do_get_random_str_with_characters_digits(length=16):
    """
    Generate a random string of given length.
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def do_get_random_str_only_digits(length=16):
    """
    Generate a random string of given length.
    """
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))


def do_get_digits_str_in_format_length(digits_num, length):
    """
    生成指定长度的数字字符串，左侧补零
    :param digits_num:
    :param length:
    :param digits_num:
    :param length:
    :return:
    """
    digits_str = str(digits_num).zfill(length)
    return digits_str

def do_files_identical(src: str, dst: str, method: str = "exist", bufsize: int = 4 * 1024 * 1024) -> bool | None:
    """
    返回 True 当且仅当 src 与 dst 的内容完全一致。
    - 先比较文件大小，不同直接 False
    - method="auto": 优先使用 filecmp.cmp 的逐块比较（比整文件哈希更省）
      失败或不可用时退化到哈希比较
    - method="hash": 使用哈希（blake2b，更快更安全；如需 md5 可改）
    - method="filesize": 只做文件大小的比较（不计算哈希）
    - method="exist": 只检查文件是否存在（不计算哈希）
    - method="byte": 逐字节比较（最严格）
    """
    if not os.path.exists(dst):
        return False
    if method == "exist":
        return True

    s1 = os.stat(src)
    s2 = os.stat(dst)
    if s1.st_size != s2.st_size:
        return False
    if method == "filesize":
        return True

    if method == "auto":
        try:
            # 深比较（shallow=False）：逐块对比，发现不同会立刻返回
            return filecmp.cmp(src, dst, shallow=False)
        except Exception:
            method = "hash"  # 回退到哈希

    if method == "hash":
        h1 = hashlib.blake2b(digest_size=32)
        h2 = hashlib.blake2b(digest_size=32)
        with open(src, "rb") as f1, open(dst, "rb") as f2:
            while True:
                b1 = f1.read(bufsize)
                b2 = f2.read(bufsize)
                if not b1 and not b2:
                    break
                h1.update(b1)
                h2.update(b2)
        return h1.digest() == h2.digest()


    if method == "byte":
        # 兜底：逐块字节对比（不计算哈希）
        with open(src, "rb") as f1, open(dst, "rb") as f2:
            while True:
                b1 = f1.read(bufsize)
                b2 = f2.read(bufsize)
                if b1 != b2:
                    return False
                if not b1:  # 两边都 EOF
                    return True
    return None