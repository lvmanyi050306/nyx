function generate_report_figures(projectRoot)
%GENERATE_REPORT_FIGURES 生成改进版报告所需的新增图表。

if nargin < 1
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
end
addpath(fullfile(projectRoot, 'code'));
addpath(fullfile(projectRoot, 'code', 'utils'));

outDir = fullfile(projectRoot, 'results', 'report_figures');
ensure_folder(outDir);

draw_overall_workflow(fullfile(outDir, 'overall_workflow.png'));
draw_transfer_function(fullfile(outDir, 'transfer_function_design.png'));
write_representative_stats(projectRoot, fullfile(outDir, 'representative_density_stats.csv'));
end

function draw_overall_workflow(outFile)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1400 820]);
ax = axes(fig);
axis(ax, [0 1 0 1]);
axis(ax, 'off');
hold(ax, 'on');

boxColor = [0.93 0.96 1.00];
routeColor = [1.00 0.96 0.88];
finalColor = [0.93 1.00 0.93];
edgeColor = [0.24 0.34 0.48];

draw_box(ax, 0.06, 0.82, 0.20, 0.07, 'Nyx .dat 原始数据', boxColor, edgeColor);
draw_box(ax, 0.30, 0.82, 0.20, 0.07, 'little-endian float32 读取', boxColor, edgeColor);
draw_box(ax, 0.54, 0.82, 0.18, 0.07, '自动推断 n×n×n', boxColor, edgeColor);
draw_box(ax, 0.76, 0.82, 0.18, 0.07, 'z-y-x → x-y-z 恢复', boxColor, edgeColor);
draw_arrow(ax, 0.26, 0.855, 0.30, 0.855);
draw_arrow(ax, 0.50, 0.855, 0.54, 0.855);
draw_arrow(ax, 0.72, 0.855, 0.76, 0.855);

draw_box(ax, 0.34, 0.68, 0.32, 0.07, 'log10 密度变换与百分位归一化', [0.95 0.93 1.0], edgeColor);
draw_arrow(ax, 0.85, 0.82, 0.50, 0.75);

draw_box(ax, 0.06, 0.49, 0.26, 0.12, sprintf('路线一：体绘制与传递函数设计\n输出：关键帧体绘制图、传递函数对比图'), routeColor, edgeColor);
draw_box(ax, 0.37, 0.49, 0.26, 0.12, sprintf('路线二：统计分析与直方图热力图\n输出：统计曲线、histogram、heatmap'), routeColor, edgeColor);
draw_box(ax, 0.68, 0.49, 0.26, 0.12, sprintf('路线三：高密度筛选与结构分析\n输出：P99 MIP、等值面、结构指标'), routeColor, edgeColor);

draw_arrow(ax, 0.50, 0.68, 0.19, 0.61);
draw_arrow(ax, 0.50, 0.68, 0.50, 0.61);
draw_arrow(ax, 0.50, 0.68, 0.81, 0.61);

draw_box(ax, 0.30, 0.30, 0.40, 0.08, '交互式 linked brushing 仪表盘', finalColor, edgeColor);
draw_arrow(ax, 0.19, 0.49, 0.40, 0.38);
draw_arrow(ax, 0.50, 0.49, 0.50, 0.38);
draw_arrow(ax, 0.81, 0.49, 0.60, 0.38);

draw_box(ax, 0.32, 0.14, 0.36, 0.08, '宇宙密度演化规律总结', [1.00 0.94 0.94], edgeColor);
draw_arrow(ax, 0.50, 0.30, 0.50, 0.22);

text(ax, 0.5, 0.96, 'Nyx 宇宙密度演化可视分析总体流程图', ...
    'HorizontalAlignment', 'center', 'FontSize', 20, 'FontWeight', 'bold', 'Color', [0.08 0.16 0.28]);

exportgraphics(fig, outFile, 'Resolution', 220);
close(fig);
end

function draw_transfer_function(outFile)
x = linspace(0, 1, 500);
voidAlpha = 0.035 + 0.12 .* smoothstep(0.02, 0.30, 1 - x) + 0.06 .* smoothstep(0.20, 0.55, x);
filamentAlpha = 0.02 .* smoothstep(0.08, 0.34, x) + 0.18 .* smoothstep(0.34, 0.82, x);
nodeAlpha = 0.02 .* smoothstep(0.20, 0.50, x) + 0.34 .* smoothstep(0.72, 0.98, x);
voidAlpha = min(voidAlpha, 0.55);
filamentAlpha = min(filamentAlpha, 0.55);
nodeAlpha = min(nodeAlpha, 0.55);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1100 720]);
tiledlayout(5, 1, 'Padding', 'compact', 'TileSpacing', 'compact');

ax = nexttile([4 1]);
plot(ax, x, voidAlpha, 'LineWidth', 2.4, 'Color', [0.15 0.42 0.80]); hold(ax, 'on');
plot(ax, x, filamentAlpha, 'LineWidth', 2.4, 'Color', [0.75 0.20 0.55]);
plot(ax, x, nodeAlpha, 'LineWidth', 2.4, 'Color', [0.95 0.48 0.10]);
grid(ax, 'on');
xlabel(ax, 'normalized log-density');
ylabel(ax, 'opacity');
title(ax, '三种体绘制传递函数设计对比', 'FontWeight', 'bold');
legend(ax, {'空洞观察型', '丝状结构型', '高密度节点型'}, 'Location', 'northwest');
ylim(ax, [0 0.42]);
xlim(ax, [0 1]);

ax2 = nexttile;
cmap = custom_nyx_colormap(256);
imagesc(ax2, linspace(0, 1, 256), [0 1], reshape(cmap, [1 256 3]));
set(ax2, 'YTick', [], 'XLim', [0 1]);
xlabel(ax2, '自定义 Nyx LUT 颜色映射');
box(ax2, 'on');

exportgraphics(fig, outFile, 'Resolution', 220);
close(fig);
end

function write_representative_stats(projectRoot, outFile)
statsFile = fullfile(projectRoot, 'data', 'processed', 'density_stats.csv');
T = readtable(statsFile, 'TextType', 'string');
targets = [0; 30; 60; 99];
rows = zeros(numel(targets), 1);
for i = 1:numel(targets)
    [~, rows(i)] = min(abs(T.time_index - targets(i)));
end
S = T(rows, :);
R = table();
R.time_step = S.time_index;
R.mean_density = S.mean_density;
R.std_density = S.std_density;
R.max_density = S.max_density;
R.P05 = S.p05_density;
R.P50 = S.p50_density;
R.P95 = S.p95_density;
R.P99 = S.p99_density;
R.P99_over_mean = S.p99_density ./ S.mean_density;
R.P99_minus_P01 = S.p99_density - S.p01_density;
writetable(R, outFile);
end

function draw_box(ax, x, y, w, h, label, faceColor, edgeColor)
rectangle(ax, 'Position', [x y w h], 'Curvature', 0.08, 'FaceColor', faceColor, ...
    'EdgeColor', edgeColor, 'LineWidth', 1.4);
text(ax, x + w/2, y + h/2, label, 'HorizontalAlignment', 'center', ...
    'VerticalAlignment', 'middle', 'FontSize', 12, 'FontWeight', 'bold', ...
    'Color', [0.10 0.15 0.22]);
end

function draw_arrow(ax, x1, y1, x2, y2)
annotation(ax.Parent, 'arrow', [x1 x2], [y1 y2], 'LineWidth', 1.4, 'Color', [0.22 0.30 0.42]);
end
