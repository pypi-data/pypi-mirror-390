#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
获取所有股票代码和名称并保存到CSV文件

该脚本会获取以下市场的股票数据：
- A股 (stock_cn_lists)
- 美股 (stock_us_lists) 
- 港股 (stock_hk_lists)
- 北交所 (stock_bj_lists)
- B股 (stock_b_lists)
- 纳斯达克 (nasdaq_lists)
"""

import os
import sys
import csv
import time
import pandas as pd
from datetime import datetime
from thsdk import THS


def main():
    """主函数"""
    print(f"开始获取A股所有股票数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with THS() as ths:
            # 获取A股板块数据
            response = ths.block_data(0xC6A6)
            df = pd.DataFrame(response.get_result())
            save_path ="./stocks.csv"
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(f"已保存到 {save_path}，共 {len(df)} 条记录")
    except Exception as e:
        print(f"程序执行出错: {e}")
        return


if __name__ == "__main__":
    main()
