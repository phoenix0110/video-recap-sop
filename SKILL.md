---
name: video-recap-sop
description: 引导大模型按 Step 0–4 执行 B 站二创视频制作。在用户开始二创任务或讨论流程时启用。这是 orchestrator skill，本身不写脚本也不剪视频，只负责协调 bilibili-competitor-radar、gameshow-recap-creator、video-use 三个 sub-skill，并强制遵守项目目录规范。
---

# 二创视频 Workflow SOP

> 适用于 Game Show / Reality Show 的 B 站二创视频制作

---

## 0. 文档用途

这是大模型执行二创视频任务的 **Standard Operating Procedure**。每次开始一个新的二创任务前，先通读这份文档，然后按步骤执行。

**它是 orchestrator skill。** 只负责：
1. 协调三个 sub-skill 的调用顺序
2. 强制遵守项目目录规范
3. 在每一步记录状态到项目 README.md

---

## 1. 强制守则：错误必须弹出（动手前先看）

**核心规则**：执行任何 Step 时，一旦发现脚本 / 命令报错，必须**立即停止并向用户报告**。**绝对禁止**：

- ❌ 静默重试（同一报错重复跑）
- ❌ 自己写补丁代码绕过
- ❌ 闷头继续往下跑下一个 Step
- ❌ 把多个报错攒成一段轻描淡写的总结
- ❌ 说"差不多了" / "基本完成" / "应该成功了"

正确做法：**报错 → 弹栈 → 停手 → 等用户拍板**。

### 1.1 必须弹出的场景

| 触发条件 | 处理方式 |
|---|---|
| 任何 sub-skill 脚本返回非 0 退出码 | 完整贴出错误输出（不要只贴 exit code） |
| ffmpeg / yt-dlp / edge-tts 等命令行报错 | 贴出 stderr 关键 5–10 行 |
| 期望生成的文件不存在 / 为 0 字节 | 列出预期路径 vs 实际状态 |
| Skill 自己报告"发现缺什么" | 把缺什么原样汇报，不要默默绕路 |
| 跑超过 3 分钟没出新日志 | 视为卡死，弹出询问是否继续等 |
| 同一个错连报 3 次 | 立刻建议人工介入，不要再自动重试 |

### 1.2 弹出模板

发现错误时，回复必须包含这五件事，缺一不可：

1. **在哪一步**：Step X 的子任务 Y（用 SOP 里的 Step 编号）
2. **在哪个文件 / 命令**：绝对路径或脚本名
3. **报错原文**：关键 5–10 行（不要省略 stack trace）
4. **已尝试过什么**：列出来（不要 silent retry）
5. **明确询问**：要用户决定下一步怎么办（修代码 / 换 backend / 跳过 / 重跑）

### 1.4 配套约定

- 项目 README.md 加一节 `## 中断记录`，每次中断都追加一行（时间 / Step / 错误 / 决策）
- 用户确认前，不要继续后续 Step
- 即使"看起来快好了"，也必须弹出确认，不许自动收尾

---

## 2. 三个 Skill 总览

| # | Skill | 角色 | 是否必经 |
|---|---|---|---|
| 1 | `bilibili-competitor-radar` | 选题 / 竞品 / 热度调研 | ❌ **辅助前置**，已有清晰选题时跳过 |
| 2 | `gameshow-recap-creator` | 写解说脚本 | ✅ **必经** |
| 3 | `video-use` | 视频剪辑合成 | ✅ **必经** |

**何时启用 Skill 1？**
- 用户说"我想做个新题材的二创，你帮我调研一下" → 启用
- 用户直接说"做 The Traitors S01E01" → 跳过（已有清晰选题）
---

## 3. 二创项目目录规范

每次开始一个二创任务，必须按以下结构创建项目目录：

```
outputs/
└── projects/
    └── <二创视频名称>/                  # 根目录，以本次视频命名
        ├── final.mp4                   # ⭐ 根目录：Video Use 产出的最终成片
        ├── README.md                   # 项目记录（流水线回放 + 状态 + 包装清单）
        ├── gameshow-recap-creator/     # Skill 2 输出（脚本）
        │   ├── pre-analysis.md         # 第一层：角色 / 目标 / 主线 / 爆点
        │   ├── episode-brief.md        # 单集梗概：一→二层交接（临时，二层定稿后删）
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
| `<根>/gameshow-recap-creator/episode-brief.md` | Skill 2（第一层产出 → 第二层消费） | Step 2 生成，**第二层定稿后删除** |
| `<根>/gameshow-recap-creator/recap-script.md` | Skill 2（第二层） | Step 2 |
| `<根>/video-use/edit/*` | Skill 3 | Step 3 |
| `<根>/final.mp4` | 大模型从 `video-use/edit/final.mp4` 复制 | Step 3 完成时 |

> **临时文件 `episode-brief.md`**：第一层交给第二层的单集梗概（整集走向 + 主线地图 + 必须包含的爆点 / 转折点 / 亮点）。作用是让第二层在按时间线写脚本之前，先拿到整集全局视野和一张"不许漏"的清单。**第二层读完即用，定稿后删除——不进最终交付物，也不留存在项目目录。**

---

## 4. 工作流步骤

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
   - `episode-brief.md`：单集梗概，**临时交接文件**
     - 内容：整集走向 + 主线地图 + 必须包含的核心爆点 + 转折点与亮点
     - 用途：让第二层在按时间线写脚本前，先拿到整集全局视野和一张"不许漏"的清单
     - 生命周期：第一层产出 → 第二层读取 → 第二层定稿后**删除**（不进交付物）
   - `recap-script.md`：第二层（11 分钟解说脚本）
5. 确认 `episode-brief.md` 已被第二层删除；**若仍残留，手动清理后再进 Step 3**
6. **不要跳到 Step 3**，先在项目 README.md 记录 Skill 2 完成状态

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

## 5. Skill 详细说明

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

## 6. 数据流对照表

| 数据名称 | 产生方 | 消费方 | 格式 | 存储位置 |
|---|---|---|---|---|
| 选题报告 | `bilibili-competitor-radar` | `gameshow-recap-creator`（可选输入） | Markdown | `<根>/competitor-report.md`（可选） |
| 解说脚本 | `gameshow-recap-creator` | `video-use` | Markdown | `<根>/gameshow-recap-creator/recap-script.md` |
| 最终成片 | `video-use` | 人工审核 → B 站上传 | MP4 | `<根>/final.mp4` |

---

## 7. 已验证的端到端样例

**项目**：`outputs/projects/The-Traitors-UK-S01E01/`

| 阶段 | 状态 |
|---|---|
| Bilibili Competitor Radar | ⏭️ 跳过（已确定选题） |
| Gameshow Recap Creator | ✅ 已完成（11 分钟解说脚本） |
| Video Use | ⏳ 待运行 |

样例证明 `gameshow-recap-creator` 可以独立完成脚本生成，不需要任何外部输入。下一步是把 `recap-script.md` 喂给 `video-use` 跑剪辑流水线。