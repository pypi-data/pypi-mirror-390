import requests

import mns_common.utils.data_frame_util as data_frame_util
import json
import datetime

import threading
from concurrent.futures import ThreadPoolExecutor
import mns_common.component.proxies.proxy_common_api as proxy_common_api
from loguru import logger
import concurrent.futures
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

fields = ("f352,f2,f3,f5,f6,f8,f10,f11,f22,f12,f14,f15,f16,f17,"
          "f18,f20,f21,f26,f33,f34,f35,f62,f66,f69,f72,f100,f184,f211,f212"),
fs = "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048"


max_number = 5800
# 分页条数
PAGE_SIZE = 100


def get_stocks_num(pn, proxies, page_size, time_out):
    """
     获取单页股票数据
     """
    # 获取当前日期和时间
    current_time = datetime.datetime.now()

    # 将当前时间转换为时间戳（以毫秒为单位）
    current_timestamp_ms = int(current_time.timestamp() * 1000)

    url = "https://33.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "cb": "jQuery1124046660442520420653_" + str(current_timestamp_ms),
        "pn": str(pn),
        "pz": str(page_size),  # 每页最大200条
        "po": "0",
        "np": "3",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "wbp2u": "|0|0|0|web",
        "fid": "f12",
        "fs": fs,
        "fields": fields,
        "_": current_timestamp_ms
    }
    try:
        if proxies is None:
            r = requests.get(url, params, timeout=time_out)
        else:
            r = requests.get(url, params, proxies=proxies, timeout=time_out)

        data_text = r.text

        begin_index_total = data_text.index('"total":')

        end_index_total = data_text.index('"diff"')

        total_number = int(data_text[begin_index_total + 8:end_index_total - 1])

        return total_number

    except Exception as e:
        logger.error("获取第{}页股票列表异常:{}", pn, str(e))
        return 0


def get_stock_page_data_time_out(pn, proxies, page_size, time_out):
    """
    获取单页股票数据
    """
    # 获取当前日期和时间
    current_time = datetime.datetime.now()

    # 将当前时间转换为时间戳（以毫秒为单位）
    current_timestamp_ms = int(current_time.timestamp() * 1000)

    url = "https://33.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "cb": "jQuery1124046660442520420653_" + str(current_timestamp_ms),
        "pn": str(pn),
        "pz": str(page_size),  # 每页最大200条
        "po": "0",
        "np": "3",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "wbp2u": "|0|0|0|web",
        "fid": "f12",
        "fs": fs,
        "fields": fields,
        "_": current_timestamp_ms
    }
    try:
        if proxies is None:
            r = requests.get(url, params, timeout=time_out)
        else:
            r = requests.get(url, params, proxies=proxies, timeout=time_out)

        data_text = r.text
        if pn == 1:
            try:
                begin_index_total = data_text.index('"total":')

                end_index_total = data_text.index('"diff"')
                global max_number
                max_number = int(data_text[begin_index_total + 8:end_index_total - 1])
            except Exception as e:
                logger.error("获取第{}页股票列表异常:{}", pn, str(e))
                return pd.DataFrame()

        begin_index = data_text.index('[')
        end_index = data_text.index(']')
        data_json = data_text[begin_index:end_index + 1]
        data_json = json.loads(data_json)
        if data_json is None:
            return pd.DataFrame()
        else:
            result_df = pd.DataFrame(data_json)
            result_df['page_number'] = pn
            return result_df
    except Exception as e:
        logger.error("获取第{}页股票列表异常:{}", pn, str(e))
        return pd.DataFrame()


