# 视频二创项目 Progress Checklist

> **项目名称：** `{{PROJECT_NAME}}`
> **源视频：** `{{SOURCE_VIDEOS}}`
> **目标时长：** `{{TARGET_DURATION}}`
> **创建时间：** `{{CREATED_AT}}`

---

## Step 1：准备源素材

- [ ] 源视频文件存在且可读（`source/` 目录下）
- [ ] SRT/VTT 带时间码字幕已获取（优先发布者字幕；无字幕时已重新转写）
- [ ] 源文件保持原始状态，未做任何修改
- [ ] `README.md` 已创建，包含视频元数据（标题、频道、时长、URL）

---

## Step 2：生成解说脚本

### Layer 1：初稿

- [ ] 题材已通过 `genres/_index.md` 路由确认
- [ ] `pre-analysis.md` 已写入（题材、主线、钩子、中文昵称、原声目标比例）
- [ ] 初稿遵循已选择的 narrator persona（如适用）
- [ ] 脚本字段格式正确：`**画面**`、`**旁白**` > 行、`**原声保留**`
- [ ] `validate_script_format.py` exit 0
- [ ] 初稿原声占比在目标预估范围内

### Layer 2：叙事编辑

- [ ] 钩子提出的悬念在正文中被回收
- [ ] 核心问题经起因、推进和结果形成完整故事
- [ ] 必要信息在转折/决定之前已出现
- [ ] 必保留节点无遗漏，次要内容未重复或挤占主线
- [ ] 外国文化品牌/典故/笑点已按受众语境处理
- [ ] 单 section 内无连续多段 ≤30s 原声违反完整交流规范
- [ ] 已对照题材指南复核结构
- [ ] Layer 2 自检 8 项全部通过

### Layer 3：对齐

- [ ] `check_alignment.py` exit 0
- [ ] 源时间线单调递增（钩子段后）
- [ ] 画面范围覆盖旁白所述内容
- [ ] 旁白事实/数字/引用已与 SRT 源字幕核对
- [ ] 逐段人工审核通过

### Layer 4：润色

- [ ] `humanizer-zh` 口播润色已执行
- [ ] `shuorenhua` 只标问题审稿已执行
- [ ] 润色前快照已保存至 `draft-history/`
- [ ] `narration-review.md` 已创建
- [ ] `narration-review.json` 已创建
- [ ] JSON 中 `checks` 五项均为 true
- [ ] `validate_narration_review.py` exit 0
- [ ] 非旁白字段（结构、标题、时间码、画面、原声、称呼、翻译）未被改动

### Step 2 交付物

- [ ] `recap-script.md` 存在
- [ ] `narration-review.md` 存在
- [ ] `narration-review.json` 存在
- [ ] 交付时附一句话说明润色重点及审稿结果

---

## Step 3：剪辑前确认

- [ ] 整体节奏已确认（沉浸 / 自然推进 / 更紧凑）
- [ ] 原声在旁白下的音量方案已确认
- [ ] 字幕样式已确认（单行底部白字）
- [ ] 配音性别偏好已确认（男声 / 女声）
- [ ] 具体音色已确认（speaker_id + resource_id，剪映 SAMI 内置）
- [ ] 确定值已写入 EDL 和项目记录

---

## Step 4：剪辑与时间重排

### 前置校验

- [ ] `validate_narration_review.py` 对当前脚本再次运行 exit 0
- [ ] 脚本如有文字改动，旧审核已失效并重新完成 Layer 4

### 选片与 TTS

- [ ] Cue 映射已建立：旁白时间/文本 → 源字幕时间/原话 → 画面范围/首尾依据
- [ ] 所有片段保持原片 1× 速度
- [ ] TTS 试配已核实音色和独立片段效果
- [ ] TTS 批量生成完成，`sentences-manifest.json` 已产出
- [ ] 每条字幕 = 独立 WAV 音频

### 时间线构建

