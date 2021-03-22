import json
from datetime import datetime
import requests

API_TLSCOVID_ENDPOINT = 'http://localhost:5001/api/tlscovid/'

PAYLOAD = {
    'query': 'portugal',
    'index': 'pt',
    'sources': ['publico', 'observador']
}

INTERVAL_SIZE = 10

REPORT_FILE = 'report.json'

def write_report(data):
    with open(REPORT_FILE, 'a+') as fp:
        json.dump(data, fp, indent=4)


# ToDo:
# Automatically get topics, domains and interval size

# def get_topics():
#     r = requests.get(API_TLSCOVID_ENDPOINT +
#                      'get-result', json=PAYLOAD)


# def get_domains():
#     r = requests.get(API_TLSCOVID_ENDPOINT +
#                      'get-result', json=PAYLOAD)


def get_precision(kms_retrieved, docs_total):
    return kms_retrieved/docs_total


def get_recall(kms_retrieved, kms_total):
    return kms_retrieved/kms_total


def get_fscore(precision, recall):
    return 2 * ((precision * recall) / (precision + recall))


def compute_metrics():

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-result', json=PAYLOAD)

    result_str = r.json()

    payload = PAYLOAD
    payload['result'] = result_str

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-intervals', json=payload)

    query = payload['query']
    print('Query:', query)

    intervals = r.json()['results']

    report = []

    query_report = {}
    query_report[query] = []

    for interval in intervals:
        start_date = datetime.strptime(interval["from"], '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
        end_date = datetime.strptime(interval["to"], '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')

        interval_report = {}
        interval_report['start_date'] = start_date
        interval_report['end_date'] = end_date

        print(start_date, "until", end_date)
        
        keyphrases = interval["keyphrases"]
        
        kms_retrieved = [keyphrase for keyphrase in keyphrases if keyphrase['is_km'] == 'True']
        num_kms_retrieved = len(kms_retrieved)

        # Get key moments in interval
        payload = PAYLOAD
        payload['start_date'] = start_date
        payload['end_date'] = end_date

        r = requests.get(API_TLSCOVID_ENDPOINT + 'get-keymoments-in-range', json=payload)

        kms_in_interval = r.json()
        num_kms_in_interval = len(kms_in_interval)

        precision = get_precision(num_kms_retrieved, INTERVAL_SIZE)
        recall = get_recall(num_kms_retrieved, num_kms_in_interval)
        fscore = get_fscore(precision, recall)

        interval_report['precision'] = precision
        interval_report['recall'] = recall
        interval_report['fscore'] = fscore

        query_report[query].append(interval_report)

    return query_report

stats = compute_metrics()

write_report(stats)
