- Filter packets by HTTP protocol. Locate an internal IP downloading a pyc file from a remote server. Extract pyc file and decompile it we know it is a file encryption and exfiltration script. The script has a fixed send-to port which is 22993. We can know this script is the attacker’s tool to exfiltrate file to external.
  - attacker: 10.151.198.69
    - download file from his server 93.132.55.192
- `ip.src == 10.151.198.69 and not quic and tcp.port == 22993` filter out three file transfer packets. Follow TCP stream, download them as raw data.
- Decrypted it by reverse enginering attacker’s script.

```
import time
import math
import sys

def decrypt(encrypt_bytes, current_time):
    key_bytes = str(current_time).encode('utf-8')
    init_key_len = len(key_bytes)
    data_bytes_len = len(encrypt_bytes)
    
    # Adjust key length to match the length of encrypted data
    temp1 = data_bytes_len // init_key_len
    temp2 = data_bytes_len % init_key_len
    key_bytes *= temp1
    key_bytes += key_bytes[:temp2]
    
    # Decrypt by XORing again with the same key
    decrypted_bytes = bytes((a ^ b for a, b in zip(key_bytes, encrypt_bytes)))
    return decrypted_bytes

def main():
    # Read the encrypted file (first argument)
    encrypted_file = sys.argv[1]
    
    # Use the timestamp as used during encryption (passed as second argument or calculate it)
    if len(sys.argv) > 2:
        current_time = int(sys.argv[2])  # Use provided time
    else:
        current_time = math.floor(time.time())  # Fallback to current time
    
    # Read the encrypted data
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt the data
    decrypted_data = decrypt(encrypted_data, current_time)
    
    # Save the decrypted file
    output_file = 'decrypted_output.bin'
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print(f"Decrypted data written to {output_file}")

if __name__ == '__main__':
    main()
```

# Get flag

```
python3 decrypt.py encrypted_whole.bin 1726595769 
file encrypted_whole.bin
mv encrypted_whole.bin encrypted_whole.jpg
```

![img](https://api.2h0ng.wiki:443/noteimages/2024/09/30/23-22-36-57427ed8522fb019fb49853eb1aba80f.png)