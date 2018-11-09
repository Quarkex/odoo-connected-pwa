#!/usr/bin/env python3
import yaml
import xmlrpc.client as rpc
from flask import Flask, render_template, url_for, jsonify, request

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

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js')

    @app.route('/api/read', methods=['POST'])
    def api_read():

        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if uid != False: # If user hasn't successfully authenticated this will be False

            models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
            has_access_rights = models.execute_kw(db, uid, password, test_module,
                    'check_access_rights', ['read'], {'raise_exception': False})

            if has_access_rights:

                search = request.get_json(True)['search_string']
                if search == None:
                    records = models.execute_kw(db, uid, password, test_module,
                            'search_read', [], {'fields': fields})
                else:
                    records = models.execute_kw(db, uid, password, test_module,
                            'search_read', [[['name', 'like', search]]], {'fields': fields})


                # The jsonify() function in flask returns a flask.Response()
                # object that already has the appropriate content-type header
                # 'application/json' for use with json responses.
                return jsonify(records)

            else:
                return render_template('error.html')

        else:
            return render_template('error.html')

        return render_template('index.html')

    @app.route('/api/create', methods=['POST'])
    def api_create():

        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if uid != False: # If user hasn't successfully authenticated this will be False

            new_name = request.get_json(True)['name']

            models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
            has_access_rights = models.execute_kw(db, uid, password, test_module,
                    'check_access_rights', ['read'], {'raise_exception': False})

            if has_access_rights:
                id = models.execute_kw(db, uid, password, test_module,
                        'create', [{ 'name': new_name, }])

            else:
                return render_template('error.html')

        else:
            return render_template('error.html')

        return render_template('index.html')

    @app.route('/api/delete', methods=['POST'])
    def api_delete():

        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if uid != False: # If user hasn't successfully authenticated this will be False

            target_id = request.get_json(True)['target_id']

            models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
            has_access_rights = models.execute_kw(db, uid, password, test_module,
                    'check_access_rights', ['read'], {'raise_exception': False})

            if has_access_rights:
                id = models.execute_kw(db, uid, password, test_module,
                        'unlink', [[int(target_id)]])

            else:
                return render_template('error.html')

        else:
            return render_template('error.html')

        return render_template('index.html')

    @app.route('/api/update', methods=['POST'])
    def api_put():

        common = rpc.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        if uid != False: # If user hasn't successfully authenticated this will be False

            target_id = request.get_json(True)['target_id']
            new_name  = request.get_json(True)['name'].strip()

            models = rpc.ServerProxy('{}/xmlrpc/2/object'.format(url))
            has_access_rights = models.execute_kw(db, uid, password, test_module,
                    'check_access_rights', ['read'], {'raise_exception': False})

            if has_access_rights:
                id = models.execute_kw(db, uid, password, test_module,
                        'write', [[target_id], {"name": new_name}])

            else:
                return render_template('error.html')

        else:
            return render_template('error.html')

        return render_template('index.html')

    if __name__=='__main__':
        app.run(debug=True,host='127.0.0.1', port=flask_port)
