import time
import hashlib
from datetime import datetime
import collections
import json
import logging

from pampo import ner

from contamehistorias import engine
from contamehistorias.datasources import tlscovid

import data_sources.tlscovid.tlscovid_domains as tlscovid_domains

from .utils import convert_events_into_timeseries, convert_events_into_source_count

from cache import cache

# Setup logger
logger = logging.getLogger('api_handler_tlscovid')
logger.setLevel(logging.INFO)

LOGGER_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
logger_formatter = logging.Formatter(fmt=LOGGER_FORMAT)

# Create console handler
ch = logging.StreamHandler()
ch.setFormatter(logger_formatter)
# Add the handler to the logger
logger.addHandler(ch)

temp_summ_engine = engine.TemporalSummarizationEngine(top=10)
tlscovid_engine = tlscovid.ElasticSearchCovid()

SOURCE = 'tlscovid'

DATE_FORMAT_INPUT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT_OUTPUT = '%d/%m/%Y'

CACHE_ENABLED = True


def check_cache():
    if CACHE_ENABLED:
        cache_connected = cache.is_connected()
    else:
        cache_connected = False
    
    return cache_connected


def get_cache_key(query, index, sources, step, use_headline=False):

    query = str(query).lower()
    index = str(index).lower()

    cache_key = {'source': SOURCE, 'query': query, 'index': index, 'sources': sources, 'step': step}

    if step == 'intervals':
        if use_headline:
            cache_key['use_headline'] = 'contents'
        else:
            cache_key['use_headline'] = 'titles'

    cache_key = json.dumps(cache_key, sort_keys=True).encode('utf-8')

    cache_key = hashlib.md5(cache_key).hexdigest()

    if not sources:
        sources_str = 'all-sources'
    else:
        sources_str = '-'.join(s for s in sources)

    cache_key += '_' + SOURCE + '_' + query.replace(' ', '-') + '_' + index + '_' + sources_str

    if step == 'intervals':
        if use_headline:
            cache_key += '_contents'
        else:
            cache_key += '_titles'

    cache_key += '_' + step

    return cache_key


def is_str_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except:
        return False


def get_indices():

    return tlscovid_engine.get_all_indices()


def get_domains(payload):

    if payload and 'index' in payload:
        index = str(payload['index']).lower()
        domains = [domain for domain in tlscovid_domains.news_domains if domain['lang'] == index]
    else:
        domains = tlscovid_domains.news_domains

    return domains


def get_examples():

    topics = tlscovid_engine.get_topics()

    examples_dict = {'pt': {}, 'en': {}}

    for topic in topics:
        if topic['type'] not in examples_dict[topic['lan']]:
            examples_dict[topic['lan']][topic['type']] = [topic['topic']]
        else: 
            examples_dict[topic['lan']][topic['type']].append(topic['topic'])

    return examples_dict


def get_result(payload):

    cache_connected = check_cache()

    query = payload['query']
    index = payload['index']

    # sources is optional
    if 'sources' in payload:
        sources = payload['sources']
    else:
        sources = []

    logger.info('Query: {0}'.format(query))
    logger.info('Index: {0}'.format(index))
    logger.info('Sources: {0}'.format(sources))

    # If cache enabled, check whether result already in cache
    if cache_connected:

        cache_key = get_cache_key(query, index, sources, 'result')

        cached_result = cache.get_result(cache_key)

        # If result already in cache, get it, do nothing and return it
        if cached_result:
            logger.info('get_result: Result in cache ({0})'.format(cache_key))
            result = cached_result

        # If result not in cache, compute it, store it in cache and return it
        else:
            logger.info('get_result: Result not in cache')

            params = {'index': index}

            if sources:
                params['sources'] = sources

            result = tlscovid_engine.getResult(query, **params)

            result = tlscovid_engine.toStr(result)

            if is_str_valid_json(result):
                logger.info('get_result: Result from Elasticsearch is valid. Storing in cache ({0})'.format(cache_key))
                cache.set_result(cache_key, result)
            else:
                logger.warning('get_result: Result from Elasticsearch is invalid. Not storing in cache')
                result = []

    # If cache disabled, compute result and return it
    else:
        logger.info('get_result: Cache disabled. Computing result')

        params = {'index': index}

        if sources:
            params['sources'] = sources

        result = tlscovid_engine.getResult(query, **params)

        result = tlscovid_engine.toStr(result)

        if not is_str_valid_json(result):
            logger.warning('get_result: Result from Elasticsearch is invalid')
            result = []

    return result


