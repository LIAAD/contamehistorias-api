from elasticsearch import Elasticsearch, helpers
import utils as utils


# Get all user indices
def get_all_indices(es):
    list_indices = es.cat.indices('*,-.*', params={'format': 'json'})
    indices = [i['index'] for i in list_indices]
    return indices


# Delete index by index name
def delete_index(es, index):
    es.indices.delete(index=index, ignore=[400, 404])


# Delete all user indices
def delete_all_indices(es):
    for idx in get_all_indices(es):
        delete_index(es, idx)


def get_docs_from_index(es, index):
    response = helpers.scan(
        es,
        index=index,
        doc_type='news',
        query={"query": {"match_all": {}}}
    )
    return response


def get_docs_from_query(es, index, query):
    response = helpers.scan(
        es,
        index=index,
        doc_type='news',
        query={"query": {
            "match": {
                "news": query
            }
        }
        }
    )
    return response


def get_mapping(index):
    mapping = es.indices.get_mapping(index)
    print(mapping)


# config = utils.load_json(utils.CONFIG_PATH)

# es = Elasticsearch([{'host': config['host'], 'port': config['port']}])
