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
import pdb


# db = SqliteDatabase('bovada.db')
db = MySQLDatabase('my_app', user='root', password='admin1234',
                         host='69.55.54.79', port=3306)

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

db.connect()
db.create_tables([Bovada])


class Novada(scrapy.Spider):
    name = 'bovada'
    domain = 'https://www.bovada.lv'
    base_url = 'https://www.bovada.lv'
    sports_list = [
        'baseball',
        'basketball',
        'boxing',
        'cricket',
        'darts',
        'entertainment',
        'esports',
        'football',
        'futsal',
        'gaelic-games',
        'golf',
        'handball',
        'hockey',
        'horses-futures-props',
        'motor-sports',
        'numbers-game',
        'politics',
        'rugby-league',
        'rugby-union',
        'snooker',
        'soccer',
        'table-tennis',
        'tennis',
        'ufc-mma',
        'virtual-sports',
        'volleyball',
        'winter-olympics',
        'winter-sports'
    ]

    def start_requests(self):
        for sport in self.sports_list:
            uri = '/services/sports/event/v2/events/A/description/%s?marketFilterId=def&preMatchOnly=true' % (sport)
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
                        'name': entry['competitors'][0]['name'],
                        'competitorId': entry['competitors'][0]['id']
                    }

                    team2_name = {
                        'name': entry['competitors'][0]['name'],
                        'competitorId': entry['competitors'][0]['id']
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
                        content_list = dict()

                        for market_data in group['markets']:
                            if 'spread' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''
                                
                                for outcome in market_data['outcomes']:
                                    try:
                                        if outcome['competitorId'] == team1_name['competitorId']:
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['american']

                                            content_list[team1 + 'spread'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['american']
                                                
                                            content_list[team2 + 'spread'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['handicap'] + ')'

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['american']

                                        content_list['Draw'] = self.validate(draw_val)

                            if 'runline' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''

                                for outcome in market_data['outcomes']:
                                    try:
                                        if outcome['competitorId'] == team1_name['competitorId']:
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['american']

                                            content_list[team1 + 'spread'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['american']
                                                
                                            content_list[team2 + 'spread'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['handicap'] + ')'

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['american']

                                        content_list['Draw'] = self.validate(draw_val)


                            if 'moneyline' in market_data['description'].lower():
                                team1 = 'Team1_'
                                team2 = 'Team2_'
                                tmp_val1 = ''
                                tmp_val2 = ''

                                for outcome in market_data['outcomes']:
                                    try:
                                        if outcome['competitorId'] == team1_name['competitorId']:
                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['american']

                                            content_list[team1 + 'win'] = self.validate(tmp_val1)
                                        else:
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['american']
                                                
                                            content_list[team2 + 'win'] = self.validate(tmp_val2)
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['handicap'] + ')'

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['american']

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
                                            if 'status' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['status'].upper()

                                            if 'handicap' in outcome['price']:
                                                tmp_val1 = tmp_val1 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['price']['american']

                                            content_list[team1 + 'total'] = self.validate(tmp_val1)
                                        else:
                                            if 'status' in outcome['price']:
                                                tmp_val1 = tmp_val1 + outcome['status'].upper()
                                            if 'handicap' in outcome['price']:
                                                tmp_val2 = tmp_val2 + '(' + outcome['price']['handicap'] + ')'

                                            if 'american' in outcome['price']:
                                                tmp_val2 = tmp_val2 + outcome['price']['american']
                                                
                                            content_list[team2 + 'total'] = self.validate(tmp_val2)

                                        idx = idx + 1
                                    except:
                                        draw_val = ''
                                        if 'handicap' in outcome['price']:
                                            draw_val = draw_val + '(' + outcome['price']['handicap'] + ')'

                                        if 'american' in outcome['price']:
                                            draw_val = draw_val + outcome['price']['american']

                                        content_list['Draw'] = self.validate(draw_val)

                        # item = copy.deepcopy(content_list)
                        for content in content_list:
                            item[content] = content_list[content]

                        item['Team1_name'] = self.validate(team1_name['name'])
                        item['Team2_name'] = self.validate(team2_name['name'])
                        item['link'] = self.validate(self.domain + link);
                        item['event_id'] = self.validate(event_id)
                        item['Sport_name'] = self.validate(sport_name.replace('-', ' '))

                        item['Date'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%Y-%m-%d')
                        item['Time'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%H:%M')

                        existing_elements = Bovada.select().where(Bovada.event_id==item['event_id'])

                        # pdb.set_trace()
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

                                if 'handicap' in outcome['price']:
                                    tmp_val2 = tmp_val2 + '(' + outcome['price']['handicap'] + ')'

                                if 'american' in outcome['price']:
                                    tmp_val2 = tmp_val2 + outcome['price']['american']
                                    
                                content_list['team' + str(idx) + 'value'] = self.validate(tmp_val2)

                            item = content_list
                            item['Team1_name'] = ''
                            item['Team2_name'] = ''

                            item['link'] = self.validate(self.domain + link);
                            item['event_id'] = self.validate(event_id)
                            item['Sport_name'] = self.validate(sport_name.replace('-', ' '))

                            item['Date'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%Y-%m-%d')
                            item['Time'] = datetime.datetime.utcfromtimestamp(int(date_time) / 1000).strftime('%H:%M')
                            item['Team_list'] = json.dumps(content_list)

                            existing_elements = Bovada.select().where(Bovada.event_id==item['event_id'])

                            if len(existing_elements) > 0:
                                pdb.set_trace()
                                q = (Bovada.update({
                                        'link' : self.isEmpty(item['link']),
                                        'Date' : self.isEmpty(item['Date']),
                                        'Time' : self.isEmpty(item['Time']),
                                        'Team_list' : self.isEmpty(item['Team_list'])
                                    })
                                    .where(Bovada.event_id == item['event_id']))
                                q.execute()

                            else:
                                Bovada.create(link = self.isEmpty(item['link']),
                                    Sport_name = self.isEmpty(item['Sport_name']),
                                    Date = self.isEmpty(item['Date']),
                                    Time = self.isEmpty(item['Time']),
                                    event_id = self.isEmpty(item['event_id']),
                                    Team_list = self.isEmpty(item['Team_list']))
                        
                            yield item
                            
                            yield item
        # except:
        #     pass

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