from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, blocks, interfaces, interpreter

# fmt: off
_ORDINALS_1_TO_100 = [
    "0th", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th",
    "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th",
    "21st", "22nd", "23rd", "24th", "25th", "26th", "27th", "28th", "29th", "30th",
    "31st", "32nd", "33rd", "34th", "35th", "36th", "37th", "38th", "39th", "40th",
    "41st", "42nd", "43rd", "44th", "45th", "46th", "47th", "48th", "49th", "50th",
    "51st", "52nd", "53rd", "54th", "55th", "56th", "57th", "58th", "59th", "60th",
    "61st", "62nd", "63rd", "64th", "65th", "66th", "67th", "68th", "69th", "70th",
    "71st", "72nd", "73rd", "74th", "75th", "76th", "77th", "78th", "79th", "80th",
    "81st", "82nd", "83rd", "84th", "85th", "86th", "87th", "88th", "89th", "90th",
    "91st", "92nd", "93rd", "94th", "95th", "96th", "97th", "98th", "99th", "100th",
]
_ORDINALS_10000_TO_10100_WITH_COMMAS = [
    '10,000th', '10,001st', '10,002nd', '10,003rd', '10,004th', '10,005th', '10,006th',
    '10,007th', '10,008th', '10,009th', '10,010th', '10,011th', '10,012th', '10,013th',
    '10,014th', '10,015th', '10,016th', '10,017th', '10,018th', '10,019th', '10,020th',
    '10,021st', '10,022nd', '10,023rd', '10,024th', '10,025th', '10,026th', '10,027th',
    '10,028th', '10,029th', '10,030th', '10,031st', '10,032nd', '10,033rd', '10,034th',
    '10,035th', '10,036th', '10,037th', '10,038th', '10,039th', '10,040th', '10,041st',
    '10,042nd', '10,043rd', '10,044th', '10,045th', '10,046th', '10,047th', '10,048th',
    '10,049th', '10,050th', '10,051st', '10,052nd', '10,053rd', '10,054th', '10,055th',
    '10,056th', '10,057th', '10,058th', '10,059th', '10,060th', '10,061st', '10,062nd',
    '10,063rd', '10,064th', '10,065th', '10,066th', '10,067th', '10,068th', '10,069th',
    '10,070th', '10,071st', '10,072nd', '10,073rd', '10,074th', '10,075th', '10,076th',
    '10,077th', '10,078th', '10,079th', '10,080th', '10,081st', '10,082nd', '10,083rd',
    '10,084th', '10,085th', '10,086th', '10,087th', '10,088th', '10,089th', '10,090th',
    '10,091st', '10,092nd', '10,093rd', '10,094th', '10,095th', '10,096th', '10,097th',
    '10,098th', '10,099th', '10,100th',
]
_ORDINALS_10000_TO_10100_NO_COMMAS = [
    '10000th', '10001st', '10002nd', '10003rd', '10004th', '10005th', '10006th',
    '10007th', '10008th', '10009th', '10010th', '10011th', '10012th', '10013th',
    '10014th', '10015th', '10016th', '10017th', '10018th', '10019th', '10020th',
    '10021st', '10022nd', '10023rd', '10024th', '10025th', '10026th', '10027th',
    '10028th', '10029th', '10030th', '10031st', '10032nd', '10033rd', '10034th',
    '10035th', '10036th', '10037th', '10038th', '10039th', '10040th', '10041st',
    '10042nd', '10043rd', '10044th', '10045th', '10046th', '10047th', '10048th',
    '10049th', '10050th', '10051st', '10052nd', '10053rd', '10054th', '10055th',
    '10056th', '10057th', '10058th', '10059th', '10060th', '10061st', '10062nd',
    '10063rd', '10064th', '10065th', '10066th', '10067th', '10068th', '10069th',
    '10070th', '10071st', '10072nd', '10073rd', '10074th', '10075th', '10076th',
    '10077th', '10078th', '10079th', '10080th', '10081st', '10082nd', '10083rd',
    '10084th', '10085th', '10086th', '10087th', '10088th', '10089th', '10090th',
    '10091st', '10092nd', '10093rd', '10094th', '10095th', '10096th', '10097th',
    '10098th', '10099th', '10100th',
]
_NUMBERS_10000_TO_10100_WITH_COMMAS = [
    '10,000', '10,001', '10,002', '10,003', '10,004', '10,005', '10,006', '10,007',
    '10,008', '10,009', '10,010', '10,011', '10,012', '10,013', '10,014', '10,015',
    '10,016', '10,017', '10,018', '10,019', '10,020', '10,021', '10,022', '10,023',
    '10,024', '10,025', '10,026', '10,027', '10,028', '10,029', '10,030', '10,031',
    '10,032', '10,033', '10,034', '10,035', '10,036', '10,037', '10,038', '10,039',
    '10,040', '10,041', '10,042', '10,043', '10,044', '10,045', '10,046', '10,047',
    '10,048', '10,049', '10,050', '10,051', '10,052', '10,053', '10,054', '10,055',
    '10,056', '10,057', '10,058', '10,059', '10,060', '10,061', '10,062', '10,063',
    '10,064', '10,065', '10,066', '10,067', '10,068', '10,069', '10,070', '10,071',
    '10,072', '10,073', '10,074', '10,075', '10,076', '10,077', '10,078', '10,079',
    '10,080', '10,081', '10,082', '10,083', '10,084', '10,085', '10,086', '10,087',
    '10,088', '10,089', '10,090', '10,091', '10,092', '10,093', '10,094', '10,095',
    '10,096', '10,097', '10,098', '10,099', '10,100',
]
# fmt: on


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.OrdinalBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.OrdinalBlock()
    assert block._accepted_names == {"o", "ord"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.OrdinalBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = ""

    block = blocks.OrdinalBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = "     "

    block = blocks.OrdinalBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_non_digits_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = "abc"
    mock_ctx.interpret_segment = lambda x: x

    block = blocks.OrdinalBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_invalid_int_passing_isdigit_but_failing_int_conversion_is_rejected():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    # this passes isdigit but fails int-conversion because they're not ASCII 0-9
    mock_ctx.node.payload = "²³"
    mock_ctx.interpret_segment = lambda x: x

    block = blocks.OrdinalBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_ord_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{ord}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_ord_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{ord:1000}"
    result = ts_interpreter.process(script).body
    assert result == "1,000th"


def test_dec_ord_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{ord(c):1213123}"
    result = ts_interpreter.process(script).body
    assert result == "1,213,123"


def test_dec_ord_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{ord(i):2022}"
    result = ts_interpreter.process(script).body
    assert result == "2022nd"


def test_dec_ord_returns_correct_ordinals_for_0_to_100(
    ts_interpreter: TagScriptInterpreter,
):
    # general "does this work" test
    for i, o in enumerate(_ORDINALS_1_TO_100, start=0):
        script = f"{{ord:{i}}}"
        result = ts_interpreter.process(script).body
        assert result == o


def test_dec_ord_no_param_returns_correct_ordinals_10_000_to_10_100(
    ts_interpreter: TagScriptInterpreter,
):
    # this must insert thousands separators (commas)
    for i, o in enumerate(_ORDINALS_10000_TO_10100_WITH_COMMAS, start=10_000):
        script = f"{{ord:{i}}}"
        result = ts_interpreter.process(script).body
        assert result == o


def test_dec_ord_with_i_param_returns_correct_ordinals_10_000_to_10_100(
    ts_interpreter: TagScriptInterpreter,
):
    # this must not insert thousands separators
    for i, o in enumerate(_ORDINALS_10000_TO_10100_NO_COMMAS, start=10_000):
        script = f"{{ord(i):{i}}}"
        result = ts_interpreter.process(script).body
        assert result == o


def test_dec_ord_with_indicator_param_returns_correct_ordinals_10_000_to_10_100(
    ts_interpreter: TagScriptInterpreter,
):
    # this must not insert thousands separators
    for i, o in enumerate(_ORDINALS_10000_TO_10100_NO_COMMAS, start=10_000):
        script = f"{{ord(indicator):{i}}}"
        result = ts_interpreter.process(script).body
        assert result == o


def test_dec_ord_with_c_param_returns_separated_number_without_ordinals(
    ts_interpreter: TagScriptInterpreter,
):
    # this has thousands separators but no ordinal indicators (st, nd, rd, th)
    for i, n in enumerate(_NUMBERS_10000_TO_10100_WITH_COMMAS, start=10_000):
        script = f"{{ord(c):{i}}}"
        result = ts_interpreter.process(script).body
        assert result == n


def test_dec_ord_with_comma_param_returns_separated_number_without_ordinals(
    ts_interpreter: TagScriptInterpreter,
):
    # this has thousands separators but no ordinal indicators (st, nd, rd, th)
    for i, n in enumerate(_NUMBERS_10000_TO_10100_WITH_COMMAS, start=10_000):
        script = f"{{ord(comma):{i}}}"
        result = ts_interpreter.process(script).body
        assert result == n
