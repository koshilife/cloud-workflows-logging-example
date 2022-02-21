import os
import json

from flask import Flask, jsonify, request

GCP_PROJECT = os.environ.get('GCP_PROJECT')

app = Flask(__name__)

@app.route("/", methods=["POST"])
def main():
    try:
        logger = get_structured_logger('Cloud Run')
        logger.default('DEFAULT')
        logger.debug('DEBUG')
        logger.info('INFO')
        logger.notice('NOTICE')
        logger.warning('WARNING')
        logger.error('ERROR')
        logger.critical('CRITICAL')
        logger.alert('ALERT')
        logger.emergency('EMERGENCY')
        foo()
        bar()
    except:
        # For debug
        import logging
        logging.exception('error occurred.')
        return jsonify(dict(result='ng'))
    return jsonify(dict(result='ok'))


def foo():
    logger = get_structured_logger()
    logger.info("foo started.")
    logger.info("foo finished.")


def bar():
    logger = get_structured_logger()
    logger.info("bar started.")
    logger.info("bar finished.")


cache_logger = None
def get_structured_logger(message_prefix=None, is_reload=False):
    global cache_logger
    if cache_logger and not is_reload:
        return cache_logger

    log_fields = {}

    # refs: https://cloud.google.com/functions/docs/monitoring/logging#writing_structured_logs
    if request and request.headers.get("X-Cloud-Trace-Context") and GCP_PROJECT:
        trace = request.headers["X-Cloud-Trace-Context"].split("/")
        log_fields["logging.googleapis.com/trace"] = f"projects/{GCP_PROJECT}/traces/{trace[0]}"

    request_json = request.get_json()
    if request_json and request_json.get("workflow_execution_id"):
        log_fields["logging.googleapis.com/labels"] = {'workflows.googleapis.com/execution_id': request_json["workflow_execution_id"]}

    def _log(message, severity=None):
        if not message:
            return
        _msg = f'{message_prefix} {message}' if message_prefix else message
        payload = dict(message=_msg, severity=severity, **log_fields)
        print(json.dumps(payload))

    class CloudLoggingStructuredLogger:
        def default(self, message):
            _log(message, 'DEFAULT')
        def debug(self, message):
            _log(message, 'DEBUG')
        def info(self, message):
            _log(message, 'INFO')
        def notice(self, message):
            _log(message, 'NOTICE')
        def warning(self, message):
            _log(message, 'WARNING')
        def error(self, message):
            _log(message, 'ERROR')
        def critical(self, message):
            _log(message, 'CRITICAL')
        def alert(self, message):
            _log(message, 'ALERT')
        def emergency(self, message):
            _log(message, 'EMERGENCY')

    cache_logger = CloudLoggingStructuredLogger()
    return cache_logger

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
