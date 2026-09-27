from app.generation import (
    REFUSAL,
    build_user_prompt,
    is_refusal,
    limit_words,
    process_answer,
    system_prompt,
)


def test_citations_are_renumbered_in_order_of_use():
    result = process_answer("Fourteen characters [S3]. Changed every 180 days [S1, S3].", 5, 200)
    assert result.cited == [3, 1]
    assert result.text == "Fourteen characters [1]. Changed every 180 days [2][1]."
    assert not result.refused


def test_labels_that_were_not_retrieved_are_removed():
    result = process_answer("A made-up rule [S9]. A real rule [S2].", 5, 200)
    assert result.cited == [2]
    assert "[S9]" not in result.text and "[9]" not in result.text


def test_refusal_is_detected_and_normalized():
    result = process_answer("I can only answer questions about Veridane Bank policies.", 5, 200)
    assert result.refused and result.text == REFUSAL and result.cited == []
    assert is_refusal(REFUSAL)


def test_answers_are_trimmed_to_the_word_limit_at_a_sentence_end():
    text = (
        "Rule one applies to every account in the bank today [1]. "
        "Rule two applies to privileged accounts only [2]. " + "extra " * 40
    )
    trimmed = limit_words(text, 25)
    assert trimmed.endswith("only [2].")
    assert len(trimmed.split()) <= 25
    assert limit_words("short answer [1].", 25) == "short answer [1]."


def test_markdown_emphasis_and_headings_are_removed():
    result = process_answer("## Answer\nThe minimum is **14 characters** [S1].", 5, 200)
    assert result.text == "Answer\nThe minimum is 14 characters [1]."


def test_prompt_explains_how_to_use_revision_history():
    prompt = system_prompt(200)
    assert "Revision History" in prompt and "changes, updates, or earlier versions" in prompt
    assert "Only if no excerpt contains it" in prompt


def test_prompt_labels_each_excerpt_with_its_source():
    meta = {"doc_id": "VB-POL-002", "title": "Password Policy", "version": "3.1", "section": "4.1"}
    prompt = build_user_prompt("How long?", [(meta, "Minimum length: 14 characters")])
    assert prompt.startswith("Policy excerpts:")
    assert '[S1] VB-POL-002 Password Policy (version 3.1), section "4.1"' in prompt
    assert prompt.endswith("Question: How long?")
    assert REFUSAL in system_prompt(200) and "200 words" in system_prompt(200)


class _StubClient:
    """Mimics openai.OpenAI().chat.completions.create and records the request."""

    def __init__(self, content, finish_reason="stop"):
        from types import SimpleNamespace

        self.kwargs = None
        message = SimpleNamespace(content=content)
        self._response = SimpleNamespace(
            choices=[SimpleNamespace(message=message, finish_reason=finish_reason)]
        )
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.kwargs = kwargs
        return self._response


def _model(settings, client, **changes):
    from dataclasses import replace

    from app.generation import GroqChatModel

    model = GroqChatModel(replace(settings, groq_api_key="test-key", **changes))
    model._client = client
    return model


def test_reasoning_models_get_low_effort_and_hidden_reasoning(settings):
    client = _StubClient("Fourteen characters [S1].")
    reply = _model(settings, client, llm_reasoning_effort="low").complete("system", "user")
    assert reply == "Fourteen characters [S1]."
    assert client.kwargs["reasoning_effort"] == "low"
    assert client.kwargs["extra_body"] == {"include_reasoning": False}
    assert client.kwargs["max_completion_tokens"] == settings.llm_max_tokens


def test_reasoning_options_are_omitted_for_other_models(settings):
    client = _StubClient("Fourteen characters [S1].")
    _model(settings, client, llm_reasoning_effort="").complete("system", "user")
    assert "reasoning_effort" not in client.kwargs and "extra_body" not in client.kwargs


def test_an_empty_reply_is_an_error_not_a_refusal(settings):
    import pytest

    from app.generation import LLMUnavailableError

    client = _StubClient("", finish_reason="length")
    with pytest.raises(LLMUnavailableError, match="finish_reason=length"):
        _model(settings, client).complete("system", "user")
