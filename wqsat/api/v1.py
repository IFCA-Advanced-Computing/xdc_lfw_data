from flask import Flask, request
from flask_restplus import Resource, Api, fields
from datetime import datetime
import wqsat
from wqsat import modules
from wqsat.modules import sentinel2
from wqsat.modules import clouds
from wqsat.modules import water
from wqsat.modules import meteo
import json

app = Flask(__name__)
api = Api(app)

data_parser = api.parser()

data_parser.add_argument('region', help="Region to get data from (CdP, Sanabria, Cogotas)", type=str, required=True)
data_parser.add_argument('start_date', help="Start Date", type=str, required=True)
data_parser.add_argument('end_date',help="End Date", type=str, required=True)

#data_parser.add_argument('data', help="Region to get data from (CdP, Sanabria, Cogotas)", type=json, required=True)

model_meta = api.model('ModelMetadata', {
    'id': fields.String(required=True, description='Model identifier'),
    'name': fields.String(required=True, description='Model name'),
    'description': fields.String(required=True,
                                 description='Model description'),
    'license': fields.String(required=False, description='Model license'),
    'author': fields.String(required=False, description='Model author'),
    'version': fields.String(required=False, description='Model version'),
    'url': fields.String(required=False, description='Model url'),
})

response = api.model('ModelResponse', {
    'status': fields.String(required=True,
                            description='Response status message'),
    'predictions': fields.String(required=True, description='Predicted labels and '
                                           'probabilities')
})

@api.marshal_with(model_meta, envelope='resource')
@api.route('/test')
class BaseModel(Resource):
    def get(self):
        """Return model information."""
        r = {
            "id": "0",
            "name": "Not a model",
            "description": "Placeholder metadata, model not implemented",
            "author": "Alvaro Lopez Garcia",
        }
        return r

@api.marshal_with(response, envelope='resource')
@api.route('/cloud_coverage')
class ModelPredict(Resource):
    @api.expect(data_parser)
    def post(self):
        """Gets a list of cloud coverage percentage for the date given in the region"""

        args = data_parser.parse_args()

        region = args["region"]
        sd = args['start_date']
        ed = args['end_date']
        
        #Check dates
        try:
            start_date = datetime.strptime(sd, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(start_date))
            return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

        try:
            end_date = datetime.strptime(ed, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(end_date))
            return {'Error':'Invalid End date. Format dd-mm-YYYY'}

        json_cloud_coverage = clouds.cloud_coverage(start_date, end_date, region)
        return json_cloud_coverage

@api.marshal_with(response, envelope='resource')
@api.route('/cloud_mask')
class ModelPredict(Resource):
    @api.expect(data_parser)
    def post(self):
        """Gets a list of cloud coverage percentage for the date given in the region"""

        args = data_parser.parse_args()

        region = args["region"]
        sd = args['start_date']
        ed = args['end_date']

        #Check dates
        try:
            start_date = datetime.strptime(sd, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(start_date))
            return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

        try:
            end_date = datetime.strptime(ed, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(end_date))
            return {'Error':'Invalid End date. Format dd-mm-YYYY'}

	json_cloud_mask = clouds.cloud_mask(start_date, end_date, region)
        return json_cloud_mask

@api.marshal_with(response, envelope='resource')
@api.route('/water_surface')
class ModelPredict(Resource):
    @api.expect(data_parser)
    def post(self):
        """Gets a list of cloud coverage percentage for the date given in the region"""

        args = data_parser.parse_args()

        region = args["region"]
        sd = args['start_date']
        ed = args['end_date']

        #Check dates
        try:
            start_date = datetime.strptime(sd, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(start_date))
            return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

        try:
            end_date = datetime.strptime(ed, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(end_date))
            return {'Error':'Invalid End date. Format dd-mm-YYYY'}

	#TODO
        sat_img = sentinel2.get_sentinel2_raw(inidate,enddate,region)
        water_sur = water.water_surface(sat_img)
        return {'water_surface': '1000'}

@api.marshal_with(response, envelope='resource')
@api.route('/water_mask')
class ModelPredict(Resource):
    @api.expect(data_parser)
    def post(self):
        """Gets a list of cloud coverage percentage for the date given in the region"""

        args = data_parser.parse_args()

        region = args["region"]
        sd = args['start_date']
        ed = args['end_date']

        #Check dates
        try:
            start_date = datetime.strptime(sd, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(start_date))
            return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

        try:
            end_date = datetime.strptime(ed, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(end_date))
            return {'Error':'Invalid End date. Format dd-mm-YYYY'}

        #TODO
        sat_img = sentinel2.get_sentinel2_raw(inidate,enddate,region)
        water_sur = water.water_surface(sat_img)
        return {'water_mask': '1000'}

@api.marshal_with(response, envelope='resource')
@api.route('/meteo')
class ModelPredict(Resource):
    @api.expect(data_parser)
    def post(self):
        """Gets a list of cloud coverage percentage for the date given in the region"""

        args = data_parser.parse_args()

        region = args["region"]
        sd = args['start_date']
        ed = args['end_date']

        #Check dates
        try:
            start_date = datetime.strptime(sd, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(start_date))
            return {'Error':'Invalid Initial date. Format dd-mm-YYYY'}

        try:
            end_date = datetime.strptime(ed, "%d-%m-%Y").date()
        except ValueError:
            print("Not a valid date: '{0}'.".format(end_date))
            return {'Error':'Invalid End date. Format dd-mm-YYYY'}

        #TODO
        meteo = meteo.get_meteo(start_date,end_date,region)
        print(meteo)

@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

@api.route('/<string:todo_id>')
class TodoSimple(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}

    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}

if __name__ == '__main__':
    app.run(debug=True)
