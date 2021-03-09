from datetime import datetime
import logging
import requests
import click
import cache


logging.basicConfig(format='%(message)s', level=logging.INFO)

SOURCE = 'arquivopt'
API_ENDPOINT = 'http://localhost:5001/api/arquivopt/'
LOG_FILE = 'log_cache_arquivopt.txt'


def log_to_file(query, years, status):
    with open(LOG_FILE, 'a+') as fp:
        fp.write('Query: ' + str(query) + '\n')
        fp.write('Last years: ' + str(years) + '\n')
        fp.write('Status code: ' + str(status) + '\n')
        fp.write('Timestamp: ' + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '\n'))
        fp.write('\n')


@click.command()
@click.option('-r', '--refresh', is_flag=True, help='Whether or not to delete previous cache.')
def populate_cache(refresh):

    logging.info('Populating Conta-me Historias Arquivopt Cache\n')

    if refresh:
        logging.info('Deleting previous cache\n')
        cache.delete_keys_by_match(match='*' + SOURCE + '*')
        open(LOG_FILE, 'w').close()

    # Get examples
    r = requests.get(API_ENDPOINT + 'get-examples')

    examples = []
    for example_type, examples_list in r.json().items():
        if 'stories' in example_type:
            for ex in examples_list:
                examples.append(ex['title'])

    # Last years
    last_years = [5, 10, 15, 20]

    count = 0
    for example in examples:
        for years in last_years:

            count += 1

            logging.info(str(count) + '/' +
                         str(len(examples) * len(last_years)))

            logging.info('Query: ' + str(example))
            logging.info('Last years: ' + str(years))

            # Make API request
            payload = {
                'query': example,
                'last_years': years
            }
            r = requests.get(API_ENDPOINT + 'execute-engine', json=payload)

            logging.info('Status code: ' + str(r.status_code))

            logging.info('')

            log_to_file(example, years, r.status_code)


if __name__ == '__main__':
    populate_cache()
