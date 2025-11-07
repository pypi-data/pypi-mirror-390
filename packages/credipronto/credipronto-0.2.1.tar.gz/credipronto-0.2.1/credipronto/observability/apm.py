from dotenv import load_dotenv
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
import os


load_dotenv()


amp_config = {
    "SERVICE_NAME": os.getenv("ELASTIC_SERVICE_NAME"),
    "SERVER_URL": os.getenv("ELASTIC_SERVER_URL"),
    "ENVIRONMENT": os.getenv("ELASTIC_ENVIRONMENT"),
    "SECRET_TOKEN": os.getenv("ELASTIC_SECRET_TOKEN"),
}

apm = make_apm_client(amp_config)