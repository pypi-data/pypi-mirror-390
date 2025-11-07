# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Oliver Boehmer

"""
JMESPath keyword implementations for Robot Framework.

This module contains the keyword methods that provide JSON querying functionality
using JMESPath expressions.
"""

from typing import Any

import jmespath
from robot.api.deco import keyword


class JMESPathKeywords:
    """
    Implementation class containing all JMESPath keyword methods.

    This class provides the core keyword implementations for JSON querying
    using JMESPath expressions in Robot Framework tests.
    """

    ROBOT_LIBRARY_DOC_FORMAT = "HTML"

    @keyword(name="JSON Search")
    def json_search(self, data: Any, expression: str) -> Any:
        """<p>Execute a JMESPath query and return the raw result unaltered.</p>

            <p>This keyword executes a JMESPath expression against JSON data and returns
            the result exactly as returned by JMESPath, without any type conversion.
            Use this when you need the raw query result (dict, list, string, number, etc.).</p>

            <p><strong>Arguments:</strong></p>
            <ul>
                <li><code>data</code>: The JSON data to query (typically from ${response.json()})</li>
                <li><code>expression</code>: A JMESPath expression string</li>
            </ul>

            <p><strong>Returns:</strong> The raw JMESPath query result (can be any type)</p>

            <p><strong>Examples:</strong></p>
            <pre>
        ${result}=    JSON Search    ${json}    imdata&#91;0&#93;.fvTenant
        ${count}=     JSON Search    ${json}    length(users)
            </pre>
        """
        return jmespath.search(expression, data)

    @keyword(name="JSON Search String")
    def json_search_string(self, data: Any, expression: str) -> str:
        """<p>Execute a JMESPath query and return a single string result.</p>

            <p>This keyword executes a JMESPath expression against JSON data and returns
            the first result as a string. If the result is a list, the first element
            is returned. If no results are found, returns an empty string.</p>

            <p><strong>Arguments:</strong></p>
            <ul>
                <li><code>data</code>: The JSON data to query (typically from ${response.json()})</li>
                <li><code>expression</code>: A JMESPath expression string</li>
            </ul>

            <p><strong>Returns:</strong> A string value, or empty string if no match</p>

            <p><strong>Examples:</strong></p>
            <pre>
        ${result}=    JSON Search String    ${json}    imdata&#91;0&#93;.fvTenant.attributes.name
        ${result}=    JSON Search String    ${json}    imdata&#91;0&#93;.fvTenant.children&#91;?fvAp&#93; | &#91;0&#93;.fvAp.attributes.name
            </pre>
        """
        result = self.json_search(data, expression)

        # Handle different result types
        if result is None:
            return ""
        elif isinstance(result, list):
            # Return first element if list, or empty string if empty list
            return str(result[0]) if result else ""
        else:
            return str(result)

    @keyword(name="JSON Search List")
    def json_search_list(self, data: Any, expression: str) -> list[Any]:
        """<p>Execute a JMESPath query and return results as a list.</p>

            <p>This keyword executes a JMESPath expression against JSON data and returns
            the results as a list. If the result is not already a list, it will be
            wrapped in a list. Returns an empty list if no matches are found.</p>

            <p><strong>Arguments:</strong></p>
            <ul>
                <li><code>data</code>: The JSON data to query (typically from ${response.json()})</li>
                <li><code>expression</code>: A JMESPath expression string</li>
            </ul>

            <p><strong>Returns:</strong> A list of results, or empty list if no matches</p>

            <p><strong>Examples:</strong></p>
            <pre>
        ${results}=    JSON Search List    ${json}    imdata&#91;0&#93;.fvTenant.children&#91;*&#93;.fvAp.attributes.name
        ${ips}=        JSON Search List    ${json}    imdata&#91;0&#93;.fvBD.children&#91;*&#93;.fvSubnet.attributes.ip
            </pre>
        """
        result = self.json_search(data, expression)

        # Handle different result types
        if result is None:
            return []
        elif isinstance(result, list):
            return result
        else:
            # Wrap single result in a list
            return [result]
