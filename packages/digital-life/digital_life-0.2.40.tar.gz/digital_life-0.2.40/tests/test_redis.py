import redis
import time

def get_redis_client():
    """
    创建一个 Redis 客户端连接，包含阿里云 Redis 的认证信息。
    """
    try:
        r = redis.StrictRedis(
            host='r-2zeuujf6lqtgf5hk7xpd.redis.rds.aliyuncs.com', # 阿里云 Redis 主机
            port=6379,                                          # 阿里云 Redis 端口
            db=20,                                              # 阿里云 Redis 数据库索引
            username='skgn',                                    # 阿里云 Redis 用户名 (如果需要)
            password='Ahs2025_skgn',                                # 阿里云 Redis 密码
            decode_responses=True,                              # 自动解码响应为字符串
            socket_connect_timeout=10                           # 连接超时时间，单位秒
        )
        # 尝试进行一次ping操作，验证连接是否成功
        r.ping()
        print("成功连接到阿里云 Redis！")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"无法连接到阿里云 Redis 服务器: {e}")
        return None
    except redis.exceptions.AuthenticationError as e:
        print(f"Redis 认证失败，请检查用户名和密码: {e}")
        return None
    except Exception as e:
        print(f"连接阿里云 Redis 时发生未知错误: {e}")
        return None

def store_with_expiration(r_client, key, value, expiration_seconds=7200):
    """
    将 key-value 对存储到 Redis，并设置过期时间。

    Args:
        r_client (redis.StrictRedis): 已经建立连接的 Redis 客户端实例。
        key (str): 要存储的键。
        value (str): 要存储的值。
        expiration_seconds (int): 过期时间（秒）。默认值 7200 秒（2小时）。
    """
    if r_client is None:
        print("Redis 客户端未连接，无法执行存储操作。")
        return

    try:
        r_client.set(key, value, ex=expiration_seconds)
        print(f"键 '{key}' 已成功存储，值为 '{value}'，并设置了 {expiration_seconds} 秒的过期时间。")
    except Exception as e:
        print(f"存储键 '{key}' 时发生错误: {e}")

def get_value(r_client, key):
    """
    从 Redis 获取指定 key 的值。

    Args:
        r_client (redis.StrictRedis): 已经建立连接的 Redis 客户端实例。
        key (str): 要获取的键。

    Returns:
        str or None: 如果键存在，则返回其值；否则返回 None。
    """
    if r_client is None:
        print("Redis 客户端未连接，无法执行获取操作。")
        return None

    try:
        value = r_client.get(key)
        if value:
            print(f"获取到键 '{key}' 的值为: '{value}'")
        else:
            print(f"键 '{key}' 不存在或已过期。")
        return value
    except Exception as e:
        print(f"获取键 '{key}' 时发生错误: {e}")
        return None



if __name__ == "__main__":
    # 获取 Redis 客户端实例
    redis_client = get_redis_client()

    if redis_client: # 只有当连接成功时才执行后续操作
        # 示例用法
        my_key = "user:session:12345"
        my_value = "logged_in_user_data_xyz"
        two_hours_in_seconds = 2 * 60 * 60  # 2小时 = 7200秒

        print(f"\n--- 存储键 '{my_key}' ---")
        store_with_expiration(redis_client, my_key, my_value, two_hours_in_seconds)

        print("\n--- 尝试立即获取键 ---")
        get_value(redis_client, my_key)

        # 演示过期情况 (这里我们设置一个很短的过期时间来观察效果)
        short_lived_key = "temporary:data:abc"
        short_lived_value = "some_temp_value"
        short_expiration_seconds = 5  # 5秒过期

        print(f"\n--- 存储一个将在 {short_expiration_seconds} 秒后过期的键 '{short_lived_key}' ---")
        store_with_expiration(redis_client, short_lived_key, short_lived_value, short_expiration_seconds)

        print(f"\n--- 立即尝试获取键 '{short_lived_key}' ---")
        get_value(redis_client, short_lived_key)

        print(f"\n--- 等待 {short_expiration_seconds + 1} 秒，观察过期情况 ---")
        time.sleep(short_expiration_seconds + 1)

        print(f"\n--- 再次尝试获取键 '{short_lived_key}' ---")
        get_value(redis_client, short_lived_key)

        # 另一个2小时过期的例子
        another_key = "product:cache:item:sku789"
        another_value = "product_details_json_string"
        store_with_expiration(redis_client, another_key, another_value, two_hours_in_seconds)
        get_value(redis_client, another_key)
    else:
        print("\n由于 Redis 连接失败，未执行后续操作。")
