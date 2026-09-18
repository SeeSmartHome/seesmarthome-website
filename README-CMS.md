# SeeSmartHome — 项目管理后台版（配置前不能在线使用）

## 已做好
- 基于 V8 保留了荷兰语、English、中文、项目视频及 Netlify 询价表单。
- 旧的6组项目已搬到 `content/projects.json`，首页精选、项目列表和独立项目详情由 `build_site.py` 自动生成。
- 后台字段：项目标题/类别/介绍（三语言）、显示/隐藏、首页精选、排序、封面、图库及图库顺序、合作署名。
- `content/site-media.json` 负责首页首屏照片、项目视频和视频封面。
- 上传的照片保存在 `assets/uploads/`，原有照片及标识不被移除或修改。
- 网站预览保持 noindex，正式上线前请处理法律信息、隐私说明、图片权利与表单真实提交测试。

## 重要：目前并非已经能登录的后台
`/admin/` 使用 Decap CMS；它必须读取、写入 GitHub 仓库，并使用 OAuth 登录。
已将 `admin/config.yml` 设置为 `SeeSmartHome/seesmarthome-website`，仍需在 Netlify 配置 GitHub OAuth 和连接现有项目。
不要把 GitHub OAuth Client Secret 放进代码或聊天中。

## 启用步骤（推荐先在现有 Netlify 测试站完成）
1. 你已提供 GitHub 仓库地址 `https://github.com/SeeSmartHome/seesmarthome-website.git`。将本 ZIP **解压后，把文件夹内部的全部源代码**上传到仓库根目录（包含 `build_site.py`、`content/`、`admin/`、`netlify.toml`、`assets/` 等），不要把 ZIP 本身上传为一个文件，也不要只上传 `dist`。建议确保仓库为 Private，默认分支为 main。
2. 本包 `admin/config.yml` 的 `backend.repo` 已设置为 `SeeSmartHome/seesmarthome-website`。请核对仓库默认分支为 `main`。
3. 在现有 Netlify 项目设置中，进入 Project configuration → Developer settings → Continuous deployment → Repository → Link repository，选上面的私有 GitHub 仓库；连接**现有站点**以保留原测试域名。Netlify 使用 `netlify.toml` 自动执行 `python3 build_site.py` 并发布 `dist`。
4. GitHub Settings → Developer settings → OAuth Apps → New OAuth App，应用主页 URL 为 `https://thunderous-cranachan-51cd11.netlify.app`，Authorization callback URL 为 `https://api.netlify.com/auth/done`。如该仓库属于 GitHub Organization，管理员需确认相关第三方访问策略。
5. 在 Netlify 现有项目设置 Project configuration → Security → OAuth → Install provider → GitHub（具体标签可能因界面版本而异），安全地填写 Client ID 与 Client Secret（只在其设置页填写）。
6. 等 Netlify 从 GitHub 首次部署成功后，打开 `https://thunderous-cranachan-51cd11.netlify.app/admin/`，以具有该仓库写入权限的 GitHub 账户登录。
7. 项目管理 → 修改某个项目的封面/上传新照片/调整顺序/三语言文案 → 保存；Netlify 从 GitHub 自动重新构建。新照片首次被提交并构建完成后才会在网站上出现。
8. 在 Netlify Forms 中核实识别到 `seesmarthome-inquiries`，配置通知 `info@seesmarthome.nl`，完成测试提交。

## 日常操作
- `发布到网站` 关：项目仍保存在 CMS 内容中，但不会出现在项目列表和独立项目页。
- `在首页展示` 开：仅已发布项目有效，首页取按首页排序的前三个。
- URL代号一旦发布请勿随意改变：否则旧链接失效。
- 封面可独立于图库；图片上传请使用有商业展示授权的高清原图。
- 视频上传到 GitHub 应控制大小，建议压缩到适合网页播放后再上传。
- 修改后等 Netlify 新的构建状态为 Published 再刷新网站；不可再通过 Netlify Drop 手工上传老 ZIP 覆盖自动部署成果。

## 本地预览和验证（需要 Python 3，无第三方依赖）
`python3 build_site.py`
然后使用 `python3 -m http.server 8000 --directory dist`，在浏览器访问 `http://localhost:8000`。
`dist` 是生成结果，默认不提交 GitHub。直接打开 source 根目录的 index.html 只会展示旧静态内容；看最终版应从 dist 预览。

## 关于目前原有水印图片
旧站 V8 的部分项目照片包含平台标识。已保持原图；网站仍为仅供审阅的 noindex 版本。如果准备对外推广，先用你有授权的无水印原图在后台逐张替换，或设置该项目为不发布。
