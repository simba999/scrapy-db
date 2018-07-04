import json
import scrapy
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from lxml import etree
from lxml import html
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import math
from scrapy.contrib.exporter import CsvItemExporter
from collections import OrderedDict
from peewee import *
import uuid
import urllib
from selenium.webdriver.chrome.options import Options
import pdb


pg_db = MySQLDatabase('testdb', user='root', password='simba1234',host='localhost', port=3306)
pg_db.connect()

class BaseModel(Model):
    class Meta:
        database = pg_db

class Instacart(BaseModel):
    store_name = CharField(null=True, max_length=512)
    type = CharField(null=True, max_length=512)
    menu = CharField(null=True, max_length=512)
    menu_image = CharField(null=True, max_length=128)
    menu_item = CharField(null=True, max_length=512)
    description = TextField(null=True)
    quantity = CharField(null=True)
    price = CharField(null=True, max_length=512)
    menu_item_image = CharField(null=True, max_length=128)
    roles = TextField(null=True)
    url = TextField(null=True)

pg_db.create_tables([Instacart])

class Instacart(scrapy.Spider):
    name = 'instacart'
    domain = 'https://www.instacart.com'
    base_url = 'https://www.instacart.com/store/'
    history = ['']
    gcount = 0;
    total_count = 0;
    menu_list_url = []
    submenu_list_url = []

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--dns-prefetch-disable')
        self.driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)
        self.driver.set_window_size(1850, 1000)

    def start_requests(self):
        init_url  = 'https://python.org'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        detail_url = 'https://www.instacart.com'
        self.driver.get(detail_url)
        source = self.driver.page_source.encode("utf8")
        
        # self.driver.find_element_by_xpath('//input[@id="signup-zipcode"]').send_keys('94105')
        self.driver.find_element_by_xpath('//a[@class="login-link"]').click()
        
        self.driver.find_element_by_xpath('//input[@type="email"]').send_keys('coral1212@yahoo.com')
        self.driver.find_element_by_xpath('//input[@type="password"]').send_keys('kingsimba126!@')
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        
        ele = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="header-primary-nav-left"]//a[@class="primary-nav-link"]')))
        ele.click()
        time.sleep(2)
        source = self.driver.page_source.encode("utf8")
        tree = etree.HTML(source)

        pages = tree.xpath('//div[contains(@class, "retailer-chooser-retailer-option-list-wrapper")]//a[@class="retailer-option-inner-wrapper absolute-center"]')
        
                
        # scrape menu pages
        for entry in self.menu_list_url:
            self.driver.get(entry['menu_link'])
            time.sleep(1)
            # WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="filter-container"]')))

            source = self.driver.page_source.encode('utf-8')
            tree = etree.HTML(source)

            sub_menu_list = tree.xpath('//ul[@class="department-selector"]//li[@class="aisle"]//a/@href')

            for sub_menu in sub_menu_list[1:]:
                tmp = {}
                tmp['menu_link'] = entry['menu_link']
                tmp['menu_name'] = entry['menu_name']
                tmp['store_name'] = entry['store_name']
                tmp['menu_image'] = entry['menu_image']
                tmp['submenu_link'] = self.base_url + sub_menu.encode('utf-8')

                self.submenu_list_url.append(tmp)
        # except:
        #     print("store error")
        #     pdb.set_trace()

        with open('turls.csv', 'w') as csvfile:
            fieldnames = ["menu_name", "menu_link", "menu_image", "submenu_link", "store_name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for submenu in self.submenu_list_url:
                writer.writerow(submenu)


        try:
            histories = BackStage.select().where(BackStage.cid==item['cid'])

            flag = 0
            for entry in histories:
                if flag == 1:
                    entry.delete_instance()
                else:
                    print "%s is already in db" % (entry.cid)
                    flag = 1
            if flag == 0:
                BackStage.create(cid=item['cid'],
                    audition_locations=self.isEmpty(item['audition_locations']),
                    description=self.isEmpty(item['description']),
                    compensation=self.isEmpty(item['compensation']),
                    expires_utc=self.isEmpty(item['expires_utc']),
                    posted_date_utc=self.isEmpty(item['posted_date_utc']),
                    sponsored_start_datetime_utc=self.isEmpty(item['sponsored_start_datetime_utc']),
                    sponsored_end_datetime_utc=self.isEmpty(item['sponsored_end_datetime_utc']),
                    production_types=self.isEmpty(item['production_types']),
                    title=self.isEmpty(item['title']),
                    roles=self.isEmpty(item['roles']),
                    url=self.isEmpty(item['url']))
        except:
            pass

    def validate(self, item):
        try:
            return item.strip().replace(u'\u2014', '').replace(u'\u2022', '').replace(u'\xa0', ' ')
        except:
            return ''

    def isEmpty(self, item):
        if item == '' or item == None:
            return ''
        else:
            return item