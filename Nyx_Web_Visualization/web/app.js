"use strict";

// Nyx Density Explorer 前端主逻辑。
// 说明：本页面只懒加载当前时间步的降采样体数据，不会一次性读取全部 100 个体。

const DATA_BASE = "assets/data/";

const state = {
  metadata: null,
  stats: [],
  histograms: null,
  heatmap: null,
  hessianFraction: [],
  stages: [],
  currentTime: 0,
  lowPct: 99,
  highPct: 100,
  direction: "Z",
  viewMode: "maskedMIP",
  transferMode: "balanced",
  volumeCache: new Map(),
  sortedCache: new Map(),
  currentVolume: null,
  currentMask: null,
  selectedCount: 0,
  isPlaying: false,
  playTimer: null,
  brushStartPct: null
};

const el = {};

document.addEventListener("DOMContentLoaded", init);

/**
 * 初始化 DOM、事件和数据加载。
 */
async function init() {
  cacheElements();
  bindEvents();
  setStatus("loading", "正在加载 Web 数据", "读取 metadata、统计量、直方图和阶段信息。");
  try {
    await loadMetadata();
    await loadStats();
    await loadHistograms();
    await loadAuxiliaryData();
    configureControls();
    renderTimeDensityHeatmap();
    renderMetricCurves();
    await updateDashboard();
    setStatus("ready", "Web 数据加载完成", `${state.metadata.time_steps} 个时间步，${state.metadata.web_grid_size}³ Web 体数据。`);
  } catch (err) {
    console.error(err);
    setStatus("error", "数据加载失败", "请先运行 scripts/preprocess_for_web.py 生成 web/assets/data/ 数据文件。");
    showOverlay("请先运行预处理脚本生成 web/assets/data 数据。\n\npython Nyx_Web_Visualization/scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64");
  }
}

/**
 * 缓存页面元素。
 */
function cacheElements() {
  const ids = [
    "statusDot", "loadStatus", "loadDetail", "timeSlider", "timeLabel", "playBtn",
    "speedSelect", "lowPct", "highPct", "lowPctLabel", "highPctLabel", "directionSelect",
    "viewModeSelect", "tfSelect", "resetBtn", "selectedCount", "selectedRatio", "stageLabel",
    "viewSubtitle", "spatialCanvas", "canvasOverlay", "histCanvas", "heatmapCanvas",
    "metricCanvas", "brushExplain", "analysisText", "keyFindingList"
  ];
  ids.forEach((id) => { el[id] = document.getElementById(id); });
  el.quickBrushButtons = Array.from(document.querySelectorAll(".chip-button[data-range]"));
}

/**
 * 绑定用户交互事件。
 */
function bindEvents() {
  el.timeSlider.addEventListener("input", async () => {
    state.currentTime = Number(el.timeSlider.value);
    await updateDashboard();
  });

  el.lowPct.addEventListener("input", async () => {
    state.lowPct = Math.min(Number(el.lowPct.value), Number(el.highPct.value) - 0.1);
    el.lowPct.value = String(state.lowPct);
    await updateDashboard(false);
  });

  el.highPct.addEventListener("input", async () => {
    state.highPct = Math.max(Number(el.highPct.value), Number(el.lowPct.value) + 0.1);
    el.highPct.value = String(state.highPct);
    await updateDashboard(false);
  });

  el.directionSelect.addEventListener("change", async () => {
    state.direction = el.directionSelect.value;
    await updateDashboard(false);
  });

  el.viewModeSelect.addEventListener("change", async () => {
    state.viewMode = el.viewModeSelect.value;
    await updateDashboard(false);
  });

  el.tfSelect.addEventListener("change", async () => {
    state.transferMode = el.tfSelect.value;
    await updateDashboard(false);
  });

  el.quickBrushButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const [low, high] = btn.dataset.range.split(",").map(Number);
      state.lowPct = low;
      state.highPct = high;
      await updateDashboard(false);
    });
  });

  el.playBtn.addEventListener("click", () => {
    if (state.isPlaying) stopAnimation();
    else playAnimation();
  });

  el.resetBtn.addEventListener("click", async () => {
    state.currentTime = 0;
    state.lowPct = 99;
    state.highPct = 100;
    state.direction = "Z";
    state.viewMode = "maskedMIP";
    state.transferMode = "balanced";
    syncControls();
    await updateDashboard();
  });

  addHistogramBrushEvents();
  el.heatmapCanvas.addEventListener("click", async (evt) => {
    if (!state.heatmap) return;
    const rect = el.heatmapCanvas.getBoundingClientRect();
    const x = (evt.clientX - rect.left) / rect.width;
    const t = Math.max(0, Math.min(state.metadata.time_steps - 1, Math.floor(x * state.metadata.time_steps)));
    state.currentTime = t;
    await updateDashboard();
  });

  el.metricCanvas.addEventListener("click", async (evt) => {
    if (!state.stats.length) return;
    const rect = el.metricCanvas.getBoundingClientRect();
    const x = (evt.clientX - rect.left) / rect.width;
    const t = Math.max(0, Math.min(state.stats.length - 1, Math.round(x * (state.stats.length - 1))));
    state.currentTime = t;
    await updateDashboard();
  });
}