def repeated_acquisition_ask(per_page, max_number, time_out, max_workers=5):
    total_pages = (max_number + per_page - 1) // per_page  # 向上取整
    result_df = pd.DataFrame()
    df_lock = Lock()  # 线程安全的DataFrame合并锁

    def fetch_pages(page_nums):
        """单个线程处理一组页面，复用代理IP直到失效"""
        proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
        proxies = {"https": proxy_ip, "http": proxy_ip}
        thread_results = []  # 线程内临时存储结果

        for page_num in page_nums:
            while True:  # 重试循环（复用当前IP）
                try:
                    page_df = get_stock_page_data_time_out(
                        page_num, proxies, per_page, time_out
                    )
                    if data_frame_util.is_not_empty(page_df):
                        logger.info("线程{} 页面{}获取成功（IP复用中）",
                                    threading.get_ident(), page_num)
                        thread_results.append(page_df)
                        break  # 成功后继续用当前IP处理下一页
                    else:
                        logger.warning("页面数据为空:{},重试中...", page_num)
                        # 数据为空，更换IP
                        proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
                        proxies = {"https": proxy_ip, "http": proxy_ip}
                        time.sleep(0.2)
                except BaseException as e:
                    logger.error("线程{} 页面{}获取异常[{}]，更换IP重试",
                                 threading.get_ident(), page_num, str(e))
                    # 发生异常，更换IP
                    proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
                    proxies = {"https": proxy_ip, "http": proxy_ip}
                    time.sleep(1)
        return thread_results

    # 页面分配：平均分配给每个线程
    def split_pages(total, workers):
        pages = list(range(1, total + 1))
        avg = total // workers
        remainder = total % workers
        split = []
        start = 0
        for i in range(workers):
            end = start + avg + (1 if i < remainder else 0)
            split.append(pages[start:end])
            start = end
        return split

    # 分配页面组
    page_groups = split_pages(total_pages, max_workers)

    # 多线程执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_pages, group) for group in page_groups]

        # 合并结果
        for future in as_completed(futures):
            try:
                thread_dfs = future.result()
                if thread_dfs:
                    with df_lock:
                        result_df = pd.concat([result_df] + thread_dfs, ignore_index=True)
            except Exception as e:
                logger.error("线程结果处理失败:{}", str(e))

    return result_df


def repeated_acquisition_ask_sync(time_out):
    per_page = PAGE_SIZE
    total_pages = (max_number + per_page - 1) // per_page  # 向上取整
    result_df = pd.DataFrame()
    now_page = 1
    proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
    while now_page <= total_pages:
        proxies = {"https": proxy_ip,
                   "http": proxy_ip}
        try:
            page_df = get_stock_page_data_time_out(now_page, proxies, PAGE_SIZE, time_out)
            if data_frame_util.is_not_empty(page_df):
                result_df = pd.concat([page_df, result_df])
                logger.info("获取页面数据成功:{}", now_page)
                now_page = now_page + 1
            else:
                time.sleep(0.2)
                proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
                logger.info("获取页面数据失败:{}", now_page)
        except BaseException as e:
            time.sleep(1)
            proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
        # 示例调用
    return result_df


def repeated_acquisition_ask_async(time_out, max_number, num_threads, pages_per_thread):
    per_page = PAGE_SIZE
    total_pages = (max_number + per_page - 1) // per_page  # 向上取整
    result_df = pd.DataFrame()

    # 创建线程锁以确保线程安全
    df_lock = Lock()

    # 计算每个线程处理的页数范围
    def process_page_range(start_page, end_page, thread_id):
        nonlocal result_df
        local_df = pd.DataFrame()
        current_page = start_page
        proxy_ip = proxy_common_api.generate_proxy_ip_api(1)

        while current_page <= end_page and current_page <= total_pages:
            proxies = {"https": proxy_ip, "http": proxy_ip}
            try:
                page_df = get_stock_page_data_time_out(current_page, proxies, PAGE_SIZE, time_out)
                if data_frame_util.is_not_empty(page_df):
                    local_df = pd.concat([local_df, page_df])
                    logger.info("线程{}获取页面数据成功: {}", thread_id, current_page)
                    current_page += 1
                else:
                    time.sleep(0.2)
                    proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
                    logger.info("线程{}获取页面数据失败: {}", thread_id, current_page)
            except BaseException as e:
                time.sleep(1)
                proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
                logger.error("线程{}处理页面{}时发生错误: {}", thread_id, current_page, e)

        with df_lock:
            result_df = pd.concat([result_df, local_df])
        return len(local_df)

    # 计算每个线程的页面范围
    page_ranges = []
    for i in range(num_threads):
        start_page = i * pages_per_thread + 1
        end_page = (i + 1) * pages_per_thread
        if start_page > total_pages:
            break
        page_ranges.append((start_page, end_page, i + 1))

    # 使用线程池执行任务
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 提交所有任务
        futures = [
            executor.submit(process_page_range, start, end, tid)
            for start, end, tid in page_ranges
        ]

        # 等待所有任务完成并获取结果
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error("线程执行出错: {}", e)

    return rename_real_time_quotes_df(result_df)


