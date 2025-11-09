# Bloomsays

## What is Bloomsays?
Bloomsays is a fun python package with some of our favorite lines from Professor Bloomberg. 

## Instructions
pip install -e .

run python: python

## Usage
Ater installation, you can import and call the functions from the package
```python
from bloomsays.wisdom import avg, random_quote, coding_wisdom, study_tip, jokes

#Get your average grade
avg(90, 80, 100)

#Get a random quote from Professor Bloomberg!
random_quote()

#Get some coding wisdom with your specified language
coding_wisdom("Python")

# Get personalized study tips
wisdom.study_tip(hours_available=3, difficulty="hard")

# Enjoy some programming humor
wisdom.jokes(2)

```

## Functions
### `avg(*grades)`

Calculate the average of your grades and display it with Professor Bloomberg's majestic ASCII art.

**Parameters:**
- `*grades` (float): Variable number of grade values (integers or floats)

**Returns:**
- `float`: The calculated average

**Raises:**
- `ValueError`: If no grades are provided

**Example:**
```python
from bloomsays import wisdom

# Calculate average of multiple grades
result = wisdom.avg(90, 85, 95, 78, 92)
# Output: Displays "Your average grade is 88.00" in a speech bubble with Bloomberg ASCII art
# Returns: 88.0

# Works with decimals too
result = wisdom.avg(89.5, 92.3, 87.8)
# Returns: 89.87
```

---

### `random_quote(n=1)`

Display random inspirational (and occasionally intimidating) quotes from Professor Bloomberg's legendary syllabus and course communications.

**Parameters:**
- `n` (int, optional): Number of quotes to display. Default is 1. Must be at least 1.

**Returns:**
- `list`: List of the selected quote strings

**Raises:**
- `ValueError`: If n is less than 1

**Example:**
```python
from bloomsays import wisdom

# Get a single quote (default)
quotes = wisdom.random_quote()
# Output: One random Bloomberg quote with ASCII art
# Returns: ['Ask Bloombot!']

# Get multiple quotes at once
quotes = wisdom.random_quote(3)
# Output: Three random quotes in a single bubble with ASCII art
# Returns: ['everything is due at class time', 'Quizzes: 25%', 'Discord is our main source of communication']
```

**Available Quotes:**
- "Everything is due at class time"
- "Ask Bloombot!"
- "Quizzes: 25%"
- "Exercises & Projects: 75%"
- "Discord is our main source of communication"
- "Read the instructions carefully"
- "Test your code before submitting"
- "Git commit early and often"
- "Merge conflicts are a learning opportunity"
- "The documentation is your friend"

---

### `coding_wisdom(language="Python")`

Receive programming wisdom from Professor Bloomberg tailored to your specific language. Because different languages have different philosophies!

**Parameters:**
- `language` (str, optional): Programming language name. Default is "Python".
  - Supported languages: "Python", "JavaScript", "Java", "C++"
  - Any other language uses general programming wisdom

**Returns:**
- `str`: The wisdom message (without the language prefix)

**Example:**
```python
from bloomsays import wisdom

# Get Python wisdom (default)
tip = wisdom.coding_wisdom()
# Output: "Python wisdom: Remember: readability counts!" with ASCII art
# Returns: "Remember: readability counts!"

# Get JavaScript-specific wisdom
tip = wisdom.coding_wisdom("JavaScript")
# Output: "JavaScript wisdom: Always use const and let, never var" with ASCII art
# Returns: "Always use const and let, never var"

# Get wisdom for any language
tip = wisdom.coding_wisdom("Rust")
# Output: "Rust wisdom: Write clean, readable code" with ASCII art
# Returns: "Write clean, readable code"
```

**Wisdom by Language:**
- **Python**: Focus on readability, list comprehensions, virtual environments, PEP 8, pytest
- **JavaScript**: Async/await, const/let, arrow functions, npm, console.log usage
- **Java**: OOP design, exceptions, interfaces, JVM, unit tests
- **C++**: Memory management, RAII, smart pointers, STL, compile warnings
- **Default**: General best practices for any language

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

**Example:**
```python
from bloomsays import wisdom

# Default: 2 hours, medium difficulty
tip = wisdom.study_tip()
# Output: "You have decent time. Use it wisely!\nReview your notes thoroughly" with ASCII art
# Returns: "Review your notes thoroughly"

# Cramming for hard material with little time
tip = wisdom.study_tip(hours_available=0.5, difficulty="hard")
# Output: "Time is tight! Focus on the most important concepts.\nSeek help during office hours" with ASCII art
# Returns: "Seek help during office hours"

# Plenty of time for easy material
tip = wisdom.study_tip(hours_available=5, difficulty="easy")
# Output: "Great! You have plenty of time to master this.\nQuick review session should do it!" with ASCII art
# Returns: "Quick review session should do it!"

# Case doesn't matter
tip = wisdom.study_tip(3, "HARD")
# Works the same as difficulty="hard"
```