/**
 * 读取 metadata.json。
 */
async function loadMetadata() {
  const res = await fetch(DATA_BASE + "metadata.json");
  if (!res.ok) throw new Error("metadata.json missing");
  state.metadata = await res.json();
}

/**
 * 读取 density_stats.json。
 */
async function loadStats() {
  const res = await fetch(DATA_BASE + "density_stats.json");
  if (!res.ok) throw new Error("density_stats.json missing");
  state.stats = await res.json();
}

/**
 * 读取 histograms.json 和 time-density heatmap。
 */
async function loadHistograms() {
  const [histRes, heatRes] = await Promise.all([
    fetch(DATA_BASE + "histograms.json"),
    fetch(DATA_BASE + "time_density_heatmap.json")
  ]);
  if (!histRes.ok || !heatRes.ok) throw new Error("histogram data missing");
  state.histograms = await histRes.json();
  state.heatmap = await heatRes.json();
}

/**
 * 读取可选的 Hessian 占比和阶段划分数据，缺失时降级为空。
 */
async function loadAuxiliaryData() {
  state.hessianFraction = await fetchJsonOrEmpty(DATA_BASE + "hessian_fraction.json");
  state.stages = await fetchJsonOrEmpty(DATA_BASE + "time_similarity_stage.json");
}

/**
 * 容错读取 JSON。
 */
