import datetime
import os

import betfairlightweight as bf
import pandas as pd
from betfairlightweight.filters import market_filter
from pandas import DataFrame as df

from scraper_models import Scraper


class BetfairEx(Scraper):
    def __init__(self, username, password, app_key, certs=None):
        super().__init__(name='Betfair', url='https://www.betfair.com/', id=1)
        self.client = None
        self.username = username
        self.password = password
        self.app_key = app_key
        self.certs = certs

    def search(self):
        pass

    def scrape(self):
        pass

    def json(self):
        pass

    def get_client(self):
        if not self.client:
            self.client = bf.APIClient(username=self.username,
                                       password=self.password,
                                       app_key=self.app_key,
                                       certs=self.certs)
            self.client.login()
        return self.client

    # def get_account_id(self):
    #     client = self.get_client
    #     accounts = client.get_accounts()
    #     return accounts[0]['id']
    #
    # def get_wallet_id(self):
    #     client = self.get_client()
    #     account_id = self.get_account_id()
    #     wallets = client.get_wallets(account_id)
    #     return wallets[0]['id']
    #
    # def get_transactions(self):
    #     client = self.get_client()
    #     wallet_id = self.get_wallet_id()
    #     transactions = client.get_transactions(wallet_id)
    #     return transactions

    def get_sports(self):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        event_types = client.betting.list_event_types()

        sport_ids = df({
            'name': [event_type_object.event_type.name for event_type_object in event_types],
            'scraped_id': [event_type_object.event_type.id for event_type_object in event_types]
        })

        return sport_ids

    def get_leagues(self, sport_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        leagues = client.betting.list_competitions(market_filter(event_type_ids=[sport_id]))

        league_ids = df({
            'name': [league_object.competition.name for league_object in leagues],
            'scraped_id': [league_object.competition.id for league_object in leagues]
        })

        return league_ids

    def get_events(self, league_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        events = client.betting.list_events(market_filter(competition_ids=[league_id]))

        event_ids = df({
            'name': [event_object.event.name for event_object in events],
            'scraped_id': [event_object.event.id for event_object in events],
            'date': [event_object.event.open_date.date() for event_object in events],
            'time': [event_object.event.open_date.time() for event_object in events]
        })

        return event_ids

    def get_market_types(self, sport_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        market_categories = client.betting.list_market_types(market_filter(event_type_ids=[sport_id]))

        market_category_ids = df({
            'name': [market_category_object.market_type for market_category_object in market_categories]
            # 'scraped_id': [market_category_object.market_type.id for market_category_object in market_categories]
        })

        return market_category_ids

    def get_match_markets(self, event_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        markets = client.betting.list_market_catalogue(market_filter(event_ids=[event_id]), max_results=100)

        # market_ids = df({
        #     'name': [market_object.market_definition.name for market_object in markets],
        #     'scraped_id': [market_object.market_definition.id for market_object in markets]
        # })
        markets_df = df({
            'name': [market_object.market_name for market_object in markets],
            'scraped_id': [market_object.market_id for market_object in markets]
        })

        return markets_df

    def get_match_markets_detailed(self, event_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        markets = client.betting.list_market_book(market_filter(event_ids=[event_id]))

        # market_ids = df({
        #     'name': [market_object.market_definition.name for market_object in markets],
        #     'scraped_id': [market_object.market_definition.id for market_object in markets]
        # })
        markets_df = df({
            'name': [market_object.market_name for market_object in markets],
            'scraped_id': [market_object.market_id for market_object in markets]
        })
        c = markets[0].market_book
        return markets_df

    def get_specific_mat_markets(self, event_id, market_type_str):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        markets = client.betting.list_market_catalogue(market_filter(event_ids=[event_id], market_type_codes=[market_type_str]))

        markets_df = df({
            'name': [market_object.market_name for market_object in markets],
            'scraped_id': [market_object.market_id for market_object in markets]
        })

        return markets_df

    def get_market_book(self, market_id):
        client = self.get_client()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the
        # name of the sport
        market_book = client.betting.list_market_book(market_ids=[market_id])

        return market_book



