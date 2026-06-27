# Nyx Density Explorer Web 展示说明

## 1. 项目简介

`Nyx Density Explorer` 是《基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析》的 Web 交互展示版本。页面通过降采样体数据、密度直方图、time-density heatmap、统计曲线和 linked brushing，展示 Nyx 宇宙学模拟密度场从相对均匀到高低密度分化、丝状结构和节点逐渐显现的过程。

本系统用于数据可视化课程展示和答辩演示，结论不作为正式天体物理科学结论。

## 2. 运行方法

### 步骤 1：生成 Web 数据

在项目根目录运行：

```bash
python scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
```

也可以直接运行 Web 子项目脚本：

```bash
python Nyx_Web_Visualization/scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
```

脚本会生成：

- `web/assets/data/metadata.json`
- `web/assets/data/density_stats.json`
- `web/assets/data/histograms.json`
- `web/assets/data/time_density_heatmap.json`
- `web/assets/data/hessian_fraction.json`
- `web/assets/data/time_similarity_stage.json`
- `web/assets/data/volumes/vol_0000.bin` 等降采样体数据

### 步骤 2：启动本地服务器

```bash
cd Nyx_Web_Visualization/web
python -m http.server 8000
```

### 步骤 3：浏览器打开

```text
http://localhost:8000
```

由于浏览器安全限制，不建议直接双击 `index.html` 打开，应通过本地服务器运行。

## 3. 页面交互说明

1. 拖动 `Time Step` 滑条可以切换当前时间步。
2. 点击 `Play` 可以播放 Nyx 密度场随时间演化的过程。
3. 调整 `Density Percentile Range` 可以选择特定密度百分位区间。
4. 默认选择 `99% - 100%`，对应 top 1% 高密度体素。
5. 切换 `Projection Direction` 可以观察 X/Y/Z 不同方向投影。
6. 切换 `View Mode` 可以在 MIP、Mask、Slice 和简化 Volume Composite 之间切换。
7. 切换 `Transfer Function` 可以比较 Void、Filament、Node 和 Balanced 不同视觉映射。
8. 在 histogram 上拖拽可以进行密度区间刷选，并联动更新空间视图。
9. 点击 time-density heatmap 或统计曲线可以跳转到对应时间步。
10. 底部 `Analysis & Interpretation` 面板会根据当前时间步、密度区间、投影方向和视图模式自动更新解释文字。

## 4. 答辩展示顺序

1. 打开首页，说明 Nyx 数据是三维时序密度体。
2. 点击播放按钮，展示宇宙密度随时间演化。
3. 切换到 t=0000、t=0030、t=0060、t=0099，对比空间结构变化。
4. 展示 histogram，说明密度分布逐渐扩散，高密度尾部增强。
5. 将 density range 设置为 99% 到 100%，展示 top 1% 高密度体素。
6. 切换 X/Y/Z 投影方向，说明高密度体素集中在节点和丝状交汇处。
7. 展示 time-density heatmap，说明全时间步密度分布变化。
8. 展示统计曲线，说明 std、P99、P99/mean 和 P99-P01 的变化。
9. 使用 Low、Mid、High、Top 1% 快捷刷选按钮，对比不同密度区间的空间分布。
10. 最后展示 `Analysis & Interpretation` 动态解释面板，说明统计特征与空间结构的双向关联。

## 5. 数据与性能说明

- 浏览器不会一次性加载全部体数据，只会懒加载当前时间步的 `vol_xxxx.bin`。
- 每个体数据默认为 `64×64×64` 的 normalized log-density Float32Array。
- 如果电脑性能较弱，可以将预处理参数改为 `--size 48`。
- 已加载过的时间步会缓存在浏览器内存中，重复访问时不再重新请求。
- 若没有运行预处理脚本，页面会提示先生成 `web/assets/data/`。

## 6. 常见问题

**Q1：页面打开后一直显示 Loading 怎么办？**  
A1：请确认已运行预处理脚本，并通过 `python -m http.server` 启动页面，而不是直接双击 HTML。

**Q2：播放时比较卡怎么办？**  
A2：可重新预处理为 `--size 48`，或切换到 MIP、Mask、Slice 模式，避免使用 Volume Composite。

**Q3：为什么不直接加载原始 128×128×128×100 数据？**  
A3：完整数据体量较大，不适合浏览器一次性加载。本项目采用降采样和懒加载，以保证课堂演示流畅。

**Q4：top 1% 是什么？**  
A4：top 1% 表示当前时间步中密度值位于最高 1% 的体素，即 P99 到 P100 区间，常用于观察高密度尾部在空间中的分布。

**Q5：这些结构解释是否是正式天体物理结论？**  
A5：不是。本系统强调数据可视化课程实验中的方法展示，关于空洞、丝状结构和节点的描述来自给定数据与可视化结果。
