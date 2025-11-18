# WxPusher 通知组件

一个用于 Home Assistant 的 WxPusher 通知组件，可通过 WxPusher 服务向微信发送通知消息。

## 功能介绍

该组件允许 Home Assistant 通过 WxPusher API 发送通知到微信，支持自定义消息内容和标题，适用于家庭自动化场景中的事件提醒。

## 安装方法

1. 下载本组件的所有文件
2. 将 `wxpusher` 文件夹复制到 Home Assistant 的 `custom_components` 目录下
3. 重启 Home Assistant

## 配置步骤

1. 在 WxPusher 平台获取 `app_token` 和 `uid`：
   - 访问 [WxPusher 官网](https://wxpusher.zjiecode.com/) 注册账号
   - 创建应用获取 `app_token`
   - 在应用中获取用户的 `uid`
2. 在 Home Assistant 中配置：
   - 进入 Home Assistant 管理界面，依次点击 **配置 > 集成 > 添加集成**
   - 搜索并选择 **WxPusher 通知**
   - 输入获取到的 `app_token` 和 `uid` 完成配置

## 使用方法

通过调用 Home Assistant 的通知服务发送消息，示例服务调用：

```yaml
service: notify.wxpusher
data:
  message: "这是一条来自 Home Assistant 的测试消息"
  title: "测试通知"
```

## 参数说明

- `message`：必填，通知的具体内容
- `title`：可选，通知的标题（会作为消息摘要显示）

## 常见问题

1. **发送失败提示 "API 返回列表（错误）"**
   - 通常是 `app_token` 或 `uid` 不正确，请检查配置中的参数是否与 WxPusher 平台一致
2. **发送超时或网络错误**
   - 请检查 Home Assistant 服务器是否能访问互联网，以及是否能连接 `https://wxpusher.zjiecode.com`
3. **如何更新配置**
   - 进入 **配置 > 集成**，找到已配置的 WxPusher 集成
   - 点击 **选项** 即可修改 `app_token` 和 `uid`

## 依赖说明

- 要求 `requests>=2.25.1` 库（组件会自动处理依赖安装）

## 相关链接

- [WxPusher 官方文档](https://wxpusher.zjiecode.com/docs/)
- [项目源码](https://github.com/flamestsui/wxpusher)
