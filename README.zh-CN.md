# 视频去字幕 / 去文字 API 接入示例（国内站）

[English](README.md) · [简体中文](README.zh-CN.md)

这是剪狐（UnMarkAI）视频去字幕 API 的接入示例，代码是 Python 和 cURL。可以去掉视频画面里的硬字幕、标题、时间戳和贴纸文字。处理在剪狐的服务端完成，仓库里没有模型和处理引擎。

本文按国内站来写。国内站和海外站的路径、字段相同，区别在接口地址、密钥和计费币种。英文 README 写的是海外站。

- API 文档（功能说明）：https://unmarkai.cn/developers/docs/
- 获取 API 密钥（控制台）：https://unmarkai.cn/developers/?tab=keys
- OpenAPI 契约：https://unmarkai.cn/openapi-v1.yaml （server 选 `https://unmarkai.cn/api`，路径里已经带 `/v1`）

## 先说明几点

- REST 地址是 `https://unmarkai.cn/api/v1`，MCP 地址是 `https://unmarkai.cn/api/mcp`。
- 控制台用手机号登录，在里面创建 `uma_live_*` 密钥。手机号登录的会话不能拿来调接口。
- 国内站和海外站的密钥、钱包是分开的，海外站的密钥在国内站用不了，反过来也一样。
- 按人民币计费，余额通过微信充值。

## 快速开始

需要 Python 3.10+，在仓库根目录执行：

```bash
git clone https://github.com/DayBreak-u/unmarkai-video-text-removal-api.git
cd unmarkai-video-text-removal-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export UNMARKAI_API_BASE='https://unmarkai.cn/api/v1'
export UNMARKAI_API_KEY='uma_live_replace_with_your_key'
python examples/remove_text.py --file ./source.mp4
```

不设 `UNMARKAI_API_BASE` 时示例会请求海外站，所以国内站一定要先设好。结果保存在 `output/`。`.env.example` 只是模板，脚本不会自动读取，密钥放在服务端的环境变量里。

```bash
# HTTPS 视频直链，不支持平台的播放页
python examples/remove_text.py --url 'https://your-cdn.example/owned-video.mp4'
# 继续查询已有任务，不会重新创建
python examples/remove_text.py --job-id job_REPLACE
# 用已经上传好的文件创建任务
python examples/remove_text.py --upload-id upl_REPLACE --idempotency-key your-stable-request-id
```

脚本会打印 upload ID、job ID 和幂等键。重试创建请求时，upload ID、参数和幂等键都要和原来一样。重新跑 `--file` 会产生新的上传。本地轮询超时不会取消服务端的任务。

## 三种模式

- `all_area`：全画面识别和处理，`rect` 传 null。
- `sel_area`：一个矩形，面积不能超过画面的一半。适合位置固定的字幕条或角落时间戳。
- `multi_area`：多个矩形组成的数组，按全画面价格计费。

坐标用源视频的像素值 `{x1,y1,x2,y2}`，不是百分比，也不是预览窗口里的坐标，矩形要在画面范围内。

```bash
python examples/remove_text.py --file ./source.mp4 --mode sel_area --rect-json examples/rect.json
python examples/remove_text.py --file ./source.mp4 --mode multi_area --rect-json examples/rects.json
```

示例坐标是按 1280×720 的视频写的，换成自己视频的尺寸再用。如果字幕是可以开关的 SRT/VTT 字幕轨，直接关掉或替换就行，不需要走这个接口。被文字挡住的画面是 AI 补出来的，背景在动、有头发或复杂纹理的地方可能会糊或有痕迹，整段结果要看一遍。

## cURL

```bash
export UNMARKAI_API_BASE='https://unmarkai.cn/api/v1'
export UNMARKAI_API_KEY='uma_live_replace_with_your_key'
bash examples/quickstart.sh ./source.mp4
```

需要 Bash、cURL 和 jq。脚本只负责上传、建任务和查一次状态，后续轮询和下载用 Python 示例的 `--job-id`。请求流程和重试注意事项见 [docs/api.md](docs/api.md)。

## MCP 接入

国内站的 MCP 地址是 `https://unmarkai.cn/api/mcp`，用同一把 API 密钥鉴权。目前只有去字幕相关的工具，翻译要走 REST。以 Claude Code 为例：

```bash
claude mcp add --transport http unmarkai https://unmarkai.cn/api/mcp \
  --header "Authorization: Bearer $UNMARKAI_API_KEY"
```

其他客户端字段名可能不一样，需要的连接信息就是地址和 `Authorization: Bearer uma_live_...` 这个请求头。工具有上传、直链导入、建去字幕任务、查任务、取消、查余额和估价。本地视频的字节仍然要由你自己的 shell 上传。Skill 的写法可以参考 [unmarkai-skills](https://github.com/DayBreak-u/unmarkai-skills)，里面的地址按国内站替换。

## 价格

| 模式 | 元 / 分钟 |
|---|---|
| 单区域 `sel_area` | 1.20 |
| 多区域 `multi_area` 或全画面 `all_area` | 2.40 |

这是标准价。每个视频按秒向上取整，最低按 15 秒计费。任务开始前会按实际时长冻结费用，成功后结算，失败或允许的取消会释放。账户折扣和实际单价以 `GET /v1/balance` 返回的为准，金额币种是 CNY。

## 限制

- 单个视频最多 2 GiB、60 分钟，支持 MP4、MOV、AVI、MKV、WebM、MPEG，以服务端校验为准。
- 任务是异步的，可以轮询，也可以在控制台配置回调，示例用的是轮询。
- 下载链接会过期，拿到后尽快下载。还在保留期内的话，重新查询任务可以拿到新链接。
- 只处理你自己拥有、已获授权或明确允许编辑的视频。

## 相关仓库

- 视频翻译 API 示例：https://github.com/DayBreak-u/unmarkai-video-translation-api

## 开发

```bash
python -m unittest discover -s tests -v
bash -n examples/quickstart.sh
```

测试用的是模拟响应，不会上传视频，也不会扣费。示例代码和文档用 [MIT](LICENSE) 许可，托管服务按剪狐的服务条款使用。