async function fetchJsonOrEmpty(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

/**
 * 配置控件范围。
 */
function configureControls() {
  const maxTime = Math.max(0, state.metadata.time_steps - 1);
  el.timeSlider.max = String(maxTime);
  syncControls();
}

/**
 * 将内部状态同步到控件。
 */
function syncControls() {
  el.timeSlider.value = String(state.currentTime);
  el.lowPct.value = String(state.lowPct);
  el.highPct.value = String(state.highPct);
  el.directionSelect.value = state.direction;
  el.viewModeSelect.value = state.viewMode;
  el.tfSelect.value = state.transferMode;
}

/**
 * 根据 timeIndex 懒加载对应体数据。
 */
async function loadVolume(timeIndex) {
  if (state.volumeCache.has(timeIndex)) {
    return state.volumeCache.get(timeIndex);
  }
  const step = state.metadata.steps[timeIndex];
  if (!step) throw new Error(`time step ${timeIndex} not found`);
  const res = await fetch(DATA_BASE + step.volume_file);
  if (!res.ok) throw new Error(`volume ${step.volume_file} missing`);
  const buffer = await res.arrayBuffer();
  const volume = new Float32Array(buffer);
  state.volumeCache.set(timeIndex, volume);
  return volume;
}

/**
 * 计算当前体数据的百分位阈值。
 */
function computePercentile(volume, pct) {
  const key = state.currentTime;
  let sorted = state.sortedCache.get(key);
  if (!sorted) {
    sorted = Array.from(volume).sort((a, b) => a - b);
    state.sortedCache.set(key, sorted);
  }
  if (pct <= 0) return sorted[0];
  if (pct >= 100) return sorted[sorted.length - 1];
  const pos = (pct / 100) * (sorted.length - 1);
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  const frac = pos - lo;
  return sorted[lo] * (1 - frac) + sorted[hi] * frac;
}

/**
 * 根据百分位生成 mask。
 */
function makeMask(volume, lowPct, highPct) {
  const low = computePercentile(volume, lowPct);
  const high = computePercentile(volume, highPct);
  const mask = new Uint8Array(volume.length);
  let count = 0;
  for (let i = 0; i < volume.length; i++) {
    const ok = volume[i] >= low && volume[i] <= high;
    if (ok) {
      mask[i] = 1;
      count++;
    }
  }
  state.selectedCount = count;
  return mask;
}

/**
 * 统一更新当前时间步所有视图。
 */
async function updateDashboard(loadNewVolume = true) {
  syncControls();
  el.timeLabel.textContent = String(state.currentTime).padStart(4, "0");
  el.lowPctLabel.textContent = formatPct(state.lowPct);
  el.highPctLabel.textContent = formatPct(state.highPct);
  showOverlay("Loading volume...");
  try {
    if (loadNewVolume || !state.currentVolume) {
      state.currentVolume = await loadVolume(state.currentTime);
    }
    state.currentMask = makeMask(state.currentVolume, state.lowPct, state.highPct);
    updateMetrics();
    renderSpatialView();
    renderHistogram(state.currentTime);
    renderTimeDensityHeatmap();
    renderMetricCurves();
    updateConclusionCards();
    updateAnalysisPanel();
    hideOverlay();
  } catch (err) {
    console.error(err);
    showOverlay(`加载失败：${err.message}`);
  }
}

/**
 * 渲染主空间视图。
 */
function renderSpatialView() {
  const canvas = el.spatialCanvas;
  const volume = state.currentVolume;
  const mask = state.currentMask;
  if (!volume) return;
  if (state.viewMode === "mip") {
    renderMIP(volume, state.direction, canvas);
  } else if (state.viewMode === "mask") {
    renderMaskProjection(volume, mask, state.direction, canvas, false);
  } else if (state.viewMode === "slice") {
    renderSlice(volume, state.direction, canvas);
  } else if (state.viewMode === "composite") {
    renderVolumeComposite(volume, canvas);
  } else {
    renderMaskProjection(volume, mask, state.direction, canvas, true);
  }
  el.viewSubtitle.textContent = `t=${String(state.currentTime).padStart(4, "0")} · ${state.direction} · ${state.viewMode}`;
}

/**
 * 绘制最大强度投影。
 */
function renderMIP(volume, direction, canvas) {
  const n = state.metadata.web_grid_size;
  const values = new Float32Array(n * n);
  values.fill(0);
  projectVolume(volume, null, direction, values, "mip");
  drawScalarImage(values, n, n, canvas, state.transferMode);
}

/**
 * 绘制 mask 投影或 mask 后 MIP。
 */
function renderMaskProjection(volume, mask, direction, canvas, maskedMIP) {
  const n = state.metadata.web_grid_size;
  const values = new Float32Array(n * n);
  values.fill(0);
  projectVolume(volume, mask, direction, values, maskedMIP ? "maskedMIP" : "mask");
  drawScalarImage(values, n, n, canvas, maskedMIP ? state.transferMode : "mask");
}

/**
 * 绘制中心切片。
 */
function renderSlice(volume, direction, canvas) {
  const n = state.metadata.web_grid_size;
  const values = new Float32Array(n * n);
  const mid = Math.floor(n / 2);
  for (let a = 0; a < n; a++) {
    for (let b = 0; b < n; b++) {
      let x, y, z;
      if (direction === "Z") [x, y, z] = [a, b, mid];
      else if (direction === "Y") [x, y, z] = [a, mid, b];
      else [x, y, z] = [mid, a, b];
      values[b * n + a] = volume[index3(x, y, z, n)];
    }
  }
  drawScalarImage(values, n, n, canvas, state.transferMode);
}

/**
 * 简化 alpha compositing 体绘制，默认按当前方向从后向前合成。
 */
function renderVolumeComposite(volume, canvas) {
  const n = state.metadata.web_grid_size;
  const rgb = new Float32Array(n * n * 3);
  const alphaAcc = new Float32Array(n * n);
  for (let depth = n - 1; depth >= 0; depth--) {
    for (let a = 0; a < n; a++) {
      for (let b = 0; b < n; b++) {
        let x, y, z;
        if (state.direction === "Z") [x, y, z] = [a, b, depth];
        else if (state.direction === "Y") [x, y, z] = [a, depth, b];
        else [x, y, z] = [depth, a, b];
        const v = volume[index3(x, y, z, n)];
        const color = getTransferColor(v, state.transferMode);
        const alpha = getTransferAlpha(v, state.transferMode) * (1 - alphaAcc[b * n + a]);
        const p = (b * n + a) * 3;
        rgb[p] += color[0] * alpha;
        rgb[p + 1] += color[1] * alpha;
        rgb[p + 2] += color[2] * alpha;
        alphaAcc[b * n + a] += alpha;
      }
    }
  }
  drawRGBImage(rgb, n, n, canvas);
}

/**
 * 三维索引。预处理输出采用 x-y-z 数组的 C-order 展平。
 */
function index3(x, y, z, n) {
  return x * n * n + y * n + z;
}

/**
 * 根据方向进行投影。
 */
function projectVolume(volume, mask, direction, out, mode) {
  const n = state.metadata.web_grid_size;
  for (let a = 0; a < n; a++) {
    for (let b = 0; b < n; b++) {
      let maxVal = 0;
      let selected = false;
      for (let d = 0; d < n; d++) {
        let x, y, z;
        if (direction === "Z") [x, y, z] = [a, b, d];
        else if (direction === "Y") [x, y, z] = [a, d, b];
        else [x, y, z] = [d, a, b];
        const idx = index3(x, y, z, n);
        if (mask && !mask[idx]) continue;
        selected = true;
        if (mode === "mask") {
          maxVal = 1;
          break;
        }
        if (volume[idx] > maxVal) maxVal = volume[idx];
      }
      out[b * n + a] = selected ? maxVal : 0;
    }
  }
}

/**
 * 将标量场绘制为彩色图像。
 */
function drawScalarImage(values, w, h, canvas, mode) {
  const off = document.createElement("canvas");
  off.width = w;
  off.height = h;
  const ctx = off.getContext("2d");
  const image = ctx.createImageData(w, h);
  for (let i = 0; i < values.length; i++) {
    const color = getTransferColor(values[i], mode);
    image.data[i * 4] = color[0];
    image.data[i * 4 + 1] = color[1];
    image.data[i * 4 + 2] = color[2];
    image.data[i * 4 + 3] = mode === "mask" && values[i] <= 0 ? 18 : 255;
  }
  ctx.putImageData(image, 0, 0);
  const target = canvas.getContext("2d");
  target.clearRect(0, 0, canvas.width, canvas.height);
  target.imageSmoothingEnabled = false;
  target.drawImage(off, 0, 0, canvas.width, canvas.height);
  drawSpatialAnnotations(target, canvas);
}

/**
 * 绘制 RGB 合成图像。
 */
function drawRGBImage(rgb, w, h, canvas) {
  const off = document.createElement("canvas");
  off.width = w;
  off.height = h;
  const ctx = off.getContext("2d");
  const image = ctx.createImageData(w, h);
  for (let i = 0; i < w * h; i++) {
    image.data[i * 4] = Math.min(255, rgb[i * 3]);
    image.data[i * 4 + 1] = Math.min(255, rgb[i * 3 + 1]);
    image.data[i * 4 + 2] = Math.min(255, rgb[i * 3 + 2]);
    image.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
  const target = canvas.getContext("2d");
  target.clearRect(0, 0, canvas.width, canvas.height);
  target.imageSmoothingEnabled = false;
  target.drawImage(off, 0, 0, canvas.width, canvas.height);
  drawSpatialAnnotations(target, canvas);
}

/**
 * 绘制空间视图文字标注。
 */
function drawSpatialAnnotations(ctx, canvas) {
  ctx.save();
  ctx.fillStyle = "rgba(2, 5, 13, 0.62)";
  ctx.fillRect(14, 14, 300, 72);
  ctx.fillStyle = "#eaf6ff";
  ctx.font = "600 20px Microsoft YaHei, sans-serif";
  ctx.fillText(`Time Step ${String(state.currentTime).padStart(4, "0")}`, 28, 44);
  ctx.font = "14px Microsoft YaHei, sans-serif";
  ctx.fillStyle = "#9fdfff";
  ctx.fillText(`${formatPct(state.lowPct)}%-${formatPct(state.highPct)}% · ${state.direction} · ${state.viewMode}`, 28, 70);
  ctx.restore();
}

/**
 * 绘制当前时间步直方图和刷选范围。
 */
function renderHistogram(timeIndex) {
  const canvas = el.histCanvas;
  const ctx = canvas.getContext("2d");
  const item = state.histograms.items[timeIndex];
  if (!item) return;
  const probs = item.probability;
  const maxP = Math.max(...probs, 1e-12);
  const pad = { l: 42, r: 18, t: 24, b: 34 };
  const w = canvas.width - pad.l - pad.r;
  const h = canvas.height - pad.t - pad.b;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawPanelGrid(ctx, pad, w, h);

  ctx.fillStyle = "rgba(73, 207, 255, 0.7)";
  probs.forEach((p, i) => {
    const x = pad.l + (i / probs.length) * w;
    const bw = Math.max(1, w / probs.length);
    const bh = (p / maxP) * h;
    ctx.fillRect(x, pad.t + h - bh, bw, bh);
  });
  renderHistogramBrush(state.lowPct, state.highPct, ctx, pad, w, h, probs);

  ctx.fillStyle = "#dcecff";
  ctx.font = "13px Microsoft YaHei, sans-serif";
  ctx.fillText("probability", 8, 18);
  ctx.fillText("log-density bins", pad.l + w - 110, canvas.height - 8);
}

/**
 * 在直方图上绘制当前百分位刷选区间。
 */
function renderHistogramBrush(lowPct, highPct, ctx, pad, w, h, probs) {
  const x1 = percentileToX(lowPct, probs, pad.l, w);
  const x2 = percentileToX(highPct, probs, pad.l, w);
  ctx.fillStyle = "rgba(255, 157, 63, 0.28)";
  ctx.fillRect(Math.min(x1, x2), pad.t, Math.abs(x2 - x1), h);
  ctx.strokeStyle = "#ffd56f";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x1, pad.t);
  ctx.lineTo(x1, pad.t + h);
  ctx.moveTo(x2, pad.t);
  ctx.lineTo(x2, pad.t + h);
  ctx.stroke();
}

/**
 * 将百分位近似映射到直方图横坐标。
 */
function percentileToX(pct, probs, x0, w) {
  const target = pct / 100;
  let acc = 0;
  for (let i = 0; i < probs.length; i++) {
    acc += probs[i];
    if (acc >= target) return x0 + (i / Math.max(1, probs.length - 1)) * w;
  }
  return x0 + w;
}

/**
 * 直方图 brush 交互。
 */
function addHistogramBrushEvents() {
  const canvas = el.histCanvas;
  const pctFromEvent = (evt) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (evt.clientX - rect.left) / rect.width));
    return x * 100;
  };
  canvas.addEventListener("pointerdown", (evt) => {
    state.brushStartPct = pctFromEvent(evt);
    canvas.setPointerCapture(evt.pointerId);
  });
  canvas.addEventListener("pointermove", async (evt) => {
    if (state.brushStartPct === null) return;
    const p = pctFromEvent(evt);
    state.lowPct = Math.max(0, Math.min(state.brushStartPct, p));
    state.highPct = Math.min(100, Math.max(state.brushStartPct, p));
    if (state.highPct - state.lowPct < 0.1) state.highPct = Math.min(100, state.lowPct + 0.1);
    await updateDashboard(false);
  });
  canvas.addEventListener("pointerup", () => {
    state.brushStartPct = null;
  });
}

