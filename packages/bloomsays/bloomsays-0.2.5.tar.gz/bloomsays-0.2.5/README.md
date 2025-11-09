# Bloomsays 👨‍🏫

[![CI](https://github.com/swe-students-fall2025/3-python-package-team_orchid/actions/workflows/build.yaml/badge.svg?branch=pipfile-experiment)](https://github.com/swe-students-fall2025/3-python-package-team_orchid/actions/workflows/build.yaml)
[![PyPI version](https://badge.fury.io/py/bloomsays.svg)](https://badge.fury.io/py/bloomsays)



## What is Bloomsays?
Bloomsays is a fun python package with some of our favorite lines from Professor Bloomberg. 

## Installation

[Here is the link to the PyPi page](https://pypi.org/project/bloomsays/)

```
pip install bloomsays
```

## Usage
Ater installation, you can import and call the functions from the package
```python
from bloomsays.wisdom import avg, random_quote, coding_wisdom, study_tip, jokes

# Get your average grade
avg(90, 80, 100)

# Get a random quote from Professor Bloomberg!
random_quote()

# Get some coding wisdom with your specified language
coding_wisdom("Python")

# Get personalized study tips
study_tip(hours_available=3, difficulty="hard")

# Enjoy some programming humor
jokes(2)

```

## Functions

For a demonstration of all functions, see [`example.py`](src/example.py:1).

### `avg(*grades)`

Calculate the average of your grades and display it with Professor Bloomberg's majestic ASCII art.

**Parameters:**
- `*grades` (float): Variable number of grade values (integers or floats)

**Returns:**
- `float`: The calculated average

**Raises:**
- `ValueError`: If no grades are provided

---

### `random_quote(n=1)`

Display random inspirational (and occasionally intimidating) quotes from Professor Bloomberg's legendary syllabus and course communications.

**Parameters:**
- `n` (int, optional): Number of quotes to display. Default is 1. Must be at least 1.

**Returns:**
- `list`: List of the selected quote strings

**Raises:**
- `ValueError`: If n is less than 1

---

### `coding_wisdom(language="Python")`

Receive programming wisdom from Professor Bloomberg tailored to your specific language. Because different languages have different philosophies!

**Parameters:**
- `language` (str, optional): Programming language name. Default is "Python".
  - Supported languages: "Python", "JavaScript", "Java", "C++"
  - Any other language uses general programming wisdom

**Returns:**
- `str`: The wisdom message (without the language prefix)

---

### `study_tip(hours_available=2, difficulty="medium")`

Get personalized study advice from Professor Bloomberg based on your available time and the difficulty of your material. The advice adapts to your situation!

**Parameters:**
- `hours_available` (float, optional): Number of hours you have to study. Default is 2. Must be non-negative.
- `difficulty` (str, optional): Difficulty level of the material. Options: "easy", "medium", or "hard". Default is "medium". Case-insensitive.

**Returns:**
- `str`: A personalized study tip (base tip without the time advice)

**Raises:**
- `ValueError`: If hours_available is negative

---

### `jokes(n=1)`

Get random programming jokes to lighten the mood during those long debugging sessions. Laughter is the best debugger!

**Parameters:**
- `n` (int, optional): Number of jokes to display. Default is 1.

**Returns:**
- `list`: List of the selected joke strings

---

## Example Program

Want to see all functions in action? Check out our [example.py](./src/example.py) file!

---

## Example Output
```
  ______________
 | ask Bloombot |
  ==============
       \
        \

        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&%%%##(##&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%%#%%%%%%%%%#######%@&@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@@@@%%#%%&%%%###%%####(#%&&&%%%%&&@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@%&&&&&#((///((((////**////(#&&&&&&%@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@&&&&&&%#(////***************////(#@@&&&@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@&&&@&#(///***************,*****///(&@&&&@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@&&&&&#(///********,,,,,,,,,,,****///(&&&&&@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@&&&&%(////*****,*,*,,,,,,,,,,,,****//#&&@&@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@&&&&&%(////*******,,,,,,,,,,********//(&&&&&@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@&@&&&%////**********,,,,,,,,,,******//(%&&&&@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@&@@&&%(///*******,,,,,,,,,,,,,,******//#&@&&@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@&&@@&%(///(#(####(/****,**//(%%%%##(///(&&&@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@&&&&(//%###%##%%###(/***/(((%&&&&%###((&@&//@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@(((#&&(//(#%#(*##,/(/(/***///(**#*/(((///&%#((/@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@/(//&&(//***//*////////****/*****/******/#(**/*@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@/(/(%&(//***/*******//**,,*/*******,,**//##(*/@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@/(#(&(///*********///*,,,,*//*********//%%(*#@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@///&%(//********/////****///*******///(&%//&@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@(/&&##((///**//((#&##%####(//***//(###&#/&@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@(&&&&%#(/(%%###%%%##%##%%%((##(((##%&&&@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@&&&&%##%&%&&%###%##((###%%%%#%%%%%&&&@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@&&&&&&%&%%#//(////////////%&&&#&&&&@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@@@(%&@&&&&%#((((###%##((((((%&&&&@&%@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@@,#%/#&&&&&&&&%##%%#%%%##(#%&&%&&@&@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@@..(&//(&&&&&&&&&%%%%#%%(%%&&@&&@%(@@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@@....,///(%&&&&@&&&&%%%%%&&&&@@@&(/..@@@@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@@@@.......////((#%&&&&&&@&&&@&@&&@%(//*,../@@@@@@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@@@@@............//(((((((##&&@@@@@&&#/////#,,......(@@@@@@@@@@@@@@@@
        @@@@@@@@@@@@%..........    ...*///////(((((((//////*//&(.......... *@@@@@@@@@@@@
        @@@@@@@@@%.                 ..,..//**///////////****//%/*. ............ .&@@@@@@
        
```

## Project Structure
```
.
├── .github/                # GitHub Actions workflows
│   └── workflows/
│       └── build.yaml
├── src/                    # Source code
│   └── bloomsays/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bubble.py
│       └── wisdom.py
│   └── example.py
├── tests/                  # Test files
│   ├── test_bubble.py
│   └── test_wisdom.py
├── .gitignore
├── LICENSE
├── Pipfile                 # Pipenv dependencies
├── Pipfile.lock
├── pyproject.toml          # Project configuration for packaging
├── README.md
└── TODO
```

## 🛠️ Developer Guide

To contribute to this project, first set up your local development environment:

```bash
# 1. Clone the repository
git clone https://github.com/swe-students-fall2025/3-python-package-team_orchid.git
cd 3-python-package-team_orchid

# 2. Install dependencies using Pipenv
pipenv install --dev

# 3. Activate the virtual environment
pipenv shell
```
After setup, you can run tests, build the package, and test your changes.

### Running Tests

Run the complete test suite with verbose output:
```bash
pytest tests/ -v
```

You can also run tests for specific files or functions:
```bash
# Test only the wisdom functions
pytest tests/test_wisdom.py

# Test a single specific test
pytest tests/test_wisdom.py::Tests::test_avg_simple
```

## Contributors
- Luna Suzuki - [github](https://github.com/lunasuzuki)
- Kazi Hossain - [github](https://github.com/kazisean)
- Tawhid Zaman - [github](https://github.com/TawhidZGit)
- Jack Chen - [github](https://github.com/a247686991)
- Howard Appel - [github](https://github.com/hna2019)



