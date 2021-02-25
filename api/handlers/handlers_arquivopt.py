import time
import hashlib
from datetime import datetime, date, timedelta
import collections
import json

from pampo import ner

from contamehistorias import engine
from contamehistorias.datasources import webarchive

import data_sources.arquivopt.arquivopt_examples as arquivopt_examples
import data_sources.arquivopt.arquivopt_domains as arquivopt_domains

from .utils import convert_events_into_timeseries, convert_events_into_source_count

import cache

temp_summ_engine = engine.TemporalSummarizationEngine()
arquivopt_engine = webarchive.ArquivoPT()


DATE_FORMAT_INPUT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT_OUTPUT = '%d/%m/%Y'

CACHE_ENABLED = True


def check_cache():
    if CACHE_ENABLED:
        cache_connected = cache.is_connected()
    else:
        cache_connected = False
    
    return cache_connected


def get_cache_key(query, last_years, step):

    query = str(query).lower()
    last_years = str(last_years)

    cache_key = {'source': 'arquivopt', 'query': query, 'last_years': last_years, 'step': step}
    cache_key = json.dumps(cache_key, sort_keys=True).encode('utf-8')

    cache_key = hashlib.md5(cache_key).hexdigest()

    return cache_key


def get_domains():

    return arquivopt_domains.news_domains_pt


def get_examples():

    examples_dict = {
        'stories_persons': arquivopt_examples.stories_persons,
        'stories_justice': arquivopt_examples.stories_justice,
        'stories_culture': arquivopt_examples.stories_culture,
        'stories_history': arquivopt_examples.stories_history,
        'stories_sports': arquivopt_examples.stories_sports,
        'stories_general': arquivopt_examples.stories_general,
        'blacklist_ngrams': arquivopt_examples.blacklist_ngrams,
    }

    return examples_dict


def get_result(payload):

    cache_connected = check_cache()

    query = payload['query']
    last_years = payload['last_years']

    print('Query:', query)
    print('Last years:', last_years)

    # If cache enabled, check whether result already in cache
    if cache_connected:

        cache_key = get_cache_key(query, last_years, 'result')

        cached_result = cache.get_result(cache_key)

        # If result already in cache, get it, do nothing and return it
        if cached_result:
            print('get_result: Result in cache (' + str(cache_key) + ')')
            result = cached_result

        # If result not in cache, compute it, store it in cache and return it
        else:
            print('get_result: Result not in cache')

            date_end = datetime(year=date.today().year-1, month=12, day=31)
            date_start = date_end - timedelta(days=last_years * 365)

            domains = [item['url']
                       for item in arquivopt_domains.news_domains_pt]

            params = {'domains': domains, 'from': date_start, 'to': date_end}

            result = arquivopt_engine.getResult(query, **params)

            result = arquivopt_engine.toStr(result)

            print('get_result: Storing result in cache (' + str(cache_key) + ')')
            cache.set_result(cache_key, result)

    # If cache disabled, compute result and return it
    else:
        print('get_result: Cache disabled. Computing result')

        date_end = datetime(year=date.today().year-1, month=12, day=31)
        date_start = date_end - timedelta(days=last_years * 365)

        domains = [item['url'] for item in arquivopt_domains.news_domains_pt]

        params = {'domains': domains, 'from': date_start, 'to': date_end}

        result = arquivopt_engine.getResult(query, **params)

        result = arquivopt_engine.toStr(result)

    return result


def get_intervals(payload):

    cache_connected = check_cache()

    query = payload['query']
    last_years = payload['last_years']

    result_arquivo_str = payload['result']
    result_arquivo = arquivopt_engine.toObj(result_arquivo_str)

    # If there are no results from arquivo search return empty list
    if not result_arquivo:
        print('get_intervals: No results from arquivo search')
        return []

    # If cache enabled, check whether result already in cache
    if cache_connected:

        cache_key = get_cache_key(query, last_years, 'intervals')

        cached_result = cache.get_result(cache_key)

        # If result already in cache, get it, do nothing and return it
        if cached_result:
            print('get_intervals: Result in cache (' + str(cache_key) + ')')
            result = cached_result

        # If result not in cache, compute it, store it in cache and return it
        else:
            print('get_intervals: Result not in cache')

            result_intervals = temp_summ_engine.build_intervals(
                result_arquivo, 'pt', query)

            result = temp_summ_engine.serialize(result_intervals)

            print('get_intervals: Storing result in cache (' + str(cache_key) + ')')
            cache.set_result(cache_key, result)

    # If cache disabled, compute result and return it
    else:
        print('get_intervals: Cache disabled. Computing result')
        result_intervals = temp_summ_engine.build_intervals(
            result_arquivo, 'pt', query)

        result = temp_summ_engine.serialize(result_intervals)

    return result