/**
 * 绘制 time-density heatmap。
 */
function renderTimeDensityHeatmap() {
  if (!state.heatmap) return;
  const canvas = el.heatmapCanvas;
  const ctx = canvas.getContext("2d");
  const values = state.heatmap.values;
  const tCount = values.length;
  const bCount = values[0]?.length || 0;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const pad = { l: 72, r: 24, t: 36, b: 56 };
  const w = canvas.width - pad.l - pad.r;
  const h = canvas.height - pad.t - pad.b;
  const maxLog = Math.max(...values.flat().map((v) => Math.log10(v + 1e-8)));
  const minLog = -8;

  for (let t = 0; t < tCount; t++) {
    for (let b = 0; b < bCount; b++) {
      const v = Math.log10(values[t][b] + 1e-8);
      const norm = clamp((v - minLog) / (maxLog - minLog || 1), 0, 1);
      const color = heatColor(norm);
      ctx.fillStyle = `rgb(${color[0]},${color[1]},${color[2]})`;
      const x = pad.l + (t / tCount) * w;
      const y = pad.t + h - ((b + 1) / bCount) * h;
      ctx.fillRect(x, y, Math.ceil(w / tCount) + 1, Math.ceil(h / bCount) + 1);
    }
  }
  drawCurrentTimeLine(ctx, pad, w, h, tCount);
  drawAxisLabels(ctx, canvas, "time step", "log-density");
}

