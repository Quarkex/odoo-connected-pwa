#!/usr/bin/env python3
import yaml
import string
import random
import time
import xmlrpc.client as rpc
from flask import Flask, render_template, url_for, jsonify, request

# Load configuration:
#####################
with open("config.yml", 'r') as stream:
    try:
        conf = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        conf = None

if conf == None:
    print("No configuration file provided.")
else:
    app = Flask(__name__)
    url = conf['odoo_url']
    db = conf['odoo_database']
    test_module = conf['target_module'] + '.' + conf['target_model']
    fields = conf['fields']

    sessions = {}

    flask_port = conf['server_port']
    if flask_port == None:
        flask_port = 5000

    # Define behaviour methods:
    ###########################

    def login(username, password):
        # this contrast with odoo and return a session token
        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if ( uid != False ):
            token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(48))
            sessions[token] = { 'uid': uid, 'password': password, 'time': time.time() }
            return token
        else:
            return False

    def isLogged(token):
        if token in sessions:
            # if the difference between current time and timestamp is less or
            # equal to 30min
            if ( (time.time() - sessions[token]['time']) <= (30 * 60) ):
                sessions[token]['time']: time.time()
                return { 'uid': sessions[token]['uid'], 'password': sessions[token]['password'], 'status': 'logged' }
            else:
                sessions.pop(token, None) # remove expired session.
                return { 'uid': sessions[token]['uid'], 'status': 'session-expired' }
        else:
            return { 'status': 'no-session' }

    def isAuthorized(token, task):
        user = isLogged(token)
        if user['status'] == 'logged':
            models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
            return models.execute_kw(db, user['uid'], user['password'], test_module,
                    'check_access_rights', [task], {'raise_exception': False})
        else:
            return False

    def odooDo(token, task, mask, arguments=None):
        output = {}
        user = isLogged(token)
        if user['status'] == 'logged':
            if isAuthorized(token, task):
                common = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
                if(arguments == None):
                    output['result'] = common.execute_kw(db, user['uid'], user['password'], test_module, task, mask)
                else:
                    output['result'] = common.execute_kw(db, user['uid'], user['password'], test_module, task, mask, arguments)

                output['status']='ok'

            else:
                output['status']='unauthorized'

        else:
            output['status']=user['status']

        return output

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js')

    @app.route('/api/login', methods=['POST'])
    def api_login():
        username = request.get_json(True)['username']
        password = request.get_json(True)['password']
        token = login(username, password)
        if (token == False):
            return jsonify({'status': 'unautenticated'})
        else:
            return jsonify({'status': 'ok', 'session_token': token})


    @app.route('/api/read', methods=['POST'])
    def api_read():
        token = request.get_json(True)['session_token']
        search = request.get_json(True)['search_string']

        if search == None:
            output = odooDo(token, 'search_read', [], {'fields': fields})
        else:
            output = odooDo(token, 'search_read', [[['name', 'like', search]]], {'fields': fields})

        return jsonify(output)

    @app.route('/api/create', methods=['POST'])
    def api_create():
        token = request.get_json(True)['session_token']
        new_name  = request.get_json(True)['name'].strip()

        output = odooDo(token, 'create', [{"name": new_name}])
        return jsonify(output)

    @app.route('/api/delete', methods=['POST'])
    def api_delete():
        token = request.get_json(True)['session_token']
        target_id = request.get_json(True)['target_id']

        output = odooDo(token, 'unlink', [[int(target_id)]])
        return jsonify(output)

    @app.route('/api/update', methods=['POST'])
    def api_put():
        token = request.get_json(True)['session_token']
        target_id = request.get_json(True)['target_id']
        new_name  = request.get_json(True)['name'].strip()

        output = odooDo(token, 'write', [[target_id], {"name": new_name}])
        return jsonify(output)

    if __name__=='__main__':
        app.run(debug=True,host='0.0.0.0', port=flask_port)

