# Public API workflow

Canonical contract: [https://unmarkai.net/openapi-v1.yaml](https://unmarkai.net/openapi-v1.yaml). Version checked against the public contract on 2026-10-24. Recheck it when updating examples.

1. Obtain an `uma_live_*` key with `jobs:write`, `jobs:read` and `balance:read` scopes from the [API console](https://unmarkai.net/dashboard/api/keys).
2. `POST /v1/uploads` with filename, MIME and byte size, then PUT bytes to its signed URL with **every returned header unchanged**. Do not send the API key to the storage origin. Signed PUT is one-shot; a consumed ticket may return 412.
3. Alternatively, `POST /v1/url-uploads` with `source_url`, then poll `GET /v1/uploads/{upload_id}` until `uploaded`. HTTPS direct media URLs only. `failed` and `expired` are terminal import states.
4. `POST /v1/jobs` with a ready `upload_id` and an `Idempotency-Key`. Retrying uses exactly the same body and key. Save both IDs. Do not resubmit a whole workflow after losing the creation response.
5. Poll `GET /v1/jobs/{job_id}`, or integrate [signed webhook events](https://unmarkai.net/dashboard/api/docs). `failed` and `canceled` are terminal. Inspect `error.code` and the request ID.
6. On `succeeded`, download available results without API Authorization headers; signed links are temporary. A local polling timeout does not cancel the server task.

## Example request

```json
{
  "type": "remove_text",
  "input": {
    "upload_id": "upl_REPLACE"
  },
  "mode": "sel_area",
  "rect": {
    "x1": 44,
    "y1": 520,
    "x2": 1236,
    "y2": 708
  }
}
```

`result.url` is the cleaned video URL. Inspect temporal consistency around scene cuts and text changes.

## Error handling

The example retries GET and idempotent job creation on transient connection errors and 429/502/503/504, with bounded backoff. It never blindly retries a signed PUT, review PATCH or an unkeyed upload POST. On an uncertain upload result, inspect the upload before creating a replacement. Review conflicts require a fresh fetch, not an unconditional overwrite. API responses have `error.code`, `error.message`, `error.request_id`; example errors show code and request ID without dumping signed URLs.

## cURL options

`examples/quickstart.sh` expects MP4 by default; set `CONTENT_TYPE=video/quicktime` etc. for other accepted formats. It creates the upload and task and checks status once. For a complete bounded poll and download, resume with `python examples/remove_text.py --job-id job_REPLACE`.

For a region, use `MODE=sel_area RECT_JSON='{"x1":44,"y1":520,"x2":1236,"y2":708}' bash examples/quickstart.sh source.mp4`. Coordinates are only suitable for the recorded 1280×720 tutorial source.

For an uncertain create response, preserve `output/curl/request.json` and the printed key and retry only the same POST /jobs request. Do not rerun the entire shell script with the same key, because that produces a different upload ID.
