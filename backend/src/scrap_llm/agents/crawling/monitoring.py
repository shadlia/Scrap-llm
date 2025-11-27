from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from dotenv import load_dotenv
import os
import base64
from .config import APP_NAME


load_dotenv()

public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

LANGFUSE_AUTH = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
OTEL_EXPORTER_OTLP_HEADERS = f"Authorization=Basic {LANGFUSE_AUTH}"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = OTEL_EXPORTER_OTLP_HEADERS
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
    "https://langfuse-v7bb6gldtq-ew.a.run.app/api/public/otel"
)
provider = TracerProvider(resource=Resource.create({"service.name": "crawling_agent"}))

print("provider", provider)
exporter = OTLPSpanExporter()
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("crawling_agent")
