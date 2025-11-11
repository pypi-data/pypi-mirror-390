from typing import Sequence

import pytest
from codemie_sdk.models.assistant import ToolKitDetails, ToolDetails
from hamcrest import assert_that, has_item, greater_than

from codemie_test_harness.tests.enums.model_types import ModelTypes
from codemie_test_harness.tests.enums.tools import Toolkit, FileManagementTool
from codemie_test_harness.tests.test_data.llm_test_data import MODEL_RESPONSES
from codemie_test_harness.tests.utils.client_factory import get_client
from codemie_test_harness.tests.utils.env_resolver import get_environment
from codemie_test_harness.tests.utils.pytest_utils import check_mark

SIMPLE_GREETING_PROMPT = "Just say one word: 'Hello'"


def get_model_names(llm_utils) -> Sequence[str]:
    """Get list of available model names."""
    return [row.base_name for row in llm_utils.list_llm_models()]


def pytest_generate_tests(metafunc):
    if "model_type" in metafunc.fixturenames:
        is_smoke = check_mark(metafunc, "smoke")
        test_data = []
        env = get_environment()
        if is_smoke:
            available_models = get_client().llms.list()
            for model in available_models:
                test_data.append(pytest.param(model.base_name))
        else:
            for model_data in MODEL_RESPONSES:
                test_data.append(
                    pytest.param(
                        model_data.model_type,
                        marks=pytest.mark.skipif(
                            env not in model_data.environments,
                            reason=f"Skip on non {'/'.join(str(env) for env in model_data.environments[:-1])} envs",
                        ),
                    )
                )

        metafunc.parametrize("model_type", test_data)


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.api
@pytest.mark.smoke
def test_assistant_with_different_models(
    llm_utils, assistant_utils, model_type, similarity_check, filesystem_integration
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )

    tool = ToolKitDetails(
        toolkit=Toolkit.FILE_MANAGEMENT,
        tools=[
            ToolDetails(
                name=FileManagementTool.GENERATE_IMAGE, settings=filesystem_integration
            )
        ],
        settings=filesystem_integration,
    )

    _assistant = assistant_utils.create_assistant(model_type, toolkits=[tool])
    response = assistant_utils.ask_assistant(_assistant, SIMPLE_GREETING_PROMPT)

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.top_p
@pytest.mark.api
@pytest.mark.smoke
def test_assistant_with_different_models_with_top_p_parameter(
    llm_utils, assistant_utils, model_type, similarity_check
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )
    _assistant = assistant_utils.create_assistant(model_type, top_p=0.5)
    response = assistant_utils.ask_assistant(_assistant, SIMPLE_GREETING_PROMPT)

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.temperature
@pytest.mark.api
@pytest.mark.smoke
def test_assistant_with_different_models_with_temperature_parameter(
    llm_utils, assistant_utils, model_type, similarity_check
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )
    _assistant = assistant_utils.create_assistant(model_type, temperature=0.5)
    response = assistant_utils.ask_assistant(_assistant, SIMPLE_GREETING_PROMPT)

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.api
@pytest.mark.smoke
def test_assistant_with_different_models_with_datasource_attached(
    llm_utils,
    assistant_utils,
    model_type,
    similarity_check,
    datasource_utils,
    default_embedding_llm,
    kb_context,
    file_datasource,
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )

    _assistant = assistant_utils.create_assistant(
        model_type, context=[kb_context(file_datasource)]
    )
    response = assistant_utils.ask_assistant(_assistant, SIMPLE_GREETING_PROMPT)

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.sub_assistant
@pytest.mark.api
@pytest.mark.smoke
def test_assistant_with_different_models_with_sub_assistant(
    llm_utils, assistant_utils, model_type, similarity_check
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )

    # Create sub-assistant with default model
    sub_assistant = assistant_utils.create_assistant(
        system_prompt="You are a specialized sub-assistant.",
    )

    # Create parent assistant with the parametrized model that delegates to sub-assistant
    parent_assistant = assistant_utils.create_assistant(
        llm_model_type=model_type,
        system_prompt="You are a coordinator assistant.",
        assistant_ids=[sub_assistant.id],
    )

    # Test parent assistant that should delegate to sub-assistant
    response = assistant_utils.ask_assistant(parent_assistant, SIMPLE_GREETING_PROMPT)

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        response = "\n".join(response.split("\n")[-3:])
    similarity_check.check_similarity(response, "Hello")


@pytest.mark.assistant
@pytest.mark.llm
@pytest.mark.api
@pytest.mark.smoke
def test_chatting_with_different_models_in_stream_mode(
    llm_utils, assistant_utils, model_type, similarity_check, filesystem_integration
):
    assert_that(
        get_model_names(llm_utils),
        has_item(model_type),
        f"{model_type} is missing in backend response",
    )

    tool = ToolKitDetails(
        toolkit=Toolkit.FILE_MANAGEMENT,
        tools=[
            ToolDetails(
                name=FileManagementTool.GENERATE_IMAGE, settings=filesystem_integration
            )
        ],
        settings=filesystem_integration,
    )

    _assistant = assistant_utils.create_assistant(model_type, toolkits=[tool])

    is_o_model = model_type in [
        ModelTypes.O1,
        ModelTypes.O3_MINI,
        ModelTypes.O3_2025_04_16,
        ModelTypes.O4_MINI_2025_04_16,
    ]

    if not is_o_model:
        streaming_prompt = (
            "Write a short paragraph (10 sentences) about the importance of testing. "
            "Make sure to mention unit tests, integration tests, and end-to-end tests."
        )

        response_metadata = assistant_utils.ask_assistant(
            _assistant, streaming_prompt, stream=True, return_stream_metadata=True
        )

        chunk_count = response_metadata["chunk_count"]
        thought_count = response_metadata["thought_count"]

        assert_that(
            chunk_count,
            greater_than(5),
            f"Expected true streaming with many chunks, got only {chunk_count} (thoughts: {thought_count})",
        )

        assert_that(
            thought_count,
            greater_than(3),
            f"Expected multiple incremental thought chunks, got only {thought_count} (total chunks: {chunk_count})",
        )

    simple_response = assistant_utils.ask_assistant(
        _assistant, SIMPLE_GREETING_PROMPT, stream=True
    )

    if model_type in [ModelTypes.DEEPSEEK_R1, ModelTypes.RLAB_QWQ_32B]:
        simple_response = "\n".join(simple_response.split("\n")[-3:])
    similarity_check.check_similarity(simple_response, "Hello")