/**
 * 绘制统计指标曲线。
 */
function renderMetricCurves() {
  if (!state.stats.length) return;
  const canvas = el.metricCanvas;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const pad = { l: 72, r: 24, t: 44, b: 56 };
  const w = canvas.width - pad.l - pad.r;
  const h = canvas.height - pad.t - pad.b;
  drawPanelGrid(ctx, pad, w, h);
  const series = [
    ["mean_density", "#5fd8ff", "mean"],
    ["std_density", "#ffb04f", "std"],
    ["P99", "#ff6b8b", "P99"],
    ["P99_over_mean", "#a875ff", "P99/mean"],
    ["P99_minus_P01", "#38e3a1", "P99-P01"]
  ];
  series.forEach(([key, color, label], idx) => {
    drawMetricLine(ctx, key, color, pad, w, h);
    ctx.fillStyle = color;
    ctx.font = "22px Microsoft YaHei, sans-serif";
    ctx.fillText(label, pad.l + 8 + idx * 150, 30);
  });
  drawCurrentTimeLine(ctx, pad, w, h, state.stats.length);
  drawAxisLabels(ctx, canvas, "time step", "normalized metrics");
}

/**
 * 绘制单条指标曲线。
 */
function drawMetricLine(ctx, key, color, pad, w, h) {
  const vals = state.stats.map((d) => Number(d[key] || 0));
  const minV = Math.min(...vals);
  const maxV = Math.max(...vals);
  ctx.strokeStyle = color;
  ctx.lineWidth = 4;
  ctx.beginPath();
  vals.forEach((v, i) => {
    const x = pad.l + (i / Math.max(1, vals.length - 1)) * w;
    const y = pad.t + h - ((v - minV) / (maxV - minV || 1)) * h;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

/**
 * 更新数值指标卡。
 */
function updateMetrics() {
  const total = state.currentVolume ? state.currentVolume.length : 0;
  const ratio = total ? state.selectedCount / total : 0;
  el.selectedCount.textContent = state.selectedCount.toLocaleString();
  el.selectedRatio.textContent = `${(ratio * 100).toFixed(2)}%`;
  const stage = getCurrentStage();
  el.stageLabel.textContent = stage;
  updateQuickBrushState();
}

/**
 * 根据当前时间步更新结论卡片。
 */
function updateConclusionCards() {
  const message = getBrushInterpretation();
  if (el.brushExplain) el.brushExplain.textContent = message;
}

/**
 * 更新底部动态解释面板，说明当前时间步、刷选区间和空间视图的分析意义。
 */
function updateAnalysisPanel() {
  if (!el.analysisText || !el.keyFindingList) return;
  const ratio = getSelectedRatio();
  const stage = getCurrentStage();
  const rangeLabel = `${formatPct(state.lowPct)}%-${formatPct(state.highPct)}%`;
  const viewLabel = describeViewMode(state.viewMode);
  const directionLabel = describeDirection(state.direction);
  const transferLabel = describeTransferFunction(state.transferMode);

  el.analysisText.textContent = getBrushInterpretation();
  el.keyFindingList.innerHTML = [
    `<li>当前时间步：t=${String(state.currentTime).padStart(4, "0")}；演化阶段：${stage}。</li>`,
    `<li>当前密度区间：${rangeLabel}；被选体素比例：${(ratio * 100).toFixed(2)}%。</li>`,
    `<li>当前空间视图：${directionLabel} 方向的 ${viewLabel}，传递函数为 ${transferLabel}。</li>`,
    "<li>分析目的：把统计直方图中的密度区间映射回空间位置，观察数值分布与三维结构之间的对应关系。</li>"
  ].join("");
}

/**
 * 根据刷选区间生成面向答辩展示的解释文字。
 */
function getBrushInterpretation() {
  const topOne = state.lowPct >= 98.9 && state.highPct >= 99.9;
  const midDensity = state.lowPct >= 39.5 && state.lowPct <= 40.5 && state.highPct >= 69.5 && state.highPct <= 70.5;
  const lowDensity = state.lowPct <= 0.5 && state.highPct >= 19.5 && state.highPct <= 20.5;
  if (topOne) {
    return "当前选择的是密度分布右尾的 Top 1% 高密度体素。空间视图中被高亮的区域可用于观察极高密度体素是否集中在丝状结构交汇处和节点区域，从而验证统计高尾部与宇宙网致密结构之间的对应关系。";
  }
  if (midDensity) {
    return "当前选择的是中密度区间，适合观察连续丝状结构和过渡区域。该区间有助于理解空洞边界与高密度节点之间的连接关系。";
  }
  if (lowDensity) {
    return "当前选择的是低密度区间，适合观察低密度背景和可能的宇宙空洞区域。该视图可以帮助比较低密度区域与高密度节点在空间上的分离关系。";
  }
  return "当前选择的是自定义密度百分位区间，系统将统计分布中的该区间映射回空间视图，用于分析数值分布与三维结构之间的关系。";
}

/**
 * 高亮当前匹配的快捷刷选按钮。
 */
function updateQuickBrushState() {
  if (!el.quickBrushButtons) return;
  el.quickBrushButtons.forEach((btn) => {
    const [low, high] = btn.dataset.range.split(",").map(Number);
    const active = Math.abs(state.lowPct - low) < 0.05 && Math.abs(state.highPct - high) < 0.05;
    btn.classList.toggle("active", active);
  });
}

function getSelectedRatio() {
  const total = state.currentVolume ? state.currentVolume.length : 0;
  return total ? state.selectedCount / total : 0;
}

function describeDirection(direction) {
  if (direction === "X") return "X/YZ";
  if (direction === "Y") return "Y/XZ";
  return "Z/XY";
}

function describeViewMode(mode) {
  const labels = {
    mip: "最大强度投影",
    mask: "二值 mask 投影",
    maskedMIP: "mask 后最大强度投影",
    slice: "中心切片",
    composite: "简化体绘制"
  };
  return labels[mode] || mode;
}

function describeTransferFunction(mode) {
  const labels = {
    balanced: "Balanced 综合显示",
    void: "Void 低密度增强",
    filament: "Filament 中密度增强",
    node: "Node 高密度增强"
  };
  return labels[mode] || mode;
}

/**
 * 播放时间演化动画。
 */
function playAnimation() {
  state.isPlaying = true;
  el.playBtn.textContent = "Pause";
  const tick = async () => {
    if (!state.isPlaying) return;
    state.currentTime += 1;
    if (state.currentTime >= state.metadata.time_steps) {
      state.currentTime = 0;
    }
    await updateDashboard();
    state.playTimer = window.setTimeout(tick, Number(el.speedSelect.value));
  };
  tick();
}

/**
 * 停止播放。
 */
function stopAnimation() {
  state.isPlaying = false;
  el.playBtn.textContent = "Play";
  if (state.playTimer) window.clearTimeout(state.playTimer);
  state.playTimer = null;
}

/**
 * 根据 transfer function 返回 RGB。
 */
function getTransferColor(value, mode) {
  const v = clamp(value, 0, 1);
  if (mode === "mask") {
    return v > 0 ? [255, 210, 96] : [8, 12, 24];
  }
  if (mode === "void") {
    const boost = 1 - v;
    return interpolateColor([11, 20, 46], [65, 210, 255], boost * 0.85);
  }
  if (mode === "filament") {
    const mid = 1 - Math.abs(v - 0.55) / 0.55;
    return interpolateColor([18, 20, 54], [61, 232, 201], clamp(mid, 0, 1));
  }
  if (mode === "node") {
    const hot = smoothstep(0.72, 1.0, v);
    return interpolateColor([19, 18, 45], [255, 236, 166], hot);
  }
  if (v < 0.25) return interpolateColor([4, 7, 18], [21, 50, 111], v / 0.25);
  if (v < 0.58) return interpolateColor([21, 50, 111], [128, 72, 206], (v - 0.25) / 0.33);
  if (v < 0.82) return interpolateColor([128, 72, 206], [255, 143, 55], (v - 0.58) / 0.24);
  return interpolateColor([255, 143, 55], [255, 252, 214], (v - 0.82) / 0.18);
}

/**
 * alpha compositing 使用的透明度传递函数。
 */
function getTransferAlpha(value, mode) {
  const v = clamp(value, 0, 1);
  if (mode === "void") return 0.018 + 0.05 * (1 - v);
  if (mode === "filament") return 0.018 + 0.12 * smoothstep(0.28, 0.75, v) * (1 - smoothstep(0.92, 1.0, v));
  if (mode === "node") return 0.012 + 0.22 * smoothstep(0.72, 1.0, v);
  return 0.012 + 0.11 * smoothstep(0.2, 0.92, v);
}

function smoothstep(edge0, edge1, x) {
  const t = clamp((x - edge0) / (edge1 - edge0 || 1), 0, 1);
  return t * t * (3 - 2 * t);
}

function interpolateColor(a, b, t) {
  const u = clamp(t, 0, 1);
  return [
    Math.round(a[0] + (b[0] - a[0]) * u),
    Math.round(a[1] + (b[1] - a[1]) * u),
    Math.round(a[2] + (b[2] - a[2]) * u)
  ];
}

function heatColor(v) {
  if (v < 0.33) return interpolateColor([6, 10, 28], [61, 94, 196], v / 0.33);
  if (v < 0.66) return interpolateColor([61, 94, 196], [182, 73, 204], (v - 0.33) / 0.33);
  return interpolateColor([182, 73, 204], [255, 218, 102], (v - 0.66) / 0.34);
}

function clamp(x, a, b) {
  return Math.max(a, Math.min(b, x));
}

function drawPanelGrid(ctx, pad, w, h) {
  ctx.strokeStyle = "rgba(170, 205, 255, 0.12)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + (i / 4) * h;
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(pad.l + w, y);
    ctx.stroke();
  }
}

function drawCurrentTimeLine(ctx, pad, w, h, count) {
  const x = pad.l + (state.currentTime / Math.max(1, count - 1)) * w;
  ctx.strokeStyle = "#ffd56f";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(x, pad.t);
  ctx.lineTo(x, pad.t + h);
  ctx.stroke();
}

function drawAxisLabels(ctx, canvas, xText, yText) {
  ctx.save();
  ctx.fillStyle = "#dcecff";
  ctx.font = "21px Microsoft YaHei, sans-serif";
  ctx.textAlign = "right";
  ctx.fillText(xText, canvas.width - 24, canvas.height - 16);
  ctx.translate(22, canvas.height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = "center";
  ctx.fillText(yText, 0, 0);
  ctx.restore();
}

function getCurrentStage() {
  const row = state.stages.find((d) => Number(d.time_index) === state.currentTime);
  return row ? String(row.stage_label || row.stage || "--") : "--";
}

function formatPct(v) {
  return Number(v).toFixed(Number.isInteger(Number(v)) ? 0 : 1);
}

function setStatus(kind, title, detail) {
  el.loadStatus.textContent = title;
  el.loadDetail.textContent = detail;
  el.statusDot.classList.toggle("ready", kind === "ready");
}

function showOverlay(text) {
  el.canvasOverlay.textContent = text;
  el.canvasOverlay.classList.remove("hidden");
}

function hideOverlay() {
  el.canvasOverlay.classList.add("hidden");
}
