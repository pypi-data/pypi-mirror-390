import logging
from flask import Flask, request, json, Response, abort, send_file
from paste.translogger import TransLogger
import os
from tempfile import TemporaryDirectory
import autotwin_gmglib as gmg
import autotwin_pnglib as png
from autotwin_autlib import automata_learner as aut
from autotwin_bselib import soc_est as bse
import shutil
import io
import zipfile
import pandas
from werkzeug.exceptions import HTTPException

LOG_FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MSG_FORMAT = (
    "%(REMOTE_ADDR)s - %(REMOTE_USER)s "
    '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
    '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"'
)

logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT, level=logging.INFO)
app = Flask("proc-mining-serv")
wsgi = TransLogger(app, format=MSG_FORMAT, setup_console_handler=False)

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_DATABASE = os.environ["NEO4J_DATABASE"]

CLUSTERING_DIRECTORY = "clusterings"
BATTERY_MODEL_DIRECTORY = "battery-models"


@app.post("/graph-model")
def create_graph_model() -> Response:
    """Create a graph model in the SKG.

    Returns:
        Response with model ID.
    """
    request_data = request.get_data()
    request_data = json.loads(request_data)
    config = gmg.load_config()
    config = gmg._deep_update(request_data, config)
    work_directory = TemporaryDirectory()
    config["work_path"] = work_directory.name
    config["neo4j"]["uri"] = NEO4J_URI
    config["neo4j"]["username"] = NEO4J_USERNAME
    config["neo4j"]["password"] = NEO4J_PASSWORD
    config["neo4j"]["database"] = NEO4J_DATABASE
    if config["data"]["clustering"]["path"] != "":
        clustering_path = config["data"]["clustering"]["path"]
        source_path = os.path.join(CLUSTERING_DIRECTORY, clustering_path)
        target_path = os.path.join(config["work_path"], clustering_path)
        shutil.copy(source_path, target_path)

    gmg.import_log(config)
    gmg.import_config(config)
    log = gmg.load_log(config)
    model = gmg.generate_model(log, config)
    model_id = gmg.export_model(model, log, config)
    response_data = json.dumps({"model_id": model_id})
    return Response(response_data, status=201, mimetype="application/json")


@app.post("/petri-net")
def create_petri_net() -> Response:
    """Create a Petri net in the SKG.

    Returns:
        Response with model ID.
    """
    request_data = request.get_data()
    request_data = json.loads(request_data)
    config = gmg.load_config()
    config = gmg._deep_update(request_data, config)
    work_directory = TemporaryDirectory()
    config["work_path"] = work_directory.name
    config["neo4j"]["uri"] = NEO4J_URI
    config["neo4j"]["username"] = NEO4J_USERNAME
    config["neo4j"]["password"] = NEO4J_PASSWORD
    config["neo4j"]["database"] = NEO4J_DATABASE
    config["path"] = dict()
    config["path"]["recons_state"] = os.path.join(
        work_directory.name, "recons_state.csv"
    )
    config["path"]["input_data"] = os.path.join(
        work_directory.name, "input_data.csv"
    )
    config["path"]["model"] = os.path.join(work_directory.name, "model")

    png.reconstruct_state(config)
    png.generate_input_data(
        config["path"]["recons_state"], config["path"]["input_data"]
    )
    data = png.load_data(config["path"]["input_data"])
    alg = png.Algorithm(data)
    alg.generate_model(data)
    alg.save_model(config["path"]["model"])
    model = alg.load_model(config["path"]["model"])
    model_id = alg.export_model(model, config)
    response_data = json.dumps({"model_id": model_id})
    return Response(response_data, status=201, mimetype="application/json")


@app.post("/automaton")
def create_automaton() -> Response:
    """Create an automaton in the SKG.

    Returns:
        Response with model ID.
    """
    request_data = request.get_data()
    request_data = json.loads(request_data)
    pov = request_data["model"]["pov"].upper()
    interval = request_data["data"]["filters"]["interval"]
    schema = request_data["name"].split(maxsplit=1)[0].lower()
    version = request_data["version"] if "version" in request_data.keys() else ""
    _, model_id = aut.start_automata_learning(
        pov, interval[0], interval[1], schema, version
    )
    response_data = json.dumps({"model_id": model_id})
    return Response(response_data, status=201, mimetype="application/json")


