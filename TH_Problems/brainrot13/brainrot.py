def convert(word):
    new = ""
    x = len(word)

    # Step 1: Add x to first char
    first_char = chr((ord(word[0]) -96 + x - 1) % 26 + 1 + 96)
    new += first_char
    # print(f"Step 1 (add): '{word[0]}' + {x} = '{first_char}'")

    add = False
    prev = first_char

    for i in range(1, len(word)):
        curr = word[i]

        if add:
            val = (ord(curr) - 96) + (ord(prev) - 96)
            result = (val - 1) % 26 + 1   # keep in 1..26
            op = '+'
        else:
            # print(prev, curr)
            val = -(ord(prev) - ord(curr))
            result = (val + 26 - 1) % 26 + 1
            op = '-'

        result_char = chr(result + 96)
        print(f"Step {i+1} ({'add' if add else 'sub'}): '{curr}' {op} '{prev}' = '{result_char}'")

        new += result_char
        prev = result_char
        add = not add

    return new

def rot_thirteen(word):
    result = ""
    for char in word:
        if char.isalpha():
            # Determine the ASCII offset based on case
            offset = ord('A') if char.isupper() else ord('a')
            # Apply the ROT13 algorithm: (char_position + 13) % 26
            rotated = chr((ord(char) - offset + 13) % 26 + offset)
            result += rotated
        else:
            # Non-alphabetic characters remain unchanged
            result += char
    return result

def brainrot(word):
    r = rot_thirteen(word)
    print("Rot:", r)
    c = convert(r)
    print("con", c)
    assert(c == convert(rot_thirteen(word)))
    return convert(rot_thirteen(word))

if __name__ == "__main__":
    word = "freshgenzbrainz"
    print("Final result:", brainrot(word))
    word = "super_rot_xor"
    print(brainrot(word))
