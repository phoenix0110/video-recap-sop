---
name: video-recap-sop
description: 标准操作流程，引导大模型按 Step 0–4 执行 B 站二创视频制作。在用户开始二创任务、讨论流程或要求"按 SOP 来做"时启用。这是 orchestrator skill，本身不写脚本也不剪视频，只负责协调 bilibili-competitor-radar、gameshow-recap-creator、video-use 三个 sub-skill，并强制遵守项目目录规范。
---

# 二创视频 Workflow SOP

> 适用于 Game Show / Reality Show 的 B 站二创视频制作
> 最后更新：2026-07-22

---

## 0. 文档用途

这是大模型执行二创视频任务的 **Standard Operating Procedure**。每次开始一个新的二创任务前，先通读这份文档，然后按步骤执行。

**不要把它当成 README。** 它的目的是告诉我"一步一步怎么走"，而不是告诉我"系统长什么样"。

**它是 orchestrator skill。** 本身不产出任何视频 / 脚本 / 报告，只负责：
1. 协调三个 sub-skill 的调用顺序
2. 强制遵守项目目录规范
3. 在每一步记录状态到项目 README.md

---

## 1. 三个 Skill 总览

| # | Skill | 角色 | 是否必经 |
|---|---|---|---|
| 1 | `bilibili-competitor-radar` | 选题 / 竞品 / 热度调研 | ❌ **辅助前置**，已有清晰选题时跳过 |
| 2 | `gameshow-recap-creator` | 写解说脚本 | ✅ **必经** |
| 3 | `video-use` | 视频剪辑合成 | ✅ **必经** |

**何时启用 Skill 1？**
- 用户说"我想做个新题材的二创，你帮我调研一下" → 启用
- 用户直接说"做 The Traitors S01E01" → 跳过（已有清晰选题）

**何时跳过 Skill 1？**
- 用户已经指定了具体节目 / 集数（如"S01E01"）
- 用户之前已经做过同类题材的竞品调研

---

## 2. 二创项目目录规范

每次开始一个二创任务，必须按以下结构创建项目目录：

```
outputs/
└── projects/
    └── <二创视频名称>/                  # 根目录，以本次视频命名
        ├── final.mp4                   # ⭐ 根目录：Video Use 产出的最终成片
        ├── README.md                   # 项目记录（流水线回放 + 状态 + 包装清单）
        ├── gameshow-recap-creator/     # Skill 2 输出（脚本）
        │   ├── pre-analysis.md         # 第一层：角色 / 目标 / 主线 / 爆点
        │   └── recap-script.md         # 第二层：解说脚本（旁白 + 画面 + 花字）
        └── video-use/                  # Skill 3 工作目录
            ├── transcripts/            # ASR 转写 JSON（可选）
            └── edit/                   # 编辑过程产物
                ├── project.md          # 项目记忆
                ├── takes_packed.md     # 短语级转写
                ├── edl.json            # 剪辑决策
                ├── master.srt          # 输出时间线字幕
                ├── preview.mp4         # 自检预览
                └── final.mp4           # ← 完成后复制到根目录
```

### 命名规范

- 根目录：用视频名，**英文 / 拼音 + 横线**，避免空格和中文路径
- 示例：`The-Traitors-UK-S01E01`、`Survivor-S47E01`、`Squid-Game-S02E01`
- 子目录名固定为 `gameshow-recap-creator/` 和 `video-use/`，与 Skill 名一致

### 文件职责

| 文件 | 谁负责 | 何时生成 |
|---|---|---|
| `<根>/README.md` | 大模型在 Step 1 创建 | 项目启动时 |
| `<根>/gameshow-recap-creator/pre-analysis.md` | Skill 2（第一层） | Step 2 |
| `<根>/gameshow-recap-creator/recap-script.md` | Skill 2（第二层） | Step 2 |
| `<根>/video-use/edit/*` | Skill 3 | Step 3 |
| `<根>/final.mp4` | 大模型从 `video-use/edit/final.mp4` 复制 | Step 3 完成时 |

---

## 3. 工作流步骤

### Step 0：通读本 SOP

每次新任务开始前，第一件事是读这份文档（自己在 skill 文件夹里找 `~/.workbuddy/skills/video-recap-sop/SKILL.md`），建立工作流记忆。

### Step 1：判断是否需要 Skill 1

询问用户：
- "你想做的二创题材是什么？" → 若用户已指定具体节目 / 集数，跳过 Skill 1
- 若用户开放题材，启用 Skill 1（`bilibili-competitor-radar`），输出 `competitor-report.md`（可选放在项目目录里）

### Step 2：创建项目目录 + 启用 Skill 2（gameshow-recap-creator）

1. 创建项目目录：
   ```
   outputs/projects/<视频名>/gameshow-recap-creator/
   ```
