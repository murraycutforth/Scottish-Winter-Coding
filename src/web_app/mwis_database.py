from sqlalchemy import MetaData, create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.utils import database_cache_path


db_path = database_cache_path()
metadata = MetaData()
engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False}, echo=False)  # echo=False
Base = declarative_base()
db_session = sessionmaker(bind=engine)()


class Mwis(Base):
    __tablename__ = 'mwis'
    id = Column(Integer, primary_key=True)
    location = Column(String)
    date = Column(String)
    days_ahead = Column(String)
    headline = Column(String)
    freezing_level = Column(String)
    how_windy = Column(String)
    chance_cloud_free = Column(String)
    how_wet = Column(String)


# Retrieving data from the database
def get_mwis_forecast():
    return db_session.query(Mwis)



def get_raw_forecasts(data, location, forecast_attr):
    data_raw = [(forecast.date, forecast.days_ahead, getattr(forecast, forecast_attr)) for forecast in data if forecast.location==location]
    return get_latest_info_per_day(data_raw)


# Get one forecast per date, using latest one
def get_latest_info_per_day(all_forecasts):
    forecasts = {}
    for info_tuple in all_forecasts:
        date = info_tuple[0]
        days_ahead = info_tuple[1]
        info = info_tuple[2]

        if not date in forecasts:
            forecasts[date] = (days_ahead, info)
        else:
            if days_ahead < forecasts[date][0]:
                forecasts[date] = (days_ahead, info)

    return sorted((k, v[1]) for k, v in forecasts.items())




data = get_mwis_forecast()
LOCATIONS = sorted(set(forecast.location for forecast in data))
