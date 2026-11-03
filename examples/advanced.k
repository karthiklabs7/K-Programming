# K Programming 0.6 test

say "=== K 0.6 ADVANCED ENGINE ==="

student = {"name": "Karthik", "language": "K Programming", "level": 6}

say student["name"]
say student["language"]
say student["level"]
say length(student)
say type(student)

numbers = [40, 10, 30, 20]
numbers.add(50)
say numbers
numbers.remove(10)
say numbers
numbers.sort()
say numbers

message = "  Welcome to K Programming  "
say message.strip()
say message.upper()
say message.lower()
say message.replace("K", "K Programming")

say type(numbers)
say type(message)
say length(numbers)

say "=== K 0.6 TEST FINISHED ==="
