import requests

API_TLSCOVID_ENDPOINT = 'http://localhost:5001/api/tlscovid/'

TEST_PAYLOAD = {
    'query': 'portugal',
    'index': 'pt'
}

TEST_PAYLOAD_WITH_SOURCES = {
    'query': 'portugal',
    'index': 'pt',
    'sources': ['publico']
}

TEST_PAYLOAD_WITH_SOURCES_DATE_RANGE = {
    'query': 'alemanha',
    'index': 'pt',
    'sources': ['publico'],
    'start_date': '2020-12-23',
    'end_date': '2020-12-24'
}

TEST_PAYLOAD_NO_RESULTS = {
    'query': '',
    'index': 'en'
}


def test_get_indices():
    print('Testing get-indices endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-indices')

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_indices()


def test_get_domains():
    print('Testing get-domains endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-domains')

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_domains()


def test_get_examples():
    print('Testing get-examples endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-examples')

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_examples()


def test_get_result():
    print('Testing get-result endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-result', json=TEST_PAYLOAD)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_result()


def test_get_intervals():
    print('Testing get-intervals endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-result', json=TEST_PAYLOAD)

    result_str = r.json()

    payload = TEST_PAYLOAD
    payload['result'] = result_str

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-intervals', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_intervals()


def test_execute_engine():
    print('Testing execute-engine endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'execute-engine', json=TEST_PAYLOAD)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_execute_engine()


def test_get_events():
    print('Testing get-events endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'execute-engine', json=TEST_PAYLOAD)

    result_engine = r.json()

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-events', json=result_engine)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_events()


def test_get_titles():
    print('Testing get-titles endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'execute-engine', json=TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-events', json=result_engine)

    res_events = r.json()['res_events']

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-titles', json=res_events)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_titles()


def test_get_entities_terms():
    print('Testing get-entities-terms endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'execute-engine', json=TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-events', json=result_engine)

    res_events = r.json()['res_events']

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-titles', json=res_events)

    all_titles = r.json()
    query_term_corr = result_engine['query_term_corr']

    payload = {
        'all_titles': all_titles,
        'query_term_corr': query_term_corr
    }

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'get-entities-terms', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_entities_terms()


def test_get_timeseries():
    print('Testing get-timeseries endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT +
                     'execute-engine', json=TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-events', json=result_engine)
    end_intervals_dates = r.json()['end_intervals_dates']

    payload = {
        'result': result_engine,
        'end_intervals_dates': end_intervals_dates
    }

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-timeseries', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_timeseries()


def test_get_documents_from_query_in_date_range():
    print('Testing get-docs-in-range endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-docs-in-range', json=TEST_PAYLOAD_WITH_SOURCES_DATE_RANGE)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_documents_from_query_in_date_range()


def test_get_key_moments_from_query_in_date_range():
    print('Testing get-keymoments-in-range endpoint')

    r = requests.get(API_TLSCOVID_ENDPOINT + 'get-keymoments-in-range', json=TEST_PAYLOAD_WITH_SOURCES_DATE_RANGE)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_get_key_moments_from_query_in_date_range()
