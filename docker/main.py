import json
from pathlib import Path

from flask import Flask, Response, request

from src.ssurgo_provider.tools import retrieve_soil_composition


def launch(port="8180", host="0.0.0.0"):
    app = Flask(__name__)

    @app.route('/')
    def status():
        return "READY TO RETURN SSURGO DATA"

    @app.route('/soil_data', methods=['GET'])
    def get_soil_data():
        arguments = request.args

        try:
            lat = float(arguments.get('lat'))
            long = float(arguments.get('long'))
            state_code = arguments.get('state_code')
            ssurgo_folder_path = Path().absolute().parent / 'resources' / 'SSURGO' / 'soils_GSSURGO_oh_3905571_01' \
                                 / 'soils' / 'gssurgo_g_oh' / 'gSSURGO_OH.gdb'
            soil_data_list = retrieve_soil_composition((lat, long), ssurgo_folder_path)
            return Response(response=json.dumps(soil_data_list[0].to_dict(), sort_keys=True, ensure_ascii=False),
                            mimetype='application/json')
        except Exception as err:
            return Response(
                response=json.dumps({"error": str(err)}, sort_keys=True, ensure_ascii=False),
                mimetype='application/json', status=500
            )

    app.run(host=host, port=port)


if __name__ == '__main__':
    launch()