2. 创建项目 README.md
3. 调用 Skill 2，输入：
   - 原片字幕（SRT / JSON / TXT）
   - 原视频文件路径（用于确认时长）
   - 场景类型：A 完整节目 / B 剧集（某集）
4. Skill 2 输出：
   - `pre-analysis.md`：第一层（角色名单 + 游戏目标 + 主线地图 + 核心爆点）
   - `recap-script.md`：第二层（11 分钟解说脚本）
5. **不要跳到 Step 3**，先在项目 README.md 记录 Skill 2 完成状态

### Step 3：启用 Skill 3（video-use）

1. 读 `recap-script.md`，把脚本喂给 `~/.workbuddy/skills/video-use/`
2. video-use 会创建 `<根>/video-use/edit/` 子目录结构
3. 视频剪辑流程（video-use 内部）：
   - inventory：ffprobe 源文件
   - transcribe：跳过（已有官方 SRT）
   - pack：`recap-script.md` 作为 EDL 输入
   - LLM reasons：基于 recap-script 的时间码决策
   - render：per-segment extract + concat + 字幕 + 花字
   - self-eval：每个切点 ±1.5s 自检，最多 3 轮
4. video-use 产出 `<根>/video-use/edit/final.mp4`
5. **复制** `final.mp4` 到 `<根>/final.mp4`
6. 更新项目 README.md，记录最终成片路径与状态

### Step 4：人工审核 + 上传

- 打开 `final.mp4` 检查
- 按项目 README.md 的"包装清单"补齐封面 / 标签 / 简介
- 上传到 B 站

---

## 4. Skill 详细说明

### 4.1 bilibili-competitor-radar（辅助前置，draft）

- **本地路径**：`~/.workbuddy/skills/bilibili-competitor-radar/`
- **Git 状态**：本地已 init draft v0.1
- **当前能力**：依赖 `bilibili-all-in-one`，提供竞品搜索 / 热度探测 / 对标账号画像 / 选题报告生成（人工）
- **已知缺口**：无关键词搜索 / 无 UP 主监控 / 无增长率排序 / 无自动报告
- **何时补齐**：作为独立仓库迭代

### 4.2 gameshow-recap-creator（核心）

- **本地路径**：`~/.workbuddy/skills/gameshow-recap-creator/`
- **Git 状态**：本地已 init，待推 GitHub
- **职责**：理解原视频，输出二创解说脚本
- **两层处理**：
  - 第一层（Pre-Analysis）：角色名单 + 游戏目标 + 主线地图 + 核心爆点
  - 第二层（Script Writing）：8 段结构化解说脚本
- **输入**：原片字幕（SRT/JSON/TXT）+ 元数据 + 场景类型
- **输出**：Markdown 脚本（旁白 + 画面时间码 + 花字 + 剪辑标注 + 包装清单）
- **已验证**：The Traitors UK S01E01 → `projects/The-Traitors-UK-S01E01/gameshow-recap-creator/`

### 4.3 video-use（核心）

- **本地路径**：`~/.workbuddy/skills/video-use/`
- **GitHub**：https://github.com/phoenix0110/video-use
- **职责**：执行视频剪辑，把脚本变视频
- **能力**：切片 / 拼接 / 烧字幕 / 加花字 / TTS 音轨 / 30ms 淡入淡出 / 自检渲染
- **转写双 backend**：ElevenLabs Scribe（付费） / 本地 openai-whisper（免费，无 API key）
- **12 条 Hard Rules**：字幕最后 / per-segment extract / 30ms 淡入淡出 / PTS-shift 花字 / 输出时间线 offset / 词边界切点 / 30–200ms padding 等

---

## 5. 数据流对照表

| 数据名称 | 产生方 | 消费方 | 格式 | 存储位置 |
|---|---|---|---|---|
| 选题报告 | `bilibili-competitor-radar` | `gameshow-recap-creator`（可选输入） | Markdown | `<根>/competitor-report.md`（可选） |
| 解说脚本 | `gameshow-recap-creator` | `video-use` | Markdown | `<根>/gameshow-recap-creator/recap-script.md` |
| 最终成片 | `video-use` | 人工审核 → B 站上传 | MP4 | `<根>/final.mp4` |

---

## 6. 已验证的端到端样例

**项目**：`outputs/projects/The-Traitors-UK-S01E01/`

| 阶段 | 状态 |
|---|---|
| Bilibili Competitor Radar | ⏭️ 跳过（已确定选题） |
| Gameshow Recap Creator | ✅ 已完成（11 分钟解说脚本） |
| Video Use | ⏳ 待运行 |

样例证明 `gameshow-recap-creator` 可以独立完成脚本生成，不需要任何外部输入。下一步是把 `recap-script.md` 喂给 `video-use` 跑剪辑流水线。