import logging
import json
from datetime import datetime
import requests

logging.basicConfig(format='%(message)s', level=logging.INFO)

API_TLSCOVID_ENDPOINT = 'http://localhost:5001/api/tlscovid/'


# ToDo: Automatically get interval size
INTERVAL_SIZE = 10


def write_report(file_name, data):
    with open(file_name, 'a+', encoding='utf-8') as fp:
        json.dump(data, fp, indent=4, ensure_ascii=False)


def get_topics():
    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-examples')

    topics = {}
    for idx, topics_dict in r.json().items():
        topics.setdefault(idx, [])
        for _, topics_list in topics_dict.items():
            topics[idx].extend(topics_list)

    return topics


def get_domains():
    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-domains')

    domains = {}
    for domain in r.json():
        domains.setdefault(domain['lang'], [])
        domains[domain['lang']].append(domain['name'])

    return domains


def get_precision(kms_retrieved, docs_total):
    try:
        precision = kms_retrieved/docs_total
    except ZeroDivisionError:
        precision = 0
    
    return precision


def get_recall(kms_retrieved, kms_total):
    try:
        recall = kms_retrieved/kms_total
    except ZeroDivisionError:
        recall = 0

    return recall


def get_fscore(precision, recall):
    try:
        fscore = 2 * ((precision * recall) / (precision + recall))
    except ZeroDivisionError:
        fscore = 0
    
    return fscore


# use_headline False to use titles
# use_headline True to use contents
def compute_metrics(use_headline=True):

    topics = get_topics()
    domains = get_domains()

    headline_type = 'titles' if not use_headline else 'contents'

    topic_count = 0
    for lang, topics_list in topics.items():
        
        lang_domains = domains[lang]
        
        payload = {
            'index': lang,
            'sources': lang_domains,
            'use_headline': use_headline
        }

        report = {}
        file_name = 'report_' + headline_type + '_' + lang + '.json'

        for i, topic in enumerate(topics_list):
            
            topic_count += 1
            
            # Global counter
            logging.info(str(topic_count) + '/' +str(sum(map(len, topics.values()))))

            # Collection counter
            logging.info(str(i+1) + '/' + str(len(topics_list)) + ' (' + lang + ')')
            
            logging.info('Query: ' + topic + '\n')

            payload['query'] = topic
            
            r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-result', json=payload)

            result_str = r.json()

            payload['result'] = result_str

            r = requests.get(API_TLSCOVID_ENDPOINT +
                            'get-intervals', json=payload)

            intervals = r.json()['results']

            report[topic] = []

            for interval in intervals:
                start_date = datetime.strptime(interval["from"], '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                end_date = datetime.strptime(interval["to"], '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')

                interval_report = {}
                interval_report['lang'] = lang
                interval_report['sources'] = lang_domains

                interval_report['start_date'] = start_date
                interval_report['end_date'] = end_date

                # logging.info("from " + start_date + " until " + end_date)
                
                keyphrases = interval["keyphrases"]
                
                kms_retrieved = [keyphrase for keyphrase in keyphrases if keyphrase['is_km'] == 'True']
                num_kms_retrieved = len(kms_retrieved)

                # Get key moments in interval
                payload['start_date'] = start_date
                payload['end_date'] = end_date

                r = requests.get(API_TLSCOVID_ENDPOINT + 'get-keymoments-in-range', json=payload)

                kms_in_interval = r.json()
                num_kms_in_interval = len(kms_in_interval)

                # Compute metrics
                precision = get_precision(num_kms_retrieved, INTERVAL_SIZE)
                recall = get_recall(num_kms_retrieved, num_kms_in_interval)
                fscore = get_fscore(precision, recall)

                # Populate report
                interval_report['interval_size'] = INTERVAL_SIZE
                interval_report['num_kms_retrieved_in_interval'] = num_kms_retrieved
                interval_report['num_kms_in_interval'] = num_kms_in_interval

                interval_report['precision@' + str(INTERVAL_SIZE)] = precision
                interval_report['recall@' + str(INTERVAL_SIZE)] = recall
                interval_report['fscore@' + str(INTERVAL_SIZE)] = fscore

                report[topic].append(interval_report)

        write_report(file_name, report)
    

if __name__ == '__main__':
    compute_metrics()
