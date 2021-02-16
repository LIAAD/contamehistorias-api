# https://www.elastic.co/guide/en/elasticsearch/reference/current/fielddata.html#enable-fielddata-text-fields
# https://towardsdatascience.com/getting-started-with-elasticsearch-in-python-c3598e718380

import argparse
import os
import datetime
from urllib.parse import urlparse
from elasticsearch import Elasticsearch, helpers
import utils as utils


NEWS_SOURCES_LAN = {
    'publico': 'pt',
    'observador': 'pt',
    'cnn': 'en',
    'guardian': 'en'
}

MAPPING = {
    "mappings": {
        "properties": {
            "date": {
                "type": "date"
            },
            "is_km": {
                "type": "boolean"
            },
            "lan": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "news": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "source": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
                "fielddata": True
            },
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "topic": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                },
                "fielddata": True
            },
            "url": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            }
        }
    }
}


def parse_url(url):
    return urlparse(url).netloc.replace('.', '_')


def populate_db(es, mapping, data, idx):

    es.indices.create(
        index=idx,
        body=mapping,
        ignore=400  # ignore 400 already exists code
    )

    helpers.bulk(
        es,
        data,
        index=idx
    )


def add_km_flag(data, is_km):
    for doc in data:
        doc['is_km'] = is_km

    return data


def create_topics_index(es, data):
    es.indices.create(
        index='topics',
        ignore=400  # ignore 400 already exists code
    )

    helpers.bulk(
        es,
        data,
        index='topics'
    )


def main(args):

    if args is not None:
        config = utils.load_json(utils.CONFIG_PATH)

        es = Elasticsearch([{'host': config['host'], 'port': config['port']}])

        data = utils.load_json(args.file)

        if 'topics' in args.file:
            create_topics_index(es, data)
            return

        for source in NEWS_SOURCES_LAN:
            if source in args.file:

                if 'km' in args.file:
                    km_flag = True
                else:
                    km_flag = False

                data = add_km_flag(data, km_flag)

                populate_db(es, MAPPING, data, NEWS_SOURCES_LAN[source])


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', help='Path to JSON data file', required=True)
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print('Provided path does not exist!')
        return None

    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
