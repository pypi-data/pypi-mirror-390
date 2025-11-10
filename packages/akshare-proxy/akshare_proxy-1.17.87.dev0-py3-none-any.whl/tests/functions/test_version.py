import akshare as ak
from akshare.utils.context import AkshareConfig


def test_func():
    print("Start Test")

    """ 创建代理字典 """
    proxies = {
        "http": "http://415b8ce2027f2686bd2d__cr.cn,hk:1207de794b991714@proxy.cheapproxy.net:823",
        "https": "http://415b8ce2027f2686bd2d__cr.cn,hk:1207de794b991714@proxy.cheapproxy.net:823"
    }
    """ 创建代理字典 """
    AkshareConfig.set_proxies(proxies)

    hk_short_sale = ak.stock_hk_short_sale(start_date="20120901", end_date="20121019")
    print(hk_short_sale)




if __name__ == '__main__':
    print(ak.__version__)
    test_func()
