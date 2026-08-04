# 全仓库维护计划

## Goal

在不改变 Portfolio 页面行为、Mundus 事实合同、媒体证据和发布边界的前提下，降低验证层的混合职责与重复路径逻辑。

## Architecture

- 测试按合同域组织，而不是集中在单一聚合文件。
- claim semantics 解析由独立模块拥有，facts verifier 负责规则与 revision 编排。
- Pages base-path 规范化由单一前端工具拥有，各 Astro owner 只消费结果。

## Tech Stack

- Astro 7
- Python 3.9 `unittest`
- TypeScript
- Node.js 22

## Baseline / Authority Refs

- 当前分支：`feat/mundus-next`
- 当前基线：`e0fc643836065cadf61713aae5eff8f4c90534f0`
- Task 1 RED 合同：现有 62 项 Python tests
- Mundus authority：`378fe528ca1c8f83f0280f83383b5e785e851285`
- 发布边界：Draft PR only；不 merge、不 deploy

## Compatibility Boundary

- 保持 `scripts.verification.facts` 的现有可导入符号。
- 保持所有测试类、测试方法和断言语义。
- 保持 Astro 生成的 Pages base-path URL。
- 不修改媒体、browser evidence、facts catalog 或产品文案。

## First-Principles Review

- First Principle：维护应减少混合职责和重复 owner，同时保持所有可观察行为。
- Non-negotiables：Task 1 合同、Mundus/Chronorbis 边界、immutable evidence、Draft PR 非部署边界不能变化。
- Assumptions to Drop：大文件不必一次性全部拆；生成证据和锁文件不属于维护型源码。
- Smallest Sufficient Path：只拆测试聚合、claim semantics owner 和重复 base-path owner。
- Escalation Signal：任何 snapshot、HTML、事实验证或 browser evidence 改变都停止并回退该项拆分。

## Architecture Integrity Lens

- Invariant：每类行为只有一个 canonical owner，原导入和页面输出保持兼容。
- Canonical owner / contract：测试文件按合同域；`claim_semantics.py` 负责静态语义；路径工具负责 Pages base。
- Responsibility overlap：当前 `facts.py` 同时承担 parser 与 verifier；多个 Astro 文件重复规范化 base path。
- Higher-level simplification：提取 owner，不增加 fallback、adapter 或第二套实现。
- Retirement / falsifier：旧聚合测试文件和内联 parser/base helper 必须删除；全量 gate 或输出差异会否决拆分。
- Verdict：proceed。

## Plan Pressure Test

- Owner / contract / retirement：owner 清晰，旧内联实现直接退休。
- Architecture integrity / higher-level path：通过共享 owner 解决，不在调用方增加分支。
- Verification scope：unit tests、build、release verifier、diff check。
- Task executability：均为机械迁移或保持 API 的模块提取。
- Pressure result：proceed。

## Plan-Time Complexity Check

- Target files：`tests/test_release_verification.py`、`scripts/verification/facts.py`、重复 base-path 的 Astro 文件。
- Existing size / shape signals：1688 行测试聚合；542 行 parser/verifier 混合模块；6 处 base-path 规范化。
- Owner fit：测试类天然形成四个域；claim parser 与 verifier 可单向依赖；路径工具无状态。
- Add-in-place risk：继续扩展会加重聚合文件和重复实现。
- Better file boundary：按域拆 test module；新增 claim semantics owner；新增 path owner。
- Recommendation：split task。

## Tasks

### Task 1：按合同域拆分 release verification tests

**Files**

- Delete: `tests/test_release_verification.py`
- Create: `tests/test_mundus_case_study.py`
- Create: `tests/test_structured_facts.py`
- Create: `tests/test_browser_evidence.py`
- Create: `tests/test_privacy_scan.py`

**Why**

四个独立测试域不应共享一个 1688 行文件。

**Impact / Compatibility**

只迁移 imports、测试类和 `unittest.main()`；测试名称与断言保持不变。

**Verification**

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

- [ ] 记录拆分前 62/62 GREEN。
- [ ] 按类边界机械迁移代码。
- [ ] 删除聚合文件，确认没有测试丢失。
- [ ] 运行 62/62 GREEN。
- [ ] 检查 diff 仅包含文件重组。

### Task 2：提取 claim semantics owner

**Files**

