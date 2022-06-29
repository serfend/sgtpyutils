from sgtpyutils.encode import basexx


def test_base64():
    content = 'UOIzVDP2Vzs5UDEyUzL1Vvc4WOApUvU0VOY3WDwoUOIz'
    problem_table = 'ABCDEFGHIJSTUVWKLMNOPQRXYZabcdqrstuvwxefghijklmnopyz0123456789+/'
    result = basexx.base64_decode(content=content, problem_table=problem_table)
    assert result == b'123456789012345678901234567890123'

    result = result.decode('ascii')
    result = basexx.base64_encode(content=result, problem_table=problem_table)
    assert result == content


def test_base32():
    content = 'TRLT5amLBoLT5Z6Fa5LqN6mkTomqR66Da4LqX5mgBwkkP5wmTZ6D===='
    problem_table = 'NoPqRsTuVwXyZaBcDeFgHiJkLm765432'
    result = basexx.base32_decode(content=content, problem_table=problem_table)
    assert result == b'10n78ppn3ro00o70r2opop5s3roqq937'

    result = result.decode('ascii')
    result = basexx.base32_encode(content=result, problem_table=problem_table)
    assert result == content


def test_base16():
    content = b'testinfo'
    result = basexx.base16_encode(content=content)
    assert '74657374696E666F' == result

    result = basexx.base16_decode(content=result)
    assert content == result


def test_base58():
    content = b'testinfo'
    result = basexx.base58_encode(content=content)
    assert 'LUC1e9BXj9g' == result

    result = basexx.base58_decode(content=result)
    assert content == result


def test_base85():
    content = b'testinfo'
    result = basexx.base85_encode(content=content)
    assert 'bY*jNX>Mk3' == result

    result = basexx.base85_decode(content=result)
    assert content == result


def test_base91():
    content = b'testinfo'
    result = basexx.base91_encode(content=content)
    assert 'fPNKP:Qk1T' == result

    result = basexx.base91_decode(content=result)
    assert content == result