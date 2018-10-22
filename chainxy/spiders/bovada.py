import json
import scrapy
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from lxml import etree
from chainxy.items import ChainItem
from lxml import html
import csv
import time
import math
from scrapy.contrib.exporter import CsvItemExporter
from peewee import *
import uuid
import urllib
import datetime
import copy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display

import pdb


db = SqliteDatabase('bovada.db')
# db = MySQLDatabase('my_app', user='root', password='Admin1234!@#$', host='localhost', port=3306)

class BaseModel(Model):
    class Meta:
        database = db

class Bovada(BaseModel):
    event_id = CharField(null=True)
    Date = CharField(null=True)
    Time = CharField(null=True)
    Sport_name = CharField(null=True)
    Date = CharField(null=True)
    Team1_name = CharField(null=True)
    Team1_points = CharField(null=True)
    Team1_spread = CharField(null=True)
    Team1_win = CharField(null=True)
    Team1_total = CharField(null=True)
    Team2_name = CharField(null=True)
    Team2_points = CharField(null=True)
    Team2_spread = CharField(null=True)
    Team2_win = CharField(null=True)
    Team2_total = CharField(null=True)
    Draw = CharField(null=True)
    link = CharField(null=True)
    Team_list = CharField(null=True)
    last_update = CharField(null=False)

db.connect()
db.create_tables([Bovada])


