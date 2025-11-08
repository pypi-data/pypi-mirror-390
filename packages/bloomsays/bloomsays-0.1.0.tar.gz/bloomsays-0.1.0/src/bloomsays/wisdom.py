import random
import textwrap
from pathlib import Path
from .bubble import make_bubble

allJokes = [
        "I was about to crack a joke on Ubuntu’s text editor, but you might not gedit.",
        "I’d tell them a UDP joke but there’s no guarantee that they would get it.",
        "When I wrote this, only God and I understood what I was doing. Now, God only knows.",
        "#define TRUE FALSE //Happy debugging suckers",
        "Which body part does a programmer know best? -> ARM",
        "What do you call a busy waiter? -> A server.",
        "What do you call an idle server? -> A waiter",
        "!false -> It's funny 'cause it's true."
        ]
# source : https://zriyansh.medium.com/top-programming-jokes-that-will-make-your-day-or-night-6d986b338f2d
# https://github.com/wesbos/dad-jokes


ascii_art = r"""
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
        """


def avg(*grades):

    average = sum(grades)/ len(grades)
    message = f"Your average grade is {average:.2f}"

    bubble = make_bubble(message)
    print(f"{bubble}\n{ascii_art}")

    return average

def random_quote(n=1):
    profLines = ["everything is due at class time", "ask Bloombot", "Quizzes: 25%", "Exercises & Projects: 75%", "Discord is our main source of communitcation"]
    selected_quotes = random.choices(profLines, k=n)

    bubble_text = "\n".join(selected_quotes)
    
    bubble = make_bubble(bubble_text)
    print(f"{bubble}\n{ascii_art}")
    
    return selected_quotes

def coding_wisdom(language="Python"):
    wisdom_dict = {
        "Python": [
            "Remember: readability counts!",
            "Use list comprehensions wisely",
            "Virtual environments are your friend",
            "PEP 8 is the style guide to follow",
            "Test your code with pytest"
        ],
        "JavaScript": [
            "Async/await makes life easier",
            "Always use const and let, never var",
            "Arrow functions are your friend",
            "npm install is just the beginning",
            "Console.log is for debugging only"
        ],
        "Java": [
            "Object-oriented design matters",
            "Exceptions should be exceptional",
            "Use interfaces wisely",
            "The JVM is powerful but watch memory",
            "Unit tests save production bugs"
        ],
        "C++": [
            "Manage your memory carefully",
            "RAII is your best friend",
            "Smart pointers over raw pointers",
            "The STL is incredibly powerful",
            "Compile warnings are errors in disguise"
        ],
        "default": [
            "Write clean, readable code",
            "Test early, test often",
            "Documentation is never optional",
            "Version control is essential",
            "Code reviews make better developers"
        ]
    }
    
    wisdom_list = wisdom_dict.get(language, wisdom_dict["default"])
    message = random.choice(wisdom_list)
    full_message = f"{language} wisdom: {message}"
    
    bubble = make_bubble(full_message)
    print(f"{bubble}\n{ascii_art}")
    
    return message

def jokes (n=1):
    randomSelect = random.choices(allJokes, k=n)
    
    bubble_text = "\n".join(randomSelect)
    
    bubble = make_bubble(bubble_text)
    print(f"{bubble}\n{ascii_art}")
    
    return randomSelect

def study_tip(hours_available=2, difficulty="medium"): 
    if hours_available < 0:
        raise ValueError("Hours must be non-negative")
    
    difficulty = difficulty.lower()
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"
    
    tips = {
        "easy": [
            "Quick review session should do it!",
            "Focus on the key concepts",
            "Practice a few examples",
            "Make sure you understand the basics"
        ],
        "medium": [
            "Break it into manageable chunks",
            "Practice problems are essential",
            "Review your notes thoroughly",
            "Try explaining it to someone else"
        ],
        "hard": [
            "Start early, don't cram!",
            "Work through multiple examples",
            "Seek help during office hours",
            "Form a study group if possible",
            "Break down complex problems step by step"
        ]
    }
    
    base_tip = random.choice(tips[difficulty])
    
    if hours_available < 1:
        time_advice = "Time is tight! Focus on the most important concepts."
    elif hours_available < 3:
        time_advice = "You have decent time. Use it wisely!"
    else:
        time_advice = "Great! You have plenty of time to master this."
    
    message = f"{time_advice}\n{base_tip}"
    
    bubble = make_bubble(message)
    print(f"{bubble}\n{ascii_art}")
    
    return base_tip
