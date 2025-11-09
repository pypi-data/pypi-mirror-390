import pytest
from bloomsays import wisdom

class Tests:

    def test_avg_simple(self, capsys):
        wisdom.avg(97, 76, 67)
        captured = capsys.readouterr()
        assert "Your average grade is 80.00" in captured.out
        assert "____" in captured.out
        assert "@@@@" in captured.out

    def test_avg_identical_numbers(self, capsys):
        wisdom.avg(67, 67, 67)
        captured = capsys.readouterr()
        assert "Your average grade is 67.00" in captured.out
        assert "____" in captured.out
        assert "@@@@" in captured.out

    def test_avg_random_floats(self, capsys):
        wisdom.avg(5.5, 7.3, 8.2)
        captured = capsys.readouterr()
        assert "Your average grade is 7.00" in captured.out
        assert "____" in captured.out
        assert "@@@@" in captured.out

    def test_random_quote_runs(self, capsys):
        wisdom.random_quote(3)
        captured = capsys.readouterr()
        assert "____" in captured.out
        assert "@@@@" in captured.out

    def test_random_quote_default(self, capsys):
        wisdom.random_quote()
        captured = capsys.readouterr()
        assert any("|" in line for line in captured.out.splitlines())
        assert "@@@@" in captured.out

    def test_random_quote_multiple_quotes_in_bubble(self, capsys):
        wisdom.random_quote(2)
        captured = capsys.readouterr()
        lines = captured.out.splitlines()
        bubble_lines = [line for line in lines if "|" in line and "Your" not in line and "wisdom" not in line and "bloomsays" not in line]
        assert len(bubble_lines) >= 2
        assert "@@@@" in captured.out

    def test_coding_wisdom_default(self, capsys):
        message = wisdom.coding_wisdom()
        captured = capsys.readouterr()
        assert isinstance(message, str)
        assert "Python wisdom:" in captured.out
        assert "@@@" in captured.out
    
    def test_coding_wisdom_javascript(self, capsys):
        message = wisdom.coding_wisdom("JavaScript")
        captured = capsys.readouterr()
        assert isinstance(message, str)
        assert "JavaScript wisdom:" in captured.out
        assert "@@@" in captured.out
    
    def test_coding_wisdom_java(self, capsys):
        message = wisdom.coding_wisdom("Java")
        captured = capsys.readouterr()
        assert isinstance(message, str)
        assert "Java wisdom:" in captured.out
        assert "@@@" in captured.out
    
    def test_coding_wisdom_cpp(self, capsys):
        message = wisdom.coding_wisdom("C++")
        captured = capsys.readouterr()
        assert isinstance(message, str)
        assert "C++ wisdom:" in captured.out
        assert "@@@" in captured.out
    
    def test_coding_wisdom_unknown_language(self, capsys):
        message = wisdom.coding_wisdom("COBOL")
        captured = capsys.readouterr()
        assert isinstance(message, str)
        assert "COBOL wisdom:" in captured.out
        assert "@@@" in captured.out
    
    def test_coding_wisdom_returns_string(self):
        message = wisdom.coding_wisdom("Python")
        assert isinstance(message, str)
        assert len(message) > 0

    def test_jokes_default(self, capsys):
        getJoke = wisdom.jokes()
        getReturn = capsys.readouterr()

        assert isinstance(getJoke, list)
        assert len(getJoke) == 1
        assert getJoke[0] in wisdom.allJokes
        assert "____" in getReturn.out
        assert "@@@@" in getReturn.out

    def test_joke_true_value(self):
        numJokes = 2
        output = wisdom.jokes(n=2)

        assert isinstance(output, list)
        assert len(output) == numJokes
        assert all(isinstance(i, str) for i in output)
    
    def test_jokes_multiple (self, capsys):
        numJokes = 3
        getJokes = wisdom.jokes(n=numJokes)
        getReturn = capsys.readouterr()

        assert isinstance(getJokes, list)
        assert len(getJokes) == numJokes
        for joke in getJokes:
            assert joke in wisdom.allJokes

        assert "____" in getReturn.out
        assert "@@@@" in getReturn.out
        
        numJokesLine = [line for line in getReturn.out.splitlines() if "|" in line]
        assert len(numJokesLine) >= numJokes
    
    def test_study_tip_default(self, capsys):
        tip = wisdom.study_tip()
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out
        assert "|" in captured.out
    
    def test_study_tip_easy(self, capsys):
        tip = wisdom.study_tip(2, "easy")
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out
    
    def test_study_tip_medium(self, capsys):
        tip = wisdom.study_tip(3, "medium")
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out
    
    def test_study_tip_hard(self, capsys):
        tip = wisdom.study_tip(5, "hard")
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out
    
    def test_study_tip_short_time(self, capsys):
        tip = wisdom.study_tip(0.5, "hard")
        captured = capsys.readouterr()
        assert "Time is tight" in captured.out
    
    def test_study_tip_long_time(self, capsys):
        tip = wisdom.study_tip(10, "easy")
        captured = capsys.readouterr()
        assert "plenty of time" in captured.out
    
    def test_study_tip_negative_hours(self):
        with pytest.raises(ValueError, match="Hours must be non-negative"):
            wisdom.study_tip(-1, "medium")
    
    def test_study_tip_invalid_difficulty(self, capsys):
        tip = wisdom.study_tip(2, "impossible")
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out
    
    def test_study_tip_case_insensitive(self, capsys):
        tip = wisdom.study_tip(2, "HARD")
        captured = capsys.readouterr()
        assert isinstance(tip, str)
        assert "@@@" in captured.out