def execute_engine(payload):

    # Get result from arquivopt
    time_start_get_result = time.time()

    result_arquivo_str = get_result(payload)

    time_spent_get_result = time.time() - time_start_get_result

    # If there are no results from arquivo search return empty list
    if not arquivopt_engine.toObj(result_arquivo_str):
        print('execute_engine: No results from arquivo search')
        return []
    
    # Build intervals
    get_intervals_payload = payload
    get_intervals_payload['result'] = result_arquivo_str

    time_start_build_intervals = time.time()
    
    result_intervals = get_intervals(get_intervals_payload)
    
    time_spent_build_intervals = time.time() - time_start_build_intervals

    # If could not build intervals return empty list
    if not result_intervals:
        print('execute_engine: Could not build intervals')
        return []

    # Stats
    print('Time spent to get result from arquivopt:', time_spent_get_result)

    print('Time spent to build intervals:', time_spent_build_intervals)

    result_intervals['stats']['time'] = float(
        time_spent_get_result + time_spent_build_intervals)

    print('Total time spent:',
          result_intervals['stats']['time'])

    result = result_intervals

    return result


def get_events(payload):

    keywords_by_intervals = [(item['from'], item['to'])
                             for item in payload['results']]

    events = [{'selected': '', 'date_id_str': item[1], 'date_readable_str': item[1],
               'from': item[0]} for item in keywords_by_intervals]

    if(len(events) > 0):
        events[0]['selected'] = 'selected'

    res_events = []
    d_dict = {}

    end_intervals_dates = []
    for event in events:
        event_date = None
        event_date_from = None

        event_date = datetime.strptime(
            event['date_id_str'], DATE_FORMAT_INPUT)
        event_date_from = datetime.strptime(
            event['from'], DATE_FORMAT_INPUT)

        res_event = event
        res_event['date_id_str'] = event_date.strftime(DATE_FORMAT_OUTPUT)
        res_event['date_id_str_from'] = event_date_from.strftime(
            DATE_FORMAT_OUTPUT)

        if(res_event['date_id_str'] not in d_dict.keys()):
            d_dict[res_event['date_id_str']] = 1

            res_event['date_readable_str'] = event_date.strftime(
                '%m/%Y')
            res_event['date_full_readable_str'] = event_date.strftime(
                '%d/%m/%Y')
            res_event['from_date_full_readable_str'] = event_date_from.strftime(
                '%d/%m/%Y')

            end_intervals_dates.append(event_date.strftime('%Y-%m-%d'))

            res_event['title'] = ''

            all_keywords_by_interval = [item['keyphrases'] for item in payload['results'] if datetime.strptime(
                item['to'], DATE_FORMAT_INPUT).date() == event_date.date()]

            keywords_by_sentiment = {
                'all': all_keywords_by_interval,
            }

            res_event['description'] = keywords_by_sentiment

            res_events.append(res_event)

    result_dict = {
        'res_events': res_events,
        'end_intervals_dates': end_intervals_dates
    }

    return result_dict


def get_titles(payload):

    all_titles = []
    for event in payload:
        keywords = [
            keywords for keywords in event['description']['all']]
        for title in keywords:
            for t in title:
                all_titles.append(t['kw'])

    return all_titles


def get_entities_terms(payload):

    all_titles = payload['all_titles']
    query_term_corr = payload['query_term_corr']

    all_content = '. '.join(all_titles)
    entities = ner.extract_entities(all_content)

    top_entities = collections.Counter(entities).most_common(30)

    related_terms = [{'text': x[0], 'size':x[1]} for x in query_term_corr]
    entity_terms = [{'text': x[0], 'size':x[1]} for x in top_entities]

    result_dict = {
        'related_terms': related_terms,
        'entity_terms': entity_terms
    }

    return result_dict


def get_timeseries(payload):

    result = payload['result']
    end_intervals_dates = payload['end_intervals_dates']

    news_timeseries_rs = convert_events_into_timeseries(
        result['news_for_timeline'])
    news_timeseries = news_timeseries_rs['result']

    sources_analysis = convert_events_into_source_count(
        result['news_for_timeline'])

    sources_overall = {
        'data': [item['pubdate'] for item in sources_analysis],
        'labels': [result['domains'][item['source_id']] for item in sources_analysis],
    }

    aggregated_headlines = [item['count'] for item in news_timeseries]
    overall_timeseries = {
        'data': json.dumps(aggregated_headlines),
        'labels': [item['pubdate'] for item in news_timeseries]
    }

    overall_timeseries['intervals_series'] = [
        0] * len(overall_timeseries['data'])

    for end_intervals_date in end_intervals_dates:
        pos_idex = overall_timeseries['labels'].index(end_intervals_date)
        overall_timeseries['intervals_series'][pos_idex] = max(
            aggregated_headlines)

    overall_timeseries['radius'] = [
        3 if x != 0 else 0 for x in aggregated_headlines]
    overall_timeseries['intervals_series_radius'] = [
        1 if x != 0 else 0 for x in overall_timeseries['intervals_series']]

    result_dict = {
        'news_timeseries_rs': news_timeseries_rs,
        'sources_overall': sources_overall,
        'overall_timeseries': overall_timeseries
    }

    return result_dict
