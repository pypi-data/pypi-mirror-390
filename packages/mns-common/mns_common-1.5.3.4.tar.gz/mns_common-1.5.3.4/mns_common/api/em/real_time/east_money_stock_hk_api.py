import os
import sys

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import pandas as pd
from loguru import logger
import requests
import time
import numpy as np
import mns_common.component.proxies.proxy_common_api as proxy_common_api
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import mns_common.utils.data_frame_util as data_frame_util
import json
import mns_common.component.cookie.cookie_info_service as cookie_info_service

# 最大返回条数
max_number = 4500
# 最小返回条数
min_number = 4400
# 分页条数
page_number = 100

fields = ("f352,f2,f3,f5,f6,f8,f10,f11,f22,f12,f14,f15,f16,f17,f18,f20,f21,f26,"
          "f33,f34,f35,f62,f66,f69,f72,f100,f184,f211,f212")


def hk_real_time_quotes_page_df(cookie, pn, proxies):
    try:
        headers = {
            'Cookie': cookie
        }

        current_timestamp = str(int(round(time.time() * 1000, 0)))

        url_new = ('https://61.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112409497467688484127_' + str(
            current_timestamp) +
                   '&pn=' + str(pn) +
                   '&pz=50000'
                   '&po=1'
                   '&np=3'
                   '&ut=bd1d9ddb04089700cf9c27f6f7426281'
                   '&fltt=2'
                   '&invt=2'
                   '&wbp2u=4253366368931142|0|1|0|web'
                   '&fid=f12'
                   '&fs=m:116+t:3,m:116+t:4,m:116+t:1,m:116+t:2'
                   '&fields=' + fields +
                   '&_=' + str(current_timestamp))

        if proxies is None:
            r = requests.get(url_new, headers=headers)
        else:
            r = requests.get(url_new, headers=headers, proxies=proxies)
        result = r.content.decode("utf-8")

        if pn == 1:
            try:
                begin_index_total = result.index('"total":')

                end_index_total = result.index('"diff"')
                global max_number
                max_number = int(result[begin_index_total + 8:end_index_total - 1])
            except Exception as e:
                logger.error(f"获取第{pn}页港股列表异常: {e}")
                return pd.DataFrame()

        startIndex = result.index('"diff"')
        endIndex = result.index('}]}')

        result = result[startIndex + 7:endIndex + 2]

        data_json = json.loads(result)

        temp_df = pd.DataFrame(data_json)

        temp_df = temp_df.rename(columns={

            "f12": "symbol",
            "f14": "name",
            "f3": "chg",
            "f2": "now_price",
            "f5": "volume",
            "f6": "amount",
            "f8": "exchange",
            "f10": "quantity_ratio",
            "f22": "up_speed",
            "f11": "up_speed_05",

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
        temp_df['disk_diff_amount'] = round(
            (temp_df['outer_disk'] - temp_df['inner_disk']) * temp_df[
                "average_price"],
            2)
        return temp_df
    except Exception as e:
        logger.error("获取港股列表,实时行情异常:{}", e)
        return pd.DataFrame()


def thread_pool_executor(cookie, proxies):
    """
       使用多线程获取所有ETF数据
       """
    # 计算总页数，假设总共有1000条数据，每页200条

    per_page = page_number
    total_pages = (max_number + per_page - 1) // per_page  # 向上取整

    # 创建线程池
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交任务，获取每页数据
        futures = [executor.submit(hk_real_time_quotes_page_df, cookie, pn, proxies)
                   for pn in range(1, total_pages + 1)]

        # 收集结果
        results = []
        for future in futures:
            result = future.result()
            if not result.empty:
                results.append(result)

    # 合并所有页面的数据
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame()


def get_hk_real_time_quotes(cookie, proxies):
    # 获取第一页数据
    page_one_df = hk_real_time_quotes_page_df(cookie, 1, proxies)
    # 数据接口正常返回5600以上的数量
    if page_one_df.shape[0] > min_number:
        page_one_df.drop_duplicates('symbol', keep='last', inplace=True)
        return page_one_df
    else:
        page_df = thread_pool_executor(cookie, proxies)
        page_df.drop_duplicates('symbol', keep='last', inplace=True)
        return page_df





if __name__ == '__main__':
    em_cookie_test = cookie_info_service.get_em_cookie()
    test_df = get_ggt_real_time_quotes(em_cookie_test, 30, 6)
    print(test_df)
