say "=== K 0.8 LOOP TEST ==="

numbers = [10, 20, 30, 40, 50]

for item in numbers {
    say item
}

say "Continue test"

for item in [1, 2, 3, 4, 5] {
    if item == 3 {
        continue
    }
    say item
}

say "Break test"

for item in [1, 2, 3, 4, 5] {
    if item == 4 {
        break
    }
    say item
}

say "=== K 0.8 TEST FINISHED ==="
