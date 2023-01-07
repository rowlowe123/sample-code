# Creating a dataSportBase that stores the statistics of players across multiple sports
import datetime

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Time, DateTime, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()
Base = declarative_base()


class SportBase(Base):
    """
    This is abstract class used to build all sqlalchemy models
    Contains methods to be used by all models
    """

    # Add a static reference to a session
    # This session will be used by all models
    # This will allow for a single session to be used for all models

    # Every table will have a created and name column, so create them here
    created = Column(DateTime, default=datetime.datetime.now)

    # name = Column(String(128), nullable=False)


    __abstract__ = True


    def __init__(self, name, created):
        # AttributeError: 'function' object has no attribute 'get'
        # Fix this by adding the polymorphic_on column to the table

        if name is not None:
            self.name = name
        if created is not None:
            self.created = created

    def __repr__(self):
        if self.name:

            return '<{}: {}>'.format(self.__class__.__name__,
                                     self.name)
        else:
            # return class name and id
            return '<{}: {}>'.format(self.__class__.__name__,
                                     self.id)

    # def __str__(self):
    #     return self.name

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def sub_to_db(self):
        """
        This method submits the object to the database using the session
        Overrides for this method should ensure the object is in the correct state before submission
        :param session: sqlalchemy session
        :return: Bool - True if successful, False if not
        """
        try:
            session.add(self)
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False

    def flush(self):
        """
        This method flushes the object to the database using the session
        Overrides for this method should ensure the object is in the correct state before submission
        :param session: sqlalchemy session
        :return: Bool - True if successful, False if not
        """
        try:
            session.flush()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False

    # Make static format_df method available to all models

    @staticmethod
    def format_df(df_no_format, drop_duplicates=True, drop_all_na=False, remove_all_redudant=False):
        """
        Standardize dataframes to a common format that matches the db schema.
        :param drop_all_na:
        :param remove_all_redudant:
        :param drop_duplicates:
        :param df_no_format:
        :param
        :return:
        """
        # Lowercase all column names
        df_no_format.columns = [x.lower() for x in df_no_format.columns]

        # Remove duplicate records
        if drop_duplicates:
            df_no_format.drop_duplicates(inplace=True)
        # Remove records with null values
        if drop_all_na:
            df_no_format.dropna(inplace=True)
        if remove_all_redudant:
            # Remove any columns where that are not directly specified in the db schema
            df_no_format = df_no_format[[col for col in df_no_format.columns if col in self.__table__.columns.keys()]]
        return df_no_format


class Statistic(SportBase):
    """
    This class represents a statistic that is associated with a player.
    """
    __tablename__ = 'statistic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    interval = Column(Integer, default=1)

    # Goals, Points, Assists, Corners, Free Throws, Tries, Runs, Handicap, Default=0
    @staticmethod
    def format_df(df_no_format):
        """
        Standardize dataframes to a common format that matches the db schema.
        :param df_no_format:
        :return:
        """
        super().format_df(df_no_format)
        # Read stat map from csv
        stat_map = pd.read_csv('stat_map.csv')
        # Remove all columns that are not in the stat_map
        df = df_no_format[[col for col in df_no_format.columns if col in stat_map['statistic_name'].values]]

        return df_no_format


class Player(SportBase):
    """
    This class represents a player.
    """
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(32), nullable=False)
    name = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False)
    primary_position = Column(String(32))  # Turn into position table list

    def __init__(self, name, full_name=None, is_active=None, primary_position=None, created=None):
        super().__init__(name, created)
        if full_name is not None:
            self.full_name = full_name
        if is_active is not None:
            self.is_active = is_active
        if primary_position is not None:
            self.primary_position = primary_position

    def format_df(df_no_format):
        """
        Standardize dataframes to a common format that matches the db schema.
        :param df_no_format:
        :return:
        """
        # df = super().format_df(df_no_format, drop_duplicates=True, drop_all_na=False, remove_all_redudant=False)
        # drop dupesa
        df_no_format.drop_duplicates(inplace=True)
        # lowercase all column names
        df_no_format.columns = [x.lower() for x in df_no_format.columns]
        # Set as df
        df = df_no_format
        # Convert player_name to name
        df.rename(columns={'player_name': 'name'}, inplace=True)
        # Convert player_id to scraped_id
        df.rename(columns={'player_id': 'scraped_id'}, inplace=True)
        # Copy name to full_name if full_name is null
        # if not column full_name exists, create it
        if 'full_name' not in df.columns:
            df['full_name'] = df['name']
        # Set is_active to true if not specified
        if 'is_active' not in df.columns:
            df['is_active'] = True
        # Set primary_position to null if not specified
        if 'primary_position' not in df.columns:
            df['primary_position'] = ''

        return df


class Source(SportBase, Base):
    """
    This class represents a source.
    """
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    url = Column(String(32), nullable=False)
    is_predictive = Column(Boolean, nullable=False)

    def __init__(self, name, url, is_predictive, created=None):
        super().__init__(name, created)
        self.name = name
        self.url = url
        self.is_predictive = is_predictive


class Sport(SportBase):
    """
    This class represents a sport.
    """
    __tablename__ = 'sport'
    id = Column(Integer, primary_key=True, autoincrement=True, sqlite_on_conflict_primary_key='IGNORE')
    name = Column(String(32), nullable=False, unique=True)

    # def __init__(self, name, created=None):
    #     super().__init__(name, created)


