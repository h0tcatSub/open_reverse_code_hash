import random
import ECC
import sys
import time
import bitcoin
import base58
import numpy as np
import hashlib
from ECC import Point

global G, G2, G3
G = Point(Point.Gx, Point.Gy)
G2 = Point(Point.Gx, Point.Gy)
G3 = Point(Point.Gx, Point.Gy)
def check_key(reverse_code, address):
    global G, G2, G3
    hex_reverse_code = format(reverse_code, "028x")
    b58 = str(base58.b58encode(hex_reverse_code.encode()))
    b58 = b58[1:].replace("\'", "")
    hash_key = hashlib.sha256(b58.encode()).hexdigest()
    weak_key_1 = int(hash_key, 16)
    weak_pubkey_x = bitcoin.compress(bitcoin.privkey_to_pubkey(hash_key))[2:]
    weak_key_2 = f"{b58}{weak_pubkey_x}"
    weak_key_2 = int(hashlib.sha256(weak_key_2.encode()).hexdigest(), 16)
    #weak_key = weak_key_1 * weak_key_2
    G2 = G * weak_key_1
    G3 = G * weak_key_2
    weak_point = (G2 * G3).x
    x_hash_02 = bitcoin.hash160(f'02{format(weak_point, "064x")}'.encode())
    x_hash_03 = bitcoin.hash160(f'03{format(weak_point, "064x")}'.encode())
    private_key_02 = f"{x_hash_02}{hex_reverse_code}"
    private_key_03 = f"{x_hash_03}{hex_reverse_code}"
    address_02 = bitcoin.pubkey_to_address(bitcoin.privkey_to_pubkey(int(private_key_02, 16) % Point.order))
    address_03 = bitcoin.pubkey_to_address(bitcoin.privkey_to_pubkey(int(private_key_03, 16) % Point.order))
    
    return (address_02 == address) or (address_03 == address)
    #return 
check_key_vec = np.vectorize(check_key)

def crack_reverse_code_special_method(address, bits_size = 10): # ダブルハッシュされた値は事前に調べること。
    starttime = time.time()
    bits_size = 2 ** bits_size
    print("[+] Start analysis... Kill that elliptic curve cryptography!!")
    code_vector   = np.arange(bits_size)
    result_vector   = np.array([])
    progress = 0
    while True:
        print(f"Progress : {progress}, Code : {code_vector}")
        result_vector = check_key_vec(code_vector[:], address)
        if np.any(result_vector):
            endtime = time.time( - starttime)
            print("[+] FOUND Reverse Code !!")
            reverse_code = int(np.where(result_vector == True)[0]) + progress
            reverse_code = format(reverse_code, "028x")
            print(f"sol time {endtime}")
            print()
            print(f"Reverse Code : {reverse_code}")
            if random.randint(0, 100) >= 80: # 単純に楽しみたいだけ
                print("Accelerator >> It's a one-way street from here on out!!")
                return reverse_code
            print("Kamijo Touma >> Kill that illusion!!")
            print()
            return reverse_code
        code_vector += bits_size
        progress += bits_size


debug_address = "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH" # == 1 compressed
reverse_code = crack_reverse_code_special_method(debug_address)
print()
print(reverse_code)