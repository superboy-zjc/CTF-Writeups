# Password Protector

Writeup

- decompile high version pyc: https://pylingual.io/view_chimera?identifier=a8248199c23e2852cded943489637e2abf5f6cc0af576d3eb98eac570268530f
- exp

```
import base64

def reverse_flip(text):
    return ''.join([chr(ord(c) - 1) for c in text])

def recover_original_content(flipped_content, bittysEnc):
    # Step 1: Reverse the flip
    reversed_flipped_content = reverse_flip(flipped_content)
    
    # Step 2: Base64 decode the reversed flipped content
    decoded_content = base64.b64decode(reversed_flipped_content)
    
    # Step 3: Base64 decode the bittys key
    bittys = base64.b64decode(bittysEnc)
    
    # Step 4: XOR the decoded content with the bittys key to recover the original data
    original_content = bytes(a ^ b for a, b in zip(decoded_content, bittys))
    
    return original_content

# The flipped portion of the message
flipped_content = "Ocmu{9gtufMmQg8G0eCXWi3MY9QfZ0NjCrXhzJEj50fumttU0ymp"

# The bittys key provided in the original message
bittysEnc = "Zfo5ibyl6t7WYtr2voUEZ0nSAJeWMcN3Qe3/+MLXoKL/p59K3jgV"

# Recover the original content
original_content = recover_original_content(flipped_content, bittysEnc)
print("Recovered content:", original_content.decode('utf-8'))
```

