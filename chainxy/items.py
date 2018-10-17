# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ChainItem(Item):
    event_id = Field()
    Date = Field()
    Time = Field()
    Sport_name = Field()
    Team1_name = Field()
    Team1_points = Field()
    Team1_spread = Field()
    Team1_win = Field()
    Team1_total = Field()
    Team2_name = Field()
    Team2_points = Field()
    Team2_spread = Field()
    Team2_win = Field()
    Team2_total = Field()
    Draw = Field()
    link = Field()
    Team_list = Field()
    last_update = Field()

