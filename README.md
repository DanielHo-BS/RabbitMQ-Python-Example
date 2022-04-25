# **RabbitMQ-Python-Example**

# Introduction

Message Queue(MQ) 顧名思義就是把 **訊息message** 放到 **佇列Queue。**我們可以把它想成是「郵局」，作為「寄件者」與「收件者」之間訊息傳遞的橋樑。

最大的好處就是**傳遞失敗的時候訊息(郵件)還會保留在郵局中**、不會消失，只要事後發現錯誤原因(EX. 地址填錯、門市關轉等)，就可以重新傳遞郵件。

![https://miro.medium.com/max/1400/1*hV5D_VQAHcVoh5F5LFW6IQ.jpeg](https://miro.medium.com/max/1400/1*hV5D_VQAHcVoh5F5LFW6IQ.jpeg)

# Usage

![https://miro.medium.com/max/1400/1*Mn9M05fsQxacpCtY85e9Kw.jpeg](https://miro.medium.com/max/1400/1*Mn9M05fsQxacpCtY85e9Kw.jpeg)

RabbitMQ 當作中間傳遞媒介，讓後端程式可以慢慢消化訂單

## Installation RabbitMQ

Use provided script to configure RabbitMQ repsositories

```bash
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | sudo bash
```

To install RabbitMQ Server on ubuntu 18.04 | 20.04

Update apt list first ,then install `rabbitmq-server`package:

```bash
sudo apt update
sudo apt install rabbitmq-server
```

If it disabled, enable it by running:

```bash
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

Activate:

```bash
rabbitmq-server
```

Open on Web with localhost:15672

Username and Password : guest


## Installation Python Packages

Using `pip` to install theses packages:

* pika
* pymysql

```bash
pip install pika pymysql
```



## Perpare

先在本地的 mysql 建一張表 `tb_order`在 db `test` 之中，紀錄邏輯是只要有使用者下訂單，就記一筆 user_id 到表中。

```sql
CREATE DATABASE `test`;

USE `test`;

CREATE TABLE `test`.`tb_order` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '自增主鍵',
  `user_id` varchar(256) NOT NULL COMMENT '下訂單的user_id',
  `db_insert_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '寫入時間',
  `db_update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='訂單表';
```

## ****Message Queue 架構****

- `send.py` : 將收到的 數字i 轉換成 user_id，並送入 MQ
    
    ```python
    import sys
    import pika
    import hashlib
    
    m = hashlib.md5()
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello') # 宣告一個名為 'hello' 的訊息佇列
    # 將輸入的參數轉成 sha-256 值
    try:
        b_msg = sys.argv[1]
    except:
        b_msg = "Hello World!"
    
    m.update(b_msg.encode("utf-8"))
    sha_val = m.hexdigest()
    
    # 把訊息放進名稱為：hello 的佇列中
    channel.basic_publish(exchange='',routing_key='hello',body=sha_val)
    print(f" [x] Sent {sha_val}")
    connection.close()
    ```
Using `rabbitmqctl list_queues` to check the msg.

```bash
sudo rabbitmqctl list_queues   
```
****
- `request.py` : 模擬 1~100 的 user 發出 `send.py`
    
    ```python
    import sys, os
    
    for i in range(1,100):
        os.system(f'python3 send.py {i}')
    
    os._exit(0)
    ```
****
- `receive.py` : 消化 `request.py`送過來的訊息，並插入資料庫
    
    ```python
    import pika
    import pymysql
    import random
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db= 'test', charset='utf8')
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
        # 隨機中斷連線，模擬塞資料塞到一半斷線
        brk = random.randint(1, 10)
        if brk==5:
            print("opps! something wrong, byebye~~")
            conn.close()
        ################################
        return
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    def callback(ch, method, properties, body):
        body = body.decode("utf-8")
        insert_into_db(val=body)
        print(f" [x] Received {body}")
        ch.basic_ack(delivery_tag = method.delivery_tag) # <- 每次成功 cossume 都會 popout
    
    channel.basic_co
    
    ```

# Reference

[RabbitMQ 訊息佇列-實作](https://miro.medium.com/max/1400/1*hV5D_VQAHcVoh5F5LFW6IQ.jpeg)

[Install RabbitMQ Server on Ubuntu 22.04|20.04|18.04](https://computingforgeeks.com/how-to-install-latest-rabbitmq-server-on-ubuntu-linux/)