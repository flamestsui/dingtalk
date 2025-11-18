# 钉钉机器人通知组件
[![Lastest Release](https://img.shields.io/github/release/flamestsui/dingtalk.svg?style=flat)](https://github.com/flamestsui/dingtalk/releases)[![GitHub All Releases](https://img.shields.io/github/downloads/flamestsui/dingtalk/total)](https://github.com/flamestsui/dingtalk/releases)

一个用于 Home Assistant 的钉钉机器人通知组件，可通过钉钉机器人 API 向钉钉群组发送通知消息，支持多种消息类型和用户@功能。

## 功能介绍

该组件允许 Home Assistant 通过钉钉机器人 API 向指定钉钉群组发送通知，核心功能包括：
- 支持多种消息类型：文本（text）、Markdown、链接（link）、卡片（actioncard）
- 可@指定用户（通过手机号）
- 适配钉钉机器人的安全验证机制（支持加签方式）
- 集成 Home Assistant 通知服务，易于在自动化场景中调用

## 依赖说明

- 要求 `requests>=2.25.1` 库（组件会自动处理依赖安装）

## 安装方法

1. 下载本组件的所有文件
2. 将 `dingtalk` 文件夹复制到 Home Assistant 的 `custom_components` 目录下
3. 重启 Home Assistant

## 配置步骤

1. 在钉钉中获取机器人 Webhook 和 Secret：
   - 打开目标钉钉群组，进入「群设置 > 智能群助手 > 添加机器人 > 自定义机器人」
   - 完成安全设置（推荐使用「加签」方式以提高安全性）
   - 保存获取到的 Webhook 地址和 Secret（若启用加签则需记录 Secret）

2. 在 Home Assistant 中配置集成：
   - 进入 Home Assistant 管理界面，依次点击 **配置 > 集成 > 添加集成**
   - 搜索并选择 **钉钉机器人通知**
   - 在配置表单中输入：
     - 钉钉机器人 Webhook 地址（必填）
     - 密钥（可选，仅当机器人启用加签时需要）
   - 完成配置并保存

## 使用方法

通过调用 Home Assistant 的 `notify.dingtalk` 服务发送通知，以下是不同消息类型的示例：

### 文本消息
```yaml
service: notify.dingtalk
data:
  message: "这是一条来自 Home Assistant 的文本消息"
  title: "文本通知标题"  # 标题会显示在消息内容上方，用分隔线分隔
  target: ["13800138000", "13900139000"]  # 需要@的用户手机号列表（可选）

```

### Markdown 消息

```yaml
service: notify.dingtalk
data:
  message: "## 标题\n- 列表项1\n- 列表项2"
  title: "Markdown通知"
  data:
    type: "markdown"
```

### 链接消息

```yaml
service: notify.dingtalk
data:
  message: "这是链接描述"
  title: "链接标题"
  data:
    type: "link"
    url: "https://www.example.com"
    picurl: "https://www.example.com/image.jpg"  # 可选
```

## 参数说明

- `message`：必填，通知的具体内容

- `title`：可选，通知的标题（不同消息类型显示方式不同）

- `target`：可选，需要 @的用户手机号列表

- ```
  data
  ```

  ：可选，消息扩展参数

  - `type`：消息类型，可选值：`text`（默认）、`markdown`、`link`、`actioncard`
  - `url`：链接消息或卡片消息的跳转地址
  - `picurl`：链接消息的图片地址

## 常见问题

1. 发送失败提示 "错误码：300001" 等
   - 通常是 Webhook 地址或 Secret 不正确，请检查配置是否与钉钉机器人设置一致
2. 发送超时或网络错误
   - 请检查 Home Assistant 服务器是否能访问互联网，以及是否能连接钉钉机器人 API 服务器
3. 如何更新配置
   - 进入 **配置 > 集成**，找到已配置的「钉钉机器人通知」
   - 点击 **选项** 即可修改 Webhook 和 Secret

## 相关链接

- [钉钉自定义机器人官方文档](https://developers.dingtalk.com/document/app/custom-robot-access)
- [项目源码](https://github.com/flamestsui/dingtalk)
