import pika
import pymysql
import random
conn = pymysql.connect(host='localhost', port=3306,
                       user='root', passwd='adlinkros', db='test', charset='utf8')
cursor = conn.cursor()

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')

# 定義接收到訊息後、將資料塞入資料庫的函式
def insert_into_db(val):
    sql = f"""
    INSERT INTO test.tb_order(`user_id`) VALUES ('{val}')
    """
    print(sql)
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)

################################
    '''# 隨機中斷連線，模擬塞資料塞到一半斷線
    brk = random.randint(1, 10)
    if brk == 5:
        print("opps! something wrong, byebye~~")
        conn.close()
    ################################
    return'''

print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    body = body.decode("utf-8")
    insert_into_db(val=body)
    print(f" [x] Received {body}")
    # <- 每次成功 cossume 都會 popout
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume('hello',callback) # 宣告消費來自 hello 的訊息
channel.start_consuming()

# To exit by ctl + c