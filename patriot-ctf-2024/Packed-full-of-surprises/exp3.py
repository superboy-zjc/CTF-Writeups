from Crypto.Cipher import AES

# Key and IV from the C code (reversed byte order)
key = bytes.fromhex('0123456789abcdef1032547698badcfef0e1d2c3b4a5968778695a4b3c2d1e0f')
iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')

def decrypt_file(input_file, output_file):
    # Create AES cipher in CFB mode with 128-bit segments
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)

    # Read the encrypted data
    with open(input_file, 'rb') as f_enc:
        encrypted_data = f_enc.read()

    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data)

    # Write the decrypted data to output file
    with open(output_file, 'wb') as f_dec:
        f_dec.write(decrypted_data)

if __name__ == '__main__':
    # Specify your encrypted input file and decrypted output file
    input_encrypted_file = 'flag.txt.enc'
    output_decrypted_file = 'decrypted_flag.txt'

    decrypt_file(input_encrypted_file, output_decrypted_file)
    print(f"Decryption complete. Decrypted data saved to {output_decrypted_file}.")

