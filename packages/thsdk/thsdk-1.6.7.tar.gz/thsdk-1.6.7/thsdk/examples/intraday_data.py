from thsdk import THS
import pandas as pd
import time

with THS() as ths:
    response = ths.intraday_data("USZA300033")
    print("股票日内分时数据:")
    if not response.is_success():
        print(f"错误信息: {response.err_info}")

    df = pd.DataFrame(response.get_result())
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    print(df)
    time.sleep(1)

    response = ths.intraday_data("USHI1A0001")
    print("指数日内分时数据:")
    if not response.is_success():
        print(f"错误信息: {response.err_info}")

    df = pd.DataFrame(response.get_result())
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    print(df)
    time.sleep(1)
