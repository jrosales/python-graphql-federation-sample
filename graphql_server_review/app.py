from ariadne import graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

from prometheus_flask_exporter import PrometheusMetrics

from schema.schema import SchemaCreator

schemaCreator = SchemaCreator()
schema = schemaCreator.getSchema()

app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.run(debug=False)

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.3')

@app.route("/", methods=["GET"])
@metrics.summary('requests_by_status', 'Request latencies by status')
def graphql_playgroud():
    return PLAYGROUND_HTML, 200


@app.route("/", methods=["POST"])
@metrics.summary('queries', 'Q latencies by status')
def graphql_server():
    data = request.get_json()
    print(data)
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    print(jsonify(result))
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8302)