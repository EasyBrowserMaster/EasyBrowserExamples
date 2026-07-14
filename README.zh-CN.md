# EasyBrowser 示例

两个最小化的 EasyBrowser 测试示例：

- `cloudflare_turnstile.py`
- `recaptcha_v3_score_detector.py`

## 安装

从 PyPI 安装 SDK：

```bash
pip install easybrowser-sdk
patchright install chromium
```

安装示例依赖：

```bash
pip install -r requirements.txt
```

本地开发 SDK 时，再以 editable 模式安装兄弟目录中的 SDK：

```bash
pip install -e ..\sdk
```

需要先安装并运行 EasyLauncher，下载地址：

https://easybrowser.pages.dev/

## 运行

```bash
python cloudflare_turnstile.py
python recaptcha_v3_score_detector.py
```

示例使用固定测试网址，不需要命令行参数。
