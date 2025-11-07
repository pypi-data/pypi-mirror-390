# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Oliver Boehmer


"""Unit tests for JMESPath library."""

import pytest

from JMESPathLibrary import JMESPathLibrary


class TestJsonSearch:
    """Tests for json_search keyword."""

    @pytest.fixture
    def library(self) -> JMESPathLibrary:
        """Create JMESPath library instance."""
        return JMESPathLibrary()

    def test_returns_dict(self, library: JMESPathLibrary) -> None:
        """Test that dict result is returned unaltered."""
        data = {"user": {"name": "Alice", "age": 30}}
        result = library.json_search(data, "user")
        assert result == {"name": "Alice", "age": 30}
        assert isinstance(result, dict)

    def test_returns_list(self, library: JMESPathLibrary) -> None:
        """Test that list result is returned unaltered."""
        data = {"users": ["Alice", "Bob", "Charlie"]}
        result = library.json_search(data, "users")
        assert result == ["Alice", "Bob", "Charlie"]
        assert isinstance(result, list)

    def test_returns_string(self, library: JMESPathLibrary) -> None:
        """Test that string result is returned unaltered."""
        data = {"name": "Alice"}
        result = library.json_search(data, "name")
        assert result == "Alice"
        assert isinstance(result, str)

    def test_returns_number(self, library: JMESPathLibrary) -> None:
        """Test that number result is returned unaltered."""
        data = {"age": 30}
        result = library.json_search(data, "age")
        assert result == 30
        assert isinstance(result, int)

    def test_returns_none_for_no_match(self, library: JMESPathLibrary) -> None:
        """Test that None is returned for no match."""
        data = {"name": "Alice"}
        result = library.json_search(data, "missing")
        assert result is None

    def test_jmespath_function(self, library: JMESPathLibrary) -> None:
        """Test using JMESPath function."""
        data = {"users": ["Alice", "Bob", "Charlie"]}
        result = library.json_search(data, "length(users)")
        assert result == 3


class TestJsonSearchString:
    """Tests for json_search_string keyword."""

    @pytest.fixture
    def library(self) -> JMESPathLibrary:
        """Create JMESPath library instance."""
        return JMESPathLibrary()

    def test_simple_path(self, library: JMESPathLibrary) -> None:
        """Test simple object path."""
        data = {"name": "Alice", "age": 30}
        result = library.json_search_string(data, "name")
        assert result == "Alice"

    def test_nested_path(self, library: JMESPathLibrary) -> None:
        """Test nested object path."""
        data = {"user": {"name": "Bob", "age": 25}}
        result = library.json_search_string(data, "user.name")
        assert result == "Bob"

    def test_array_access(self, library: JMESPathLibrary) -> None:
        """Test array element access."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        result = library.json_search_string(data, "users[0].name")
        assert result == "Alice"

    def test_filter_expression(self, library: JMESPathLibrary) -> None:
        """Test filter with pipe."""
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        result = library.json_search_string(data, "users[?age > `25`] | [0].name")
        assert result == "Alice"

    def test_no_match_returns_empty_string(self, library: JMESPathLibrary) -> None:
        """Test that no match returns empty string."""
        data = {"name": "Alice"}
        result = library.json_search_string(data, "missing")
        assert result == ""

    def test_error_handling(self, library: JMESPathLibrary) -> None:
        """Test that invalid expression raises error."""
        import jmespath.exceptions

        data = {"name": "Alice"}
        with pytest.raises(jmespath.exceptions.IncompleteExpressionError):
            library.json_search_string(data, "invalid[")


class TestJsonSearchList:
    """Tests for json_search_list keyword."""

    @pytest.fixture
    def library(self) -> JMESPathLibrary:
        """Create JMESPath library instance."""
        return JMESPathLibrary()

    def test_simple_list(self, library: JMESPathLibrary) -> None:
        """Test simple list result."""
        data = {"names": ["Alice", "Bob", "Charlie"]}
        result = library.json_search_list(data, "names")
        assert result == ["Alice", "Bob", "Charlie"]

    def test_wildcard_projection(self, library: JMESPathLibrary) -> None:
        """Test wildcard array projection."""
        data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
        result = library.json_search_list(data, "users[*].name")
        assert result == ["Alice", "Bob"]

    def test_filter_list(self, library: JMESPathLibrary) -> None:
        """Test filtered list result."""
        data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
        result = library.json_search_list(data, "users[?age > `25`].name")
        assert result == ["Alice"]

    def test_single_result_wrapped_in_list(self, library: JMESPathLibrary) -> None:
        """Test that single result is wrapped in list."""
        data = {"name": "Alice"}
        result = library.json_search_list(data, "name")
        assert result == ["Alice"]

    def test_no_match_returns_empty_list(self, library: JMESPathLibrary) -> None:
        """Test that no match returns empty list."""
        data = {"name": "Alice"}
        result = library.json_search_list(data, "missing")
        assert result == []

    def test_error_handling(self, library: JMESPathLibrary) -> None:
        """Test that invalid expression raises error."""
        import jmespath.exceptions

        data = {"name": "Alice"}
        with pytest.raises(jmespath.exceptions.IncompleteExpressionError):
            library.json_search_list(data, "invalid[")
