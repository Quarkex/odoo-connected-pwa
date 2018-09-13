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

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/sw.js', methods=['GET'])
    def sw():
        return app.send_static_file('sw.js')

    @app.route('/api', methods=['POST'])
    def api_get():

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

    if __name__=='__main__':
        app.run(debug=True,host='127.0.0.1')