- Create: `scripts/verification/claim_semantics.py`
- Modify: `scripts/verification/facts.py`

**Why**

Astro/MDX 静态语义解析与事实 catalog/revision 验证是不同职责。

**Impact / Compatibility**

`facts.py` 继续导出 `extract_mdx_visible_text`、`extract_astro_rendered_semantics`、`extract_claim_semantics` 和 `_AstroLiteralParser`。

**Verification**

```bash
python3 -m unittest tests.test_structured_facts tests.test_mundus_case_study -v
```

- [ ] 以现有 parser tests 作为 characterization baseline。
- [ ] 迁移 parser 与 extractor，不改变实现。
- [ ] 从 `facts.py` 显式兼容导入原符号。
- [ ] 运行 focused GREEN。
- [ ] 搜索确认旧 parser 实现没有残留。

### Task 3：统一 Astro Pages base-path owner

**Files**

- Create: `src/utils/paths.ts`
- Modify: `src/components/BaseLayout.astro`
- Modify: `src/components/MundusStory.astro`
- Modify: `src/components/ProjectMedia.astro`
- Modify: `src/components/SideBGallery.astro`
- Modify: `src/content/projects/dialogtree.mdx`
- Modify: `src/pages/index.astro`
- Modify: `src/pages/projects/[...slug].astro`

**Why**

同一 base-path 规范化逻辑存在七份 owner。

**Impact / Compatibility**

保留局部变量名 `base` 和 `asset`，只把实现指向共享工具，避免改变模板与 Task 1 文本合同。

**Verification**

```bash
npm test
npm run build
```

- [ ] 以当前 build 和 URL tests 作为 characterization baseline。
- [ ] 新增无状态路径工具。
- [ ] 替换重复声明并保留局部变量名。
- [ ] 运行 tests/build GREEN。
- [ ] 搜索确认 base 规范化只剩单一 owner。

### Task 4：完整 gate 与复杂度审计

**Files**

- No product files.

**Why**

证明拆分没有改变行为、证据或发布边界。

**Verification**

```bash
npm audit --audit-level=high
npm test
npm run build
npm run verify -- --mundus-root "/Users/bytedance/Desktop/Zen/Mundus"
git diff --check
git status --short
```

- [ ] 运行 security gate。
- [ ] 运行 62 项 tests。
- [ ] 构建六个页面。
- [ ] 运行 facts/browser/privacy release verifier。
- [ ] 复核文件尺寸、重复 owner、diff 与工作树状态。

## Repair Track

- Root cause：验证合同按历史任务累积在单文件中；静态语义 parser 与 facts 编排共置；base path 被各调用方重复拥有。
- Canonical owner：合同域 test modules、claim semantics module、path utility。
- Minimal sufficient stable repair：机械拆分和直接导入，不重写算法。
- Compatibility boundary：原测试、原 facts API、原页面 URL。
- Verification：完整本地 gate。

## Retirement Track

- Old owner：`test_release_verification.py`、`facts.py` 内联 parser、Astro 内联 base normalization。
- Active status：本次拆分后不再保留。
- Keep reason：无。
- Deletion trigger：新 owner 接管且完整 gate 通过时立即删除。

## Risks

- 文本合同可能依赖实现符号位置；通过 `facts.py` 兼容导出和保留 Astro 局部变量名规避。
- 机械拆分可能遗漏测试；通过测试总数和完整 discovery 校验。
- Astro utility 可能影响 Vite 环境值；通过六页 build 和 release verifier 校验。

## Non-Goals

- 不重写 browser/facts regex。
- 不拆媒体 capture 事务。
- 不调整 UI、文案、图片或 evidence。
- 不增加 lint/format 依赖。
- 不提交、推送、合并或部署。

## Execution Outcome

- Task 1 completed：测试按四个合同域拆分，测试数量保持 62。
- Task 2 completed：claim semantics owner 已提取，`facts.py` 保持兼容导出。
- Task 3 reverted：共享前端路径工具改变了 Astro 构建产物字节，触发
  `browser-build.json` digest mismatch。按 falsifier 撤销全部前端改动，
  未刷新 evidence 掩盖差异；重复 base-path owner 作为有证据约束的保留项。
- Additional hygiene：`.gitignore` 增加 Python cache 规则，并删除本次生成的
  `__pycache__` 派生目录。
