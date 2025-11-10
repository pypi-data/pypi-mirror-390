import json
import random

from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from pydantic import BaseModel, Field

from yuanfen import Config, Logger, Redis


class SmsSendCodeRequest(BaseModel):
    """发送短信验证码请求"""

    system: str = Field(..., description="系统标识")
    phone: str = Field(..., description="手机号", pattern=r"^1[3-9]\d{9}$")
    length: int = Field(6, description="验证码长度", ge=4, le=6)


class SmsVerifyCodeRequest(BaseModel):
    """验证短信验证码请求"""

    system: str = Field(..., description="系统标识")
    phone: str = Field(..., description="手机号", pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., description="验证码", min_length=4, max_length=6)


class SmsService:
    """短信服务类

    用于发送和验证短信验证码，基于阿里云短信服务。

    所需配置项 (config):
        redis:
            host: str - Redis 服务器地址
            port: int - Redis 服务器端口
            password: str - Redis 密码
            db: int - Redis 数据库编号
            prefix: str - Redis 键前缀
        aliyun:
            access_key_id: str - 阿里云 AccessKey ID
            access_key_secret: str - 阿里云 AccessKey Secret
            sms_sign_name: str - 短信签名名称
            sms_template_code: str - 短信模板代码

    功能特性:
        - 验证码有效期: 300秒 (5分钟)
        - 最大验证次数: 5次
        - 重新发送间隔: 60秒
    """

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.redis = Redis(config["redis"])
        self.client = DysmsapiClient(
            open_api_models.Config(
                access_key_id=config["aliyun"]["access_key_id"],
                access_key_secret=config["aliyun"]["access_key_secret"],
            )
        )
        self.expiry_time = 300  # 验证码有效期，单位：秒
        self.max_attempts = 5  # 最大验证次数
        self.resend_interval = 60  # 发送间隔限制，单位：秒

    async def send_code(self, request: SmsSendCodeRequest):
        redis_code_key = f"sms:{request.system}:code:{request.phone}"
        existing_code = self.redis.get(redis_code_key)
        if existing_code:
            ttl = self.redis.ttl(redis_code_key)
            self.logger.info(f"ttl: {ttl}")
            if ttl > self.expiry_time - self.resend_interval:
                raise Exception("发送过于频繁，请稍后再试")

        # 生成验证码
        code = str(random.randint(10 ** (request.length - 1), 10**request.length - 1))

        # 构造短信发送请求
        send_req = dysmsapi_models.SendSmsRequest(
            phone_numbers=request.phone,
            sign_name=self.config["aliyun"]["sms_sign_name"],
            template_code=self.config["aliyun"]["sms_template_code"],
            template_param=json.dumps({"code": code}),
        )

        # 发送短信
        send_resp = await self.client.send_sms_async(send_req)

        # 检查发送结果
        if send_resp.body.code != "OK":
            self.logger.error(f"短信发送失败: {send_resp.body.message}")
            raise Exception(f"短信发送失败: {send_resp.body.message}")

        # 存储验证码到 Redis（5分钟有效期）
        code_data = json.dumps({"code": code, "attempts": 0})
        self.redis.set(redis_code_key, code_data, self.expiry_time)
        self.logger.info(f"验证码已发送到 {request.phone}")

    async def verify_code(self, request: SmsVerifyCodeRequest):
        redis_code_key = f"sms:{request.system}:code:{request.phone}"
        code_data_json = self.redis.get(redis_code_key)
        if not code_data_json:
            raise Exception("验证码已过期或不存在")

        code_data = json.loads(code_data_json)
        if code_data["attempts"] >= self.max_attempts:
            self.redis.delete(redis_code_key)
            raise Exception("验证次数过多，验证码已失效，请重新获取")

        if request.code != code_data["code"]:
            code_data["attempts"] += 1
            self.redis.set(redis_code_key, json.dumps(code_data), self.redis.ttl(redis_code_key))
            raise Exception("验证码错误")

        # 验证成功，删除验证码
        self.redis.delete(redis_code_key)
        self.logger.info(f"手机号 {request.phone} 验证成功")
