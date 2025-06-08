from ya_tagscript.util import split_at_substring_zero_depth


def test_simple_needle():
    haystack = "abcdefghijklmnopqrstuvwxyz"
    needle = "h"
    out = split_at_substring_zero_depth(haystack, needle)
    assert out == ["abcdefg", "ijklmnopqrstuvwxyz"]


def test_nested_needle():
    haystack = "hello{world}w{wor}{ld}world{test}"
    needle = "world"
    out = split_at_substring_zero_depth(haystack, needle)
    assert out == ["hello{world}w{wor}{ld}", "{test}"]


def test_missing_needle_returns_whole_haystack_in_list():
    haystack = "hello"
    needle = ""
    out = split_at_substring_zero_depth(haystack, needle)
    assert out == ["hello"]


def test_max_split_limits_splits():
    haystack = "hello world this is fun"
    needle = " "
    out = split_at_substring_zero_depth(haystack, needle, max_split=2)
    assert len(out) == 3
    assert out == ["hello", "world", "this is fun"]


def test_max_split_larger_than_occurrences_splits_correctly():
    haystack = "hello world this is a test"
    needle = " "
    out = split_at_substring_zero_depth(haystack, needle, max_split=20000)
    assert len(out) == 6
    assert out == ["hello", "world", "this", "is", "a", "test"]


def test_max_split_minus_one_means_unlimited():
    haystack = "hello world this is a fun test again"
    needle = " "
    out = split_at_substring_zero_depth(haystack, needle, max_split=-1)
    assert len(out) == 8
    assert out == ["hello", "world", "this", "is", "a", "fun", "test", "again"]


def test_do_not_discard_empty_out_elements_from_successive_needle_occurrences():
    haystack = "  test                hello       world                again     "
    needle = " "
    out = split_at_substring_zero_depth(haystack, needle)
    assert len(out) == 47
    # fmt: off
    assert out == [
        "",        "",        "test",    "",        "",
        "",        "",        "",        "",        "",
        "",        "",        "",        "",        "",
        "",        "",        "",        "hello",   "",
        "",        "",        "",        "",        "",
        "world",   "",        "",        "",        "",
        "",        "",        "",        "",        "",
        "",        "",        "",        "",        "",
        "",        "again",   "",        "",        "",
        "",        "",
    ]
    # fmt: on
