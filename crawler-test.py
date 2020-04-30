import pandas as pd
from bs4 import BeautifulSoup as bs
import urllib.request as req
from selenium import webdriver
from flask import Flask,jsonify
from flask import request as fk_re
from flask_pymongo import PyMongo
import sys
import os
import re
import json
import requests
import time
from datetime import date, timedelta, datetime
import base64
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
options = Options()
# Use Selenium without opening the browser
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome()
web_url = "https://rent.591.com.tw/?kind=0&region" #Go to this URL
region_li= ['1','3']
data_dict={}
# driver.find_element_by_xpath('//dd[contains(text(),"台北市"]').click()
# driver.find_element_by_link_text('2').click()

app = Flask(__name__)

def main():
    for region in region_li: # Run the region you want
        driver.get(f"{web_url}={region}") # Go to this website
        time.sleep(3)
        soup = bs(driver.page_source,'lxml') # Get the web front-end code
        page_li = soup.find_all('a', attrs={'class': 'pageNum-form'}) # Find all pages
        for page_no in range(int(page_li[-1].text)): # Run page from 1 to last
            page = page_no+1
            if page != 1:
                driver.find_element_by_link_text(f"{page}").click() # Click the page text
                time.sleep(3)
                soup = bs(driver.page_source,'lxml') 
            # Find all rental information list on this page.
            rent_li = soup.find_all('li', attrs={'class': 'pull-left infoContent'}) 
            for rent_info in rent_li: # Rental detail URL
                # Get the detail page html label
                soup_detail = request_detail(rent_info)
                # Find and process rental price, house and user info
                price_string(soup_detail)
                house_info(soup_detail)
                other_info(soup_detail)
                # Insert data to mongodb
                insert_mongodb(data_dict)

def request_detail(rent_info):
    url= f"https:{rent_info.a.get('href').strip()}"
    request = req.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"
    })
    with req.urlopen(request) as res:
        detail_html = res.read().decode("utf-8")
    soup_detail = bs(detail_html,'lxml') 
    return soup_detail

def price_string(soup_detail):
    price = soup_detail.find('div', attrs={'class': 'price clearfix'})
    price_value = price.text
    price_num = [int(s) for s in price_value.replace(',','').split() if s.isdigit()][0]
    data_dict['price']= price_num
    # return price_num

def house_info(soup_detail):
    detail_info = soup_detail.find('div', attrs={'class': 'detailInfo clearfix'}) 
    attr = detail_info.find('ul', attrs={'class': 'attr'}) 
    attr_li = attr.findChildren("li" , recursive=False)
    for att_de in attr_li:
        if '型態' in att_de.text:
            data_dict['house_type']= string_dealer(att_de.text[6:])
        if '現況' in att_de.text:
            data_dict['curr_status']= string_dealer(att_de.text[6:])

def user_info(soup_detail):
    user_detail = soup_detail.find('div', attrs={'class': 'userInfo'}) 
    user = user_detail.find('div', attrs={'class': 'avatarRight'}) 
    user_text = strQ2B(user.text)
    user_identity= user_text[user_text.find('(')+1:user_text.find(')')] 
    data_dict['user_identity']= string_dealer(user_identity)
    user_name = user_text[:user_text.find('(')]
    data_dict['user_name']= string_dealer(user_name)
    phone = user_detail.find('span', attrs={'class': 'dialPhoneNum'}) 
    if phone:
        phone_num = phone.get('data-value')
        data_dict['phone_num']= string_dealer(phone_num)

def other_info(soup_detail):
    other_info = soup_detail\
                .find('ul', attrs={'class': 'clearfix labelList labelList-1'})\
                .find_all('li')
    for other in other_info:
        if '性別要求' in other.text:
            data_dict['gender']= string_dealer(other.text[5:])
    # print(data_dict)

def string_dealer(mix_string):
    ok_string = mix_string.strip('\n').strip(' ')
    return ok_string

def strQ2B(ustring):
    # Transform fullwidth to halfwidth
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # Fullwidth blank space transformation
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374): 
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

def mongodb_conn():
    mongo = PyMongo(app, uri="mongodb://admin:1234@cluster-test-shard-00-00-vlbbu.mongodb.net:27017,cluster-test-shard-00-01-vlbbu.mongodb.net:27017,cluster-test-shard-00-02-vlbbu.mongodb.net:27017/test?ssl=true&replicaSet=Cluster-test-shard-0&authSource=admin&retryWrites=true&w=majority",
    connect=True)
    return mongo

def insert_mongodb(data_dict):
    mongo = mongodb_conn()
    collect = mongo.db.rent_collection
    rent_data = data_dict
    # Insert Data 
    collect.insert_one(rent_data) 
    



@app.route('/')
def home():
    return "Hello Flask"


@app.route('/detail/telephone/<phone>', methods=['GET'])
def mongo_query(phone):
    result_li =[]
#     phone = '0986-851-077'
    mongo = mongodb_conn()
    collection = mongo.db.rent_collection 
    online_users = collection.find(
        {"gender": {'$ne':'女生'},
         "user_identity": {'$not':{"$regex" : "屋主.*"}},
         "phone_num": {"$regex" : f'{phone}.*'}
        },
        {'_id':0}
    )
    for i in online_users:
        print(i)
        result_li.append(i)
        mongo_data = json.dumps(result_li,ensure_ascii=False).encode('utf8')
    return mongo_data

if __name__== "__main__":
    main()
    app.run()