@app.get("/api/v1/projects/ids")
def get_bm_project_ids() -> Response:
    """Get the project IDs of battery models.

    Returns:
        Response with project IDs.
    """
    rack_ids = bse.get_rack_ids()
    response_data = json.dumps(
        [{"projectUUID": id_, "scenarioUUID": id_} for id_ in rack_ids]
    )
    return Response(response_data, status=200, mimetype="application/json")


@app.get("/api/v1/scenario-executions/ids")
def get_bm_execution_ids() -> Response:
    """Get the execution IDs of battery models.

    Returns:
        Response with execution IDs.
    """
    rack_ids = bse.get_rack_ids()
    response_data = json.dumps([{"uuid": id_} for id_ in rack_ids])
    return Response(response_data, status=200, mimetype="application/json")


@app.get("/api/v1/scenario-executions/<execution_id>/parameters")
def get_bm_parameters(execution_id) -> Response:
    """Get the parameters of a battery model.

    Args:
        execution_id: Execution ID.

    Returns:
        Response with parameters.
    """
    rack_ids = bse.get_rack_ids()
    if execution_id not in rack_ids:
        abort(404)
    response_data = json.dumps(list())
    return Response(response_data, status=200, mimetype="application/json")


@app.get("/api/v1/scenario-executions/<execution_id>/json")
def get_bm_estimations_json(execution_id) -> Response:
    """Get estimations by a battery model.

    Args:
        execution_id: Execution ID.

    Returns:
        Response with estimations.
    """
    rack_ids = bse.get_rack_ids()
    if execution_id not in rack_ids:
        abort(404)
    request_data = request.get_data()
    request_data = json.loads(request_data)
    interval = request_data["interval"]
    result = bse.run_soc_period(
        execution_id, start_ms=interval[0], end_ms=interval[1],
        model_dir=BATTERY_MODEL_DIRECTORY
    )
    response_data = json.dumps(
        {
            "component": "C12",
            "data": [
                {
                    "name": "Battery DT SoC",
                    "description": "Battery DT SoC results",
                    "type": "chart",
                    "payload": json.dumps(
                        [
                            {
                                "time": result["time_axis"][x],
                                "value": result["soc_estimated"][x],
                            }
                            for x in range(len(result["time_axis"]))
                        ]
                    ),
                },
                {
                    "name": "Battery DT Voltage",
                    "description": "Battery DT Voltage results",
                    "type": "chart",
                    "payload": json.dumps(
                        [
                            {
                                "time": result["time_axis"][x],
                                "value": result["v_pred_ekf"][x],
                            }
                            for x in range(len(result["time_axis"]))
                        ]
                    ),
                },
            ],
        }
    )
    return Response(response_data, status=200, mimetype="application/json")


@app.get("/api/v1/scenario-executions/<execution_id>/out")
def get_bm_estimations_out(execution_id) -> Response:
    """Get estimations by a battery model.

    Args:
        execution_id: Execution ID.

    Returns:
        Response with estimations.
    """
    rack_ids = bse.get_rack_ids()
    if execution_id not in rack_ids:
        abort(404)
    request_data = request.get_data()
    request_data = json.loads(request_data)
    interval = request_data["interval"]
    result = bse.run_soc_period(
        execution_id, start_ms=interval[0], end_ms=interval[1],
        model_dir=BATTERY_MODEL_DIRECTORY
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as file:
        frame = pandas.DataFrame(
            {"time": result["time_axis"], "value": result["soc_estimated"]}
        )
        file.writestr("Battery DT SoC.csv", frame.to_csv(index=False))
        frame = pandas.DataFrame(
            {"time": result["time_axis"], "value": result["v_pred_ekf"]}
        )
        file.writestr("Battery DT Voltage.csv", frame.to_csv(index=False))
    buffer.seek(0)
    return send_file(
        buffer, mimetype="application/octet-stream", as_attachment=True,
        download_name="out.zip"
    )


@app.errorhandler(HTTPException)
def transform_exception(error) -> Response:
    """Transform an HTTP exception into the JSON format.

    Returns:
        Response with error information.
    """
    response = error.get_response()
    response.data = json.dumps(
        {
            "code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response


if __name__ == "__main__":
    import waitress

    waitress.serve(wsgi, host="localhost")
