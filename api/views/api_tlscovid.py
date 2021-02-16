from flask import Blueprint, request, jsonify

from handlers import handlers_tlscovid

api_tlscovid = Blueprint('api_tlscovid', __name__)


@api_tlscovid.route('/get-domains', methods=['GET'])
def get_domains():

    # Handle request
    result = handlers_tlscovid.get_domains()

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

    # payload as {'query': str,' index': str}

    result = handlers_tlscovid.get_result(payload)

    return jsonify(result), 200


@api_tlscovid.route('/get-intervals', methods=['GET'])
def get_intervals():

    # Handle request
    payload = request.json

    # payload as {'query': str,' index': str, 'result': from /get-result}

    result = handlers_tlscovid.get_intervals(payload)

    return jsonify(result), 200


@api_tlscovid.route('/execute-engine', methods=['GET'])
def execute_engine():

    # Handle request
    payload = request.json

    # payload as {'query': str,' index': str}

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
