# video-recap-sop

B 站二创视频工作流 SOP（Standard Operating Procedure）。orchestrator skill，引导大模型按 Step 0–4 执行：

1. **Step 0**：通读本 SOP
2. **Step 1**：判断是否启用 `bilibili-competitor-radar`（辅助前置，可选）
3. **Step 2**：创建项目目录 + 启用 `gameshow-recap-creator`（必经）
4. **Step 3**：启用 `video-use`（必经）
5. **Step 4**：人工审核 + 上传 B 站

## 适用场景

- 用户开始一个新的二创视频任务
- 用户说"按 SOP 来做"或"按流程走"
- 用户要求查阅工作流 / 验证步骤是否符合规范

## 不是

- ❌ 不是一个 README
- ❌ 不产出任何视频 / 脚本 / 报告
- ❌ 不替代三个 sub-skill 的具体执行

## 它做什么

- 协调 `bilibili-competitor-radar` / `gameshow-recap-creator` / `video-use` 三个 sub-skill 的调用顺序
- 强制遵守项目目录规范（`outputs/projects/<视频名>/{gameshow-recap-creator,video-use}/`）
- 在每一步记录状态到项目 README.md
- 维护数据流（竞品报告 → 解说脚本 → 最终成片）

## License

MIT