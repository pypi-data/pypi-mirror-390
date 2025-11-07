# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Oliver Boehmer

"""
JMESPath library for Robot Framework.

This library provides high-performance JSON querying capabilities using JMESPath expressions,
offering a modern alternative to JSONPath for Robot Framework tests.
"""

from .keywords import JMESPathKeywords

__version__ = "0.1.0"
__all__ = ["JMESPathLibrary"]


class JMESPathLibrary(JMESPathKeywords):
    """<p>JMESPath is a Robot Framework library that provides high-performance JSON querying
        using <a href="https://jmespath.org/">JMESPath</a> expressions.</p>

        <h2>Why JMESPath?</h2>

        <p>JMESPath offers significant advantages over JSONPath for Robot Framework testing:</p>
        <ul>
            <li><strong>Better Performance</strong>: Native Python implementation with superior performance</li>
            <li><strong>More Powerful</strong>: Rich filtering, projections, and transformations</li>
            <li><strong>Better Maintained</strong>: Active development and strong community support</li>
            <li><strong>Simpler Syntax</strong>: Cleaner, more intuitive query expressions</li>
            <li><strong>Standardized</strong>: Well-defined specification and behavior</li>
        </ul>

        <h2>Installation</h2>

        <pre>pip install robotframework-jmespath</pre>

        <h2>Usage</h2>

        <p>The library provides keywords for querying JSON data with JMESPath expressions.</p>

        <h3>Quick Start</h3>

        <pre>
    *** Settings ***
    Library    JMESPathLibrary

    *** Test Cases ***
    Query JSON Data
        ${json}=    Set Variable    ${{ {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]} }}
        ${name}=    JSON Search String    ${json}    users&#91;0&#93;.name
        Should Be Equal    ${name}    Alice

        ${names}=    JSON Search List    ${json}    users&#91;*&#93;.name
        Should Contain    ${names}    Alice
        Should Contain    ${names}    Bob
        </pre>

        <h2>JMESPath Syntax Overview</h2>

        <h3>Basic Operations</h3>

        <table border="1">
            <tr>
                <th>Operation</th>
                <th>Example</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>Object access</td>
                <td><code>foo.bar</code></td>
                <td>Access nested object</td>
            </tr>
            <tr>
                <td>Array access</td>
                <td><code>foo&#91;0&#93;</code></td>
                <td>Access array element</td>
            </tr>
            <tr>
                <td>Array slice</td>
                <td><code>foo&#91;0:2&#93;</code></td>
                <td>Slice array</td>
            </tr>
            <tr>
                <td>Wildcard</td>
                <td><code>foo&#91;*&#93;.bar</code></td>
                <td>All array elements</td>
            </tr>
            <tr>
                <td>Filter</td>
                <td><code>foo&#91;?bar=='value'&#93;</code></td>
                <td>Filter array</td>
            </tr>
            <tr>
                <td>Pipe</td>
                <td><code>foo | &#91;0&#93;</code></td>
                <td>Chain expressions</td>
            </tr>
        </table>

        <h3>Common Patterns</h3>

        <p><strong>Access nested object:</strong></p>
        <pre>imdata&#91;0&#93;.fvTenant.attributes.name</pre>

        <p><strong>Filter array by attribute (with pipe):</strong></p>
        <pre>imdata&#91;0&#93;.fvTenant.children&#91;?fvAp.attributes.name=='AP1'&#93; | &#91;0&#93;</pre>

        <p><strong>Get all names from array:</strong></p>
        <pre>imdata&#91;0&#93;.fvTenant.children&#91;*&#93;.fvAp.attributes.name</pre>

        <p><strong>Filter with multiple conditions:</strong></p>
        <pre>users&#91;?age &gt; `25` &amp;&amp; active == `true`&#93;</pre>

        <h2>Usage with REST API Testing</h2>

        <p>JMESPath library works excellently with RequestsLibrary for REST API testing.</p>

        <h3>Example: API Testing with RequestsLibrary</h3>

        <pre>
    *** Settings ***
    Library    RequestsLibrary
    Library    JMESPathLibrary

    *** Test Cases ***
    Verify API Response
        # Make API call
        ${response}=    GET    https://jsonplaceholder.typicode.com/posts/1
        ${json}=        Set Variable    ${response.json()}

        # Query with JMESPath
        ${user_id}=    JSON Search String    ${json}    userId
        Should Be Equal As Numbers    ${user_id}    1

        # Query nested objects
        ${title}=    JSON Search String    ${json}    title
        Should Not Be Empty    ${title}
        </pre>

        <h3>Example: Cisco ACI API Testing</h3>

        <pre>
    *** Settings ***
    Library    RequestsLibrary
    Library    JMESPathLibrary

    Suite Setup    Create Session    apic    https://apic.example.com

    *** Test Cases ***
    Verify Tenant Configuration
        # Make API call
        ${response}=    GET On Session    apic    /api/mo/uni/tn-TENANT1.json
        ...    params=rsp-subtree=full
        ${json}=        Set Variable    ${response.json()}

        # Query tenant name
        ${tenant_name}=    JSON Search String    ${json}
        ...    imdata&#91;0&#93;.fvTenant.attributes.name
        Should Be Equal    ${tenant_name}    TENANT1

        # Query nested objects with filter
        ${ap_name}=    JSON Search String    ${json}
        ...    imdata&#91;0&#93;.fvTenant.children&#91;?fvAp.attributes.name=='AP1'&#93; | &#91;0&#93;.fvAp.attributes.name
        Should Be Equal    ${ap_name}    AP1

        # Get all subnet IPs as list
        ${subnets}=    JSON Search List    ${json}
        ...    imdata&#91;0&#93;.fvTenant.children&#91;*&#93;.fvBD.children&#91;*&#93;.fvSubnet.attributes.ip
        Should Contain    ${subnets}    10.0.0.1/24
        </pre>

        <h2>Comparison with JSONPath</h2>

        <table border="1">
            <tr>
                <th>Feature</th>
                <th>JSONPath</th>
                <th>JMESPath</th>
            </tr>
            <tr>
                <td>Root</td>
                <td><code>$</code></td>
                <td><code>(implicit)</code></td>
            </tr>
            <tr>
                <td>Child access</td>
                <td><code>$.foo.bar</code></td>
                <td><code>foo.bar</code></td>
            </tr>
            <tr>
                <td>Recursive descent</td>
                <td><code>$..field</code></td>
                <td>Not supported*</td>
            </tr>
            <tr>
                <td>Array filter</td>
                <td><code>$&#91;?(@.age &gt; 25)&#93;</code></td>
                <td><code>&#91;?age &gt; `25`&#93;</code></td>
            </tr>
            <tr>
                <td>Wildcard</td>
                <td><code>$.*</code></td>
                <td><code>*</code> or <code>&#91;*&#93;</code></td>
            </tr>
            <tr>
                <td>Pipe/Chain</td>
                <td>Not supported</td>
                <td><code>foo | &#91;0&#93;</code></td>
            </tr>
        </table>

        <p><em>*For recursive descent, use explicit paths: <code>children&#91;?fvAp&#93;</code></em></p>

        <h2>Resources</h2>

        <ul>
            <li><a href="https://jmespath.org/tutorial.html">JMESPath Tutorial</a></li>
            <li><a href="https://jmespath.org/specification.html">JMESPath Specification</a></li>
            <li><a href="https://robotframework.org/">Robot Framework Documentation</a></li>
            <li><a href="https://github.com/netascode/robotframework-jmespath">GitHub Repository</a></li>
        </ul>
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "HTML"
    __version__ = __version__
