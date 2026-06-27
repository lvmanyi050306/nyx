function step9_hessian_cosmic_web_classification(projectRoot)
%STEP9_HESSIAN_COSMIC_WEB_CLASSIFICATION Hessian 特征值宇宙网结构粗分类。
%   基于 log-density 的二阶局部变化，将体素粗略分为 Void、Sheet、
%   Filament 和 Node。该方法用于课程可视化分析，不作为严格天体物理结论。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end

rawDir = fullfile(projectRoot, 'data', 'raw');
procDir = fullfile(projectRoot, 'data', 'processed');
outDir = fullfile(projectRoot, 'results', '09_hessian_cosmic_web');
reportDir = fullfile(projectRoot, 'results', 'report_figures');
ensure_folder(procDir); ensure_folder(outDir); ensure_folder(reportDir);

files = list_dat_files(rawDir);
timeIndex = arrayfun(@(f) parse_time_index(f.name), files);
targets = [0 30 60 99];
selIdx = choose_closest_indices(timeIndex, targets);
N = numel(files);

time_index = reshape(timeIndex, [], 1);
filename = reshape(string({files.name}), [], 1);
void_fraction = zeros(N, 1);
sheet_fraction = zeros(N, 1);
filament_fraction = zeros(N, 1);
node_fraction = zeros(N, 1);

classCache = containers.Map('KeyType', 'double', 'ValueType', 'any');
logCache = containers.Map('KeyType', 'double', 'ValueType', 'any');

for i = 1:N
    fprintf('Step 9 Hessian 分类：%s (%d/%d)\n', files(i).name, i, N);
    [classVol, logVs] = classify_one_frame(files(i));
    total = numel(classVol);
    void_fraction(i) = nnz(classVol == 1) / total;
    sheet_fraction(i) = nnz(classVol == 2) / total;
    filament_fraction(i) = nnz(classVol == 3) / total;
    node_fraction(i) = nnz(classVol == 4) / total;

    if any(selIdx == i) || i == selIdx(end)
        classCache(i) = classVol;
        logCache(i) = logVs;
    end
end

T = table(time_index, filename, void_fraction, sheet_fraction, filament_fraction, node_fraction);
writetable(T, fullfile(procDir, 'hessian_cosmic_web_fraction.csv'));

draw_class_slices(selIdx, timeIndex, classCache, outDir, reportDir);
draw_fraction_curve(timeIndex, void_fraction, sheet_fraction, filament_fraction, node_fraction, outDir, reportDir);
draw_filament_node_mip(selIdx(end), timeIndex(selIdx(end)), classCache, logCache, outDir, reportDir);

fprintf('Step 9 完成：Hessian 宇宙网分类结果已保存到 %s\n', outDir);
end

function [classVol, logVs] = classify_one_frame(fileInfo)
V = read_nyx_dat(fullfile(fileInfo.folder, fileInfo.name));
logV = log10(max(V, eps('single')));
logVs = smooth_log_density(logV, 1.2);
logVs = downsample_volume(logVs, 64);
logVs = normalize_percentile(logVs, 2, 99);

[l1, l2, l3] = compute_hessian_eigenvalues_3d(logVs);
vals = abs(double([l1(:); l2(:); l3(:)]));
vals = vals(isfinite(vals));
if isempty(vals)
    tau = 0.03;
else
    tau = max(local_prctile(vals, 70), 1e-4);
end
classVol = classify_cosmic_web_hessian(l1, l2, l3, tau);
end

function Vs = smooth_log_density(V, sigma)
if exist('imgaussfilt3', 'file') == 2
    Vs = imgaussfilt3(V, sigma);
elseif exist('smooth3', 'file') == 2
    Vs = smooth3(V, 'gaussian', 5);
else
    % 无 Image Processing Toolbox 时使用简单 separable Gaussian 卷积降级。
    radius = max(1, ceil(3 * sigma));
    x = -radius:radius;
    g = exp(-(x.^2) ./ (2 * sigma^2));
    g = g ./ sum(g);
    Vs = convn(single(V), reshape(g, [], 1, 1), 'same');
    Vs = convn(Vs, reshape(g, 1, [], 1), 'same');
    Vs = convn(Vs, reshape(g, 1, 1, []), 'same');
end
Vs = single(Vs);
end

