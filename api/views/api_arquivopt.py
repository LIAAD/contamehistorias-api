from flask import request, jsonify, Blueprint

from handlers import handlers_arquivopt

api_arquivopt = Blueprint('api_arquivopt', __name__)


@api_arquivopt.route('/get-domains', methods=['GET'])
def api_arquivopt_get_domains():

    # Handle request
    domains = handlers_arquivopt.arquivopt_get_domains()

    return jsonify(domains), 200


@api_arquivopt.route('/get-examples', methods=['GET'])
def api_arquivopt_get_examples():

    # Handle request
    examples = handlers_arquivopt.arquivopt_get_examples()

    return jsonify(examples), 200


@api_arquivopt.route('/get-result', methods=['GET'])
def api_arquivopt_get_result():

    # Handle request
    payload = request.json

    # payload as {'query': str,' last_years': int}

    result = handlers_arquivopt.arquivopt_get_result(payload)

    return jsonify(result), 200


@api_arquivopt.route('/get-intervals', methods=['GET'])
def api_arquivopt_get_intervals():

    # Handle request
    payload = request.json

    # payload as {'query': str,' last_years': int, 'result': from /get-result}

    result = handlers_arquivopt.arquivopt_get_intervals(payload)

    return jsonify(result), 200


@api_arquivopt.route('/execute-engine', methods=['GET'])
def api_arquivopt_execute_engine():

    # Handle request
    payload = request.json

    # payload as {'query': str,' last_years': int}

    result = handlers_arquivopt.arquivopt_execute_engine(payload)

    return jsonify(result), 200


@api_arquivopt.route('/get-events', methods=['GET'])
def api_arquivopt_get_events():

    # Handle request
    payload = request.json

    # payload is the result from /execute-engine

    result = handlers_arquivopt.arquivopt_get_events(payload)

    return jsonify(result), 200


@api_arquivopt.route('/get-titles', methods=['GET'])
def api_arquivopt_get_titles():

    # Handle request
    payload = request.json

    # payload is res_events from /get-events['res_events']

    result = handlers_arquivopt.arquivopt_get_titles(payload)

    return jsonify(result), 200


@api_arquivopt.route('/get-entities-terms', methods=['GET'])
def api_arquivopt_get_entities_terms():

    # Handle request
    payload = request.json

    # payload is {'all_titles': from /get-titles, 'query_term_corr': from /execute-engine["query_term_corr"]}

    result = handlers_arquivopt.arquivopt_get_entities_terms(payload)

    return jsonify(result), 200


@api_arquivopt.route('/get-timeseries', methods=['GET'])
def api_arquivopt_get_timeseries():

    # Handle request
    payload = request.json

    # payload is {'result': from /execute-engine, 'end_intervals_dates': from /get-events['end_intervals_dates']}

    result = handlers_arquivopt.arquivopt_get_timeseries(payload)

    return jsonify(result), 200
