import collections
from datetime import datetime
import pandas as pd


def convert_events_into_source_count(news_for_timeline):
    raw_events = []
    for item in news_for_timeline:

        data = datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").date()

        source = item[1]

        raw_events.append({"pubdate": data, "source_id": source})

    df = pd.DataFrame(raw_events)
    df = df.groupby(["source_id"]).count()
    df['source_id'] = df.index

    result = df.T.to_dict().values()

    return result


def convert_events_into_timeseries(news_for_timeline):

    news_for_timeline = list(news_for_timeline)

    raw_events = [datetime.strptime(item[0], "%Y-%m-%d %H:%M:%S").date().strftime('%Y-%m-%d') for item in news_for_timeline]

    result = []
    for d, count in collections.Counter(raw_events).items():
        result.append({'pubdate': d, 'count': count})

    first_date = result[0]['pubdate']
    last_date = result[-1]['pubdate']

    return {"result": result,
            "first_date": first_date,
            "last_date": last_date}
