function step5_high_density_selection(projectRoot)
%STEP5_HIGH_DENSITY_SELECTION P99 高密度区域筛选、投影与等值面。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '05_high_density');
ensure_folder(outDir);

files = list_dat_files(rawDir);
timeIdx = arrayfun(@(f) parse_time_index(f.name), files);
targets = [0 60 99];
pick = zeros(size(targets));
for i = 1:numel(targets)
    [~, pick(i)] = min(abs(timeIdx - targets(i)));
end
pick = unique(pick, 'stable');

for i = 1:numel(pick)
    f = files(pick(i));
    V = read_nyx_dat(fullfile(f.folder, f.name));
    thr = local_prctile(double(V(:)), 99);
    mask = V >= thr;
    ratio = nnz(mask) / numel(mask);
    logV = log10(max(V, eps('single')));
    masked = logV;
    masked(~mask) = min(logV(:));

    mipX = squeeze(max(masked, [], 1));
    mipY = squeeze(max(masked, [], 2));
    mipZ = squeeze(max(masked, [], 3));

    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1200 430]);
    tiledlayout(1, 3, 'Padding', 'compact', 'TileSpacing', 'compact');
    nexttile; imagesc(mipX'); axis image off; title('X-MIP'); colormap hot; colorbar;
    nexttile; imagesc(mipY'); axis image off; title('Y-MIP'); colormap hot; colorbar;
    nexttile; imagesc(mipZ'); axis image off; title('Z-MIP'); colormap hot; colorbar;
    sgtitle(sprintf('Top 1%% high-density voxels t%04d: %d voxels, %.3f%%', timeIdx(pick(i)), nnz(mask), ratio * 100));
    save_figure(fig, fullfile(outDir, sprintf('top1_percent_t%04d.png', timeIdx(pick(i)))));
    close(fig);
end

% t0099 或最后时间步等值面。
[~, idx99] = min(abs(timeIdx - 99));
V = read_nyx_dat(fullfile(files(idx99).folder, files(idx99).name));
draw_p99_isosurface(V, timeIdx(idx99), fullfile(outDir, 'top1_percent_isosurface_t0099.png'));
draw_nested_isosurfaces(V, timeIdx(idx99), fullfile(outDir, 'nested_isosurfaces_t0099.png'));
end

function draw_p99_isosurface(V, ti, outFile)
if exist('isosurface', 'file') ~= 2
    warning('当前 MATLAB 不支持 isosurface，跳过三维等值面。');
    return;
end
thr = local_prctile(double(V(:)), 99);
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 660]);
p = patch(isosurface(V, thr));
isonormals(V, p);
p.FaceColor = [1.0 0.72 0.18]; p.EdgeColor = 'none'; p.FaceAlpha = 0.86;
axis equal tight off; view(3); camlight headlight; lighting gouraud;
title(sprintf('P99 high-density isosurface  t%04d', ti), 'FontWeight', 'bold');
save_figure(fig, outFile); close(fig);
end

function draw_nested_isosurfaces(V, ti, outFile)
if exist('isosurface', 'file') ~= 2
    return;
end
levels = local_prctile(double(V(:)), [90 95 99]);
colors = [0.18 0.55 0.95; 0.86 0.30 0.65; 1.00 0.78 0.18];
alphas = [0.18 0.32 0.82];
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 820 720]);
hold on;
for i = 1:numel(levels)
    p = patch(isosurface(V, levels(i)));
    isonormals(V, p);
    p.FaceColor = colors(i, :);
    p.EdgeColor = 'none';
    p.FaceAlpha = alphas(i);
end
axis equal tight off; view(3); camlight headlight; lighting gouraud;
title(sprintf('Nested density isosurfaces P90/P95/P99  t%04d', ti), 'FontWeight', 'bold');
legend({'P90 丝状外壳','P95 聚集区域','P99 极高密度节点'}, 'Location', 'southoutside', 'Orientation', 'horizontal');
save_figure(fig, outFile); close(fig);
end

function files = list_dat_files(rawDir)
files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
if isempty(files), error('没有可用 .dat 文件。'); end
[~, idx] = sort({files.name}); files = files(idx);
end

function ti = parse_time_index(name)
tok = regexp(name, '\d+', 'match', 'once');
if isempty(tok), ti = NaN; else, ti = str2double(tok); end
end

function q = local_prctile(x, p)
x = x(isfinite(x)); x = sort(x(:));
pos = 1 + (numel(x) - 1) .* p(:)' ./ 100;
lo = floor(pos); hi = ceil(pos); w = pos - lo;
q = (1 - w) .* x(lo)' + w .* x(hi)';
end
