function step8_density_gradient_phase_space(projectRoot)
%STEP8_DENSITY_GRADIENT_PHASE_SPACE density-gradient 二维相空间分析。
%   将 normalized log-density 与 normalized gradient magnitude 组合为二维
%   相空间热力图，用于区分空洞背景、丝状边界、节点边界和致密核心。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end

rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '08_density_gradient_phase_space');
reportDir = fullfile(projectRoot, 'results', 'report_figures');
ensure_folder(outDir); ensure_folder(reportDir);

files = list_dat_files(rawDir);
timeIndex = arrayfun(@(f) parse_time_index(f.name), files);
targets = [0 30 60 99];
selIdx = choose_closest_indices(timeIndex, targets);

densityBins = 120;
gradientBins = 120;
figCompare = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1200 980]);
tiledlayout(2, 2, 'Padding', 'compact', 'TileSpacing', 'compact');

cache = struct([]);
for k = 1:numel(selIdx)
    idx = selIdx(k);
    [Vn, gradN, logV] = load_density_gradient(files(idx));
    cache(k).idx = idx;
    cache(k).time = timeIndex(idx);
    cache(k).filename = files(idx).name;
    cache(k).Vn = Vn;
    cache(k).gradN = gradN;
    cache(k).logV = logV;

    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 650]);
    draw_phase_space(gca, Vn, gradN, densityBins, gradientBins, ...
        sprintf('Density-gradient phase space  t=%04d', timeIndex(idx)));
    save_figure(fig, fullfile(outDir, sprintf('density_gradient_phase_t%04d.png', timeIndex(idx))));
    close(fig);

    nexttile;
    draw_phase_space(gca, Vn, gradN, densityBins, gradientBins, ...
        sprintf('t=%04d', timeIndex(idx)));
end

sgtitle('Density-gradient phase space comparison', 'FontWeight', 'bold');
comparePath = fullfile(outDir, 'density_gradient_phase_compare.png');
save_figure(figCompare, comparePath);
close(figCompare);
copyfile(comparePath, fullfile(reportDir, 'density_gradient_phase_compare.png'));

% 对最接近 t0099 的时间步做二维相空间刷选，并输出空间 MIP。
[~, lastLocal] = min(abs([cache.time] - 99));
selectionPath = draw_phase_space_selection(cache(lastLocal), outDir);
copyfile(selectionPath, fullfile(reportDir, 'phase_space_selection_t0099.png'));

fprintf('Step 8 完成：density-gradient 相空间结果已保存到 %s\n', outDir);
end

function [Vn, gradN, logV] = load_density_gradient(fileInfo)
V = read_nyx_dat(fullfile(fileInfo.folder, fileInfo.name));
logV = log10(max(V, eps('single')));
Vn = normalize_percentile(logV, 5, 99.7);
gradMag = compute_gradient_magnitude(Vn);
gradN = normalize_percentile(gradMag, 1, 99);
end

function draw_phase_space(ax, Vn, gradN, densityBins, gradientBins, titleText)
x = double(Vn(:));
y = double(gradN(:));
valid = isfinite(x) & isfinite(y);
x = x(valid); y = y(valid);

inputXEdges = linspace(0, 1, densityBins + 1);
inputYEdges = linspace(0, 1, gradientBins + 1);
[counts, xEdges, yEdges] = histcounts2(x, y, inputXEdges, inputYEdges);
xCenters = 0.5 .* (xEdges(1:end-1) + xEdges(2:end));
yCenters = 0.5 .* (yEdges(1:end-1) + yEdges(2:end));

imagesc(ax, xCenters, yCenters, log10(counts' + 1));
axis(ax, 'xy');
xlim(ax, [0 1]); ylim(ax, [0 1]);
colormap(ax, parula(256));
colorbar(ax);
xlabel(ax, 'Normalized log-density');
ylabel(ax, 'Normalized gradient magnitude');
title(ax, titleText, 'FontWeight', 'bold');
grid(ax, 'on');
hold(ax, 'on');

draw_box(ax, [0.00 0.00 0.25 0.25], [0.20 0.45 0.95], 'Void bg');
draw_box(ax, [0.35 0.55 0.40 0.45], [0.10 0.70 0.50], 'Filament bd.');
draw_box(ax, [0.75 0.45 0.25 0.55], [0.90 0.25 0.10], 'Node bd.');
draw_box(ax, [0.85 0.00 0.15 0.45], [0.55 0.10 0.10], 'Dense core');
hold(ax, 'off');
end

function draw_box(ax, pos, color, labelText)
rectangle(ax, 'Position', pos, 'EdgeColor', color, 'LineWidth', 1.5, 'LineStyle', '--');
text(ax, pos(1) + 0.01, pos(2) + pos(4) - 0.04, labelText, ...
    'Color', color, 'FontSize', 8, 'FontWeight', 'bold', ...
    'BackgroundColor', 'w', 'Margin', 1);
end

function outputPath = draw_phase_space_selection(cacheItem, outDir)
Vn = cacheItem.Vn;
gradN = cacheItem.gradN;
logV = cacheItem.logV;
t = cacheItem.time;

masks = { ...
    Vn < 0.25 & gradN < 0.25, ...
    Vn > 0.35 & Vn < 0.75 & gradN > 0.55, ...
    Vn > 0.75 & gradN > 0.45, ...
    Vn > 0.85 & gradN < 0.45};
titles = {'Void background', 'Filament boundary', 'Node boundary', 'Dense core'};

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1150 920]);
tiledlayout(2, 2, 'Padding', 'compact', 'TileSpacing', 'compact');
for i = 1:4
    nexttile;
    mip = masked_mip(logV, masks{i}, 3);
    imagesc(mip');
    axis image off;
    colormap(gca, custom_nyx_colormap(256));
    colorbar;
    ratio = nnz(masks{i}) ./ numel(masks{i}) .* 100;
    title(sprintf('%s  (%.2f%% voxels)', titles{i}, ratio), 'FontWeight', 'bold');
end
sgtitle(sprintf('Density-gradient phase-space selections  t=%04d', t), 'FontWeight', 'bold');
outputPath = fullfile(outDir, 'phase_space_selection_t0099.png');
save_figure(fig, outputPath);
close(fig);
end

function M = masked_mip(logV, mask, dim)
if nnz(mask) == 0
    sz = size(logV);
    if dim == 1, M = zeros(sz(2), sz(3)); elseif dim == 2, M = zeros(sz(1), sz(3)); else, M = zeros(sz(1), sz(2)); end
    return;
end
tmp = double(logV);
tmp(~mask) = -inf;
M = squeeze(max(tmp, [], dim));
M(~isfinite(M)) = min(double(logV(:)));
end

function idx = choose_closest_indices(timeIndex, targets)
idx = zeros(size(targets));
for i = 1:numel(targets)
    [~, idx(i)] = min(abs(timeIndex - targets(i)));
end
idx = unique(idx, 'stable');
end

function files = list_dat_files(rawDir)
files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
if isempty(files), error('data/raw 下没有可用 .dat 文件。'); end
[~, idx] = sort({files.name});
files = files(idx);
end

function ti = parse_time_index(name)
tok = regexp(name, '\d+', 'match', 'once');
if isempty(tok), ti = NaN; else, ti = str2double(tok); end
end
