# Save for X — 官网

Chrome 扩展 [Save for X](https://chromewebstore.google.com/) 的产品官网：功能说明、定价，以及隐私政策、服务条款、退款、版权与支持页面。

中英双语。**`zh/` 下的中文页由 `scripts/make-zh.py` 从英文源生成，不要手写** —— 手写两份必然漂移，结构对等测试会失败。改完英文页后重新生成：

```sh
python3 scripts/make-zh.py
```

## 本地预览

```sh
npm run serve
```

打开 `http://127.0.0.1:4174/`。

## 测试

```sh
npm test
```

浏览器验收另需 playwright（可选，用 `CHROME_PATH` 指定浏览器）：

```sh
npm run test:browser
```

会在 `screenshots/` 生成截图，在 `test-results/` 生成指标。
