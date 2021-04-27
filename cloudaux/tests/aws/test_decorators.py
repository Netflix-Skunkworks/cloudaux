"""
.. module: cloudaux.tests.aws.test_decorators
    :platform: Unix
    :copyright: (c) 2021 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Patrick Sanders <psanders@netflix.com>
"""

from mock import MagicMock, call

from cloudaux.aws.decorators import paginated


def test_paginated_single_page():
    mock_responder = MagicMock()
    mock_responder.side_effect = [
        {
            "NextToken": None,
            "Data": ["a", "b"]
        },
    ]

    @paginated("Data", request_pagination_marker="NextToken", response_pagination_marker="NextToken")
    def retrieve_letters(**kwargs):
        return mock_responder(**kwargs)

    result = retrieve_letters()
    assert result == ["a", "b"]
    assert mock_responder.call_count == 1
    mock_responder.assert_has_calls([call()])


def test_paginated_multiple_pages():
    mock_responder = MagicMock()
    mock_responder.side_effect = [
        {
            "NextToken": "1",
            "Data": ["a", "b"]
        },
        {
            "NextToken": "2",
            "Data": ["c", "d"]
        },
        {
            "NextToken": None,
            "Data": ["e", "f"]
        },
    ]

    @paginated("Data", request_pagination_marker="NextToken", response_pagination_marker="NextToken")
    def retrieve_letters(**kwargs):
        return mock_responder(**kwargs)

    result = retrieve_letters()
    assert result == ["a", "b", "c", "d", "e", "f"]
    assert mock_responder.call_count == 3
    mock_responder.assert_has_calls([call(), call(NextToken="1"), call(NextToken="2")])


def test_paginated_multiple_pages_empty_results():
    mock_responder = MagicMock()
    mock_responder.side_effect = [
        {
            "NextToken": "1",
            "Data": []
        },
        {
            "NextToken": "2",
            "Data": []
        },
        {
            "NextToken": "3",
            "Data": ["e", "f"]
        },
        {
            "NextToken": None,
            "Data": []
        },
    ]

    @paginated("Data", request_pagination_marker="NextToken", response_pagination_marker="NextToken")
    def retrieve_letters(**kwargs):
        return mock_responder(**kwargs)

    result = retrieve_letters()
    assert result == ["e", "f"]
    assert mock_responder.call_count == 4
    mock_responder.assert_has_calls([call(), call(NextToken="1"), call(NextToken="2"), call(NextToken="3")])
