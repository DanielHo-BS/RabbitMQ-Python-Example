import sys
import pika
import hashlib

m = hashlib.md5()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')  # 宣告一個名為 'hello' 的訊息佇列
# 將輸入的參數轉成 sha-256 值
try:
    b_msg = sys.argv[1]
except:
    b_msg = "Hello World!"

m.update(b_msg.encode("utf-8"))
sha_val = m.hexdigest()

# 把訊息放進名稱為：hello 的佇列中
channel.basic_publish(exchange='', routing_key='hello', body=sha_val)
print(f" [x] Sent {sha_val}")
connection.close()