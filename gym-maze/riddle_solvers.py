from scapy.all import rdpcap, DNSQR, IP
import base64
from io import BytesIO
import io
from amazoncaptcha import AmazonCaptcha
from PIL import Image
import jwt
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
import numpy as np
import time

def cipher_solver(question):
    start_time = time.time()
    padding = 4 - len(question) % 4
    question += "=" * padding
    decoded = base64.b64decode(question).decode("utf-8")
    cipherBits, shiftBits = decoded.split(',')
    shift = int(shiftBits[:-1],2)
    cipherBits = cipherBits[1:]

    capital = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    small =   ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    
    solution=""
    for i in range(len(cipherBits)//7):
        num = int(cipherBits[i*7:(i+1)*7], 2)
        num = (num) % 128
        index = (ord(chr(num).lower())-97) - shift

        if num>96 : #small
            solution += small[index]
        else: #capital
            solution += capital[index]
    
    end_time = time.time()
    print("Time taken for cipher: ", end_time - start_time, "seconds")
    return solution


def captcha_solver(question):
    start_time = time.time()
    img_bytes = BytesIO()
    img = Image.fromarray(np.array(question).astype('uint8'))
    img.save(img_bytes, format='JPEG')
    captcha = AmazonCaptcha(img_bytes)
    captcha.img = img
    solution = captcha.solve()
    end_time = time.time()
    print("Time taken for captcha: ", end_time - start_time, "seconds")
    return solution

def pcap_solver(question):
    start_time = time.time()
    pcap_data = base64.b64decode(question)
    packets = rdpcap(io.BytesIO(pcap_data))
    data={}
    for packet in packets:
        if DNSQR in packet and IP in packet and packet[IP].src == '188.68.45.12':
            dns_query_name = packet[DNSQR].qname.decode('utf-8')
            num = dns_query_name.find('.')
            rank_base64 = dns_query_name[:num]
            padding = 4 - len(rank_base64) % 4
            rank_base64 += "=" * padding
            first = base64.b64decode(rank_base64).decode('utf-8')
            cipherbase64 = dns_query_name[num+1:dns_query_name.find('.',num+1)]
            padding = 4 - len(cipherbase64) % 4
            cipherbase64 += "=" * padding
            second = base64.b64decode( cipherbase64 ).decode('utf-8')
            data[first] = second 
    data = dict(sorted(data.items()))
    solution =""
    for i in data:
        solution+=data[i]
    end_time = time.time()
    print("Time taken for pcap: ", end_time - start_time, "seconds")
    return solution



def server_solver(question):
    decoded_token = jwt.decode(question, options={"verify_signature": False}, algorithms=["RS256"])

    decoded_token['admin'] = True
    key = decoded_token['rand']

    new_token = jwt.encode(decoded_token, key)
    return new_token

def resize_to_fit(image, width, height):
    (h, w) = image.shape[:2]
    if w > h:
        image = imutils.resize(image, width=width)
    else:
        image = imutils.resize(image, height=height)
    padW = int((width - image.shape[1]) / 2.0)
    padH = int((height - image.shape[0]) / 2.0)
    image = cv2.copyMakeBorder(image, padH, padH, padW, padW, cv2.BORDER_REPLICATE)
    image = cv2.resize(image, (width, height))
    return image