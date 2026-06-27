from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "report"
SOURCE_MD = REPORT_DIR / "Nyx宇宙密度演化可视分析_技术报告_参考风格扩写版.md"
OUT_MD = REPORT_DIR / "Nyx宇宙密度演化可视分析_技术报告_附录代码格式优化版.md"
OUT_DOCX = REPORT_DIR / "Nyx宇宙密度演化可视分析_技术报告_附录代码格式优化版.docx"


APPENDIX = r'''# 7 附录：核心代码

本附录仅保留能够体现项目核心方法的代码片段，不粘贴完整源文件。代码按照数据读取与验证、密度统计与预处理、体数据渲染、高密度结构验证、交互式刷选和 Web 展示系统六类组织。每段代码均保留行号，便于正文引用和答辩讲解。

## 7.1 数据读取与验证核心代码

### 7.1.1 Nyx 二进制体数据读取

该代码对应 `read_nyx_dat.m`，用于从 Nyx 原始 `.dat` 文件中读取 little-endian float32 数据，并将一维数组恢复为三维体数据。输入为单个 `.dat` 文件路径，输出为 x-y-z 顺序的三维密度场 `V`。

```matlab
1  function V = read_nyx_dat(filename)
2      fid = fopen(filename, 'r', 'ieee-le');
3      if fid < 0
4          error('无法打开数据文件：%s', filename);
5      end
6      data = fread(fid, inf, 'single=>single');
7      fclose(fid);
8
9      n = infer_grid_size(numel(data));
10     nz = n; ny = n; nx = n;
11
12     Vzyx = reshape(data, [nz, ny, nx]);
13     V = permute(Vzyx, [3, 2, 1]);
14     V = single(V);
15 end
```

Code Listing 1: Nyx 二进制体数据读取核心代码

### 7.1.2 网格尺寸自动推断

该代码对应 `infer_grid_size.m`，用于根据文件字节数或体素数量推断三维体数据边长 `n`，并检查体素数量是否可以构成 `n×n×n` 立方体。该步骤保证后续 `reshape` 不会在异常文件上继续运行。

```matlab
1  function n = infer_grid_size(inputValue)
2      if ischar(inputValue) || isstring(inputValue)
3          info = dir(inputValue);
4          fileBytes = info.bytes;
5          voxelCount = fileBytes / 4;
6      else
7          voxelCount = double(inputValue);
8      end
9
10     n = round(voxelCount^(1/3));
11     if n^3 ~= voxelCount
12         error('文件尺寸异常：体素数量 %.0f 不能构成 n×n×n 立方体。', voxelCount);
13     end
14 end
```

Code Listing 2: 网格尺寸自动推断核心代码

### 7.1.3 中心切片验证

该代码对应 `step1_check_data.m`，用于提取 XY、XZ、YZ 三个中心切片，检查读取方向和轴顺序是否正确。若轴顺序错误，中心切片通常会出现不连续条纹、错位或异常纹理。

```matlab
1  n = size(V, 1);
2  mid = round(n / 2);
3
4  sliceXY = squeeze(V(:, :, mid));
5  sliceXZ = squeeze(V(:, mid, :));
6  sliceYZ = squeeze(V(mid, :, :));
7
8  figure('Color', 'w');
9  subplot(1, 3, 1);
10 imagesc(log10(max(sliceXY, eps))); axis image off; title('XY center slice');
11 subplot(1, 3, 2);
12 imagesc(log10(max(sliceXZ, eps))); axis image off; title('XZ center slice');
13 subplot(1, 3, 3);
14 imagesc(log10(max(sliceYZ, eps))); axis image off; title('YZ center slice');
15 colormap hot; colorbar;
```

Code Listing 3: 中心切片验证核心代码

## 7.2 密度统计与预处理核心代码

### 7.2.1 log-density 变换与百分位归一化

该代码对应 `normalize_percentile.m`，用于解决原始 density 动态范围较大导致中低密度结构不明显的问题。通过 `log10` 变换和 P5-P99.7 百分位归一化，将密度数据映射到适合显示的 `[0,1]` 范围。

```matlab
1  function Vn = normalize_percentile(V, lowerPct, upperPct)
2      logV = log10(max(V, eps('single')));
3      low = prctile(double(logV(:)), lowerPct);
4      high = prctile(double(logV(:)), upperPct);
5
6      if abs(high - low) < eps
7          Vn = zeros(size(logV), 'single');
8          return;
9      end
10
11     Vn = (single(logV) - single(low)) ./ single(high - low);
12     Vn = min(max(Vn, 0), 1);
13     Vn = single(Vn);
14 end
```

Code Listing 4: log-density 变换与百分位归一化核心代码

### 7.2.2 全时间步统计指标计算

该代码对应 `step2_statistics_all_frames.m`，用于遍历所有时间步，计算 mean、std、P99、P99/mean、P99-P01 等指标，为后续时序统计曲线和演化分析提供数据。

```matlab
1  datFiles = dir(fullfile(rawDir, '*.dat'));
2  datFiles = datFiles([datFiles.bytes] > 0);
3  [~, order] = sort({datFiles.name});
4  datFiles = datFiles(order);
5
6  for k = 1:numel(datFiles)
7      filename = fullfile(datFiles(k).folder, datFiles(k).name);
8      V = read_nyx_dat(filename);
9      vox = double(V(:));
10     pct = prctile(vox, [1 5 50 95 99 99.7 99.9]);
11
12     stats.time_index(k) = k - 1;
13     stats.mean_density(k) = mean(vox);
14     stats.std_density(k) = std(vox);
15     stats.max_density(k) = max(vox);
16     stats.P01(k) = pct(1);
17     stats.P99(k) = pct(5);
18     stats.P99_over_mean(k) = pct(5) / max(mean(vox), eps);
19     stats.P99_minus_P01(k) = pct(5) - pct(1);
20 end
21 statsTable = struct2table(stats);
22 writetable(statsTable, fullfile(processedDir, 'density_stats.csv'));
```

Code Listing 5: 全时间步密度统计核心代码

### 7.2.3 对数密度直方图计算

该代码对应 `step3_histogram_analysis.m`，用于构建代表时间步的 log-density histogram，并为 time-density heatmap 提供统一 bins 的概率分布数据。统一 bins 可以保证不同时间步的分布具有可比性。

```matlab
1  edges = linspace(globalLogMin, globalLogMax, 121);
2  histMatrix = zeros(numel(datFiles), numel(edges) - 1);
3
4  for k = 1:numel(datFiles)
5      V = read_nyx_dat(fullfile(datFiles(k).folder, datFiles(k).name));
6      logV = log10(max(V, eps('single')));
7      prob = histcounts(double(logV(:)), edges, 'Normalization', 'probability');
8      histMatrix(k, :) = prob;
9
10     if ismember(k - 1, keySteps)
11         figure('Color', 'w');
12         histogram(double(logV(:)), edges, 'Normalization', 'probability');
13         xlabel('log10(density)'); ylabel('Probability');
14         title(sprintf('Log-density histogram t=%04d', k - 1));
15     end
16 end
17 binCenters = (edges(1:end-1) + edges(2:end)) / 2;
```

Code Listing 6: 对数密度直方图计算核心代码

## 7.3 体数据渲染核心代码

### 7.3.1 自定义 alpha compositing 体绘制

该代码对应 `volume_render_alpha_composite.m`，是本项目体绘制的核心。代码沿视线方向逐层累积颜色和透明度，将三维密度体合成为二维图像，用于展示宇宙网整体空间结构。

```matlab
1  [nx, ny, nz] = size(Vn);
2  rgbImage = zeros(nx, ny, 3, 'single');
3  alphaImage = zeros(nx, ny, 'single');
4  lut = custom_nyx_colormap(256);
5
6  for z = nz:-1:1
7      layer = min(max(Vn(:, :, z), 0), 1);
8      idx = max(1, min(256, round(layer * 255) + 1));
9      rgbLayer = reshape(lut(idx, :), nx, ny, 3);
10
11     alpha = 0.04 * smoothstep(0.18, 0.55, layer) + ...
12             0.22 * smoothstep(0.72, 1.00, layer);
13     alpha = min(alpha, 0.32);
14
15     remain = 1 - alphaImage;
16     rgbImage = rgbImage + remain .* alpha .* single(rgbLayer);
17     alphaImage = alphaImage + remain .* alpha;
18 end
19 rgbImage = min(max(rgbImage, 0), 1);
```

Code Listing 7: 自定义 alpha compositing 体绘制核心代码

### 7.3.2 smoothstep 透明度函数

该代码对应 `smoothstep.m`，用于平滑控制不同密度区间的透明度变化，避免体绘制中出现突兀边界。相比硬阈值，smoothstep 能使丝状结构和节点边缘过渡更自然。

```matlab
1  function y = smoothstep(edge0, edge1, x)
2      if edge1 == edge0
3          y = double(x >= edge1);
4          return;
5      end
6
7      t = (x - edge0) ./ (edge1 - edge0);
8      t = min(max(t, 0), 1);
9      y = t .* t .* (3 - 2 .* t);
10     y = min(max(y, 0), 1);
11 end
```

Code Listing 8: smoothstep 透明度函数核心代码

### 7.3.3 传递函数设计

该代码对应 `custom_nyx_colormap.m` 及体绘制脚本中的 transfer function 部分，用于定义 Balanced、Void、Filament、Node 等不同显示模式，使不同密度结构得到突出。

```matlab
1  switch lower(mode)
2      case 'balanced'
3          colorLUT = custom_nyx_colormap(256);
4          alpha = 0.03 * smoothstep(0.15, 0.55, Vn) + ...
5                  0.18 * smoothstep(0.70, 1.00, Vn);
6      case 'void'
7          colorLUT = interp1([0 1], [0.05 0.10 0.28; 0.20 0.85 1.00], linspace(0,1,256));
8          alpha = 0.10 * smoothstep(0.00, 0.30, 1 - Vn);
9      case 'filament'
10         colorLUT = interp1([0 0.5 1], [0.03 0.05 0.16; 0.18 0.85 0.76; 1.00 0.55 0.20], linspace(0,1,256));
11         alpha = 0.16 * smoothstep(0.32, 0.72, Vn) .* (1 - smoothstep(0.90, 1.00, Vn));
12     case 'node'
13         colorLUT = interp1([0 1], [0.08 0.06 0.18; 1.00 0.92 0.50], linspace(0,1,256));
14         alpha = 0.24 * smoothstep(0.76, 1.00, Vn);
15 end
```

Code Listing 9: 传递函数设计核心代码

## 7.4 高密度结构验证核心代码

### 7.4.1 P99 top 1% 高密度筛选

该代码对应 `step5_high_density_selection.m`，用于根据原始 density 的 P99 阈值提取 top 1% 高密度体素，并生成 mask。该步骤用于验证直方图高密度尾部与空间中宇宙网节点结构的对应关系。

```matlab
1  V = read_nyx_dat(filename);
2  vox = double(V(:));
3  threshold = prctile(vox, 99);
4
5  mask = V >= single(threshold);
6  selectedCount = nnz(mask);
7  selectedRatio = selectedCount / numel(mask);
8
9  logV = log10(max(V, eps('single')));
10 maskedVolume = logV;
11 maskedVolume(~mask) = -inf;
12 fprintf('P99 threshold = %.6g, selected ratio = %.2f%%\n', ...
13         threshold, selectedRatio * 100);
```

Code Listing 10: P99 top 1% 高密度筛选核心代码

### 7.4.2 最大强度投影 MIP

该代码用于将三维体数据或高密度 mask 沿 X/Y/Z 方向压缩为二维图像，便于观察高密度体素在不同方向上的空间分布。MIP 会丢失深度信息，但适合快速定位强密度结构。

```matlab
1  mipX = squeeze(max(maskedVolume, [], 1));
2  mipY = squeeze(max(maskedVolume, [], 2));
3  mipZ = squeeze(max(maskedVolume, [], 3));
4
5  figure('Color', 'w');
6  subplot(1, 3, 1);
7  imagesc(mipX); axis image off; title('X-MIP');
8  subplot(1, 3, 2);
9  imagesc(mipY); axis image off; title('Y-MIP');
10 subplot(1, 3, 3);
11 imagesc(mipZ); axis image off; title('Z-MIP');
12 colormap hot; colorbar;
13 sgtitle(sprintf('Top 1%% high-density cells, ratio %.2f%%', selectedRatio * 100));
```

Code Listing 11: 高密度区域最大强度投影核心代码

### 7.4.3 多阈值等值面提取

该代码用于提取 P90、P95、P99 等不同密度阈值下的等值面，展示高密度结构由大范围丝状外壳到核心节点的层级变化。该结果补充了二维 MIP 的深度信息不足。

```matlab
1  thresholds = prctile(double(V(:)), [90 95 99]);
2  colors = [0.15 0.75 1.00; 1.00 0.62 0.18; 1.00 0.18 0.18];
3  alphas = [0.18 0.32 0.62];
4
5  figure('Color', 'w'); hold on;
6  for i = 1:numel(thresholds)
7      fv = isosurface(V, thresholds(i));
8      p = patch(fv);
9      isonormals(V, p);
10     p.FaceColor = colors(i, :);
11     p.EdgeColor = 'none';
12     p.FaceAlpha = alphas(i);
13 end
14 axis equal off; view(3); camlight; lighting gouraud;
15 title('Nested isosurfaces: P90 / P95 / P99');
```

Code Listing 12: 多阈值等值面提取核心代码

## 7.5 交互式刷选核心代码

### 7.5.1 linked brushing 密度区间筛选

该代码对应 `step7_interactive_dashboard.m`，用于根据用户在直方图或滑条中选择的密度百分位区间，实时生成空间 mask，并更新空间投影结果。

```matlab
1  function updateSelection(lowerPct, upperPct)
2      logV = log10(max(V, eps('single')));
3      lowVal = prctile(double(logV(:)), lowerPct);
4      highVal = prctile(double(logV(:)), upperPct);
5
6      mask = logV >= lowVal & logV <= highVal;
7      selectedRatio = nnz(mask) / numel(mask);
8      projection = max(logV .* single(mask), [], 3);
9
10     updateHistogram(axHist, logV, lowerPct, upperPct);
11     updateProjection(axProj, projection, selectedRatio);
12 end
```

Code Listing 13: linked brushing 密度区间筛选核心代码

### 7.5.2 交互式仪表盘回调函数

该代码用于响应时间步滑条、密度区间滑条和投影方向切换事件，实现统计视图与空间视图之间的联动更新。其核心是把控件状态统一写入当前状态变量，再调用 `refreshDashboard`。

```matlab
1  timeSlider.ValueChangedFcn = @(src, evt) refreshDashboard();
2  lowerSlider.ValueChangingFcn = @(src, evt) refreshDashboard(evt.Value, []);
3  upperSlider.ValueChangingFcn = @(src, evt) refreshDashboard([], evt.Value);
4  directionDropDown.ValueChangedFcn = @(src, evt) refreshDashboard();
5
6  function refreshDashboard(newLow, newHigh)
7      currentStep = round(timeSlider.Value);
8      if nargin >= 1 && ~isempty(newLow), lowerPct = newLow; end
9      if nargin >= 2 && ~isempty(newHigh), upperPct = newHigh; end
10     direction = directionDropDown.Value;
11
12     V = loadFrame(currentStep);
13     updateSelection(lowerPct, upperPct);
14     updateSpatialProjection(V, direction);
15     drawnow limitrate;
16 end
```

Code Listing 14: 交互式仪表盘回调函数核心代码

## 7.6 Web 展示系统核心代码

### 7.6.1 Web 数据预处理

该代码对应 `preprocess_for_web.py`，用于将原始 `.dat` 文件转换为浏览器可加载的轻量数据，包括 `metadata.json`、`density_stats.json`、`histograms.json` 和降采样后的 `vol_xxxx.bin`。

```python
1  data = np.fromfile(dat_path, dtype="<f4")
2  n = round(data.size ** (1.0 / 3.0))
3  if n ** 3 != data.size:
4      raise ValueError(f"invalid grid size: {dat_path}")
5
6  volume = data.reshape((n, n, n)).transpose(2, 1, 0)
7  log_v = np.log10(np.maximum(volume, np.finfo(np.float32).eps))
8  low, high = np.percentile(log_v, [5, 99.7])
9  norm_v = np.clip((log_v - low) / max(high - low, 1e-8), 0, 1)
10
11 small = downsample_volume(norm_v.astype(np.float32), target_size)
12 out_file = volume_dir / f"vol_{time_index:04d}.bin"
13 small.astype("<f4", copy=False).tofile(out_file)
14 metadata["steps"].append({"time_index": time_index, "volume_file": str(out_file.relative_to(data_dir))})
15 json.dump(metadata, open(data_dir / "metadata.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

Code Listing 15: Web 数据预处理核心代码

### 7.6.2 Web 体数据懒加载

该代码对应 `app.js` 中的 `loadVolume(timeIndex)`，用于按需加载当前时间步的 `vol_xxxx.bin`，避免浏览器一次性加载全部体数据。已加载过的时间步会缓存在 `volumeCache` 中。

```javascript
1  async function loadVolume(timeIndex) {
2    if (state.volumeCache.has(timeIndex)) {
3      return state.volumeCache.get(timeIndex);
4    }
5
6    const step = state.metadata.steps[timeIndex];
7    if (!step) throw new Error(`time step ${timeIndex} not found`);
8
9    const res = await fetch(DATA_BASE + step.volume_file);
10   if (!res.ok) throw new Error(`volume ${step.volume_file} missing`);
11   const buffer = await res.arrayBuffer();
12   const volume = new Float32Array(buffer);
13
14   state.volumeCache.set(timeIndex, volume);
15   return volume;
16 }
```

Code Listing 16: Web 体数据懒加载核心代码

### 7.6.3 Web 空间视图 MIP 渲染

该代码对应 `app.js` 中的 `renderMIP` 与 `projectVolume`，用于在 HTML canvas 中显示当前时间步的最大强度投影结果。不同投影方向通过改变 x/y/z 的遍历方式实现。

```javascript
1  function renderMIP(volume, direction, canvas) {
2    const n = state.metadata.web_grid_size;
3    const values = new Float32Array(n * n);
4    values.fill(0);
5    projectVolume(volume, null, direction, values, "mip");
6    drawScalarImage(values, n, n, canvas, state.transferMode);
7  }
8
9  function projectVolume(volume, mask, direction, out, mode) {
10   const n = state.metadata.web_grid_size;
11   for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) {
12     let maxVal = 0;
13     for (let d = 0; d < n; d++) {
14       const [x, y, z] = mapProjectionIndex(a, b, d, direction);
15       const idx = x * n * n + y * n + z;
16       if (!mask || mask[idx]) maxVal = Math.max(maxVal, volume[idx]);
17     }
18     out[b * n + a] = maxVal;
19   }
20 }
```

Code Listing 17: Web 空间视图 MIP 渲染核心代码

### 7.6.4 Top 1% 高密度一键筛选

该代码对应 `app.js` 中的快捷刷选按钮逻辑，用于快速设置 density percentile range 为 `99%-100%`，并刷新空间视图和解释面板。该功能面向答辩演示中对高密度节点的快速验证。

```javascript
1  document.querySelectorAll(".chip-button[data-range]").forEach((btn) => {
2    btn.addEventListener("click", async () => {
3      const [low, high] = btn.dataset.range.split(",").map(Number);
4      state.lowPct = low;
5      state.highPct = high;
6      if (low === 99 && high === 100) {
7        state.viewMode = "maskedMIP";
8        state.transferMode = "node";
9      }
10     syncControls();
11     await updateDashboard(false);
12   });
13 });
```

Code Listing 18: Top 1% 高密度一键筛选核心代码
'''


def main() -> None:
    if not SOURCE_MD.exists():
        raise FileNotFoundError(SOURCE_MD)

    text = SOURCE_MD.read_text(encoding="utf-8")
    marker = "# 7 附录：核心代码"
    idx = text.find(marker)
    if idx < 0:
        raise ValueError("未找到原附录标题：# 7 附录：核心代码")

    new_text = text[:idx].rstrip() + "\n\n" + APPENDIX.rstrip() + "\n"
    OUT_MD.write_text(new_text, encoding="utf-8")

    sys.path.insert(0, str(ROOT / "code" / "python"))
    from build_iteration_process_documents import add_markdown_to_docx

    ok = add_markdown_to_docx(OUT_MD, OUT_DOCX)
    if not ok:
        raise RuntimeError("DOCX 生成失败")

    print(OUT_MD)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