function Vd = downsample_volume(V, maxSize)
sz = size(V);
if max(sz) <= maxSize
    Vd = V;
    return;
end

scale = maxSize / max(sz);
if exist('imresize3', 'file') == 2
    Vd = imresize3(V, scale, 'linear');
else
    stride = max(1, ceil(max(sz) / maxSize));
    Vd = V(1:stride:end, 1:stride:end, 1:stride:end);
end
Vd = single(Vd);
end

function draw_class_slices(selIdx, timeIndex, classCache, outDir, reportDir)
figCompare = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1100 900]);
tiledlayout(2, 2, 'Padding', 'compact', 'TileSpacing', 'compact');

for k = 1:numel(selIdx)
    idx = selIdx(k);
    classVol = classCache(idx);
    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 720 650]);
    draw_class_slice(gca, classVol, sprintf('Hessian class center slice  t=%04d', timeIndex(idx)));
    save_figure(fig, fullfile(outDir, sprintf('hessian_class_slice_t%04d.png', timeIndex(idx))));
    close(fig);

    nexttile;
    draw_class_slice(gca, classVol, sprintf('t=%04d', timeIndex(idx)));
end

sgtitle('Hessian cosmic web classification slices', 'FontWeight', 'bold');
comparePath = fullfile(outDir, 'hessian_class_slice_compare.png');
save_figure(figCompare, comparePath);
close(figCompare);
copyfile(comparePath, fullfile(reportDir, 'hessian_class_slice_compare.png'));
end

function draw_class_slice(ax, classVol, titleText)
z = round(size(classVol, 3) / 2);
imagesc(ax, classVol(:, :, z)');
axis(ax, 'image'); axis(ax, 'off');
colormap(ax, hessian_class_colormap());
try
    clim(ax, [0.5 4.5]);
catch
    caxis(ax, [0.5 4.5]);
end
cb = colorbar(ax, 'Ticks', 1:4, 'TickLabels', {'Void','Sheet','Filament','Node'});
cb.Label.String = 'Class';
title(ax, titleText, 'FontWeight', 'bold');
end

function draw_fraction_curve(timeIndex, vf, sf, ff, nf, outDir, reportDir)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 960 560]);
plot(timeIndex, vf, 'LineWidth', 1.6); hold on;
plot(timeIndex, sf, 'LineWidth', 1.6);
plot(timeIndex, ff, 'LineWidth', 1.6);
plot(timeIndex, nf, 'LineWidth', 1.6);
grid on;
xlabel('time step'); ylabel('voxel fraction');
title('Hessian cosmic web class fractions');
legend({'Void','Sheet','Filament','Node'}, 'Location', 'best');
curvePath = fullfile(outDir, 'hessian_class_fraction_curve.png');
save_figure(fig, curvePath);
close(fig);
copyfile(curvePath, fullfile(reportDir, 'hessian_class_fraction_curve.png'));
end

function draw_filament_node_mip(idx, timeStep, classCache, logCache, outDir, reportDir)
classVol = classCache(idx);
logVs = logCache(idx);
mask = classVol == 3 | classVol == 4;
tmp = double(logVs);
tmp(~mask) = -inf;
mip = squeeze(max(tmp, [], 3));
mip(~isfinite(mip)) = min(double(logVs(:)));

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 660]);
imagesc(mip');
axis image off;
colormap(custom_nyx_colormap(256));
colorbar;
title(sprintf('Filament + Node MIP from Hessian classes  t=%04d', timeStep), 'FontWeight', 'bold');
mipPath = fullfile(outDir, 'filament_node_mip_t0099.png');
save_figure(fig, mipPath);
close(fig);
copyfile(mipPath, fullfile(reportDir, 'filament_node_mip_t0099.png'));
end

function cmap = hessian_class_colormap()
cmap = [ ...
    0.05 0.18 0.55;  % Void 深蓝
    0.00 0.65 0.75;  % Sheet 青色
    0.95 0.55 0.12;  % Filament 橙色
    0.85 0.10 0.12]; % Node 红色
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

function q = local_prctile(x, p)
x = sort(x(:));
if isempty(x), q = nan(size(p)); return; end
pos = 1 + (numel(x) - 1) .* p(:)' ./ 100;
lo = floor(pos); hi = ceil(pos); w = pos - lo;
q = (1 - w) .* x(lo)' + w .* x(hi)';
end