def rename_real_time_quotes_df(temp_df):
    temp_df = temp_df.rename(columns={
        "f2": "now_price",
        "f3": "chg",
        "f5": "volume",
        "f6": "amount",
        "f8": "exchange",
        "f10": "quantity_ratio",
        "f22": "up_speed",
        "f11": "up_speed_05",
        "f12": "symbol",
        "f14": "name",
        "f15": "high",
        "f16": "low",
        "f17": "open",
        "f18": "yesterday_price",
        "f20": "total_mv",
        "f21": "flow_mv",
        "f26": "list_date",
        "f33": "wei_bi",
        "f34": "outer_disk",
        "f35": "inner_disk",
        "f62": "today_main_net_inflow",
        "f66": "super_large_order_net_inflow",
        "f69": "super_large_order_net_inflow_ratio",
        "f72": "large_order_net_inflow",
        # "f78": "medium_order_net_inflow",
        # "f84": "small_order_net_inflow",
        "f100": "industry",
        # "f103": "concept",
        "f184": "today_main_net_inflow_ratio",
        "f352": "average_price",
        "f211": "buy_1_num",
        "f212": "sell_1_num"
    })
    if data_frame_util.is_empty(temp_df):
        return pd.DataFrame()
    else:
        temp_df.loc[temp_df['buy_1_num'] == '-', 'buy_1_num'] = 0
        temp_df.loc[temp_df['sell_1_num'] == '-', 'sell_1_num'] = 0
        temp_df.loc[temp_df['up_speed_05'] == '-', 'up_speed_05'] = 0
        temp_df.loc[temp_df['up_speed'] == '-', 'up_speed'] = 0
        temp_df.loc[temp_df['average_price'] == '-', 'average_price'] = 0
        temp_df.loc[temp_df['wei_bi'] == '-', 'wei_bi'] = 0
        temp_df.loc[temp_df['yesterday_price'] == '-', 'yesterday_price'] = 0
        temp_df.loc[temp_df['now_price'] == '-', 'now_price'] = 0
        temp_df.loc[temp_df['chg'] == '-', 'chg'] = 0
        temp_df.loc[temp_df['volume'] == '-', 'volume'] = 0
        temp_df.loc[temp_df['amount'] == '-', 'amount'] = 0
        temp_df.loc[temp_df['exchange'] == '-', 'exchange'] = 0
        temp_df.loc[temp_df['quantity_ratio'] == '-', 'quantity_ratio'] = 0
        temp_df.loc[temp_df['high'] == '-', 'high'] = 0
        temp_df.loc[temp_df['low'] == '-', 'low'] = 0
        temp_df.loc[temp_df['open'] == '-', 'open'] = 0
        temp_df.loc[temp_df['total_mv'] == '-', 'total_mv'] = 0
        temp_df.loc[temp_df['flow_mv'] == '-', 'flow_mv'] = 0
        temp_df.loc[temp_df['inner_disk'] == '-', 'inner_disk'] = 0
        temp_df.loc[temp_df['outer_disk'] == '-', 'outer_disk'] = 0
        temp_df.loc[temp_df['today_main_net_inflow_ratio'] == '-', 'today_main_net_inflow_ratio'] = 0
        temp_df.loc[temp_df['today_main_net_inflow'] == '-', 'today_main_net_inflow'] = 0
        temp_df.loc[temp_df['super_large_order_net_inflow'] == '-', 'super_large_order_net_inflow'] = 0
        temp_df.loc[temp_df['super_large_order_net_inflow_ratio'] == '-', 'super_large_order_net_inflow_ratio'] = 0
        temp_df.loc[temp_df['large_order_net_inflow'] == '-', 'large_order_net_inflow'] = 0
        # temp_df.loc[temp_df['medium_order_net_inflow'] == '-', 'medium_order_net_inflow'] = 0
        # temp_df.loc[temp_df['small_order_net_inflow'] == '-', 'small_order_net_inflow'] = 0

        temp_df["list_date"] = pd.to_numeric(temp_df["list_date"], errors="coerce")
        temp_df["wei_bi"] = pd.to_numeric(temp_df["wei_bi"], errors="coerce")
        temp_df["average_price"] = pd.to_numeric(temp_df["average_price"], errors="coerce")
        temp_df["yesterday_price"] = pd.to_numeric(temp_df["yesterday_price"], errors="coerce")
        temp_df["now_price"] = pd.to_numeric(temp_df["now_price"], errors="coerce")
        temp_df["chg"] = pd.to_numeric(temp_df["chg"], errors="coerce")
        temp_df["volume"] = pd.to_numeric(temp_df["volume"], errors="coerce")
        temp_df["amount"] = pd.to_numeric(temp_df["amount"], errors="coerce")
        temp_df["exchange"] = pd.to_numeric(temp_df["exchange"], errors="coerce")
        temp_df["quantity_ratio"] = pd.to_numeric(temp_df["quantity_ratio"], errors="coerce")
        temp_df["high"] = pd.to_numeric(temp_df["high"], errors="coerce")
        temp_df["low"] = pd.to_numeric(temp_df["low"], errors="coerce")
        temp_df["open"] = pd.to_numeric(temp_df["open"], errors="coerce")
        temp_df["total_mv"] = pd.to_numeric(temp_df["total_mv"], errors="coerce")
        temp_df["flow_mv"] = pd.to_numeric(temp_df["flow_mv"], errors="coerce")
        temp_df["outer_disk"] = pd.to_numeric(temp_df["outer_disk"], errors="coerce")
        temp_df["inner_disk"] = pd.to_numeric(temp_df["inner_disk"], errors="coerce")
        temp_df["today_main_net_inflow"] = pd.to_numeric(temp_df["today_main_net_inflow"], errors="coerce")
        temp_df["super_large_order_net_inflow"] = pd.to_numeric(temp_df["super_large_order_net_inflow"],
                                                                errors="coerce")
        temp_df["super_large_order_net_inflow_ratio"] = pd.to_numeric(temp_df["super_large_order_net_inflow_ratio"],
                                                                      errors="coerce")
        temp_df["large_order_net_inflow"] = pd.to_numeric(temp_df["large_order_net_inflow"],
                                                          errors="coerce")
        # temp_df["medium_order_net_inflow"] = pd.to_numeric(temp_df["medium_order_net_inflow"],
        #                                                    errors="coerce")
        # temp_df["small_order_net_inflow"] = pd.to_numeric(temp_df["small_order_net_inflow"], errors="coerce")

        # 大单比例
        temp_df['large_order_net_inflow_ratio'] = round((temp_df['large_order_net_inflow'] / temp_df['amount']) * 100,
                                                        2)

        # 外盘是内盘倍数
        temp_df['disk_ratio'] = round((temp_df['outer_disk'] - temp_df['inner_disk']) / temp_df['inner_disk'], 2)
        # 只有外盘没有内盘
        temp_df.loc[temp_df["inner_disk"] == 0, ['disk_ratio']] = 1688
        temp_df = temp_df.sort_values(by=['chg'], ascending=False)
        return temp_df


def get_stock_real_time_quotes(time_out, pages_per_thread):
    try_numer = 3
    while try_numer > 0:
        proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
        proxies = {"https": proxy_ip,
                   "http": proxy_ip}

        total_number = get_stocks_num(1, proxies, 20, time_out)
        if total_number > 0:
            break
        try_numer = try_numer - 1
    if total_number == 0:
        return pd.DataFrame()

    total_pages = (max_number + PAGE_SIZE - 1) // PAGE_SIZE  # 向上取整

    num_threads = int((total_pages / pages_per_thread) + 1)
    return repeated_acquisition_ask_async(time_out, max_number, num_threads, pages_per_thread)


if __name__ == '__main__':

    while True:
        # proxy_ip = proxy_common_api.generate_proxy_ip_api(1)
        # proxies = {"https": proxy_ip,
        #            "http": proxy_ip}
        time_out = 10  # Set the timeout value
        result = get_stock_real_time_quotes(time_out, 10)
        print(result)
