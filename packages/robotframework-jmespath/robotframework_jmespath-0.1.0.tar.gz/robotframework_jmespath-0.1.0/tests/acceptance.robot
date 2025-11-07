*** Settings ***
Documentation    Acceptance tests for JMESPathLibrary
Library          JMESPathLibrary

*** Variables ***
${SIMPLE_JSON}       ${{ {"name": "Alice", "age": 30} }}
${USERS_JSON}        ${{ {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 35}]} }}
${NESTED_JSON}       ${{ {"data": {"user": {"profile": {"name": "Alice", "email": "alice@example.com"}}}} }}
${ARRAY_JSON}        ${{ {"items": [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}, {"id": 3, "name": "Item3"}]} }}

*** Test Cases ***
JSON Search Returns Raw Dict
    [Documentation]    Test that JSON Search returns a dict unaltered
    ${result}=    JSON Search    ${NESTED_JSON}    data.user.profile
    Should Be Equal    ${result}[name]    Alice
    Should Be Equal    ${result}[email]    alice@example.com

JSON Search Returns Raw List
    [Documentation]    Test that JSON Search returns a list unaltered
    ${result}=    JSON Search    ${USERS_JSON}    users
    Length Should Be    ${result}    3
    Should Be Equal    ${result}[0][name]    Alice

JSON Search Returns String
    [Documentation]    Test that JSON Search returns a string unaltered
    ${result}=    JSON Search    ${SIMPLE_JSON}    name
    Should Be Equal    ${result}    Alice

JSON Search Returns Number
    [Documentation]    Test that JSON Search returns a number unaltered
    ${result}=    JSON Search    ${SIMPLE_JSON}    age
    Should Be Equal As Numbers    ${result}    30

JSON Search Returns None For No Match
    [Documentation]    Test that JSON Search returns None for no match
    ${result}=    JSON Search    ${SIMPLE_JSON}    missing
    Should Be Equal    ${result}    ${None}

JSON Search With JMESPath Function
    [Documentation]    Test using JMESPath functions
    ${result}=    JSON Search    ${USERS_JSON}    length(users)
    Should Be Equal As Numbers    ${result}    3

JSON Search String Simple Path
    [Documentation]    Test simple path query returning string
    ${result}=    JSON Search String    ${SIMPLE_JSON}    name
    Should Be Equal    ${result}    Alice

JSON Search String Nested Path
    [Documentation]    Test nested path query
    ${result}=    JSON Search String    ${NESTED_JSON}    data.user.profile.name
    Should Be Equal    ${result}    Alice

JSON Search String Array Access
    [Documentation]    Test array element access
    ${result}=    JSON Search String    ${USERS_JSON}    users[0].name
    Should Be Equal    ${result}    Alice

JSON Search String With Filter
    [Documentation]    Test filter expression with pipe
    ${result}=    JSON Search String    ${USERS_JSON}    users[?age > `25`] | [0].name
    Should Be Equal    ${result}    Alice

JSON Search String Returns Empty For No Match
    [Documentation]    Test that empty string is returned for no match
    ${result}=    JSON Search String    ${SIMPLE_JSON}    missing
    Should Be Empty    ${result}

JSON Search String Returns First Element From List
    [Documentation]    Test that first element is returned when result is a list
    ${result}=    JSON Search String    ${USERS_JSON}    users[*].name
    Should Be Equal    ${result}    Alice

JSON Search List Simple List
    [Documentation]    Test simple list result
    ${result}=    JSON Search List    ${USERS_JSON}    users[*].name
    Should Contain    ${result}    Alice
    Should Contain    ${result}    Bob
    Should Contain    ${result}    Charlie
    Length Should Be    ${result}    3

JSON Search List Wildcard Projection
    [Documentation]    Test wildcard array projection
    ${result}=    JSON Search List    ${ARRAY_JSON}    items[*].name
    Should Be Equal    ${result}[0]    Item1
    Should Be Equal    ${result}[1]    Item2
    Should Be Equal    ${result}[2]    Item3

JSON Search List With Filter
    [Documentation]    Test filtered list result
    ${result}=    JSON Search List    ${USERS_JSON}    users[?age > `25`].name
    Should Contain    ${result}    Alice
    Should Contain    ${result}    Charlie
    Should Not Contain    ${result}    Bob
    Length Should Be    ${result}    2

JSON Search List Wraps Single Result
    [Documentation]    Test that single result is wrapped in list
    ${result}=    JSON Search List    ${SIMPLE_JSON}    name
    Should Be Equal    ${result}[0]    Alice
    Length Should Be    ${result}    1

JSON Search List Returns Empty For No Match
    [Documentation]    Test that empty list is returned for no match
    ${result}=    JSON Search List    ${SIMPLE_JSON}    missing
    Should Be Empty    ${result}

JSON Search List Complex Query
    [Documentation]    Test complex nested query
    ${complex}=    Set Variable    ${{ {"data": {"items": [{"id": 1, "active": True}, {"id": 2, "active": False}, {"id": 3, "active": True}]}} }}
    ${result}=    JSON Search List    ${complex}    data.items[?active].id
    Should Contain    ${result}    ${1}
    Should Contain    ${result}    ${3}
    Should Not Contain    ${result}    ${2}
    Length Should Be    ${result}    2

Invalid Expression Should Fail
    [Documentation]    Test that invalid JMESPath expression raises error
    Run Keyword And Expect Error    *Invalid jmespath expression*    JSON Search    ${SIMPLE_JSON}    invalid[
