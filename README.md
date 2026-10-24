# UnmarkAI Video Text Removal & Subtitle Removal API

[English](README.md) · [简体中文](README.zh-CN.md)

[![API docs](https://img.shields.io/badge/API-documentation-6845cf)](https://unmarkai.net/video-text-removal-api/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](examples/remove_text.py)
[![License](https://img.shields.io/badge/examples-MIT-green)](LICENSE)

Remove burned-in subtitles, captions, titles, date stamps and promotional text from videos you own or are authorized to edit. Build subtitle cleanup into your application with the UnmarkAI REST API, or connect an AI agent through the existing text-removal MCP server and Skill.

**[Explore the API](https://unmarkai.net/video-text-removal-api/) · [Get an API key](https://unmarkai.net/dashboard/api/keys) · [Try the web tool](https://unmarkai.net/video-text-remover/)**

This repository contains open-source integration examples for a hosted API. It does not contain model weights or a self-hosted processing engine. API usage requires an API key and available API balance; website points and API USD balance are separate.

## Real subtitle removal examples

Demo text was added to licensed footage. Comparisons show actual API output without manual cleanup. The case pages include requests, source attribution, recorded charges and observed limitations. Timings and charges describe those runs, not a performance guarantee or current price quote.

| Case | Mode | Watch input and actual output |
|---|---|---|
| Tutorial captions | `sel_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/tutorial-captions/) |
| UGC product copy | `multi_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/ugc-ad-text/) |
| Vertical creator captions | `all_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/talking-head-captions/) |
| Title and headline text | `sel_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/headline-title-text/) |
| Sticker and label text | `sel_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/sticker-label-text/) |
| Date and time stamp | `sel_area` | [Watch 12-second comparison](https://unmarkai.net/examples/remove-text-from-video/security-cam-timestamp/) |

[![Remove two-line word-highlight captions from a tutorial video: synchronized before and API result](https://unmarkai.net/videos/text-removal-cases/tutorial-captions/poster.webp)](https://unmarkai.net/examples/remove-text-from-video/tutorial-captions/)

[![Remove promotional text from a UGC product video: synchronized before and API result](https://unmarkai.net/videos/text-removal-cases/ugc-ad-text/poster.webp)](https://unmarkai.net/examples/remove-text-from-video/ugc-ad-text/)

[![Remove two-line highlighted captions from a vertical creator video: synchronized before and API result](https://unmarkai.net/videos/text-removal-cases/talking-head-captions/poster.webp)](https://unmarkai.net/examples/remove-text-from-video/talking-head-captions/)

[Browse all six video text removal cases](https://unmarkai.net/examples/). Preview media remains hosted by UnmarkAI; media rights are separate from this repository’s code license.

## Quickstart: Python

Requires Python 3.10+. Run from the repository root:

```bash
git clone https://github.com/DayBreak-u/unmarkai-video-text-removal-api.git
cd unmarkai-video-text-removal-api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export UNMARKAI_API_KEY='uma_live_replace_with_your_key'
python examples/remove_text.py --file ./source.mp4
```

The command uploads your video, creates a job, polls it and saves outputs under `output/`. The key is read from the environment; `.env.example` is a template, not automatically loaded. Keep API keys on your server.

**Direct HTTPS import** (a downloadable video URL, not a YouTube/TikTok watch page):

```bash
python examples/remove_text.py --url 'https://your-cdn.example/owned-video.mp4'
```

**Resume an existing job without creating another:**

```bash
python examples/remove_text.py --job-id job_REPLACE --output output
```

**Reuse an upload:**

```bash
python examples/remove_text.py --upload-id upl_REPLACE --idempotency-key your-stable-request-id
```

The example prints upload ID, job ID and the creation idempotency key. Retries of a creation request must use the **same upload ID, options and key**. Re-running `--file` creates a fresh upload, so use `--upload-id` when retrying an uncertain job submission. A client polling timeout does not cancel a server job.

## Choose the subtitle removal mode

| Mode | Request | Use case |
|---|---|---|
| `all_area` | `rect: null` | Detect and process text across the frame |
| `sel_area` | One `{x1,y1,x2,y2}` object | Fixed caption band or corner timestamp; selected area must not exceed half of the frame |
| `multi_area` | Non-empty array of rectangles | Separate upper/lower text regions; billed at the full-frame rate |

Coordinates use **source video pixels**, not percentages or preview coordinates. Rectangles must stay inside the source frame. See the live contract for current validation rules; the web editor’s three-box limit must not be assumed to be the API limit.

```bash
# Example rectangle matches the 1280 × 720 tutorial case; adapt to YOUR source.
python examples/remove_text.py --file ./source.mp4 --mode sel_area --rect-json examples/rect.json
python examples/remove_text.py --file ./source.mp4 --mode multi_area --rect-json examples/rects.json
```

AI reconstructs pixels hidden by text. Moving texture, faces, hair and scene cuts can leave softened details or artifacts. Review the complete result. Separate SRT/VTT tracks do not need pixel reconstruction.

## REST and cURL

- [Runnable upload and creation example](examples/quickstart.sh) — requires Bash, cURL and jq.
- [Request examples and API workflow](docs/api.md).
- [Canonical OpenAPI contract](https://unmarkai.net/openapi-v1.yaml) — source of truth for fields and limits.

```bash
export UNMARKAI_API_KEY='uma_live_replace_with_your_key'
bash examples/quickstart.sh ./source.mp4
```

## AI agents: Skill and MCP

The existing [unmarkai-skills](https://github.com/DayBreak-u/unmarkai-skills) repository teaches the text cleanup workflow. Connect to the hosted MCP server at `https://api.unmarkai.net/mcp` with the same API key:

```bash
claude mcp add --transport http unmarkai https://api.unmarkai.net/mcp \
  --header "Authorization: Bearer $UNMARKAI_API_KEY"
```

See the [MCP tools and setup guide](https://unmarkai.net/video-text-removal-api/#api-agents-title) and [agent integration notes](docs/agents.md). Local video bytes still upload through your shell; URL imports run asynchronously.

## Limits, pricing and reliability

- Up to 2 GiB and 60 minutes per source video; API upload formats include MP4, MOV, AVI, MKV, WebM and MPEG. Runtime validation is authoritative.
- Jobs are asynchronous. Use bounded polling or [signed webhooks](https://unmarkai.net/dashboard/api/docs); the examples use polling.
- Download signed result links promptly. Re-fetch job status if a URL expires, while the result remains retained under the service policy.
- Base rates: selected-area cleanup $0.225/min; full-frame and multi-region cleanup $0.45/min. Billing minimums and rounding follow the current service rules. Account discounts and effective prices come from `GET /v1/balance`; check the [current API pricing](https://unmarkai.net/video-text-removal-api/#volume-pricing).
- API trial eligibility and funding rules may change; check your console. Website subscription points do not fund API jobs.

## FAQ

**Can it remove subtitles without cropping?**

The removal workflow reconstructs selected pixels while keeping the frame dimensions. Quality depends on the source and must be reviewed.

**Will this remove a switchable subtitle track?**

For switchable tracks, disable or replace the track directly. Use AI cleanup for text encoded into the picture.

**Is the processing engine open source?**

The example integration code is MIT-licensed. Processing runs on UnmarkAI’s hosted service, with its own pricing and terms.

**What may I upload?**

Only video you own, license or have explicit permission to edit. Keep attribution and required notices. Review output before publishing.

## Developer resources

- [API documentation](https://unmarkai.net/dashboard/api/docs)
- [Create an API key](https://unmarkai.net/dashboard/api/keys) · [API console](https://unmarkai.net/dashboard/api/)
- [OpenAPI contract](https://unmarkai.net/openapi-v1.yaml)
- [Agent Skills](https://github.com/DayBreak-u/unmarkai-skills) · [Text-removal MCP guide](https://unmarkai.net/video-text-removal-api/#api-agents-title)
- [Video text removal API examples](https://github.com/DayBreak-u/unmarkai-video-text-removal-api)
- [Video translation API examples](https://github.com/DayBreak-u/unmarkai-video-translation-api)
- [Contact](https://unmarkai.net/contact/) · [Privacy](https://unmarkai.net/privacy/) · [Acceptable use](https://unmarkai.net/acceptable-use/)

## Development

```bash
python -m unittest discover -s tests -v
bash -n examples/quickstart.sh
```

Tests mock API and media responses; they do not upload files or spend API credit. Report integration bugs through GitHub Issues without posting keys, signed URLs or private media. Service-account and billing questions belong in [support](https://unmarkai.net/contact/).

## License

[MIT](LICENSE) for original example code and documentation. Linked demonstration media, trademarks and the hosted service remain subject to their respective rights and terms.