- [ ] 单个视频 clip 最短不低于 5 秒
- [ ] 原片间隔 <10s 的相邻 clip 已合并为连续范围
- [ ] 源时间线重叠的 clip 已合并
- [ ] 画面无视觉重叠（同一源片段不重复出现）
- [ ] 每章内源时间线单调递增

### 原声处理

- [ ] 普通段使用 `source_under_narration` 音量
- [ ] 原声保留段使用正常音量并附中文翻译
- [ ] preserve 窗口仅来自 manifest 的显式 `preserve_windows`，未推断间隙
- [ ] 已排除源片订阅提示、频道 logo 和 end screen

### 画面对齐

- [ ] 每个 clip 的画面内容支持对应旁白描述
- [ ] 旁白提到的关键视觉要素出现在对应旁白播放的时间范围内
- [ ] 调整 src 未带入旁白未提及的新事件

### 审核与渲染

- [ ] `caption-picture-review.md` 已交付（Markdown，按场景列时码/画面/声音/字幕）
- [ ] 用户确认画面与字幕对照
- [ ] 最终渲染完成（`final.mp4`）
- [ ] 渲染后实际原声占比在目标 ±10pp 内

---

## Step 5：成片检查

- [ ] 开场预览已检查，无必要短切已删除，所有片段 1× 速度
- [ ] 逐个切点检查：画面、原声、旁白、字幕的语义与节奏连续性
- [ ] 正常速度看完整正文：转折清楚、镜头不过密、无无意义长空白
- [ ] 问题已修正并重新渲染（最多三轮完整检查）
- [ ] `README.md` 审核状态已更新

---

## Step 6：创建剪映项目

- [ ] 调用 `jianying-editor` 创建剪映项目
- [ ] 项目包含 6 条轨道：视频、原声-背景、原声-保留、旁白、字幕、配乐
- [ ] 项目名称与脚本标题或视频中文名一致

---

## Step 7：剪映项目验收

### 7.1 轨道结构完整性

- [ ] 6 条轨道全部存在：视频、原声-背景、原声-保留、旁白、字幕、配乐
- [ ] segment 数量与 EDL/manifest 交叉一致

### 7.2 音频独立提取

- [ ] 原声-背景轨 = 单独 WAV 片段（非一整条时间线音频）
- [ ] 原声-保留轨 = 单独 WAV 片段（非一整条时间线音频）
- [ ] 旁白轨 = 每条 TTS 独立音频 segment（非 `full_narration.m4a`）

### 7.3 音频内容非静音

- [ ] 每个原声-保留 WAV 的 RMS > 10

### 7.4 视频片段静音

- [ ] 视频轨所有 segment volume = 0.0

### 7.5 字幕断句正确性

- [ ] 每个 `> ` 行 = 独立 TTS section，未跨行合并
- [ ] 所有字幕 ≤ 25 个字符
- [ ] 超长子句已在标点/顿号/语义边界处二次拆分

### 7.6 时间线精度

- [ ] 所有 start_time 和 duration 为整数微秒值
- [ ] 每条轨道内相邻 segment 无重叠（2μs 容差）

### 7.7 数量交叉核对

- [ ] 视频 segment 数 = EDL ranges 数
- [ ] 旁白 segment 数 = manifest cue 数
- [ ] 字幕 segment 数 ≥ 旁白 cue 数（含 preserve 翻译）
- [ ] preserve 音频数 = timeline 中 preserve/raw_clip range 数
- [ ] 背景音频数 = timeline 中 narration range 数

### 7.8 BGM 规范

- [ ] BGM 覆盖全时间线
- [ ] 每段 BGM 有 fade-in 和 fade-out
- [ ] BGM 音量低于旁白（0.12–0.15）

### 7.9 保留边界准确性

- [ ] preserve 段源起止时间已按 SRT 核验修正
- [ ] preserve WAV 实际时长与 timeline 标注 duration 一致（容差 0.5s）

### 7.10 项目可打开

- [ ] `draft_info.json`（或 `draft_content.json`）存在且 JSON 合法
- [ ] 剪映可正常打开该项目（人工确认）