def get_intervals(payload):

    cache_connected = check_cache()

    query = payload['query']
    index = payload['index']

    # sources is optional
    if 'sources' in payload:
        sources = payload['sources']
    else:
        sources = []

    # use_headline: bool
    # if True, use news contents
    # if False, use news titles
    # defaults to False
    if 'use_headline' in payload:
        # If it is already a bool get its value
        if isinstance(payload['use_headline'], bool):
            use_headline = payload['use_headline']
        # Else, parse it
        else:
            try:
                use_headline = json.loads(payload['use_headline'].lower())
            except:
                use_headline = False
    else:
        use_headline = False

    result_tlscovid_str = payload['result']
    result_tlscovid = tlscovid_engine.toObj(result_tlscovid_str)

    # If there are no results from tlscovid search return empty list
    if not result_tlscovid:
        logger.info('get_intervals: No results from tlscovid search')
        return []

    # If cache enabled, check whether result already in cache
    if cache_connected:

        cache_key = get_cache_key(query, index, sources, 'intervals', use_headline=use_headline)

        cached_result = cache.get_result(cache_key)

        # If result already in cache, get it, do nothing and return it
        if cached_result:
            logger.info('get_intervals: Result in cache ({0})'.format(cache_key))
            result = cached_result

        # If result not in cache, compute it, store it in cache and return it
        else:
            logger.info('get_intervals: Result not in cache')

            result_intervals = temp_summ_engine.build_intervals(
                result_tlscovid, index, query, use_headline=use_headline)

            result = temp_summ_engine.serialize(result_intervals, tls_covid=True)

            logger.info('get_intervals: Storing result in cache ({0})'.format(cache_key))
            cache.set_result(cache_key, result)

    # If cache disabled, compute result and return it
    else:
        logger.info('get_intervals: Cache disabled. Computing result')
        result_intervals = temp_summ_engine.build_intervals(
            result_tlscovid, index, query, use_headline=use_headline)

        result = temp_summ_engine.serialize(result_intervals, tls_covid=True)

    return result


def execute_engine(payload):

    # Get result from tlscovid
    time_start_get_result = time.time()

    result_tlscovid_str = get_result(payload)

    time_spent_get_result = time.time() - time_start_get_result

    # If there are no results from tlscovid search return empty list
    if not tlscovid_engine.toObj(result_tlscovid_str):
        logger.info('execute_engine: No results from tlscovid search')
        return []
    
    # Build intervals
    get_intervals_payload = payload
    get_intervals_payload['result'] = result_tlscovid_str

    time_start_build_intervals = time.time()
    
    result_intervals = get_intervals(get_intervals_payload)
    
    time_spent_build_intervals = time.time() - time_start_build_intervals

    # If could not build intervals return empty list
    if not result_intervals:
        logger.info('execute_engine: Could not build intervals')
        return []

    # Stats
    logger.info('Time spent to get result from tlscovid: {0}'.format(time_spent_get_result))

    logger.info('Time spent to build intervals: {0}'.format(time_spent_build_intervals))

    result_intervals['stats']['time'] = float(
        time_spent_get_result + time_spent_build_intervals)

    logger.info('Total time spent: {0}'.format(result_intervals['stats']['time']))

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


def get_documents_from_query_in_date_range(payload):

    query = payload['query']
    index = payload['index']
    sources = payload['sources']
    start_date = payload['start_date']
    end_date = payload['end_date']

    result = tlscovid_engine.get_documents_from_query_by_sources_in_date_range(index, query, sources, start_date, end_date)

    return result


def get_key_moments_from_query_in_date_range(payload):

    query = payload['query']
    index = payload['index']
    sources = payload['sources']
    start_date = payload['start_date']
    end_date = payload['end_date']

    result = tlscovid_engine.get_key_moments_from_query_by_sources_in_date_range(index, query, sources, start_date, end_date)

    return result
