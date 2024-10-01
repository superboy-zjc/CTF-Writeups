from Crypto.Cipher import AES

# Reconstructed Key and IV from the C code
key = bytes.fromhex('efcdab8967452301fedcba98765432108796a5b4c3d2e1f00f1e2d3c4b5a6978')
iv = bytes.fromhex('07060504030201000f0e0d0c0b0a0908')

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

