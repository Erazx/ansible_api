from flask import make_response, jsonify
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({'error': 'Page Not Found', }), 404)


@main.app_errorhandler(500)
def internal_server_error(e):
    return make_response(jsonify({'error': 'Internal Server Error', }), 500)


@main.app_errorhandler(400)
def page_not_found(e):
    return make_response(jsonify({'error': e.description['message']}), 400)


@main.app_errorhandler(401)
def page_not_found(e):
    return make_response(jsonify({'error': 'NOT AUTHORIZED'}), 401)
