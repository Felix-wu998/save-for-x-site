"""从英文页面生成中文镜像 zh/*.html。

不手写中文页：结构由英文源决定，中文只提供译文。英文改了而中文没跟上时，
下面的 test/site.test.js 会因为两边结构对不上而失败。

法律页（隐私、条款、退款、版权）额外插入一句「以英文版为准」。两个语言版本
万一表述冲突，必须有一个权威版本，否则是给自己埋歧义。
"""

import pathlib
import re

# 全站共用（导航、页脚）
SHARED = {
    "Skip to content": "跳到主要内容",
    "How it works": "工作原理",
    "Compare": "对比",
    "Pricing": "价格",
    "Trust": "信任",
    "Launch status": "上线状态",
    "Screenshots always free": "截图永久免费",
    "Privacy": "隐私",
    "Terms": "条款",
    "Refunds": "退款",
    "Copyright": "版权",
    "Support": "支持",
    "© 2026 · Independent of X Corp.": "© 2026 · 与 X Corp. 无关联",
}

PAGES = {
"index.html": {
    "Save for X — HD Video, GIF & Screenshot": "Save for X — 高画质视频、GIF 与截图",
    "Save any public X post: the highest-bitrate MP4, a real GIF built on your own device, or a screenshot of the whole post. No ads, no copy-paste download sites.":
        "保存任何公开 X 帖子：最高码率 MP4、在你自己设备上生成的真 GIF，或整条帖子的截图。没有广告，不用复制粘贴到下载站。",
    "One click. Video, GIF or screenshot — saved from your timeline.":
        "一次点击。视频、GIF 或截图，直接从时间线保存。",
    "Video · GIF · Screenshot": "视频 · GIF · 截图",
    "Keep every": "留住每一个",
    "last pixel.": "像素。",
    "Save the highest-bitrate MP4 X still serves, turn a GIF post into a real .gif on your own device, or capture the whole post as an image. One click, right in your timeline.":
        "保存 X 仍在提供的最高码率 MP4，把 GIF 帖在你自己设备上转成真正的 .gif，或者把整条帖子存成图片。一次点击，就在时间线里完成。",
    "Join the launch list": "加入上线通知",
    "See how it works": "看它怎么工作",
    "Public videos only · Rights-first · Chrome extension · Review build":
        "仅限公开内容 · 权利优先 · Chrome 扩展 · 审核版本",
    "Selected quality": "所选画质",
    "Highest": "最高",
    "X's best currently available direct MP4.": "X 当前提供的最佳直连 MP4。",
    "Processing": "处理方式",
    "None": "无",
    "Your timeline already has the buttons.": "按钮就在你的时间线里。",
    "No mystery server between you and the file.": "你和文件之间没有中间服务器。",
    "Screenshots are free. Downloads are one small payment.": "截图免费。下载只需一次小额付费。",
    "Built to save public videos, not bypass access controls.": "为保存公开内容而生，不用于绕过访问限制。",
    "Clear answers before launch.": "上线前把话说清楚。",
    "Simple planned pricing": "简单的计划定价",
    "Planned lifetime access": "计划中的永久使用权",
    "One-time payment": "一次性付费",
    "Highest-bitrate MP4 X still serves": "X 仍在提供的最高码率 MP4",
    "Unlimited video and GIF downloads": "视频与 GIF 无限下载",
    "Real .gif built on your own device": "在你自己设备上生成的真 .gif",
    "Unlimited post screenshots — free for everyone": "帖子截图无限使用 —— 对所有人免费",
    "Timeline and post-page buttons": "时间线与帖子详情页均有按钮",
    "Interface in 25 languages": "界面支持 25 种语言",
    "Future maintenance updates": "后续维护更新",
    "Payments open after compliance review. No payment is collected on this website yet.":
        "支付将在合规审核通过后开放。本网站目前不收取任何款项。",
    "· 25.1 Mbps · Direct MP4": "· 25.1 Mbps · 直连 MP4",
    "Video downloaded byte-for-byte. GIF built locally. Nothing uploaded.":
        "视频逐字节下载，GIF 本地生成，不上传任何内容。",
    "Video goes from X to your download folder.": "视频从 X 直接进入你的下载文件夹。",
    "✓ Download started — highest available quality": "✓ 已开始下载 —— 最高可用画质",
    "Download directly from the X timeline.": "直接在 X 时间线里下载。",
    "0 video re-encoding": "0 次视频重编码",
    "No second compression pass.": "不做第二次压缩。",
    "5 downloads free": "5 次免费下载",
    "Real downloads before you decide.": "先真正下载几次，再决定。",
    "Planned lifetime access. No subscription.": "计划中的永久使用权。无订阅。",
    "Browse normally. Posts with a video or GIF get a download button; every non-promoted post gets a screenshot button. The extension confirms what is actually downloadable before offering it.":
        "照常刷推。含视频或 GIF 的帖子会出现下载按钮，所有非推广帖都会出现截图按钮。扩展会先确认到底有什么可下载，再决定是否提供。",
    "Eligible video posts receive a small download control beside X's More menu.":
        "符合条件的视频帖，会在 X 的「更多」菜单旁出现一个小的下载控件。",
    "We choose the best": "我们替你挑最好的",
    "The extension checks every available direct MP4 and selects the highest bitrate.":
        "扩展会检查所有可用的直连 MP4，选出码率最高的那个。",
    "Save it locally": "保存到本地",
    "The file travels directly from X to Chrome's download folder without a third-party video server.":
        "文件从 X 直接进入 Chrome 的下载文件夹，中间没有第三方视频服务器。",
    "Transparent by design": "设计上就透明",
    "Save for X is deliberately narrow: public X videos, direct MP4 files, and no video proxy or conversion pipeline.":
        "Save for X 刻意做得很窄：只处理公开的 X 内容与直连 MP4 文件，没有视频代理，也没有转换流水线。",
    "Typical download site": "常见的下载站",
    "Highest available direct MP4": "最高可用的直连 MP4",
    "Copy and paste": "复制粘贴",
    "Third-party video upload": "上传到第三方",
    "Ads and redirect pages": "广告与跳转页",
    "Use the extension only for content you own, are authorized to save, or are otherwise legally permitted to use.":
        "只对你拥有的、已获授权保存的，或依法允许你使用的内容使用本扩展。",
    "Public content only": "仅限公开内容",
    "No support for private accounts, paywalls, subscriptions, DRM, geographic restrictions, or authentication bypass.":
        "不支持私密账号、付费墙、订阅、DRM、地域限制，也不绕过身份验证。",
    "The video file is downloaded from X's video host to your browser. We do not proxy or store it.":
        "视频文件从 X 的视频服务器下载到你的浏览器。我们既不代理也不存储它。",
    "No credential collection": "不收集任何凭据",
    "The extension does not ask for or collect your X password.": "扩展不会索取也不会收集你的 X 密码。",
    "Accurate quality claim": "关于画质的准确表述",
    "\u201cHighest quality\u201d means the highest-bitrate direct MP4 X currently provides, not the creator's pre-upload source file.":
        "「最高画质」指 X 当前提供的最高码率直连 MP4，不是作者上传前的源文件。",
    "This review build intentionally avoids claiming features or payment availability that have not completed external approval.":
        "本审核版本刻意不宣称任何尚未通过外部审核的功能或支付能力。",
    "Does \u201chighest quality\u201d mean the original uploaded file?": "「最高画质」是指上传时的原始文件吗？",
    "No. It means the highest-bitrate direct MP4 X currently makes available for that public post. The extension cannot restore a creator's pre-upload source file.":
        "不是。它指 X 当前为那条公开帖子提供的最高码率直连 MP4。扩展无法还原作者上传前的源文件。",
    "Does the extension transcode or compress the video?": "扩展会转码或压缩视频吗？",
    "No. It selects a direct MP4 and downloads it without transcoding, recompressing, or rewrapping the file.":
        "不会。它选出一个直连 MP4 并原样下载，不转码、不重新压缩、不重新封装。",
    "Can it download private or restricted videos?": "它能下载私密或受限的视频吗？",
    "No. It does not bypass private accounts, paywalls, DRM, login restrictions, geographic restrictions, or other access controls.":
        "不能。它不绕过私密账号、付费墙、DRM、登录限制、地域限制或任何其它访问控制。",
    "Is payment available now?": "现在可以付费了吗？",
    "Not yet. The planned offer is unlimited free screenshots, 5 free video or GIF downloads, then $5.99 for lifetime access — $3.99 during the first month after launch. Checkout opens only after payment-provider compliance review and full purchase-flow testing.":
        "还不行。计划的方案是：截图无限免费，视频或 GIF 下载免费 5 次，之后 $5.99 获得永久使用权，上线首月为 $3.99。结算只会在支付服务商合规审核通过、且购买全流程测试完成之后开放。",
    "Is it already in the Chrome Web Store?": "它已经上架 Chrome 应用商店了吗？",
    "Not yet. The extension is in local product testing while the website, policies, payment review, and store materials are completed.":
        "还没有。扩展正在本地进行产品测试，同时完善网站、政策、支付审核与商店素材。",
    "Screenshotting a post stays free forever — no quota, no account. Video and GIF downloads come with 5 free saves, then one payment for lifetime access. No subscription, no credits, no artificial quality limits, no recurring billing. A launch price of $3.99 is planned for the first month.":
        "截图永久免费，不限次数、不需要账号。视频与 GIF 下载提供 5 次免费保存，之后一次付费获得永久使用权。无订阅、无积分、无人为画质限制、无重复扣款。上线首月计划采用 $3.99 的首发价。",
},
"privacy.html": {
    "Privacy Policy — Save for X": "隐私政策 — Save for X",
    "Privacy Policy": "隐私政策",
    "Last updated August 9, 2026": "最后更新：2026 年 8 月 9 日",
    "Save for X performs its narrow saving function without a developer-operated server, analytics tracker, advertising system, or user account. Videos, GIFs and screenshots are all handled on your own device.":
        "Save for X 只做保存这一件事，没有开发者运营的服务器、分析跟踪、广告系统或用户账号。视频、GIF 与截图全部在你自己的设备上处理。",
    "Data processed": "处理的数据",
    "Storage and sharing": "存储与分享",
    "Permissions": "权限",
    "Your control": "你的控制权",
    "Permission purposes": "各项权限的用途",
    "When you browse x.com or twitter.com, the extension examines the public post structure currently displayed by X to determine whether a post contains an eligible public video or GIF, and to place its buttons. It processes public post links and post IDs for this purpose. It does not read direct messages, typed input, or browsing history.":
        "当你浏览 x.com 或 twitter.com 时，扩展会检查 X 当前展示的公开帖子结构，判断帖子里是否有可保存的公开视频或 GIF，并据此放置按钮。为此它会处理公开帖子的链接与帖子 ID。它不读取私信、你输入的内容或浏览历史。",
    "To confirm that a post contains downloadable media and to choose the highest-bitrate version, the extension sends the public post ID to X's public embed endpoint at":
        "为确认帖子里确实有可下载的媒体、并挑出最高码率的版本，扩展会把公开帖子 ID 发送到 X 的公开嵌入接口",
    ". Video files are downloaded directly from": "。视频文件直接从",
    "to your browser.": "下载到你的浏览器。",
    "GIF conversion.": "GIF 转换。",
    "X serves GIFs as MP4. When you ask for a GIF, the extension reads that MP4 source from X and converts it to a real":
        "X 上的 GIF 实际是以 MP4 提供的。当你要 GIF 时，扩展会从 X 读取那个 MP4 源，并把它转换成真正的",
    "entirely inside your browser, using an invisible local extension page. Nothing is uploaded for conversion.":
        "，整个过程在你的浏览器内、通过一个不可见的本地扩展页面完成。转换不上传任何内容。",
    "Screenshots.": "截图。",
    "When you click a post's screenshot button, the extension calls Chrome's":
        "当你点击某条帖子的截图按钮时，扩展会调用 Chrome 的",
    ", which returns an image of the visible area of the current tab. The extension immediately crops that image locally to the post you clicked, produces a PNG and writes it to your clipboard. The image is processed entirely on your device, is never sent to the developer or any third party, and is not retained by the extension.":
        "，它返回当前标签页可见区域的图像。扩展随即在本地把图像裁剪为你点击的那条帖子，生成 PNG 并写入剪贴板。图像全程在你的设备上处理，不会发送给开发者或任何第三方，扩展也不保留它。",
    "The extension developer does not collect, store, sell, or share your personal data, browsing history, downloaded videos, X credentials, or public post IDs. The current product has no developer-operated analytics, advertising, account, or video-processing backend.":
        "扩展开发者不收集、不存储、不出售、不分享你的个人数据、浏览历史、已下载的视频、X 账号凭据或公开帖子 ID。当前产品没有开发者运营的分析、广告、账号或视频处理后端。",
    "Public post IDs are sent only to X for the requested media lookup. Video data is not sent to the extension developer.":
        "公开帖子 ID 仅发送给 X，用于你请求的媒体查询。视频数据不会发送给扩展开发者。",
    "x.com and twitter.com site access:": "x.com 与 twitter.com 站点访问：",
    "identify eligible public posts and place the download and screenshot buttons. No logic runs on any other site.":
        "识别符合条件的公开帖子，并放置下载与截图按钮。在其它任何网站上都不执行逻辑。",
    "activeTab:": "activeTab：",
    "read the current public X post URL when the extension popup is opened.":
        "在你打开扩展弹窗时读取当前公开 X 帖子的网址。",
    "downloads:": "downloads：",
    "save the selected direct MP4, or the locally generated GIF, to Chrome's download directory.":
        "把选定的直连 MP4，或本地生成的 GIF，保存到 Chrome 的下载目录。",
    "offscreen:": "offscreen：",
    "create an invisible local extension page that decodes the video and encodes the GIF on your device. It shows no interface and uploads nothing.":
        "创建一个不可见的本地扩展页面，在你的设备上解码视频、编码 GIF。它不显示任何界面，也不上传任何内容。",
    "clipboardWrite:": "clipboardWrite：",
    "write the screenshot you asked for to the clipboard. The extension never reads clipboard contents.":
        "把你请求的截图写入剪贴板。扩展从不读取剪贴板内容。",
    "cdn.syndication.twimg.com:": "cdn.syndication.twimg.com：",
    "retrieve X's public media-version list for a public post ID.":
        "按公开帖子 ID 获取 X 的公开媒体版本清单。",
    "video.twimg.com:": "video.twimg.com：",
    "download the video itself, or read the MP4 source for a GIF you asked to convert.":
        "下载视频本身，或读取你请求转换的 GIF 所对应的 MP4 源。",
    "Optional permission: access to all sites": "可选权限：访问所有网站",
    "Screenshots rely on Chrome's": "截图依赖 Chrome 的",
    ", which technically requires either broad host access or": "，该接口在技术上要求广泛的主机访问权限，或者",
    ". A click on a button inside the page does not count as invoking the extension, so": "。而点击页面内的按钮不算「调用扩展」，因此",
    "is never granted that way.": "永远不会通过这种方式被授予。",
    "Broad host access is therefore declared as an": "所以广泛主机访问被声明为",
    "optional": "可选",
    "permission. It is not requested at install time, and downloads work fully without it. The first time you want a screenshot, you enable it yourself from the extension popup and Chrome shows its own confirmation. Once granted it is used only when you click a screenshot button, and the extension still runs only on x.com and twitter.com.":
        "权限。安装时不会申请，没有它下载功能也完全可用。第一次需要截图时，你自己在扩展弹窗里开启，Chrome 会弹出它自己的确认框。授予之后也只在你点击截图按钮时使用，扩展依然只在 x.com 与 twitter.com 上运行。",
    "You can disable or remove the extension through Chrome at any time. Removing the extension stops all extension processing. Files you already downloaded remain under your control in your own download directory.":
        "你可以随时通过 Chrome 停用或移除扩展。移除后扩展的一切处理都会停止。已经下载的文件仍在你自己的下载目录里，由你掌控。",
    "This review website does not collect launch-list emails or payment information. Those workflows will receive an updated privacy disclosure before public launch.":
        "本审核版网站不收集上线通知邮箱或支付信息。相关流程会在正式上线前提供更新后的隐私说明。",
},
"terms.html": {
    "Terms of Use — Save for X": "使用条款 — Save for X",
    "Terms of Use": "使用条款",
    "Last updated June 10, 2026": "最后更新：2026 年 6 月 10 日",
    "These terms define the rights-first, public-content-only boundary of Save for X and the responsibilities of anyone who uses it.":
        "本条款界定 Save for X「权利优先、仅限公开内容」的边界，以及使用者应承担的责任。",
    "Allowed use": "允许的用途",
    "Prohibited use": "禁止的用途",
    "Quality claim": "画质表述",
    "Availability": "可用性",
    "Accurate quality claim": "关于画质的准确表述",
    "Availability and changes": "可用性与变更",
    "You may use the product only to save public content that you own, content for which you have the necessary rights or permission, or content that you are otherwise legally permitted to save and use.":
        "你只能用本产品保存以下内容：你自己拥有的公开内容、你已取得必要权利或授权的内容，或依法允许你保存和使用的内容。",
    "You are responsible for complying with applicable law, copyright rules, contracts, and platform terms.":
        "遵守适用法律、著作权规定、合同以及平台条款，是你自己的责任。",
    "You may not use the product to infringe copyright, redistribute unauthorized media, evade platform restrictions, or facilitate piracy. The product must not be used to bypass private accounts, authentication, subscriptions, paywalls, DRM, geographic restrictions, or any other access control.":
        "不得使用本产品侵犯著作权、传播未经授权的媒体、规避平台限制或协助盗版。不得用本产品绕过私密账号、身份验证、订阅、付费墙、DRM、地域限制或任何其它访问控制。",
    "Bulk account scraping and automated redistribution are outside the product's intended use.":
        "批量抓取账号内容与自动化二次分发，不在本产品的设计用途之内。",
    "\u201cHighest quality\u201d means the highest-bitrate direct MP4 X currently provides for the eligible public post. It does not mean the creator's pre-upload source file, a restored uncompressed master, or a guarantee that X will continue to provide the same version.":
        "「最高画质」指 X 当前为该条公开帖子提供的最高码率直连 MP4。它不等于作者上传前的源文件，不是还原出的无压缩母版，也不保证 X 会一直提供同一个版本。",
    "X may change its public interfaces, page structure, media formats, or availability at any time. The product may require maintenance or temporarily stop working as a result. Features, pricing, and support terms may be updated before public launch.":
        "X 可能随时更改其公开接口、页面结构、媒体格式或可用性，本产品可能因此需要维护或暂时失效。功能、价格与支持条款在正式上线前均可能调整。",
    "The current website is a review build. Payment and Chrome Web Store installation are not yet publicly available.":
        "当前网站为审核版本。支付与 Chrome 应用商店安装尚未对外开放。",
},
"refunds.html": {
    "Refund Policy — Save for X": "退款政策 — Save for X",
    "Refund Policy": "退款政策",
    "Planned public-launch policy": "计划中的上线政策",
    "This page documents the planned refund treatment for the one-time lifetime-access product before live checkout is enabled.":
        "本页记录在正式开放结算之前，针对「一次性付费、永久使用」这一形态所计划的退款处理方式。",
    "Current status": "当前状态",
    "Eligibility": "适用条件",
    "Refund effects": "退款的效果",
    "How to request": "如何申请",
    "Current payment status": "当前的支付状态",
    "Planned refund eligibility": "计划中的退款适用条件",
    "Effect of a refund": "退款的效果",
    "Request process": "申请流程",
    "No payment is collected on this review website. Live checkout opens only after payment-provider compliance approval, entitlement testing, and publication of a verified support channel.":
        "本审核版网站不收取任何款项。正式结算只会在支付服务商合规审核通过、权益发放测试完成、且公开可验证的支持渠道发布之后才开放。",
    "After launch, refund requests will be reviewed according to applicable consumer law and the live checkout terms. A refund may be appropriate when payment was duplicated, access was not delivered, or the product materially failed to perform its stated function and support could not resolve the issue.":
        "上线后，退款申请将依据适用的消费者法律与正式结算条款处理。出现重复扣款、权益未发放，或产品在实质上无法完成其声明的功能且支持无法解决时，退款是合理的。",
    "Requests involving prohibited use, access-control bypass expectations, or claims that the product should restore a creator's pre-upload source file will not change the product's stated boundary.":
        "涉及禁止用途、期望绕过访问控制，或主张产品应当还原作者上传前源文件的申请，不会改变产品既定的边界。",
    "A successful refund will revoke the related lifetime entitlement or license access. Downloaded files remain subject to the user's own legal rights and responsibilities.":
        "退款成功后，相应的永久权益或许可将被撤销。已下载的文件仍受使用者自身的法律权利与责任约束。",
    "The verified public support channel and required purchase information will be published before checkout opens. We will not ask customers to send passwords or payment-card details by email.":
        "可验证的公开支持渠道，以及申请所需的购买信息，会在结算开放前公布。我们不会要求用户通过邮件发送密码或银行卡信息。",
    "This policy will be finalized together with the live Merchant of Record terms before accepting payment.":
        "本政策将与正式的 Merchant of Record 条款一并定稿，然后才开始收款。",
},
"copyright.html": {
    "Copyright & Takedown — Save for X": "版权与下架 — Save for X",
    "Copyright & Takedown": "版权与下架",
    "Rights-first product policy": "权利优先的产品政策",
    "Save for X is intended for authorized saving of eligible public videos and does not host, proxy, index, or redistribute video files.":
        "Save for X 用于在获得授权的前提下保存符合条件的公开视频，不托管、不代理、不索引、不二次分发任何视频文件。",
    "Principle": "原则",
    "What we host": "我们托管什么",
    "Takedown notice": "下架通知",
    "Response": "处理方式",
    "Rights-first principle": "权利优先原则",
    "What the product does not host": "本产品不托管的内容",
    "Copyright and takedown notices": "版权与下架通知",
    "Response process": "处理流程",
    "Users must have the necessary copyright, license, permission, or legal basis before saving or using a public video. The product must not be used to facilitate infringement or unauthorized redistribution.":
        "在保存或使用公开视频之前，用户必须具备必要的著作权、许可、授权或法律依据。不得使用本产品协助侵权或未经授权的二次分发。",
    "The extension developer does not operate a video-download proxy, content library, search index, or file-storage service. Direct MP4 files travel from X's video host to the user's browser download directory.":
        "扩展开发者不运营视频下载代理、内容库、搜索索引或文件存储服务。直连 MP4 文件从 X 的视频服务器直接传输到用户浏览器的下载目录。",
    "A verified complaint channel will be published before public launch. A valid notice should identify the copyrighted work, the relevant public X post, the complainant's authority, the requested action, and a good-faith statement that the disputed use is not authorized.":
        "可验证的投诉渠道会在正式上线前公布。一份有效的通知应当写明：涉及的受著作权保护作品、相关的公开 X 帖子、投诉人的权利依据、请求采取的措施，以及关于争议使用未获授权的善意声明。",
    "Do not include account passwords, payment-card data, or unrelated private information in a notice.":
        "通知中请勿包含账号密码、银行卡信息或无关的私人信息。",
    "We will review credible notices, preserve relevant product evidence, and take proportionate action available to a browser-extension developer. Depending on the issue, action may include clarifying product language, restricting a known misuse pattern, suspending an entitlement, or cooperating with the relevant platform or payment provider.":
        "我们会审查可信的通知、保存相关的产品证据，并在浏览器扩展开发者力所能及的范围内采取相称的措施。视具体问题，措施可能包括澄清产品表述、限制已知的滥用方式、暂停某项权益，或配合相关平台与支付服务商。",
    "Because the product does not host the source video, removal of the original public post must be addressed to the platform hosting that post.":
        "由于本产品并不托管源视频，删除原始公开帖子需要向托管该帖子的平台提出。",
},
"support.html": {
    "Support & Launch Status — Save for X": "支持与上线状态 — Save for X",
    "Support & Launch Status": "支持与上线状态",
    "Review build · Not publicly launched": "审核版本 · 尚未公开上线",
    "The core extension is in local product testing. This website is being completed for payment-provider compliance review and Chrome Web Store preparation.":
        "核心扩展正在本地进行产品测试。本网站正在完善，用于支付服务商的合规审核与 Chrome 应用商店的上架准备。",
    "Current status": "当前状态",
    "Verified": "已验证",
    "Remaining gates": "尚待完成",
    "Contact": "联系方式",
    "What has been verified": "已经验证的内容",
    "Remaining launch gates": "上线前尚待完成的闸门",
    "Contact status": "联系方式的状态",
    "The extension identifies eligible public X posts, places its buttons inside X's own icon row, downloads the highest-bitrate direct MP4 without transcoding, converts GIF posts into real .gif files locally, and captures a whole post as a PNG.":
        "扩展能够识别符合条件的公开 X 帖子，把按钮放进 X 自己的图标行，下载最高码率的直连 MP4 且不转码，在本地把 GIF 帖转换成真正的 .gif 文件，并把整条帖子截取为 PNG。",
    "Screenshots and GIF conversion run entirely on the user's device. Live payment, launch-list collection and Chrome Web Store installation are not enabled yet.":
        "截图与 GIF 转换完全在用户设备上运行。正式支付、上线通知收集与 Chrome 应用商店安装尚未开放。",
    "74 automated tests and syntax validation pass.": "74 项自动化测试与语法校验全部通过。",
    "Buttons appear on real timelines, post pages, list timelines and search results.":
        "按钮在真实的时间线、帖子详情页、列表时间线与搜索结果中均正常出现。",
    "Downloads match an independently obtained highest-quality sample byte-for-byte.":
        "下载结果与独立获取的最高画质样本逐字节一致。",
    "Interface renders correctly in 25 languages, including right-to-left layouts.":
        "界面在 25 种语言下渲染正常，包含从右向左的排版。",
    "Promoted posts get no buttons. Posts the public endpoint cannot read show a disabled button explaining why.":
        "推广帖不显示任何按钮。公开接口读不到的帖子会显示禁用状态的按钮并说明原因。",
    "Publish this website on a verified HTTPS address.": "把本网站发布到可验证的 HTTPS 地址。",
    "Publish a verified support email and complaint channel.": "公布可验证的支持邮箱与投诉渠道。",
    "Complete Dodo Payments compliance review and account verification.":
        "完成 Dodo Payments 的合规审核与账户验证。",
    "Implement and test checkout, entitlement activation, restoration, and refund revocation.":
        "实现并测试结算、权益激活、恢复购买与退款撤销。",
    "Complete Chrome Web Store review.": "完成 Chrome 应用商店审核。",
    "A verified public support address will be published before compliance submission and before any customer payment is accepted. This review build does not invent or expose an unverified support address.":
        "可验证的公开支持邮箱会在提交合规审核之前、以及接受任何用户付款之前公布。本审核版本不会编造或展示未经验证的支持邮箱。",
    "Payments open after compliance review. No payment, account credential, or launch-list email is collected on this website.":
        "支付将在合规审核通过后开放。本网站不收取任何款项，也不收集账号凭据或上线通知邮箱。",
},
}

