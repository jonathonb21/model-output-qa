import httpx

from model_output_qa.rubric import RubricClient


def test_rubric_client_score(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://rubric.test/score",
        json={"overall": 0.8, "dimensions": {}},
    )
    client = RubricClient("http://rubric.test")
    result = client.score("def f(): pass", {"correctness": "uses a function"})
    assert result["overall"] == 0.8


def test_score_if_available_returns_none_on_error():
    client = RubricClient("http://127.0.0.1:1")
    assert client.score_if_available("x", {"a": "b"}) is None


def test_score_batch_skips_unreachable():
    client = RubricClient("http://127.0.0.1:1")
    results = client.score_batch(
        [{"answer": "a"}, {"answer": "b"}],
        rubric={"style": "clear"},
    )
    assert results == [None, None]
