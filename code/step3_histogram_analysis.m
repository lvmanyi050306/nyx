function step3_histogram_analysis(projectRoot)
%STEP3_HISTOGRAM_ANALYSIS 分析代表时间步与全时间步 log-density 直方图。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '02_histograms');
ensure_folder(outDir);

files = list_dat_files(rawDir);
timeIdx = arrayfun(@(f) parse_time_index(f.name), files);
targets = [0 30 60 99];
pick = zeros(size(targets));
for i = 1:numel(targets)
    [~, pick(i)] = min(abs(timeIdx - targets(i)));
end
pick = unique(pick, 'stable');

keyLogs = cell(numel(pick), 1);
keyLabels = strings(numel(pick), 1);
for i = 1:numel(pick)
    f = files(pick(i));
    V = read_nyx_dat(fullfile(f.folder, f.name));
    keyLogs{i} = log10(max(double(V(:)), eps));
    keyLabels(i) = sprintf('t%04d', timeIdx(pick(i)));

    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 500]);
    histogram(keyLogs{i}, 120, 'Normalization', 'probability', 'FaceColor', [0.25 0.35 0.72], 'EdgeColor', 'none');
    grid on; xlabel('log10(density)'); ylabel('probability');
    title(sprintf('Log-density histogram: %s', f.name));
    save_figure(fig, fullfile(outDir, sprintf('histogram_t%04d.png', timeIdx(pick(i)))));
    close(fig);
end

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 860 540]);
hold on;
for i = 1:numel(keyLogs)
    histogram(keyLogs{i}, 120, 'Normalization', 'probability', 'DisplayStyle', 'stairs', 'LineWidth', 1.6);
end
grid on; xlabel('log10(density)'); ylabel('probability');
title('Keyframe log-density histogram comparison');
legend(cellstr(keyLabels), 'Location', 'best');
save_figure(fig, fullfile(outDir, 'histogram_compare_keyframes.png')); close(fig);

% 全时间步统一 bin，用二维热力图展示概率分布随时间演化。
sampleMin = inf; sampleMax = -inf;
for i = 1:numel(files)
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    lx = log10(max(double(V(:)), eps));
    sampleMin = min(sampleMin, min(lx));
    sampleMax = max(sampleMax, max(lx));
end
edges = linspace(sampleMin, sampleMax, 121);
centers = (edges(1:end-1) + edges(2:end)) / 2;
H = zeros(numel(centers), numel(files));
for i = 1:numel(files)
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    lx = log10(max(double(V(:)), eps));
    counts = histcounts(lx, edges, 'Normalization', 'probability');
    H(:, i) = counts(:);
    fprintf('直方图热力图累计：%s (%d/%d)\n', files(i).name, i, numel(files));
end

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 960 620]);
imagesc(timeIdx, centers, H);
set(gca, 'YDir', 'normal');
colormap(parula); colorbar;
xlabel('time step'); ylabel('log10(density)');
title('Time-density histogram heatmap');
save_figure(fig, fullfile(outDir, 'time_density_heatmap.png')); close(fig);

save(fullfile(outDir, 'histogram_heatmap_data.mat'), 'H', 'edges', 'centers', 'timeIdx');
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
