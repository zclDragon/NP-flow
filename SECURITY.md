# Security Policy

## Supported Versions
curl -X POST 'https://aigateway.nipponpaint.com.cn/dev/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YykVjq1HeiIRnrGp' \
  -d '{
    "model": "gemini-3-pro-preview",
    "stream": false,
    "messages": [
      { "role": "user", "content": "你好，请用一句话介绍你自己。" }
    ],
    "max_completion_tokens": 128
  }'
As deer-flow doesn't provide an official release yet, please use the latest version for the security updates.
Currently, we have two branches to maintain:
* main branch for deer-flow 2.x
* main-1.x branch for deer-flow 1.x 

## Reporting a Vulnerability

Please go to https://github.com/bytedance/deer-flow/security to report the vulnerability you find.