class League(SportBase, Base):
    """
    This class represents a league.
    """
    __tablename__ = 'league'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    sport_id = Column(Integer, ForeignKey('sport.id'))
    sport = relationship(Sport, backref='leagues')

    # def __init__(self, name):
    #     self.name = name


class Team(SportBase):
    """
    This class represents a team.
    """
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    abbreviated_name = Column(String(8), nullable=False)
    short_name = Column(String(32))

    def __init__(self, name=None, abbreviated_name=None, short_name=None, created=None):
        super().__init__(name, created)
        if abbreviated_name is not None:
            self.abbreviated_name = abbreviated_name
        if short_name is not None:
            self.short_name = short_name

    @staticmethod
    def format_df(df_no_format):
        """
        Standardize dataframes to a common format that matches the db schema.
        :param df_no_format:
        :return:
        """
        df_teams = super().format_df(df_no_format, True, True)
        # Rename columns
        # Convert all columns to lower
        df_teams.columns = df_teams.columns.str.lower()
        # Rename columns if exist
        if 'id' in df_teams.columns:
            df_teams = df_teams.rename(columns={'id': 'scraped_id'})
        if 'full_name' in df_teams.columns:
            df_teams = df_teams.rename(columns={'full_name': 'name'})
        if 'abbreviation' in df_teams.columns:
            df_teams = df_teams.rename(columns={'abbreviation': 'abbreviated_name'})
        if 'team_id' in df_teams.columns:
            df_teams = df_teams.rename(columns={'team_id': 'scraped_id'})
        if 'team_abbreviation' in df_teams.columns:
            df_teams = df_teams.rename(columns={'team_abbreviation': 'abbreviated_name'})
        if 'team_city' in df_teams.columns:
            df_teams = df_teams.rename(columns={'team_city': 'city'})
        if not 'name' in df_teams.columns:
            # Add name SportBased on abbreviated_name hardcoded
            df_teams['name'] = df_teams['abbreviated_name'].map({'ATL': 'Atlanta Hawks',
                                                                 'BOS': 'Boston Celtics',
                                                                 'BKN': 'Brooklyn Nets',
                                                                 'CHA': 'Charlotte Hornets',
                                                                 'CHI': 'Chicago Bulls',
                                                                 'CLE': 'Cleveland Cavaliers',
                                                                 'DAL': 'Dallas Mavericks',
                                                                 'DEN': 'Denver Nuggets',
                                                                 'DET': 'Detroit Pistons',
                                                                 'GSW': 'Golden State Warriors',
                                                                 'HOU': 'Houston Rockets',
                                                                 'IND': 'Indiana Pacers',
                                                                 'LAC': 'Los Angeles Clippers',
                                                                 'LAL': 'Los Angeles Lakers',
                                                                 'MEM': 'Memphis Grizzlies',
                                                                 'MIA': 'Miami Heat',
                                                                 'MIL': 'Milwaukee Bucks',
                                                                 'MIN': 'Minnesota Timberwolves',
                                                                 'NOP': 'New Orleans Pelicans',
                                                                 'NYK': 'New York Knicks',
                                                                 'OKC': 'Oklahoma City Thunder',
                                                                 'ORL': 'Orlando Magic',
                                                                 'PHI': 'Philadelphia 76ers',
                                                                 'PHX': 'Phoenix Suns',
                                                                 'POR': 'Portland Trail Blazers',
                                                                 'SAC': 'Sacramento Kings',
                                                                 'SAS': 'San Antonio Spurs',
                                                                 'TOR': 'Toronto Raptors',
                                                                 'UTA': 'Utah Jazz',
                                                                 'WAS': 'Washington Wizards'})

        # Add the league_id column fixed as nba id for now, t
        # df_teams['league_id'] = self.leagues[0].league_id
        return df_teams
        return df_no_format


class LeagueRoster(SportBase, Base):
    """
    This class represents a league roster.
    """
    __tablename__ = 'league_roster'
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('league.id'))
    league = relationship(League, backref='teams')
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship(Team, backref='leagues')
    date_joined = Column(Date, nullable=False)
    date_left = Column(Date)

    def __init__(self, league, team, date_joined, date_left):
        self.league = league
        self.team = team
        self.date_joined = date_joined
        self.date_left = date_left

    @staticmethod
    def format_df(df_no_format):
        """
        Standardize dataframes to a common format that matches the db schema.
        :param df_no_format:
        :return:
        """
        super().format_df(df_no_format)
        return df_no_format


class Roster(SportBase, Base):
    """
    This class represents a roster, each record contains a player and a team.
    It also contains the date the player joined the team and the date the player left the team.
    It also contains a boolean value that indicates whether the player is still active in the team.
    """
    __tablename__ = 'roster'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('player.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    player = relationship('Player', backref='rosters')
    team = relationship('Team', backref='rosters')
    date_joined = Column(Date, nullable=False)
    date_left = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False)

    def __init__(self, player, team, date_joined, date_left, is_active):
        self.player = player
        self.team = team
        self.date_joined = date_joined
        self.date_left = date_left
        self.is_active = is_active
