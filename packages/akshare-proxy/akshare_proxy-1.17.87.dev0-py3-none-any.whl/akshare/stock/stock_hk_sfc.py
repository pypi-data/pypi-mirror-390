#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/11/9 22:15
Desc: 香港证监会公示数据
https://www.sfc.hk/TC/
"""
import re
from functools import reduce
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup

from akshare.request import requests_get


def convert_date(str_date):
    """
    字符串日期格式转换：
    如： 2025年7月18日 -> 20250718； 2025年10月10日 -> 20251010
    """
    item = re.findall("[0-9]+", str_date)
    return f"{item[0]}{item[1]:0>2}{item[2]:0>2}"


def get_stock_short_sale_hk_report_list():
    """
    获取港股证监会卖空报告列表: 报告日期、报告CSV文件地址
    """
    root_url = "https://sc.sfc.hk/TuniS/www.sfc.hk/TC/Regulatory-functions/Market/Short-position-reporting/Aggregated-reportable-short-positions-of-specified-shares"
    r = requests_get(root_url)
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("tr", scope="row")
    url_rows = []
    for row in rows:
        items = row.find_all("td")
        if len(items) == 3:
            csv_date = convert_date(items[0].text)
            csv_url = items[2].find("a").get("href")
            url_rows.append([csv_date, csv_url])
    url_rows.reverse()
    return pd.DataFrame(url_rows, columns=["报告日期", "文件地址"])


def get_stock_short_sale_hk_report(url):
    """
    根据获取港股证监会卖空CSV文件地址，获取港股证监会卖空报告内容
    """
    csv_text = requests_get(url).text
    df = pd.read_csv(StringIO(csv_text))
    df["Date"] = df["Date"].apply(lambda d: d.replace("/", ""))
    df["Stock Code"] = df["Stock Code"].apply(lambda d: f"{d:05d}")
    df.columns = ["日期", "证券代码", "证券简称", "淡仓股数", "淡仓金额"]
    df = df[df["淡仓股数"] > 0]
    return df


def stock_hk_short_sale(
        start_date: str = "20120801", end_date: str = "20900101"
) -> pd.DataFrame:
    """
    香港证监会公示数据-卖空汇总统计
    https://www.sfc.hk/TC/Regulatory-functions/Market/Short-position-reporting/Aggregated-reportable-short-positions-of-specified-shares
    :param start_date: 开始统计时间
    :type start_date: str
    :param end_date: 结束统计时间
    :type end_date: str
    :return: 港股卖空数据
    :rtype: pandas.DataFrame
    """
    report_list = get_stock_short_sale_hk_report_list()
    report_list = report_list[(end_date >= report_list["报告日期"]) & (report_list["报告日期"] >= start_date)]

    # 读取卖空报告并存储
    df_list=[]
    for index, row in report_list.iterrows():
        row_date = row.iloc[0]
        row_url = row.iloc[1]
        df = get_stock_short_sale_hk_report(row_url)
        df["日期"] = pd.to_datetime(df["日期"], format="%d%m%Y").dt.strftime("%Y%m%d")
        df_list.append(df)

    # 日期数据合并
    return pd.concat(df_list, ignore_index=True)








