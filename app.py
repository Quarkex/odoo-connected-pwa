#!/usr/bin/env python3
import yaml
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
    username = conf['odoo_username']
    password = conf['odoo_password']
    test_module = conf['target_module'] + '.' + conf['target_model']
    fields = conf['fields']

    flask_port = conf['server_port']
    if flask_port == None:
        flask_port = 5000

    # Define behaviour methods:
    ###########################

    def login(username, password):
        # TODO this should contrast with odoo and return a session token
        return 'placeholder_token'

    def isLogged(token):
        # TODO this should contrast the session token to get the username and password
        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        return common.authenticate(db, username, password, {})

    def isAuthorized(uid, task):
        models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
        return models.execute_kw(db, uid, password, test_module,
                'check_access_rights', [task], {'raise_exception': False})

    def odooDo(token, task, mask, arguments=None):
        output = {}

        uid = isLogged(token)
        if uid != False: # If user hasn't successfully authenticated this will be False
            if isAuthorized(uid, task):

                if(arguments == None):
                    output['result'] = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url)).execute_kw(db, uid, password, test_module, task, mask)
                else:
                    output['result'] = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url)).execute_kw(db, uid, password, test_module, task, mask, arguments)

                output['status']='ok'
            else:
                output['status']='unauthorized'

        else:
            output['status']='error'

        return output

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js')

    @app.route('/api/read', methods=['POST'])
    def api_read():
        search = request.get_json(True)['search_string']

        token = login('test', 'test')

        if search == None:
            output = odooDo(token, 'search_read', [], {'fields': fields})
        else:
            output = odooDo(token, 'search_read', [[['name', 'like', search]]], {'fields': fields})

        return jsonify(output)

    @app.route('/api/create', methods=['POST'])
    def api_create():
        new_name  = request.get_json(True)['name'].strip()

        token = login('test', 'test')

        output = odooDo(token, 'create', [{"name": new_name}])
        return jsonify(output)

    @app.route('/api/delete', methods=['POST'])
    def api_delete():
        target_id = request.get_json(True)['target_id']

        token = login('test', 'test')

        output = odooDo(token, 'unlink', [[int(target_id)]])
        return jsonify(output)

    @app.route('/api/update', methods=['POST'])
    def api_put():
        target_id = request.get_json(True)['target_id']
        new_name  = request.get_json(True)['name'].strip()

        token = login('test', 'test')

        output = odooDo(token, 'write', [[target_id], {"name": new_name}])
        return jsonify(output)

    if __name__=='__main__':
        app.run(debug=True,host='127.0.0.1', port=flask_port)

