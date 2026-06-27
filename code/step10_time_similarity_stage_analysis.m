function step10_time_similarity_stage_analysis(projectRoot)
%STEP10_TIME_SIMILARITY_STAGE_ANALYSIS 时间步相似性矩阵与演化阶段划分。
%   将每个时间步的 log-density histogram 看作概率向量，计算时间步之间
%   的余弦相似性，并基于 distance_from_start 进行可解释的四阶段划分。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end

rawDir = fullfile(projectRoot, 'data', 'raw');
procDir = fullfile(projectRoot, 'data', 'processed');
outDir = fullfile(projectRoot, 'results', '10_time_similarity');
reportDir = fullfile(projectRoot, 'results', 'report_figures');
ensure_folder(procDir); ensure_folder(outDir); ensure_folder(reportDir);

files = list_dat_files(rawDir);
timeIndex = arrayfun(@(f) parse_time_index(f.name), files);
N = numel(files);
numBins = 120;

% 第一遍读取用于确定统一 log-density bins。
globalMin = inf;
globalMax = -inf;
for i = 1:N
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    logV = log10(max(V, eps('single')));
    vals = double(logV(isfinite(logV)));
    globalMin = min(globalMin, min(vals));
    globalMax = max(globalMax, max(vals));
end
if ~isfinite(globalMin) || ~isfinite(globalMax) || globalMax <= globalMin
    error('无法确定 log-density histogram 范围。');
end
edges = linspace(globalMin, globalMax, numBins + 1);

H = zeros(N, numBins);
for i = 1:N
    fprintf('Step 10 histogram 向量化：%s (%d/%d)\n', files(i).name, i, N);
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    logV = log10(max(V, eps('single')));
    counts = histcounts(double(logV(:)), edges, 'Normalization', 'probability');
    H(i, :) = counts;
end

S = cosine_similarity_matrix(H);
D = 1 - S;
distanceFromStart = D(:, 1);
adjacentDistance = nan(N, 1);
if N > 1
    adjacentDistance(1:N-1) = 1 - diag(S, 1);
end

[stageLabel, splitIdx] = simple_stage_segmentation(distanceFromStart);

time_index = reshape(timeIndex, [], 1);
filename = reshape(string({files.name}), [], 1);
distance_from_start = distanceFromStart(:);
adjacent_distance = adjacentDistance(:);
stage_label = stageLabel(:);
T = table(time_index, filename, distance_from_start, adjacent_distance, stage_label);
writetable(T, fullfile(procDir, 'time_similarity_stage.csv'));
save(fullfile(procDir, 'time_similarity_stage.mat'), 'H', 'S', 'D', 'T', 'edges', 'splitIdx');

draw_similarity_matrix(S, timeIndex, outDir, reportDir);
draw_distance_matrix(D, timeIndex, outDir);
draw_adjacent_curve(timeIndex, adjacentDistance, splitIdx, outDir, reportDir);
draw_stage_segmentation(timeIndex, distanceFromStart, adjacentDistance, stageLabel, splitIdx, outDir, reportDir);

fprintf('Step 10 完成：时间步相似性与阶段划分结果已保存到 %s\n', outDir);
end

function draw_similarity_matrix(S, timeIndex, outDir, reportDir)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 650]);
imagesc(timeIndex, timeIndex, S);
axis image;
colormap(parula(256));
colorbar;
xlabel('time step'); ylabel('time step');
title('Time-step cosine similarity matrix', 'FontWeight', 'bold');
simPath = fullfile(outDir, 'time_step_similarity_matrix.png');
save_figure(fig, simPath);
close(fig);
copyfile(simPath, fullfile(reportDir, 'time_step_similarity_matrix.png'));
end

function draw_distance_matrix(D, timeIndex, outDir)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 760 650]);
imagesc(timeIndex, timeIndex, D);
axis image;
colormap(parula(256));
colorbar;
xlabel('time step'); ylabel('time step');
title('Time-step distance matrix: 1 - cosine similarity', 'FontWeight', 'bold');
save_figure(fig, fullfile(outDir, 'time_step_distance_matrix.png'));
close(fig);
end

function draw_adjacent_curve(timeIndex, adjacentDistance, splitIdx, outDir, reportDir)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 960 540]);
plot(timeIndex, adjacentDistance, 'LineWidth', 1.6, 'Color', [0.15 0.35 0.75]); hold on;
for i = 1:numel(splitIdx)
    xline(timeIndex(splitIdx(i)), '--', 'LineWidth', 1.2, 'Color', [0.75 0.15 0.15]);
end
grid on;
xlabel('time step'); ylabel('adjacent distance');
title('Adjacent time-step distribution change', 'FontWeight', 'bold');
legend({'1 - cos(H_t, H_{t+1})','stage split'}, 'Location', 'best');
curvePath = fullfile(outDir, 'adjacent_time_change_curve.png');
save_figure(fig, curvePath);
close(fig);
copyfile(curvePath, fullfile(reportDir, 'adjacent_time_change_curve.png'));
end

function draw_stage_segmentation(timeIndex, distanceFromStart, adjacentDistance, stageLabel, splitIdx, outDir, reportDir)
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1000 600]);
ax = axes(fig);
hold(ax, 'on');

stageNames = ["Early stage", "Transition stage", "Structure enhancement stage", "Late stage"];
stageColors = [ ...
    0.86 0.92 1.00; ...
    0.88 1.00 0.93; ...
    1.00 0.94 0.82; ...
    1.00 0.88 0.88];

yMax = max([distanceFromStart(:); adjacentDistance(isfinite(adjacentDistance))]);
if isempty(yMax) || yMax <= 0, yMax = 1; end
yMax = yMax * 1.12;

for s = 1:4
    idx = find(stageLabel == stageNames(s));
    if isempty(idx), continue; end
    x0 = timeIndex(idx(1));
    x1 = timeIndex(idx(end));
    patch(ax, [x0 x1 x1 x0], [0 0 yMax yMax], stageColors(s, :), ...
        'EdgeColor', 'none', 'FaceAlpha', 0.45);
    text(ax, mean([x0 x1]), yMax * 0.95, stageNames(s), ...
        'HorizontalAlignment', 'center', 'FontSize', 8, 'FontWeight', 'bold');
end

plot(ax, timeIndex, distanceFromStart, 'LineWidth', 1.8, 'Color', [0.15 0.20 0.45]);
plot(ax, timeIndex, adjacentDistance, 'LineWidth', 1.3, 'Color', [0.75 0.25 0.10]);
for i = 1:numel(splitIdx)
    xline(ax, timeIndex(splitIdx(i)), '--', 'Color', [0.25 0.25 0.25], 'LineWidth', 1.1);
end
ylim(ax, [0 yMax]);
grid(ax, 'on');
xlabel(ax, 'time step'); ylabel(ax, 'distribution distance');
title(ax, 'Evolution stage segmentation from log-density histogram similarity', 'FontWeight', 'bold');
legend(ax, {'distance from t0000','adjacent distance'}, 'Location', 'best');
hold(ax, 'off');

stagePath = fullfile(outDir, 'evolution_stage_segmentation.png');
save_figure(fig, stagePath);
close(fig);
copyfile(stagePath, fullfile(reportDir, 'evolution_stage_segmentation.png'));
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
