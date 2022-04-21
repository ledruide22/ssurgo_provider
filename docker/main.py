import json

from flask import Flask, Response, request
from shapely.geometry import Point

from src.ssurgo_provider.tools import retrieve_state_code, find_ssurgo_state_folder_path, \
    manage_retrieve_soils_composition
from ssurgo_provider.object.state_info import StateInfo, StateInfoStatus


def launch(port="8180", host="0.0.0.0"):
    app = Flask(__name__)

    @app.route('/')
    def status():
        return "READY TO RETURN SSURGO DATA"

    @app.route('/find_state', methods=['GET'])
    def get_state_name():
        arguments = request.args
        try:
            lat = float(arguments.get('lat'))
            long = float(arguments.get('long'))
            states_info_list = retrieve_state_code(Point(long, lat), disable_location_error=False)
            response = {'state_code': states_info_list[0].state_code, 'lat': states_info_list[0].point.y,
                        'long': states_info_list[0].point.x}
            return Response(
                response=json.dumps(response, sort_keys=True, ensure_ascii=False),
                mimetype='application/json')
        except Exception as err:
            return Response(
                response=json.dumps({"error": str(err)}, sort_keys=True, ensure_ascii=False),
                mimetype='application/json', status=500
            )

    @app.route('/soil_data', methods=['GET'])
    def get_soil_data():
        arguments = request.args

        try:
            lat = float(arguments.get('lat'))
            long = float(arguments.get('long'))
            state_code = str(arguments.get('state_code', None))
            points = [Point(long, lat)]
            if state_code is None:
                states_info_list = retrieve_state_code(points=points, disable_location_error=False)
            else:
                states_info_list = [StateInfo(state_code=state_code, points=points, status=StateInfoStatus.IN_PROGRESS)]
            find_ssurgo_state_folder_path(states_info_list, disable_file_error=False)
            soil_data_list = manage_retrieve_soils_composition(states_info_list)
            return Response(
                response=json.dumps(soil_data_list[0].soil_data_to_dict(), sort_keys=True, ensure_ascii=False),
                mimetype='application/json')
        except Exception as err:
            return Response(
                response=json.dumps({"error": str(err)}, sort_keys=True, ensure_ascii=False),
                mimetype='application/json', status=500
            )

    app.run(host=host, port=port)


if __name__ == '__main__':
    launch()
