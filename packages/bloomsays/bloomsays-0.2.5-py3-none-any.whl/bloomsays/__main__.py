import sys
from bloomsays import wisdom

def main():
    args = sys.argv[1:]
    if not args:
        print(f"Usage: \n bloomsays randomQuote [n] \n bloomsays joke [n] \n bloomsays codingWisdom [Python/JavaScript/Java/C++] \n bloomsays avg num1 num2 ... \n bloomsays studyTip [hours_available] [difficulty]")
        return

    command = args[0]

    if command == "randomQuote":
        n = int(args[1]) if len(args) > 1 else 1
        wisdom.random_quote(n)
    elif command == 'joke':
        n = int(args[1]) if len(args) > 1 else 1
        wisdom.jokes(n)
    elif command == "avg":
        if len(args) < 2:
            print("Usage: bloomsays avg num1 num2 ...")
            return
        try:
            numbers = [float(x) for x in args[1:]]
        except ValueError:
            print("All arguments for avg must be numbers.")
            return
        wisdom.avg(*numbers)
    elif command == "codingWisdom":
        language = args[1] if len(args) > 1 else "Python"
        wisdom.coding_wisdom(language)
    elif command == "studyTip":
        if len(args) < 3:
            print("Usage: bloomsays studyTip [hours_available] [difficulty]")
            return
        try:
            hours_available = int(args[1])
            difficulty = args[2]
        except ValueError:
            print("hours_available must be an integer.")
            return
        wisdom.study_tip(hours_available, difficulty)
    else:
        print(f"Unknown command: {command}")
        print(f"Usage: \n bloomsays randomQuote [n] \n bloomsays joke [n] \n bloomsays codingWisdom [Python/JavaScript/Java/C++] \n bloomsays avg num1 num2 ... \n bloomsays studyTip [hours_available] [difficulty]")

if __name__ == "__main__":
    main()