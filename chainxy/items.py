# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ChainItem(Item):
    title=Field()
    updated_by=Field()
    latitude=Field()
    longitude=Field()
    accomodation_name = Field()
    accomodation_type=Field()
    accomodation_address = Field()
    number_of_bedrooms=Field()
    number_of_people=Field()
    star_rating=Field()
    review_rating = Field()
    review_rating_url=Field()
    bar=Field()
    restaurant=Field()
    parking_garage=Field()
    outdoor_parking=Field()
    spa_massage_onsen=Field()
    other=Field()
    sales_channel_sources=Field()
    marketing_sources=Field()
    photos=Field()
    videos=Field()
    audio=Field()
    url=Field()