class Novada(scrapy.Spider):
    name = 'bovada'
    domain = 'https://www.bovada.lv'
    base_url = 'https://www.bovada.lv'
    sports_list = [
        'baseball',
        'basketball',
        'football',
        'soccer',
        'hockey',
        'tennis'
        'boxing',
        'cricket',
        'darts',
        'entertainment',
        'esports',
        'futsal',
        'gaelic-games',
        'golf',
        'handball',
        'horses-futures-props',
        'motor-sports',
        'numbers-game',
        'politics',
        'rugby-league',
        'rugby-union',
        'snooker',
        'table-tennis',
        'ufc-mma',
        'virtual-sports',
        'volleyball',
        'winter-olympics',
        'winter-sports'
    ]

    def __init__(self):
        # self.display = Display(visible=0, size=(1650, 1248))
        # self.display.start()
        #self.driver = webdriver.Firefox(executable_path='./geckodriver')
        # self.driver = webdriver.Chrome(executable_path="./chromedriver")


        prof = webdriver.FirefoxProfile()
        prof.set_preference('dom.webnotifications.enabled', False)

        opts = webdriver.FirefoxOptions()
        opts.set_headless(headless=True)

        self.driver = webdriver.Firefox( 
                firefox_profile=prof,
                firefox_options=opts,
                executable_path='./geckodriver')

        print(self.domain + '/sports?overlay=login')
        time.sleep(2)
        self.driver.get(self.domain + '/?overlay=login')
        try:
            element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='email']")))
        except:
            self.driver.save_screenshot('screenie.png')
            pdb.set_trace()
        element.send_keys('steven@hooley.me')
        self.driver.find_element_by_xpath("//input[@id='login-password']").send_keys('Access2017?')
        self.driver.find_element_by_xpath("//label[@id='remember-me-label']").click()
        self.driver.find_element_by_xpath("//button[@id='login-submit']").click()
        time.sleep(1)

    def spider_closed(self, spider):
        self.driver.quit()
        # self.display.stop()

    def start_requests(self):
        for sport in self.sports_list:
            uri = '/services/sports/event/v2/events/A/description/%s?marketFilterId=def&liveOnly=true' % (sport)
            req = scrapy.Request(url=self.domain + uri, callback=self.body)
            req.meta['sport_name'] = sport
            yield req

    def body(self, response):
        # try:
        res = json.loads(response.text)
        sport_name = response.meta['sport_name']

        for result in res:
            for entry in result['events']:
                event_id = entry['id']
                link = entry['link']
                if len(entry['competitors']) > 0:

                    team1_name = {
                        'name': self.validate(entry['competitors'][0]['name']),
                        'competitorId': self.validate(entry['competitors'][0]['id'])
                    }

                    team2_name = {
                        'name': self.validate(entry['competitors'][1]['name']),
                        'competitorId': self.validate(entry['competitors'][1]['id'])
                    }

                    date_time = entry['startTime']

                    for group in entry['displayGroups']:
                        item = ChainItem()
                        item['event_id'] = ''
                        item['Date'] = ''
                        item['Time'] = ''
                        item['Sport_name'] = ''
                        item['Team1_name'] = ''
                        item['Team1_points'] = ''
                        item['Team1_spread'] = ''
                        item['Team1_win'] = ''
                        item['Team1_total'] = ''
                        item['Team2_name'] = ''
                        item['Team2_points'] = ''
                        item['Team2_spread'] = ''
                        item['Team2_win'] = ''
                        item['Team2_total'] = ''
                        item['Draw'] = ''
                        item['link'] = ''
                        item['last_update'] = ''

                        content_list = dict()

                        for market_data in group['markets']:
                            if 'spread' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''
                                
                                for outcome in market_data['outcomes']:
                                    try:
                                        if outcome['competitorId'] == team1_name['competitorId'].decode():
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['handicap']

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['american'] + ')'

                                            content_list[team1 + 'spread'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['handicap']
                                                
                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['american'] + ')'

                                            content_list[team2 + 'spread'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['handicap']

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['american'] + ')'

                                        content_list['Draw'] = self.validate(draw_val)

                            if 'runline' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''

                                for outcome in market_data['outcomes']:
                                    try:
                                        if outcome['competitorId'] == team1_name['competitorId'].decode():
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['handicap']

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['american'] + ')'

                                            content_list[team1 + 'spread'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['handicap']
                                                
                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['american'] + ')'

                                            content_list[team2 + 'spread'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['handicap']

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['american'] + ')'

                                        content_list['Draw'] = self.validate(draw_val)

                            if 'moneyline' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''

                                for outcome in market_data['outcomes']:
                                    try:
                                        print('-------------\n')
                                        print(outcome, market_data)
                                        if outcome['competitorId'] == team1_name['competitorId'].decode():
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['handicap']

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['american'] + ')'

                                            content_list[team1 + 'win'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['handicap']
                                                
                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['american'] + ')'

                                            content_list[team2 + 'win'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['handicap']

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['american'] + ')'

                                        content_list['Draw'] = self.validate(draw_val)

                            if 'total' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''

                                idx = 0
                                for outcome in market_data['outcomes']:
                                    try:
                                        if idx == 0:
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['handicap']

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['american'] + ')'

                                            content_list[team1 + 'total'] = self.validate(tmp_val1)
                                        if idx == 1:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['handicap']
                                                
                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['american'] + ')'

                                            content_list[team2 + 'total'] = self.validate(tmp_val2)
                                        if idx == 2:
                                            draw_val = ''
                                            if 'handicap' in outcome['price']:
                                                draw_val = draw_val + outcome['price']['handicap']

                                            if 'american' in outcome['price']:
                                                draw_val = draw_val + '(' + outcome['price']['american'] + ')'

                                            content_list['Draw'] = self.validate(draw_val)
                                        idx = idx + 1
                                    except:
                                        pass
                                        

                        # item = copy.deepcopy(content_list)
                        for content in content_list:
                            item[content] = content_list[content]

                        item['Team1_name'] = team1_name['name']
                        item['Team2_name'] = team2_name['name']
                        item['event_id'] = self.validate(event_id)
                        item['Sport_name'] = self.validate(sport_name.replace('-', ' '))

                        item['Date'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%Y-%m-%d')
                        item['Time'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%H:%M')
                        #print(item)
                        
                        item['link'] = self.validate(self.domain +'/sports'+ link);
                        print(item)
                        # req = scrapy.Request(url=item['link'], callback=self.save_data)
                        # req.meta['item'] = item
                        # yield req
                        detail_url = ''
                        try:
                            detail_url = item['link'].decode()
                        except:
                            detail_url = item['link']

                        try:
                            self.driver.get(detail_url)
                        
                            time.sleep(3)
                            source = self.driver.page_source.encode("utf8")
                            tree = etree.HTML(source)

                            try:
                                item['Team1_points'] = self.validate(tree.xpath('//section[@class="coupon-content more-info"][1]//div[@class="results"]//span[@class="score-nr"][1]/text()')[0])
                            except:
                                item['Team1_points'] = ''

                            try:
                                item['Team2_points'] = self.validate(tree.xpath('//section[@class="coupon-content more-info"][1]//div[@class="results"]//span[@class="score-nr"][2]/text()')[0])
                            except:
                                item['Team2_points'] = ''
                            print('D*********************', item)
                        except:
                            pass

                        existing_elements = Bovada.select().where(Bovada.event_id==item['event_id'])
                        last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                        item['last_update'] = last_update
                        if len(existing_elements) > 0:
                            q = (Bovada.update({
                                    'link' : self.isEmpty(item['link']),
                                    'Date' : self.isEmpty(item['Date']),
                                    'Time' : self.isEmpty(item['Time']),
                                    'Team1_name' : self.isEmpty(item['Team1_name']),
                                    'Sport_name' : self.isEmpty(item['Sport_name']),
                                    'Team1_points' : self.isEmpty(item['Team1_points']),
                                    'Team1_spread' : self.isEmpty(item['Team1_spread']),
                                    'Team1_win' : self.isEmpty(item['Team1_win']),
                                    'Team1_total' : self.isEmpty(item['Team1_total']),
                                    'Team2_name' : self.isEmpty(item['Team2_name']),
                                    'Team2_points' : self.isEmpty(item['Team2_points']),
                                    'Team2_spread' : self.isEmpty(item['Team2_spread']),
                                    'Team2_win' : self.isEmpty(item['Team2_win']),
                                    'Team2_total' : self.isEmpty(item['Team2_total']),
                                    'Draw' : self.isEmpty(item['Draw']),
                                    'last_update': last_update
                                })
                                .where(Bovada.event_id == item['event_id']))
                            q.execute()

                        else:
                            Bovada.create(link = self.isEmpty(item['link']),
                                Sport_name = self.isEmpty(item['Sport_name']),
                                Date = self.isEmpty(item['Date']),
                                Time = self.isEmpty(item['Time']),
                                Team1_name = self.isEmpty(item['Team1_name']),
                                Team1_points = self.isEmpty(item['Team1_points']),
                                Team1_spread = self.isEmpty(item['Team1_spread']),
                                Team1_win = self.isEmpty(item['Team1_win']),
                                Team1_total = self.isEmpty(item['Team1_total']),
                                Team2_name = self.isEmpty(item['Team2_name']),
                                Team2_points = self.isEmpty(item['Team2_points']),
                                Team2_spread = self.isEmpty(item['Team2_spread']),
                                Team2_win = self.isEmpty(item['Team2_win']),
                                Team2_total = self.isEmpty(item['Team2_total']),
                                event_id = self.isEmpty(item['event_id']),
                                Draw = self.isEmpty(item['Draw']),
                                last_update=last_update)
                
                        yield item
        
                else:
                    date_time = entry['startTime']

                    for group in entry['displayGroups']:
                        item = ChainItem()
                        item['event_id'] = ''
                        item['Date'] = ''
                        item['Time'] = ''
                        item['Sport_name'] = ''
                        item['Team_list'] = ''
                        item['link'] = ''

                        content_list = dict()

                        for market_data in group['markets']:
                            idx = 0
                            for outcome in market_data['outcomes']:

                                content_list['team' + str(idx) + '_name'] = outcome['description']
                                tmp_val2 = ''

                                if 'american' in outcome['price']:
                                    tmp_val2 = tmp_val2 + '(' + outcome['price']['american'] + ')'

                                if 'handicap' in outcome['price']:
                                    tmp_val2 = tmp_val2 + outcome['price']['handicap']
                                    
                                content_list['team' + str(idx) + 'value'] = self.validate(tmp_val2)

                            item = content_list
                            item['Team1_name'] = ''
                            item['Team2_name'] = ''

                            item['link'] = self.validate(self.domain + link);
                            item['event_id'] = self.validate(event_id)
                            item['Sport_name'] = self.validate(sport_name.replace('-', ' '))

                            item['Date'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%Y-%m-%d')
                            item['Time'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%H:%M')
                            item['Team_list'] = json.dumps(self.validate(content_list))

                            existing_elements = Bovada.select().where(Bovada.event_id==item['event_id'])
                            last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                            item['last_update'] = last_update

                            if len(existing_elements) > 0:
                                q = (Bovada.update({
                                        'link' : self.isEmpty(item['link']),
                                        'Date' : self.isEmpty(item['Date']),
                                        'Time' : self.isEmpty(item['Time']),
                                        'Team_list' : self.isEmpty(item['Team_list']),
                                        'last_update' : last_update
                                    })
                                    .where(Bovada.event_id == item['event_id']))
                                q.execute()

                            else:
                                Bovada.create(link = self.isEmpty(item['link']),
                                    Sport_name = self.isEmpty(item['Sport_name']),
                                    Date = self.isEmpty(item['Date']),
                                    Time = self.isEmpty(item['Time']),
                                    event_id = self.isEmpty(item['event_id']),
                                    Team_list = self.isEmpty(item['Team_list']),
                                    last_update=last_update)
                        
                            yield item
        # except:
        #     pass

    def save_data(self, response):
        item = ChainItem()
        item = copy.deepcopy(response.meta['item'])

        item['Team1_points'] = self.validate(response.xpath('//section[@class="coupon-content more-info"][1]//div[@class="results"]//span[@class="score-nr"][1]/text()').extract_first())
        item['Team2_points'] = self.validate(response.xpath('//section[@class="coupon-content more-info"][1]//div[@class="results"]//span[@class="score-nr"][2]/text()').extract_first())
        existing_elements = Bovada.select().where(Bovada.event_id==item['event_id'])
        
        if len(existing_elements) > 0:
            q = (Bovada.update({
                    'link' : self.isEmpty(item['link']),
                    'Date' : self.isEmpty(item['Date']),
                    'Time' : self.isEmpty(item['Time']),
                    'Team1_name' : self.isEmpty(item['Team1_name']),
                    'Sport_name' : self.isEmpty(item['Sport_name']),
                    'Team1_points' : self.isEmpty(item['Team1_points']),
                    'Team1_spread' : self.isEmpty(item['Team1_spread']),
                    'Team1_win' : self.isEmpty(item['Team1_win']),
                    'Team1_total' : self.isEmpty(item['Team1_total']),
                    'Team2_name' : self.isEmpty(item['Team2_name']),
                    'Team2_points' : self.isEmpty(item['Team2_points']),
                    'Team2_spread' : self.isEmpty(item['Team2_spread']),
                    'Team2_win' : self.isEmpty(item['Team2_win']),
                    'Team2_total' : self.isEmpty(item['Team2_total']),
                    'Draw' : self.isEmpty(item['Draw'])
                })
                .where(Bovada.event_id == item['event_id']))
            q.execute()

        else:
            Bovada.create(link = self.isEmpty(item['link']),
                Sport_name = self.isEmpty(item['Sport_name']),
                Date = self.isEmpty(item['Date']),
                Time = self.isEmpty(item['Time']),
                Team1_name = self.isEmpty(item['Team1_name']),
                Team1_points = self.isEmpty(item['Team1_points']),
                Team1_spread = self.isEmpty(item['Team1_spread']),
                Team1_win = self.isEmpty(item['Team1_win']),
                Team1_total = self.isEmpty(item['Team1_total']),
                Team2_name = self.isEmpty(item['Team2_name']),
                Team2_points = self.isEmpty(item['Team2_points']),
                Team2_spread = self.isEmpty(item['Team2_spread']),
                Team2_win = self.isEmpty(item['Team2_win']),
                Team2_total = self.isEmpty(item['Team2_total']),
                event_id = self.isEmpty(item['event_id']),
                Draw = self.isEmpty(item['Draw']))
        
        yield item

    def validate(self, item):
        try:
            return item.strip().encode('utf-8')
        except:
            return ''

    def isEmpty(self, item):
        if item == '' or item == None:
            return ''
        else:
            return item
