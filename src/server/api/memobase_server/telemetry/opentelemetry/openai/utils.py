from typing import Any, Dict
from opentelemetry.sdk.resources import SERVICE_NAME, DEPLOYMENT_ENVIRONMENT
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from .instruments import Instruments
import tiktoken

def openai_tokens(text, model):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = len(encoding.encode(text))
    return num_tokens

def response_as_dict(response):
    if isinstance(response, dict):
        return response
    if hasattr(response, "model_dump"):
        return response.model_dump()
    elif hasattr(response, "parse"):
        return response_as_dict(response.parse())
    else:
        return response

def create_metrics_attributes(
    deployment_environment: str,
    operation: str,
    system: str,
    request_model: str,
    response_model: str,
    service_name: str = "memobase",
) -> Dict[Any, Any]:
    """
    Returns OTel metrics attributes
    """
    return {
        SERVICE_NAME: service_name,
        DEPLOYMENT_ENVIRONMENT: deployment_environment,
        gen_ai_attributes.GEN_AI_OPERATION_NAME: operation,
        gen_ai_attributes.GEN_AI_SYSTEM: system,
        gen_ai_attributes.GEN_AI_REQUEST_MODEL: request_model,
        gen_ai_attributes.GEN_AI_RESPONSE_MODEL: response_model,
    }

def record_metrics(instrument: Instruments, end_time, start_time, input_tokens, output_tokens,
                    deployment_environment, request_model, response_model):
    attributes = create_metrics_attributes(
        deployment_environment=deployment_environment,
        # operation=gen_ai_attributes.GenAiOperationNameValues.CHAT,
        # system=gen_ai_attributes.GenAiSystemValues.OPENAI,
        operation="chat",
        system="openai",
        request_model=request_model,
        response_model=response_model,
    )

    instrument.client_operation_duration_histogram.record(
        end_time - start_time,
        attributes,
    )
    instrument.client_token_usage_histogram.record(
        input_tokens + output_tokens,
        attributes,
    )

    instrument.requests.add(1, attributes)
    instrument.input_tokens.add(input_tokens, attributes)
    instrument.output_tokens.add(output_tokens, attributes)

