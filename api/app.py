import importlib
import json
import logging
import os
import secrets

from elody.loader import load_policies
from flask import Flask
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from healthcheck import HealthCheck
from inuits_policy_based_auth import PolicyFactory
from job_helper.job_extension import JobExtension

if os.getenv("SENTRY_ENABLED", False) in ["True", "true", True]:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        environment=os.getenv("NOMAD_NAMESPACE"),
    )

SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/spec/inuits-dams-ocr-service.json"  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)

app = Flask(__name__)
api = Api(app)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

logging.basicConfig(
    format="%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

amqp_module = importlib.import_module(os.getenv("AMQP_MANAGER", "amqpstorm_flask"))
auto_delete_exchange = os.getenv("AUTO_DELETE_EXCHANGE", False) in [
    1,
    "1",
    True,
    "True",
    "true",
]
durable_exchange = os.getenv("DURABLE_EXCHANGE", True) in [1, "1", True, "True", "true"]
passive_exchange = os.getenv("PASSIVE_EXCHANGE", False) in [
    1,
    "1",
    True,
    "True",
    "true",
]
rabbit = amqp_module.RabbitMQ(
    exchange_params=amqp_module.ExchangeParams(
        auto_delete=auto_delete_exchange,
        durable=durable_exchange,
        passive=passive_exchange,
    )
)
rabbit.init_app(app, "basic", json.loads, json.dumps)

jobs_extension = JobExtension(rabbit)

app.register_blueprint(swaggerui_blueprint)


def rabbit_available():
    connection = rabbit.get_connection()
    if connection.is_open:
        connection.close()
        return True, "Successfully reached RabbitMQ"
    return False, "Failed to reach RabbitMQ"


health = HealthCheck()
if os.getenv("HEALTH_CHECK_EXTERNAL_SERVICES", True) in ["True", "true", True]:
    health.add_check(rabbit_available)
app.add_url_rule("/health", "healthcheck", view_func=lambda: health.run())

policy_factory = PolicyFactory()
load_policies(policy_factory, logger)

from resources.ocr import Ocr
from resources.ocr_correction import OcrCorrection
from resources.status import Status
import resources.queues
from resources.spec import OpenAPISpec

api.add_resource(Ocr, "/ocr")
api.add_resource(OcrCorrection, "/ocr/correction")
api.add_resource(Status, "/status")
api.add_resource(OpenAPISpec, "/spec/inuits-dams-ocr-service.json")

if __name__ == "__main__":
    app.run()
