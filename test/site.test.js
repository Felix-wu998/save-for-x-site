import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pages = [
  "index.html",
  "privacy.html",
  "terms.html",
  "refunds.html",
  "copyright.html",
  "support.html",
];
const policyLinks = [
  "privacy.html",
  "terms.html",
  "refunds.html",
  "copyright.html",
  "support.html",
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function links(html) {
  return [...html.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
}

test("all required website and asset files exist", () => {
  for (const relativePath of [
    ...pages,
    "assets/site.css",
    "assets/site.js",
    "assets/favicon.svg",
  ]) {
    assert.equal(fs.existsSync(path.join(root, relativePath)), true, relativePath);
  }
});

test("every page includes SEO metadata and shared assets", () => {
  for (const page of pages) {
    const html = read(page);
    assert.match(html, /<title>[^<]{12,}<\/title>/);
    assert.match(html, /<meta name="description" content="[^"]{40,}"/);
    assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1"/);
    assert.match(html, /href="assets\/site\.css"/);
    assert.match(html, /src="assets\/site\.js"/);
    assert.match(html, /<main/);
    assert.match(html, /<footer/);
  }
});

test("every page links to all required policy and support pages", () => {
  for (const page of pages) {
    const pageLinks = links(read(page));
    for (const policyLink of policyLinks) {
      assert.equal(pageLinks.includes(policyLink), true, `${page} -> ${policyLink}`);
    }
  }
});

test("homepage contains the approved value proposition and honest launch state", () => {
  const html = read("index.html");
  assert.match(html, /Keep every/);
  // 产品从「只下视频」扩成「视频 + GIF + 截图」，价值主张随之改写。
  // 这里锁的是新定位里三件功能都要出现，不再锁死旧的 MP4 单一表述。
  assert.match(html, /highest-bitrate MP4 X still serves/i);
  assert.match(html, /real \.gif/i);
  assert.match(html, /screenshot/i);
  // 定价从「3 次试用 + $2.99」改为「截图永久免费 + 5 次下载试用 + $5.99」，
  // 原因是固定手续费让低价的有效抽成畸高（$2.99 时 17.4%）。断言随之更新。
  assert.match(html, /5 downloads free/i);
  assert.match(html, /Screenshots always free/i);
  assert.match(html, /\$5\.99/);
  assert.match(html, /Join the launch list/i);
  assert.doesNotMatch(html, /Buy now|Add to Chrome|Get it on Chrome Web Store/i);
  assert.match(html, /Payments open after compliance review/i);
});

test("homepage exposes core sections and accessible interaction contracts", () => {
  const html = read("index.html");
  for (const id of ["how", "compare", "pricing", "trust", "faq"]) {
    assert.match(html, new RegExp(`id="${id}"`));
  }
  assert.match(html, /class="skip-link"/);
  assert.match(html, /<details/);
  assert.match(html, /data-launch-list/);
  assert.match(html, /aria-label="Download highest available quality"/);
});

test("policy pages contain product-specific required clauses", () => {
  assert.match(read("privacy.html"), /does not collect, store, sell, or share/i);
  assert.match(read("privacy.html"), /cdn\.syndication\.twimg\.com/);
  assert.match(read("terms.html"), /public content/i);
  assert.match(read("terms.html"), /rights or permission/i);
  assert.match(read("refunds.html"), /refund/i);
  assert.match(read("copyright.html"), /takedown/i);
  assert.match(read("support.html"), /compliance review/i);
});

test("all local HTML links resolve", () => {
  for (const page of pages) {
    for (const href of links(read(page))) {
      if (
        href.startsWith("#") ||
        href.startsWith("http") ||
        href.startsWith("mailto:") ||
        href.startsWith("assets/")
      ) {
        continue;
      }

      const [pathname] = href.split("#");
      assert.equal(
        fs.existsSync(path.join(root, pathname)),
        true,
        `${page} has broken link ${href}`,
      );
    }
  }
});

test("motion system supports reduced motion and compositor-friendly reveals", () => {
  const css = read("assets/site.css");
  const js = read("assets/site.js");
  assert.match(css, /prefers-reduced-motion:\s*reduce/);
  assert.match(css, /\.reveal/);
  assert.match(css, /transform:/);
  assert.match(css, /opacity:/);
  assert.match(js, /IntersectionObserver/);
  assert.match(js, /matchMedia\("\(prefers-reduced-motion: reduce\)"\)/);
});

test("review website stays lightweight and has no third-party runtime dependency", () => {
  const runtimeFiles = ["index.html", "assets/site.css", "assets/site.js", "assets/favicon.svg"];
  const runtimeBytes = runtimeFiles.reduce(
    (total, relativePath) => total + fs.statSync(path.join(root, relativePath)).size,
    0,
  );

  assert.ok(runtimeBytes < 100_000, `homepage runtime payload is ${runtimeBytes} bytes`);
  assert.doesNotMatch(read("index.html"), /<script[^>]+src="https?:\/\//i);
  assert.doesNotMatch(read("index.html"), /<link[^>]+href="https?:\/\/[^"]+"[^>]+stylesheet/i);
});

// ── 中英双语 ───────────────────────────────────────────────
// 中文页由 scripts/make-zh.py 从英文源生成，结构必须一致。英文改了而中文
// 没重新生成时，下面几条会失败 —— 这正是不手写中文页的原因。

test("every English page has a Chinese mirror", () => {
  const zh = fs.readdirSync(`${root}/zh`).filter((f) => f.endsWith(".html")).sort();
  // pages 是按阅读顺序写的，这里只比集合
  assert.deepEqual(zh, [...pages].sort(), "zh/ 与英文页文件集合不一致，需重跑 scripts/make-zh.py");
});

test("Chinese mirrors keep the same structure as their English source", () => {
  for (const name of pages) {
    const en = read(name);
    const zh = fs.readFileSync(`${root}/zh/${name}`, "utf8");
    const count = (html, tag) => (html.match(new RegExp(`<${tag}[\\s>]`, "g")) ?? []).length;
    for (const tag of ["section", "h2", "li"]) {
      assert.equal(count(zh, tag), count(en, tag), `${name} 的 <${tag}> 数量对不上`);
    }
  }
});

test("both languages link to each other", () => {
  for (const name of pages) {
    assert.match(read(name), /class="lang-switch"[^>]*href="zh\//, `${name} 缺中文入口`);
    const zh = fs.readFileSync(`${root}/zh/${name}`, "utf8");
    assert.match(zh, /class="lang-switch"[^>]*href="\.\.\//, `zh/${name} 缺英文入口`);
    assert.match(zh, /<html lang="zh-Hans">/, `zh/${name} 未声明中文`);
  }
});

test("Chinese legal pages name English as the governing version", () => {
  // 两个语言版本若无权威版本，条款冲突时会产生歧义
  for (const name of ["privacy.html", "terms.html", "refunds.html", "copyright.html"]) {
    const zh = fs.readFileSync(`${root}/zh/${name}`, "utf8");
    assert.match(zh, /以英文版为准/, `zh/${name} 缺少效力声明`);
  }
});

test("Chinese pages fix their asset paths for the subdirectory", () => {
  for (const name of pages) {
    const zh = fs.readFileSync(`${root}/zh/${name}`, "utf8");
    assert.doesNotMatch(zh, /(href|src)="assets\//, `zh/${name} 的资源路径没改成 ../assets/`);
  }
});
