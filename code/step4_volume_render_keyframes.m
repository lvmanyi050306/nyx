function step4_volume_render_keyframes(projectRoot)
%STEP4_VOLUME_RENDER_KEYFRAMES 代表时间步体绘制和传递函数对比。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '04_volume_render');
ensure_folder(outDir);

files = list_dat_files(rawDir);
timeIdx = arrayfun(@(f) parse_time_index(f.name), files);
targets = [0 30 60 99];
pick = zeros(size(targets));
for i = 1:numel(targets)
    [~, pick(i)] = min(abs(timeIdx - targets(i)));
end
pick = unique(pick, 'stable');

imgs = cell(numel(pick), 1);
labels = strings(numel(pick), 1);
for i = 1:numel(pick)
    f = files(pick(i));
    V = read_nyx_dat(fullfile(f.folder, f.name));
    logV = log10(max(V, eps('single')));
    Vn = normalize_percentile(logV, 5, 99.7);
    imgs{i} = volume_render_alpha_composite(Vn, 'filament');
    labels(i) = sprintf('t%04d', timeIdx(pick(i)));
    imwrite(imgs{i}, fullfile(outDir, sprintf('volume_t%04d.png', timeIdx(pick(i)))));
    fprintf('体绘制完成：%s\n', f.name);
end

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1000 900]);
tiledlayout(2, 2, 'Padding', 'compact', 'TileSpacing', 'compact');
for i = 1:numel(imgs)
    nexttile; imshow(imgs{i}); title(sprintf('Volume rendering %s', labels(i)), 'FontWeight', 'bold');
end
sgtitle('Nyx keyframe volume rendering comparison');
save_figure(fig, fullfile(outDir, 'volume_keyframes_compare.png')); close(fig);

% 最接近 0099 的时间步用于传递函数对比。
[~, idx99] = min(abs(timeIdx - 99));
V = read_nyx_dat(fullfile(files(idx99).folder, files(idx99).name));
logV = log10(max(V, eps('single')));
Vn = normalize_percentile(logV, 5, 99.7);
modes = {'void', 'filament', 'node'};
titles = {'空洞观察型', '丝状结构型', '高密度节点型'};
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1280 440]);
tiledlayout(1, 3, 'Padding', 'compact', 'TileSpacing', 'compact');
for i = 1:3
    img = volume_render_alpha_composite(Vn, modes{i});
    nexttile; imshow(img); title(sprintf('%s  t%04d', titles{i}, timeIdx(idx99)), 'FontWeight', 'bold');
end
sgtitle('Transfer function comparison');
save_figure(fig, fullfile(outDir, 'transfer_function_compare_t0099.png')); close(fig);
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
