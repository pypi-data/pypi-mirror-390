import pytest

from bloomsays.bubble import make_bubble, wrap_text


def _assert_bubble_matches(out: str, expected_lines: list[str]):
	parts = out.splitlines()
	# top
	maxw = max((len(l) for l in expected_lines), default=0)
	assert parts[0] == "  " + "_" * (maxw + 2)

	# body
	body = parts[1 : 1 + len(expected_lines)]
	assert len(body) == len(expected_lines)
	for idx, (got, expect) in enumerate(zip(body, expected_lines)):
		# the first body line is prefixed with a single space in the output
		if idx == 0:
			assert got.startswith(" | ")
			inner = got[3:-2]
		else:
			# subsequent lines start with '|' directly
			assert got.startswith("| ")
			inner = got[2:-2]
		assert got.endswith(" |")
		assert inner.strip() == expect

	# bottom
	bottom = parts[1 + len(expected_lines)]
	assert bottom == "  " + "=" * (maxw + 2)

	# tail should be two lines that each end with a backslash
	assert parts[-2].endswith("\\")
	assert parts[-1].endswith("\\")


def test_simple_bubble_no_width():
	out = make_bubble("Hi")
	_assert_bubble_matches(out, ["Hi"])


def test_wrap_with_width():
	out = make_bubble("one two three", width=6)
	# wrapped into three lines
	_assert_bubble_matches(out, ["one", "two", "three"])


def test_preserve_empty_line():
	out = make_bubble("a\n\nb")
	# empty paragraph should be preserved as an empty line
	_assert_bubble_matches(out, ["a", "", "b"])


def test_text_none_raises():
	with pytest.raises(ValueError):
		make_bubble(None)


# Tests for wrap_text function
def test_wrap_text_simple():
	result = wrap_text("hello world", 10)
	assert result == ["hello", "world"]


def test_wrap_text_fits_on_one_line():
	result = wrap_text("hello", 10)
	assert result == ["hello"]


def test_wrap_text_multiple_words_fit():
	result = wrap_text("one two three four", 15)
	assert result == ["one two three", "four"]


def test_wrap_text_long_word_exceeds_width():
	# A single word longer than width should be on its own line
	result = wrap_text("short verylongword short", 10)
	assert result == ["short", "verylongword", "short"]


def test_wrap_text_empty_string():
	result = wrap_text("", 10)
	assert result == [""]


def test_wrap_text_width_one():
	result = wrap_text("a b c", 1)
	assert result == ["a", "b", "c"]


def test_wrap_text_invalid_width_zero():
	with pytest.raises(ValueError, match="width must be >= 1"):
		wrap_text("text", 0)


def test_wrap_text_invalid_width_negative():
	with pytest.raises(ValueError, match="width must be >= 1"):
		wrap_text("text", -5)


def test_wrap_text_invalid_width_none():
	with pytest.raises(ValueError, match="width must be >= 1"):
		wrap_text("text", None)

