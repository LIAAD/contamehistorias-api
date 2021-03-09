from datetime import datetime
import logging
import requests
import click
import cache


logging.basicConfig(format='%(message)s', level=logging.INFO)

SOURCE = 'tlscovid'
API_ENDPOINT = 'http://localhost:5001/api/tlscovid/'
LOG_FILE = 'log_cache_tlscovid.txt'


def log_to_file(query, idx, source, status):
    with open(LOG_FILE, 'a+') as fp:
        fp.write('Query: ' + str(query) + '\n')
        fp.write('Index: ' + str(idx) + '\n')
        fp.write('Source: ' + str(source) + '\n')
        fp.write('Status code: ' + str(status) + '\n')
        fp.write('Timestamp: ' + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '\n'))
        fp.write('\n')


@click.command()
@click.option('-r', '--refresh', is_flag=True, help='Whether or not to delete previous cache.')
def populate_cache(refresh):

    logging.info('Populating Conta-me Historias TLSCOVID Cache\n')

    if refresh:
        logging.info('Deleting previous cache\n')
        cache.delete_keys_by_match(match='*' + SOURCE + '*')
        open(LOG_FILE, 'w').close()

    # Get examples
    r = requests.get(API_ENDPOINT + 'get-examples')

    examples = {}
    for idx, examples_dict in r.json().items():
        examples.setdefault(idx, [])
        for _, examples_list in examples_dict.items():
            examples[idx].extend(examples_list)

    # Get domains
    r = requests.get(API_ENDPOINT + 'get-domains')

    domains = {}
    for domain in r.json():
        domains.setdefault(domain['lang'], [])
        domains[domain['lang']].append(domain['name'])

    count = 0
    for idx, examples_list in examples.items():

        for example in examples_list:
            count += 1

            logging.info(
                str(count) + '/' + str(sum(map(len, examples.values())) * (len(domains[idx])+1)))

            logging.info('Query: ' + str(example))
            logging.info('Index: ' + str(idx))
            logging.info('Sources: all_sources')

            # Make API request
            payload = {
                'query': example,
                'index': idx,
            }
            r = requests.get(API_ENDPOINT + 'execute-engine', json=payload)

            logging.info('Status code: ' + str(r.status_code))

            logging.info('')

            log_to_file(example, idx, 'all_sources ', r.status_code)

            for domain in domains[idx]:
                count += 1
                logging.info(str(count) + '/' +
                             str(sum(map(len, examples.values())) * (len(domains[idx])+1)))

                logging.info('Query: ' + str(example))
                logging.info('Index: ' + str(idx))
                logging.info('Sources: ' + str(domain))

                # Make API request
                payload = {
                    'query': example,
                    'index': idx,
                    'sources': [domain]
                }
                r = requests.get(API_ENDPOINT + 'execute-engine', json=payload)

                logging.info('Status code: ' + str(r.status_code))

                logging.info('')

                log_to_file(example, idx, domain, r.status_code)


if __name__ == '__main__':
    populate_cache()
