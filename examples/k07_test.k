say "=== K 0.7 TEST ==="

import "helper.k"

write_file("k_test.txt", "K Programming 0.7")
append_file("k_test.txt", " - File system working")
say read_file("k_test.txt")

try {
    say read_file("missing_k_file.txt")
}
catch {
    say "Error handled successfully"
    say error
}

say "=== K 0.7 TEST FINISHED ==="
