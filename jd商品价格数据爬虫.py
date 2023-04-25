#!/usr/bin/env python
# coding: utf-8

# In[4]:


import requests
import pandas
from lxml import etree

class jd_commodity:
    def __init__(self, name):
        self.commodity_url = f"https://search.jd.com/Search?keyword={name}&enc=utf-8&wq={name}" 
    def jd_commodity_data(self):
        res_True = 1
        try:
            res = requests.get(self.commodity_url, timeout=3)
            while res_True:
                if res.text == None:
                    res = requests.get(self.commodity_url, timeout=3)
                else:
                    res_True = 0
        except requests.exceptions.Timeout:
            print('访问超时了')
            return
        page = int(input('输入需要提取的页数'))
        self.parse_data(res, self.commodity_url, page)
        print(f"提取数据成功")
    @staticmethod
    def parse_data(res, commodity_url, page):
        if res.status_code == 200:
            parsed = etree.HTML(res.text)
            print(parsed)
            categorys = parsed.xpath('//ul[@class="J_valueList"]/li/a/@title')
            categorys_url = parsed.xpath('//ul[@class="J_valueList"]/li/a/@data-v')
            categorys_all = dict(zip(categorys,categorys_url))
            print(categorys)
            kind =  input('请输入商品类别')
            category_is = 0
            res_categorys_url_all = []
            for category in categorys_all:
                if category == kind:
                    category_is = 1
                    res_categorys_url = [f"{commodity_url}&cid3={categorys_all[category]}&page={i}" for i in range(1, page+1)]
                    for url in res_categorys_url:
                        try:
                            res_categorys_url_all.append(requests.get(url, timeout = 3))
                        except ProxyError:
                            pass
                    break
                else:
                    while category_is == 0:
                        print('未查询到品种，是否继续提取 ,请重新输入')
                        kind = input('请输入')
                        for category in categorys_all:
                            if category == kind:
                                category_is = 1
                                res_categorys_url = [f"{commodity_url}&cid3={categorys_all[category]}&page={i}" for i in range(1, page+1)]
                                for url in res_categorys_url:
                                    try:
                                        res_categorys_url_all.append(requests.get(url, timeout = 3))
                                    except ProxyError:
                                        pass
                                break
                            else:
                                category_is = 0
            if category_is:
                print('正在跳转品种页面')
                price_all = []
                shop_all = []
                url_all = []
                for res_categorys in res_categorys_url_all:
                    if res_categorys.status_code ==200:
                        parsed_categorys = etree.HTML(res_categorys.text)
                        price = parsed_categorys.xpath('//div[@class="p-price"]/strong/i/text()')
                        shop = parsed_categorys.xpath('//div[@class="p-shop"]/span/a/text()')
                        url = parsed_categorys.xpath('//div[@class="p-name p-name-type-2"]/a/@href')
                        price_all += price
                        shop_all += shop
                        url_all += url
                    else:
                        print('访问出现问题')


        minprice, maxprice = float(input('请输入最低价')), float(input('请输入最高价'))
        serial_number_choose = []
        for price_number, price in enumerate(price_all):
            try:
                serial_number_choose.append(price_number if float(price) else None)
            except ValueError:
                pass
        serial_number_choose_price = [i for i in serial_number_choose if minprice<= float(price_all[i])<= maxprice]
        print('正在进行价格升序排序')
        serial_number = sorted(serial_number_choose_price, key = lambda k : price_all[k])
        price_all = [price_all[i] for i in serial_number]
        shop_all = [shop_all[i] for i in serial_number]
        url_all = [url_all[i] for i in serial_number]
        all_project = list(zip(shop_all, url_all, price_all))
        print(all_project)
        shop_deduplication = []
        for i in all_project:
            in_it = 0
            for j in shop_deduplication:
                if i[0] == j[0]:
                    in_it = 1
                    break
            if not in_it:
                shop_deduplication.append(i)
                
        shop_all, url_all, price_all = zip(*shop_deduplication)
        data = pandas.DataFrame({
                            'shop':shop_all,
                            'url':url_all,
                            'price':price_all,
                        })
        header = ['shop', 'url', 'price']
        data.to_csv(r'D:\下载\jobleadchina.csv', index=False, mode='w', header=header)
            
if __name__ == '__main__':
    name = input('请输入商品名称')
    x = jd_commodity(name)
    x.jd_commodity_data()


# In[ ]:




