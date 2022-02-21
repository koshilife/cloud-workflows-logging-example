import os
import json

from flask import Flask, jsonify, request

GCP_PROJECT = os.environ.get('GCP_PROJECT')

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    log('Cloud Run msg1')
    log('Cloud Run msg1', 'WARNING')
    return jsonify(dict(result='ok'))


def log(message, severity='INFO'):
    log_fields = {}

    # refs: https://cloud.google.com/functions/docs/monitoring/logging#writing_structured_logs
    if request and request.headers.get("X-Cloud-Trace-Context") and GCP_PROJECT:
        trace = request.headers["X-Cloud-Trace-Context"].split("/")
        log_fields["logging.googleapis.com/trace"] = f"projects/{GCP_PROJECT}/traces/{trace[0]}"

    request_json = request.get_json()
    if request_json and request_json.get("workflow_execution_id"):
        log_fields["logging.googleapis.com/labels"] = {'workflows.googleapis.com/execution_id': request_json["workflow_execution_id"]}

    payload = dict(message=message, severity=severity, **log_fields)
    print(json.dumps(payload))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