GOVERNING = ("英文版为本政策的正式版本。中文翻译仅供理解方便，"
             "两者如有出入，以英文版为准。")

LEGAL = {"privacy.html", "terms.html", "refunds.html", "copyright.html"}


def switcher(to_zh: bool) -> str:
    """语言切换链接。英文页指向 zh/，中文页指回上一层。"""
    href = "zh/index.html" if to_zh else "../index.html"
    label = "中文" if to_zh else "English"
    lang = "zh-Hans" if to_zh else "en"
    return f'<a class="lang-switch" href="{href}" hreflang="{lang}">{label}</a>'


def translate_text_nodes(html: str, table: dict) -> str:
    """只替换标签之间的文本，不碰标签和属性。

    早先按 `>文本<` 整体匹配，结果 `<h1>Keep every <span>last pixel.</span></h1>`
    这种嵌套、以及 `&amp;` 实体全都漏掉了。按文本节点逐段查表才可靠。
    """
    # 先把 script/style 挖出来，避免误伤
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f"\x00{len(holes) - 1}\x00"

    html = re.sub(r"<(script|style)\b.*?</\1>", stash, html, flags=re.S)

    def sub_text(m):
        raw = m.group(1)
        key = raw.strip().replace("&amp;", "&")
        if not key or key not in table:
            return m.group(0)
        lead = raw[: len(raw) - len(raw.lstrip())]
        tail = raw[len(raw.rstrip()) :]
        return f">{lead}{table[key]}{tail}<"

    html = re.sub(r">([^<>]+)<", sub_text, html)

    # 会显示给用户的属性
    def sub_attr(m):
        name, val = m.group(1), m.group(2)
        key = val.strip().replace("&amp;", "&")
        return f'{name}="{table[key]}"' if key in table else m.group(0)

    html = re.sub(r'\b(content|title|aria-label|alt|placeholder)="([^"]*)"', sub_attr, html)

    for i, chunk in enumerate(holes):
        html = html.replace(f"\x00{i}\x00", chunk)
    return html


def convert(name: str, html: str) -> str:
    table = {**SHARED, **PAGES.get(name, {})}
    html = translate_text_nodes(html, table)
    html = html.replace('<html lang="en">', '<html lang="zh-Hans">')
    # 资源路径指向上一层
    html = re.sub(r'(href|src)="(assets/[^"]+)"', r'\1="../\2"', html)
    # 语言切换：英文页里那颗按钮换成回到英文的
    html = html.replace(switcher(True), switcher(False))
    if name in LEGAL:
        html = html.replace("</article>", f'<p class="governing">{GOVERNING}</p></article>', 1)
    return html


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    out = root / "zh"
    out.mkdir(exist_ok=True)
    for src in sorted(root.glob("*.html")):
        (out / src.name).write_text(convert(src.name, src.read_text()))
        print(f"zh/{src.name}")


if __name__ == "__main__":
    main()
