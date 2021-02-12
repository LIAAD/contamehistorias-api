import requests

API_ARQUIVOPT_ENDPOINT = 'http://localhost:5001/api/arquivopt/'

MAIN_TEST_PAYLOAD = {
    'query': 'obama',
    'last_years': 10
}

NO_RESULTS_TEST_PAYLOAD = {
    'query': 'covid-19',
    'last_years': 10
}


def test_arquivopt_get_domains():
    print('Testing get-domains endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-domains')

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_domains()


def test_arquivopt_get_examples():
    print('Testing get-examples endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-examples')

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_examples()


def test_arquivopt_get_result():
    print('Testing get-result endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'get-result', json=MAIN_TEST_PAYLOAD)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_result()


def test_arquivopt_get_intervals():
    print('Testing get-intervals endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'get-result', json=MAIN_TEST_PAYLOAD)

    result_arquivo_str = r.json()

    payload = MAIN_TEST_PAYLOAD
    payload['result'] = result_arquivo_str

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'get-intervals', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_intervals()


def test_arquivopt_execute_engine():
    print('Testing execute-engine endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'execute-engine', json=MAIN_TEST_PAYLOAD)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_execute_engine()


def test_arquivopt_get_events():
    print('Testing get-events endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'execute-engine', json=MAIN_TEST_PAYLOAD)

    result_engine = r.json()

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-events', json=result_engine)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_events()


def test_arquivopt_get_titles():
    print('Testing get-titles endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'execute-engine', json=MAIN_TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-events', json=result_engine)

    res_events = r.json()['res_events']

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-titles', json=res_events)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_titles()


def test_arquivopt_get_entities_terms():
    print('Testing get-entities-terms endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'execute-engine', json=MAIN_TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-events', json=result_engine)

    res_events = r.json()['res_events']

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-titles', json=res_events)

    all_titles = r.json()
    query_term_corr = result_engine['query_term_corr']

    payload = {
        'all_titles': all_titles,
        'query_term_corr': query_term_corr
    }

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'get-entities-terms', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_entities_terms()


def test_arquivopt_get_timeseries():
    print('Testing get-timeseries endpoint')

    r = requests.get(API_ARQUIVOPT_ENDPOINT +
                     'execute-engine', json=MAIN_TEST_PAYLOAD)
    result_engine = r.json()

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-events', json=result_engine)
    end_intervals_dates = r.json()['end_intervals_dates']

    payload = {
        'result': result_engine,
        'end_intervals_dates': end_intervals_dates
    }

    r = requests.get(API_ARQUIVOPT_ENDPOINT + 'get-timeseries', json=payload)

    print('Response status:', r.status_code)
    print('Response content:', r.json())

# test_arquivopt_get_timeseries()
