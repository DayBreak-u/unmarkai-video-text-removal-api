# UnmarkAI 视频去字幕 / 去文字 API

[English](README.md) · [简体中文](README.zh-CN.md)

用 REST API 去除授权视频中的硬字幕、动态字幕、标题、时间戳及宣传文字，便于重新配字幕或继续做多语言本地化。

**[API 产品与文档](https://unmarkai.net/video-text-removal-api/) · [创建 API key](https://unmarkai.net/dashboard/api/keys) · [在线工具](https://unmarkai.net/video-text-remover/)**

这是托管 API 的开源接入示例，提供 Python 与 cURL 代码；处理引擎和模型不在本仓库中。使用需要 API key 和可用 API 余额，API 美元钱包与网站积分独立。

## 真实去字幕效果

[查看六组真实案例](https://unmarkai.net/examples/)：教程字幕、UGC 宣传文字、竖屏创作者字幕、标题、贴纸和时间戳。演示文字加在授权素材上，清理结果来自真实 API；实测费用和耗时不代表固定报价或处理时限。

[![教程字幕：源视频与真实 API 输出](https://unmarkai.net/videos/text-removal-cases/tutorial-captions/poster.webp)](https://unmarkai.net/examples/remove-text-from-video/tutorial-captions/)

## 快速开始

需要 Python 3.10+，在仓库根目录执行：

```bash
git clone https://github.com/DayBreak-u/unmarkai-video-text-removal-api.git
cd unmarkai-video-text-removal-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export UNMARKAI_API_KEY='uma_live_replace_with_your_key'
python examples/remove_text.py --file ./source.mp4
```

输出保存至 `output/`。`.env.example` 仅为模板，不会自动读取；请把 key 放在服务器环境变量中。

```bash
# 直接 HTTPS 视频地址，不接受平台观看页
python examples/remove_text.py --url 'https://your-cdn.example/owned-video.mp4'
# 恢复已有任务，不重复创建
python examples/remove_text.py --job-id job_REPLACE
# 使用已经上传的文件创建任务
python examples/remove_text.py --upload-id upl_REPLACE --idempotency-key your-stable-request-id
```

示例会输出 upload ID、job ID 和幂等键。创建请求重试须复用相同 upload ID、参数及幂等键；重新运行 `--file` 会生成新的上传。轮询超时不会取消服务端任务。

## 去文字模式

- `all_area`：全画面，`rect` 为 null。
- `sel_area`：一个矩形对象，面积不超过源画面一半。
- `multi_area`：非空矩形数组，按全画面费率计费。

矩形使用源视频像素坐标 `{x1,y1,x2,y2}`，不是百分比，且必须位于画面内。不要把网页编辑器的三个框上限当成 API 限制。

```bash
python examples/remove_text.py --file source.mp4 --mode sel_area --rect-json examples/rect.json
python examples/remove_text.py --file source.mp4 --mode multi_area --rect-json examples/rects.json
```

示例坐标适用于 1280×720 的教程案例，请按自己的视频修改。独立 SRT/VTT 字幕轨可以直接关闭或替换；AI 用于已编码进画面的硬字幕。移动背景、头发和纹理可能出现软化或修复痕迹，需要检查整段结果。

## cURL、文档与 AI Agent

- [可运行 cURL 示例](examples/quickstart.sh)：需要 Bash、cURL、jq。
- [API 流程和请求说明](docs/api.md)。
- [公开 OpenAPI 契约](https://unmarkai.net/openapi-v1.yaml)。
- [Agent Skills](https://github.com/DayBreak-u/unmarkai-skills) 和 [MCP 接入指南](https://unmarkai.net/video-text-removal-api/#api-agents-title)：当前覆盖去文字流程。

可以使用现有去文字 Skill/MCP 自动选择清理模式并处理任务，详见英文 README 的连接示例。

## 限制与费用

- 每个视频最多 2 GiB / 60 分钟，支持的 API 上传格式包括 MP4、MOV、AVI、MKV、WebM、MPEG；服务端校验为准。
- 基础费率：选区去文字 $0.225/分钟，全画面及多选区 $0.45/分钟；最低计费时长与取整规则见实时文档。
- 账户实时价格及折扣以 `GET /v1/balance` 为准，详细规则见 API 页面；网站积分不能直接支付 API 任务。
- 结果下载地址会过期，请及时下载；结果仍在保留期内时可重新查询任务获取地址。
- 仅处理自有、已许可或明确获得编辑授权的视频，保留署名与必要声明。

## 相关资源

- [API documentation](https://unmarkai.net/dashboard/api/docs)
- [Create an API key](https://unmarkai.net/dashboard/api/keys) · [API console](https://unmarkai.net/dashboard/api/)
- [OpenAPI contract](https://unmarkai.net/openapi-v1.yaml)
- [Agent Skills](https://github.com/DayBreak-u/unmarkai-skills) · [Text-removal MCP guide](https://unmarkai.net/video-text-removal-api/#api-agents-title)
- [Video text removal API examples](https://github.com/DayBreak-u/unmarkai-video-text-removal-api)
- [Video translation API examples](https://github.com/DayBreak-u/unmarkai-video-translation-api)
- [Contact](https://unmarkai.net/contact/) · [Privacy](https://unmarkai.net/privacy/) · [Acceptable use](https://unmarkai.net/acceptable-use/)

## 开发与许可

```bash
python -m unittest discover -s tests -v
bash -n examples/quickstart.sh
```

测试使用模拟响应，不上传视频、不消费 API 额度。原始示例代码与文档使用 [MIT](LICENSE) 许可，演示媒体、品牌和托管服务按各自条款使用。