**Time-Based Advice:**
- **< 1 hour**: "Time is tight! Focus on the most important concepts."
- **1-3 hours**: "You have decent time. Use it wisely!"
- **3+ hours**: "Great! You have plenty of time to master this."

**Difficulty-Based Tips:**
- **Easy**: Quick reviews, key concepts, basic understanding
- **Medium**: Breaking into chunks, practice problems, explaining to others
- **Hard**: Starting early, multiple examples, office hours, study groups

---

### `jokes(n=1)`

Get random programming jokes to lighten the mood during those long debugging sessions. Laughter is the best debugger!

**Parameters:**
- `n` (int, optional): Number of jokes to display. Default is 1.

**Returns:**
- `list`: List of the selected joke strings

**Example:**
```python
from bloomsays import wisdom

# Get a single joke (default)
joke_list = wisdom.jokes()
# Output: One random programming joke with ASCII art
# Returns: ["I'd tell them a UDP joke but there's no guarantee that they would get it."]

# Get multiple jokes
joke_list = wisdom.jokes(3)
# Output: Three random jokes in a single bubble with ASCII art
# Returns: ["!false -> It's funny 'cause it's true.", "Which body part does a programmer know best? -> ARM", ...]
```

**Sample Jokes:**
- "I was about to crack a joke on Ubuntu's text editor, but you might not gedit."
- "I'd tell them a UDP joke but there's no guarantee that they would get it."
- "When I wrote this, only God and I understood what I was doing. Now, God only knows."
- "#define TRUE FALSE //Happy debugging suckers"
- "Which body part does a programmer know best? -> ARM"
- "What do you call a busy waiter? -> A server."
- "!false -> It's funny 'cause it's true."

---

## Example Program

Want to see all functions in action? Check out our [example.py](https://github.com/swe-students-fall2025/3-python-package-team_orchid/blob/main/example.py) file!

---

## Example Output
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
        
['ask Bloombot']

## 🛠️ For Contributors

Want to contribute to bloomsays? We'd love your help! Here's how to set up your development environment:

### Prerequisites

- Python 3.11 or higher (3.11, 3.12, 3.13)
- pip and pipenv

### Setup Instructions

**1. Clone the repository:**
```bash
git clone https://github.com/swe-students-fall2025/3-python-package-team_orchid.git
cd 3-python-package-team_orchid
```

**2. Install pipenv (if you don't have it):**
```bash
pip install pipenv
```

**3. Install dependencies and create virtual environment:**
```bash
pipenv install --dev
```

This creates a virtual environment and installs all necessary packages including pytest.

**4. Activate the virtual environment:**
```bash
pipenv shell
```

Your terminal prompt will change to show you're in the virtual environment: `(3-python-package-team_orchid)`

**5. Install the package in editable mode:**
```bash
pip install -e .
```

This allows you to make changes to the code and test them immediately without reinstalling.

### Running Tests

Run the complete test suite with verbose output:
```bash
pytest tests/ -v
```

Run tests with coverage report:
```bash
pytest tests/ --cov=bloomsays --cov-report=html
```

Run specific test files:
```bash
# Test only the wisdom functions
pytest tests/test_wisdom.py -v

# Test only the bubble functions
pytest tests/test_bubble.py -v
```

Run a specific test:
```bash
pytest tests/test_wisdom.py::Tests::test_avg_simple -v
```

### Testing Your Changes

After making code changes, test them:
```bash
# 1. Run all tests
pytest tests/ -v

# 2. Try the functions in Python
python -c "from bloomsays import wisdom; wisdom.random_quote()"

# 3. Test the CLI (if applicable)
python -m bloomsays
```

### Building the Package

Build distribution files locally:
```bash
# Install build tools (if not already installed)
pipenv install build twine --dev

# Build the package
python -m build
```

This creates distribution files in the `dist/` directory:
- `bloomsays-0.1.0.tar.gz` (source distribution)
- `bloomsays-0.1.0-py3-none-any.whl` (wheel distribution)

### Testing the Built Package

Install and test your local build:
```bash
# Install from the wheel file
pip install dist/bloomsays-0.1.0-py3-none-any.whl

# Test it
python -c "from bloomsays import wisdom; wisdom.jokes()"

# Uninstall when done testing
pip uninstall bloomsays
```

## Contributors
- Luna Suzuki - [github](https://github.com/lunasuzuki)
- Kazi Hossain - [github](https://github.com/kazisean)
- Tawhid Zaman - [github](https://github.com/TawhidZGit)
- Jack Chen - [github](https://github.com/a247686991)
- Howard Appel - [github](https://github.com/hna2019)


