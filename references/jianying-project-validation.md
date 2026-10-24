# 剪映项目生成与检查规范

本文件列出剪映项目自动生成后的检查标准。Step 6 创建剪映项目完成后，Step 7 按本规范逐项验收，不合格则删除重建。

---

## 1. 轨道结构完整性

| 轨道名称 | 必须存在 | 内容来源 |
|---------|---------|---------|
| 视频 | ✅ | 按 EDL 每个 range 独立导入的视频片段 |
| 原声-背景 | ✅ | 旁白段对应的**单独**源音频片段 |
| 原声-保留 | ✅ | preserve 段对应的**单独**源音频片段 |
| 旁白 | ✅ | 每条 TTS 字幕的独立音频文件 |
| 字幕 | ✅ | 每条旁白对应的文本 segment + preserve 翻译 |
| 配乐 | ✅ | BGM 片段，带 fade-in/fade-out |

缺少任一轨道即不合格。

## 2. 音频需要独立提取片段

- **原声-背景**轨：每个旁白段对应一个**单独的** WAV 片段，从拼接后源音频的对应时间位置提取，已衰减到 `source_under_narration` 音量。**禁止**使用一整条完整时间线的音频文件。
- **原声-保留**轨：每个 preserve/raw_clip 段对应一个**单独的** WAV 片段，从拼接后源音频的对应时间位置提取，保持原始音量。**禁止**使用一整条完整时间线的音频文件。
- **旁白**轨：每条 TTS 字幕对应一个独立的音频 segment 和独立的素材。**禁止**用单条 `full_narration.m4a` 替代。

**验证方法**：检查原声-背景 segment 数 = 旁白段（narration）的 timeline range 数；原声-保留 segment 数 = preserve + raw_clip 的 timeline range 数。

## 3. 音频内容非静音

- 每个原声-保留 WAV 的 RMS 必须 > 10（非静音）。
- 验证方法：对 `preserve_audio/` 下每个 WAV 计算 RMS，低于阈值则音频提取错误。

## 4. 视频片段静音

- 视频轨所有 segment 的 volume = 0.0。声音通过独立的原声-背景和原声-保留轨提供。

## 5. 字幕断句正确性

- 脚本中每个 `> ` 行是一个独立的句子，对应 TTS 中独立的 section。
- **禁止**将不同 `> ` 行的文字合并到同一条字幕或 TTS 请求中。
- **单条字幕不超过 25 个字符**。超出屏幕宽度的长子句须在标点、顿号或自然语义边界处二次拆分。
- **验证方法**：遍历 narration_manifest 中所有 cue，检查 `len(subtitle) <= 25`。抽查已知易合并的句子确认未跨行合并。

## 6. 时间线精度

- 所有 `start_time` 和 `duration` 使用整数微秒值（`round(seconds * 1_000_000)`），通过整数累加 `output_pos_us` 传递，避免浮点截断导致 SegmentOverlap。
- **验证方法**：加载 `draft_info.json`，按轨道遍历所有 segment，检查相邻 segment 之间 `start + duration <= next_start`（容差 2 微秒）。

## 7. 时长与数量交叉核对

| 指标 | 检查方法 |
|-----|---------|
| 视频 segment 数 | = `edl.json` 的 ranges 数 |
| 旁白 segment 数 | = `narration_manifest.json` 的 cue 数 |
| 字幕 segment 数 | ≥ 旁白 cue 数（含 preserve 翻译） |
| preserve 音频数 | = timeline 中 type=preserve 或 raw_clip 的 range 数 |
| 背景音频数 | = timeline 中 type=narration 的 range 数 |

## 8. BGM 规范

- BGM 覆盖全时间线，通过循环/分段实现。
- 每段 BGM 有 fade-in 和 fade-out。
- BGM 音量设置为低于旁白（默认 0.12–0.15）。

## 9. 保留边界准确性

- preserve 段的源起止时间已按 SRT 核验并修正。
- preserve WAV 的实际时长与 timeline 中标注的 duration 一致（容差 0.5s）。

## 10. 项目可打开

- 项目目录下存在 `draft_info.json`（或 `draft_content.json`）。
- JSON 结构合法，至少包含 `tracks` 数组。
- 剪映可正常打开该项目（最终由人工确认）。

---

## 自动化检查脚本模板

```python
import json
from pathlib import Path

draft_dir = Path("<剪映项目路径>")
di = draft_dir / "draft_info.json"
data = json.loads(di.read_text("utf-8"))
tracks = data["tracks"]
counts = {t.get("name", ""): len(t["segments"]) for t in tracks}

# 1. 轨道存在性
required = ["视频", "原声-背景", "原声-保留", "旁白", "字幕", "配乐"]
for name in required:
    assert name in counts, f"缺少轨道: {name}"

# 2. 无 segment 重叠
for t in tracks:
    segs = sorted(t["segments"], key=lambda s: s["target_timerange"]["start"])
    for a, b in zip(segs, segs[1:]):
        end_a = a["target_timerange"]["start"] + a["target_timerange"]["duration"]
        assert end_a <= b["target_timerange"]["start"] + 2, f"轨道 [{t['name']}] 存在重叠"

print("✅ 全部检查通过")
```
