# ZSGF.Client Python SDK

![PyPI - Version](https://img.shields.io/pypi/v/ZSGF.Client)

一个功能强大的Python SDK，为开发者提供完整的用户管理、支付、存储等服务集成。

## ✨ 特性

- 🔐 **用户认证** - 支持邮箱、手机、第三方登录
- 💰 **支付集成** - 支持支付宝、微信支付
- 📱 **微信生态** - 小程序、公众号完整支持
- 💾 **数据存储** - 云端存储服务
- 👥 **社交功能** - 用户关注、推荐系统
- 📁 **文件管理** - 文件上传、管理功能

## 📋 系统要求

- Python 3.8+

## 🚀 快速开始

### 安装

```bash
pip install ZSGF.Client
```

### 基础配置

```python
import ZSGF.Client
from ZSGF.Client.rest import ApiException

# 配置SDK
configuration = ZSGF.Client.Configuration(
    host = "https://your-api-server.com"  # 替换为您的API服务器地址
)

# 配置认证（Bearer Token）
configuration.access_token = "your-access-token"  # 替换为您的访问令牌
```

### 简单示例

```python
# 创建API客户端
with ZSGF.Client.ApiClient(configuration) as api_client:
    # 获取应用信息
    app_api = ZSGF.Client.AppApi(api_client)
    try:
        app_info = app_api.app_info("your-app-key")
        print(f"应用名称: {app_info.data.name}")
    except ApiException as e:
        print(f"API调用失败: {e}")
```

## 📚 常用功能指南

### 🔐 用户认证

#### 用户注册与登录

```python
# 用户API实例
user_api = ZSGF.Client.UserApi(api_client)

# 邮箱注册
signup_request = ZSGF.Client.EmailSignUpRequest(
    email="user@example.com",
    password="secure_password",
    verification_code="123456"  # 邮箱验证码
)

try:
    result = user_api.user_email_sign_up("your-app-key", signup_request)
    print(f"注册成功: {result.data.user_id}")
except ApiException as e:
    print(f"注册失败: {e}")

# 邮箱登录
signin_request = ZSGF.Client.EmailSignInRequest(
    email="user@example.com",
    password="secure_password"
)

try:
    result = user_api.user_email_sign_in("your-app-key", signin_request)
    print(f"登录成功: {result.data.access_token}")
except ApiException as e:
    print(f"登录失败: {e}")
```

#### 获取用户信息

```python
try:
    profile = user_api.user_profile("your-app-key")
    print(f"用户昵称: {profile.data.nickname}")
    print(f"用户邮箱: {profile.data.email}")
except ApiException as e:
    print(f"获取用户信息失败: {e}")
```

### 💰 支付功能

#### 创建支付订单

```python
# 支付宝API实例
alipay_api = ZSGF.Client.AlipayApi(api_client)

# 创建支付订单
order_request = ZSGF.Client.AlipayCreateOrderRequest(
    subject="商品购买",
    total_amount="99.00",
    out_trade_no="ORDER_" + str(int(time.time()))
)

try:
    result = alipay_api.alipay_create_order("your-app-key", order_request)
    print(f"支付订单创建成功: {result.data.qr_code}")
except ApiException as e:
    print(f"创建订单失败: {e}")
```

### 📁 文件管理

#### 文件上传

```python
# 文件API实例
file_api = ZSGF.Client.FileApi(api_client)

try:
    # 上传文件
    with open("example.jpg", "rb") as file:
        result = file_api.file_upload("your-app-key", file=file)
        print(f"文件上传成功: {result.data.file_url}")
except ApiException as e:
    print(f"文件上传失败: {e}")
```

### 💾 数据存储

#### 数据操作

```python
# 存储API实例
storage_api = ZSGF.Client.StorageApi(api_client)

# 添加数据
data = {
    "name": "张三",
    "age": 25,
    "city": "北京"
}

try:
    result = storage_api.storage_post("your-app-key", "users", data)
    print(f"数据添加成功: {result.data.id}")
except ApiException as e:
    print(f"添加数据失败: {e}")

# 查询数据
try:
    result = storage_api.storage_list("your-app-key", "users", page=1, size=10)
    for item in result.data.items:
        print(f"用户: {item.name}, 年龄: {item.age}")
except ApiException as e:
    print(f"查询数据失败: {e}")
```

## 🔧 高级配置

### 错误处理

```python
from ZSGF.Client.rest import ApiException

try:
    # API调用
    result = api_instance.some_method()
except ApiException as e:
    print(f"HTTP状态码: {e.status}")
    print(f"错误原因: {e.reason}")
    print(f"错误详情: {e.body}")
```

### 自定义超时

```python
configuration = ZSGF.Client.Configuration(
    host="https://your-api-server.com"
)

# 设置超时时间（秒）
configuration.timeout = 30
```

## 📖 API 分类说明

### 🔐 认证相关
- **AccessTokenApi** - 访问令牌管理
- **UserApi** - 用户注册、登录、资料管理
- **ExternalAccountApi** - 第三方账号绑定
- **OAuthApi** - OAuth授权

### 💰 支付相关
- **AlipayApi** - 支付宝支付
- **OrderApi** - 订单管理
- **UserCurrencyApi** - 虚拟货币

### 📱 微信生态
- **WechatApi** - 微信小程序、公众号
- **DingTalkApi** - 钉钉集成

### 💾 数据服务
- **StorageApi** - 数据存储
- **FileApi** - 文件管理

### 👥 社交功能
- **UserFriendsApi** - 好友关系
- **UserLocationApi** - 位置服务

### 📱 应用管理
- **AppApi** - 应用信息

## 📋 完整API列表

<details>
<summary>点击查看所有API方法</summary>

### AccessTokenApi - 访问令牌
| 方法 | HTTP | 描述 |
|------|------|------|
| `access_token_delete` | DELETE | 删除令牌 |
| `access_token_post` | POST | 创建令牌 |
| `access_token_put` | PUT | 更新令牌 |
| `access_tokens` | GET | 令牌列表 |

### AlipayApi - 支付宝
| 方法 | HTTP | 描述 |
|------|------|------|
| `alipay_create_order` | POST | 创建当面付订单 |
| `alipay_create_order_page_pay` | POST | 创建PC支付订单 |
| `alipay_create_order_wap_pay` | POST | 创建WAP支付订单 |
| `alipay_order_detail` | GET | 获取订单详情 |
| `alipay_order_refund` | POST | 发起订单退款 |

### UserApi - 用户管理
| 方法 | HTTP | 描述 |
|------|------|------|
| `user_email_sign_up` | POST | 邮箱注册 |
| `user_email_sign_in` | POST | 邮箱登录 |
| `user_phone_sign_up` | POST | 手机注册 |
| `user_phone_sign_in` | POST | 手机登录 |
| `user_profile` | GET | 获取个人资料 |
| `user_update_profile` | PUT | 更新个人资料 |
| `user_reset_pwd` | POST | 重置密码 |
| `user_send_email_code` | POST | 发送邮箱验证码 |
| `user_send_sms_code` | POST | 发送手机验证码 |

### StorageApi - 数据存储
| 方法 | HTTP | 描述 |
|------|------|------|
| `storage_post` | POST | 添加数据 |
| `storage_list` | GET | 查询数据 |
| `storage_detail` | GET | 数据详情 |
| `storage_put` | PUT | 更新数据 |
| `storage_delete` | DELETE | 删除数据 |
| `storage_aggregate` | GET | 聚合查询 |

### FileApi - 文件管理
| 方法 | HTTP | 描述 |
|------|------|------|
| `file_upload` | POST | 上传文件 |
| `files` | GET | 获取文件列表 |
| `file_create_folder` | POST | 创建文件夹 |
| `file_rename` | POST | 重命名文件/文件夹 |
| `file_delete` | DELETE | 删除文件/文件夹 |

### WechatApi - 微信服务
| 方法 | HTTP | 描述 |
|------|------|------|
| `wechat_js_code2_session` | GET | 校验小程序登录状态 |
| `wechat_decrypt` | GET | 解密小程序用户数据 |
| `wechat_user_info` | GET | 获取公众号H5 UnionID |
| `wechat_js_config` | GET | 配置公众号JS SDK |
| `wechat_wxa_code_get` | POST | 获取小程序码（普通） |
| `wechat_wxa_code_get_unlimited` | POST | 获取小程序码（无限制） |
| `wechat_subscribe_send` | POST | 发送小程序订阅消息 |

### UserFriendsApi - 社交功能
| 方法 | HTTP | 描述 |
|------|------|------|
| `user_follow_user` | POST | 添加关注 |
| `user_unfollow_user` | DELETE | 取消关注 |
| `user_followers` | GET | 获取粉丝列表 |
| `user_following` | GET | 获取关注列表 |
| `user_friends_near_by` | GET | 推荐附近用户 |
| `user_common_interests` | GET | 推荐相似兴趣用户 |

### OrderApi - 订单管理
| 方法 | HTTP | 描述 |
|------|------|------|
| `order_create` | POST | 创建订单 |
| `order` | GET | 获取订单详情 |
| `orders` | GET | 获取订单列表 |

### UserCurrencyApi - 虚拟货币
| 方法 | HTTP | 描述 |
|------|------|------|
| `user_currencies` | GET | 获取用户资产 |
| `user_currency_consume` | POST | 消费虚拟币 |
| `user_currency_exchange` | POST | 兑换虚拟币 |
| `user_currency_recharge` | POST | 充值虚拟币 |
| `user_currency_transactions` | GET | 虚拟币交易记录 |

### OAuthApi - OAuth授权
| 方法 | HTTP | 描述 |
|------|------|------|
| `o_auth_authorize` | POST | 获取访问令牌 |
| `o_auth_consents` | GET | 获取授权记录 |
| `o_auth_delete_consent` | DELETE | 删除授权记录 |
| `o_auth_grant_code` | POST | 获取授权码 |
| `o_auth_profile` | GET | 获取用户资料 |

### ExternalAccountApi - 外部账号
| 方法 | HTTP | 描述 |
|------|------|------|
| `external_account_sign_in` | POST | 外部账号登录 |
| `user_external_account_bind` | POST | 绑定外部账号 |
| `user_o_auth_accounts` | GET | 外部账号列表 |
| `user_o_auth_accounts_put_bind` | PUT | 更新绑定账号 |
| `user_o_auth_accounts_un_bind` | DELETE | 删除绑定账号 |

### UserLocationApi - 位置服务
| 方法 | HTTP | 描述 |
|------|------|------|
| `user_location` | GET | 获取位置详情 |
| `user_location_delete` | DELETE | 删除位置 |
| `user_location_post` | POST | 添加位置 |
| `user_location_put` | PUT | 更新位置 |
| `user_locations` | GET | 获取位置列表 |

### DingTalkApi - 钉钉集成
| 方法 | HTTP | 描述 |
|------|------|------|
| `ding_talk_user_info` | GET | 获取用户资料 |

### AppApi - 应用管理
| 方法 | HTTP | 描述 |
|------|------|------|
| `app_info` | GET | 应用详情 |

</details>

## 💡 最佳实践

### 1. 异常处理
始终使用try-catch包装API调用，处理可能的异常。

### 2. 配置管理
建议将API密钥等敏感信息存储在环境变量中：

```python
import os
configuration.access_token = os.environ.get("ZSGF_ACCESS_TOKEN")
```

### 3. 分页查询
对于列表查询，合理使用分页参数：

```python
# 分页获取数据
page = 1
size = 20
result = storage_api.storage_list("your-app-key", "table_name", page=page, size=size)
```

### 4. 资源清理
使用上下文管理器确保资源正确释放：

```python
with ZSGF.Client.ApiClient(configuration) as api_client:
    # 进行API调用
    pass  # 自动清理资源
```

## 🆘 常见问题

**Q: 如何获取API密钥？**
A: 请联系管理员或查看开发者控制台获取您的应用密钥。

**Q: 支持哪些支付方式？**
A: 目前支持支付宝支付，包括当面付、PC支付、WAP支付等。

**Q: 如何处理文件上传？**
A: 使用FileApi的file_upload方法，支持多种文件格式。

**Q: 数据存储有什么限制？**
A: 具体限制请参考服务协议，建议合理使用存储资源。

## 📞 技术支持

如果您在使用过程中遇到问题：

1. 查看本文档的常见问题部分
2. 检查API响应的错误信息
3. 联系技术支持团队

## 🔗 相关链接

- [API详细文档](docs/)
- [数据结构文档](docs/models/)
- [示例代码库](examples/)

---

**Happy Coding!** 🎉 