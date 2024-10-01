from Crypto.Cipher import AES

# Key and IV used during encryption
key = bytes.fromhex('0123456789abcdef1032547698badcfef0e1d2c3b4a596877897a6b5c4d3e2f1')
iv = bytes.fromhex('001020304050607008090a0b0c0d0e0f')

# Decrypt the file
def decrypt_file(input_file, output_file):
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)

    with open(input_file, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_file, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)

if __name__ == '__main__':
    # Input and output file paths
    input_encrypted_file = 'flag.txt.enc'
    output_decrypted_file = 'decrypted_flag.txt'

    decrypt_file(input_encrypted_file, output_decrypted_file)
    print(f"Decryption complete. Decrypted data saved to {output_decrypted_file}.")

