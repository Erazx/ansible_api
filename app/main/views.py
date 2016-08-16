from flask import make_response, jsonify, url_for, request, abort
from . import main
from .utils import is_safe_ip, check_sign
from ..tasks.exec_ansible import exec_ad_hoc, exec_playbook


@main.route('/ad_hoc', methods=['POST'])
def ad_hoc():
    # check client ip
    ip = request.remote_addr
    if not is_safe_ip(ip):
        abort(401)
    data = {
        'module_name': None,    # ansible module name
        'module_args': None,    # ansible module argumemts
        'pattern': None,        # host pattern
        'resource': None,       # self define assets, Dynamic maybe
        'su_user': None,        # su - username
        'timeout': None,        # timeout
        'forks': None,          # fork
        'timestamp': None,      # timestamp, for API Sign
        'sign': None,           # sign, for API Sign
    }
    try:
        data.update(request.get_json())
    except Exception:
        abort(400, {'message': 'Invalid Parameters!'})
    if not (data['timestamp'] and data['sign']):
        abort(400, {'message': 'sign and timestamp are required.!'})
    if not((data['pattern'] or data['resource']) and data['module_name'] and data['module_args']):
        abort(400, {'message': 'resource/pattern and module_name and module_args are required.!'})
    # clear None variables
    for k in data.keys():
        if not data[k]:
            data.pop(k)
    # get sign
    sign = data.pop('sign')
    if not check_sign(data, sign):
        abort(400, {'message': 'Sign Error!'})
    # pop timestamp
    data.pop('timestamp')
    # Here create ad_hoc task
    task = exec_ad_hoc.delay(data)
    return jsonify({'task_id': task.id, 'task_url': url_for('.task_stats', task_type='ad_hoc', task_id=task.id)}), 201


@main.route('/playbook', methods=['POST'])
def playbook():
    # check client ip
    ip = request.remote_addr
    if not is_safe_ip(ip):
        abort(401)
    data = {
        'resource': None,       # self define assets, Dynamic maybe
        'playbook': None,       # playbook filename
        'sign': None,           # sign, for API sign
        'timestamp': None,      # timestamp, for API sign
        'extra_vars': None,     # playbook extra_vars, dictionary
    }
    try:
        data.update(request.get_json())
    except Exception:
        abort(400, {'message': 'Invalid Parameters!'})
    if not (data['timestamp'] and data['sign']):
        abort(400, {'message': 'sign and timestamp are required.!'})
    if not data['playbook']:
        abort(400, {'message': 'playbook are required.!'})
    # clear None variables
    for k in data.keys():
        if not data[k]:
            data.pop(k)
    # get sign
    sign = data.pop('sign')
    if not check_sign(data, sign):
        abort(400, {'message': 'Sign Error!'})
    # pop timestamp
    data.pop('timestamp')
    # here create playbook task
    task = exec_playbook.delay(data)
    return jsonify({'task_id': task.id, 'task_url': url_for('.task_stats', task_type='playbook', task_id=task.id)}), 201


@main.route('/taskstats/<task_type>/<task_id>', methods=['GET'])
def task_stats(task_type, task_id):
    # check client ip
    ip = request.remote_addr
    if not is_safe_ip(ip):
        abort(401)

    if task_type == "ad_hoc":
        task = exec_ad_hoc.AsyncResult(task_id)
    elif task_type == "playbook":
        task = exec_playbook.AsyncResult(task_id)
    else:
        abort(400, {'message': 'Unknown Task Type!'})

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': task.info,  # this is the exception raised
        }

    return jsonify(response)
