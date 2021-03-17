from flask import Blueprint, request, jsonify

from handlers import handlers_tlscovid

api_tlscovid = Blueprint('api_tlscovid', __name__)


@api_tlscovid.route('/get-indices', methods=['GET'])
def get_indices():

    # Handle request
    result = handlers_tlscovid.get_indices()

    return jsonify(result), 200


@api_tlscovid.route('/get-domains', methods=['GET'])
def get_domains():

    # Handle request
    payload = request.json

    # Handle request
    result = handlers_tlscovid.get_domains(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-examples', methods=['GET'])
def get_examples():

    # Handle request
    result = handlers_tlscovid.get_examples()

    return jsonify(result), 200


@api_tlscovid.route('/get-result', methods=['GET'])
def get_result():

    # Handle request
    payload = request.json

    # payload as {'query': str, 'index': str, 'sources': list of str}
    # sources is optional

    result = handlers_tlscovid.get_result(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-intervals', methods=['GET'])
def get_intervals():

    # Handle request
    payload = request.json

    # payload as {'query': str, 'index': str, 'sources': list of str, 'result': from /get-result}
    # sources is optional

    result = handlers_tlscovid.get_intervals(payload)

    return jsonify(result), 200


@api_tlscovid.route('/execute-engine', methods=['GET'])
def execute_engine():

    # Handle request
    payload = request.json

    # payload as {'query': str, 'index': str}

    result = handlers_tlscovid.execute_engine(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-events', methods=['GET'])
def get_events():

    # Handle request
    payload = request.json

    # payload is the result from /execute-engine

    result = handlers_tlscovid.get_events(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-titles', methods=['GET'])
def get_titles():

    # Handle request
    payload = request.json

    # payload is res_events from /get-events['res_events']

    result = handlers_tlscovid.get_titles(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-entities-terms', methods=['GET'])
def get_entities_terms():

    # Handle request
    payload = request.json

    # payload is {'all_titles': from /get-titles, 'query_term_corr': from /execute-engine["query_term_corr"]}

    result = handlers_tlscovid.get_entities_terms(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-timeseries', methods=['GET'])
def get_timeseries():

    # Handle request
    payload = request.json

    # payload is {'result': from /execute-engine, 'end_intervals_dates': from /get-events['end_intervals_dates']}

    result = handlers_tlscovid.get_timeseries(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-docs-in-range', methods=['GET'])
def get_docs_in_range():

    # Handle request
    payload = request.json

    # payload is {'query': str, 'index': str, 'sources': list of str, 'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}

    result = handlers_tlscovid.get_documents_from_query_in_date_range(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-keymoments-in-range', methods=['GET'])
def get_key_moments_in_range():

    # Handle request
    payload = request.json

    # payload is {'query': str, 'index': str, 'sources': list of str, 'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}

    result = handlers_tlscovid.get_key_moments_from_query_in_date_range(payload)

    return jsonify(result), 200
