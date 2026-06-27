function step2_statistics_all_frames(projectRoot)
%STEP2_STATISTICS_ALL_FRAMES 计算全部时间步的密度统计量。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
procDir = fullfile(projectRoot, 'data', 'processed');
outDir = fullfile(projectRoot, 'results', '03_statistics');
ensure_folder(procDir); ensure_folder(outDir);

files = list_dat_files(rawDir);
N = numel(files);

time_index = zeros(N, 1);
filename = strings(N, 1);
mean_density = zeros(N, 1); std_density = zeros(N, 1);
min_density = zeros(N, 1); max_density = zeros(N, 1);
p01_density = zeros(N, 1); p05_density = zeros(N, 1); p50_density = zeros(N, 1);
p95_density = zeros(N, 1); p99_density = zeros(N, 1); p997_density = zeros(N, 1); p999_density = zeros(N, 1);
mean_log_density = zeros(N, 1); std_log_density = zeros(N, 1);
skew_log_density = zeros(N, 1); kurtosis_log_density = zeros(N, 1);

for i = 1:N
    filename(i) = string(files(i).name);
    time_index(i) = parse_time_index(files(i).name, i - 1);
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    x = double(V(:));
    logx = log10(max(x, eps));

    mean_density(i) = mean(x, 'omitnan');
    std_density(i) = std(x, 'omitnan');
    min_density(i) = min(x);
    max_density(i) = max(x);
    pct = local_prctile(x, [1 5 50 95 99 99.7 99.9]);
    p01_density(i) = pct(1); p05_density(i) = pct(2); p50_density(i) = pct(3);
    p95_density(i) = pct(4); p99_density(i) = pct(5); p997_density(i) = pct(6); p999_density(i) = pct(7);

    mean_log_density(i) = mean(logx, 'omitnan');
    std_log_density(i) = std(logx, 'omitnan');
    [skew_log_density(i), kurtosis_log_density(i)] = local_skew_kurt(logx);
    fprintf('统计完成：%s (%d/%d)\n', files(i).name, i, N);
end

T = table(time_index, filename, mean_density, std_density, min_density, max_density, ...
    p01_density, p05_density, p50_density, p95_density, p99_density, p997_density, p999_density, ...
    mean_log_density, std_log_density, skew_log_density, kurtosis_log_density);
writetable(T, fullfile(procDir, 'density_stats.csv'));
save(fullfile(procDir, 'statistics.mat'), 'T');

thresholdT = table(time_index, filename, p99_density, p999_density);
writetable(thresholdT, fullfile(procDir, 'high_density_threshold.csv'));

t = time_index;
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
fill([t; flipud(t)], [mean_density - std_density; flipud(mean_density + std_density)], ...
    [0.78 0.86 1.00], 'EdgeColor', 'none', 'FaceAlpha', 0.55); hold on;
plot(t, mean_density, 'b-', 'LineWidth', 1.8);
grid on; xlabel('time step'); ylabel('density'); title('Mean density with mean ± std');
legend({'mean ± std', 'mean'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'mean_std_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
plot(t, max_density, 'r-', 'LineWidth', 1.8); grid on;
xlabel('time step'); ylabel('max density'); title('Maximum density over time');
save_figure(fig, fullfile(outDir, 'max_density_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
plot(t, p01_density, '-', t, p05_density, '-', t, p50_density, '-', t, p95_density, '-', t, p99_density, '-', 'LineWidth', 1.4);
grid on; xlabel('time step'); ylabel('density percentile'); title('Density percentile curves');
legend({'P01','P05','P50','P95','P99'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'percentile_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
yyaxis left; plot(t, skew_log_density, 'LineWidth', 1.6); ylabel('log-density skewness');
yyaxis right; plot(t, kurtosis_log_density, 'LineWidth', 1.6); ylabel('log-density kurtosis');
grid on; xlabel('time step'); title('Log-density skewness and kurtosis');
legend({'skewness','kurtosis'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'log_skew_kurtosis_curve.png')); close(fig);
end

function files = list_dat_files(rawDir)
files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
if isempty(files), error('没有可用 .dat 文件。'); end
[~, idx] = sort({files.name});
files = files(idx);
end

function ti = parse_time_index(name, fallback)
tok = regexp(name, '\d+', 'match', 'once');
if isempty(tok), ti = fallback; else, ti = str2double(tok); end
end

function q = local_prctile(x, p)
x = x(isfinite(x));
x = sort(x(:));
if isempty(x), q = nan(size(p)); return; end
pos = 1 + (numel(x) - 1) .* p(:)' ./ 100;
lo = floor(pos); hi = ceil(pos);
w = pos - lo;
q = (1 - w) .* x(lo)' + w .* x(hi)';
end

function [s, k] = local_skew_kurt(x)
x = x(isfinite(x));
mu = mean(x);
sd = std(x);
if isempty(x) || sd == 0
    s = 0; k = 0; return;
end
z = (x - mu) ./ sd;
s = mean(z.^3);
k = mean(z.^4);
end
