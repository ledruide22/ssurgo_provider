import json

from flask import Flask, Response, request

from src.ssurgo_provider.tools import retrieve_multiple_soil_data


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
            states_info_list = retrieve_multiple_soil_data([(lat, long)])
            return Response(
                response=json.dumps(states_info_list[0].soil_data_to_dict(), sort_keys=True, ensure_ascii=False),
                mimetype='application/json')
        except Exception as err:
            return Response(
                response=json.dumps({"error": str(err)}, sort_keys=True, ensure_ascii=False),
                mimetype='application/json', status=500
            )

    app.run(host=host, port=port)


if __name__ == '__main__':
    launch()
