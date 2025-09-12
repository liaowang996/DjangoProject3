import requests
import hashlib
from urllib.parse import urljoin

# -------------------------- 基础配置 --------------------------
# 禅道登录页URL（替换为你的禅道地址，如 http://192.168.1.100/zentao/user-login.html）
BASE_URL = "http://127.0.0.1:8080/zentao/"
# 登录账号密码（替换为实际账号）
ACCOUNT = "你的用户名"
PASSWORD = "你的密码"


# -------------------------- 核心工具函数 --------------------------
def md5_encrypt(text):
    """MD5加密（32位小写，与JS的md5函数一致）"""
    md5 = hashlib.md5()
    md5.update(text.encode("utf-8"))
    return md5.hexdigest()


def get_dynamic_rand(session):
    """获取动态随机数rand（调用禅道的refreshRandom接口）"""
    # 构造获取rand的接口URL
    rand_url = urljoin(BASE_URL, "user/refreshRandom")
    # 发送GET请求获取rand（需用session保持会话）
    response = session.get(rand_url)
    # 接口返回的就是纯rand字符串（如 "a1b2c3d4"）
    return response.text.strip()


# -------------------------- 登录流程 --------------------------
def zentao_login():
    # 1. 创建会话（保持Cookie，避免登录态丢失）
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    })

    try:
        # 2. 获取动态rand
        rand = get_dynamic_rand(session)
        print(f"获取到动态rand：{rand}")

        # 3. 按规则加密密码
        # 步骤：原始密码 → 第一次MD5 → 拼接rand → 第二次MD5
        first_md5 = md5_encrypt(PASSWORD)
        final_password = md5_encrypt(first_md5 + rand)
        print(f"加密后密码：{final_password}")

        # 4. 构造登录请求参数（与JS源码中的POST参数一致）
        login_url = urljoin(BASE_URL, "user/login")
        login_data = {
            "account": ACCOUNT,
            "password": final_password,
            "passwordStrength": 0,  # 密码强度（可调用computePasswordStrength计算，非必需）
            "referer": "",  # 跳转来源（空值不影响登录）
            "verifyRand": rand,  # 必须携带获取到的rand
            "keepLogin": 0,  # 是否记住登录（0=不记住，1=记住）
            "captcha": ""  # 验证码（若未开启验证码，留空即可）
        }

        # 5. 发送登录请求
        response = session.post(login_url, data=login_data)
        response_data = response.content.decode("utf-8")  # 禅道返回JSON格式结果

        print("接口状态码：", response.status_code)  # 查看HTTP状态码（200=正常，404/500=异常）
        print("接口原始返回：", response.text[:1000])  # 打印前1000字符，避免内容过长
        print("接口返回结果：", response_data)
        # 6. 处理登录结果
        # if response_data.get("result") == "success":
        #     print("登录成功！跳转地址：", response_data.get("locate"))
        #     # 登录后可通过session访问禅道其他接口（如获取项目列表）
        #     # 示例：获取登录用户信息
        #     user_info_url = urljoin(BASE_URL, "user/profile")
        #     user_response = session.get(user_info_url)
        #     print("登录用户页面内容（前500字符）：", user_response.text[:500])
        # else:
        #     print("登录失败：", response_data.get("message"))

    except Exception as e:
        print("登录过程出错：", str(e))


# 执行登录
if __name__ == "__main__":
    zentao_login()