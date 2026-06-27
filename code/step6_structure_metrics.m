function step6_structure_metrics(projectRoot)
%STEP6_STRUCTURE_METRICS 计算结构指标、连通域指标与首末时间步差分。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
procDir = fullfile(projectRoot, 'data', 'processed');
outDir = fullfile(projectRoot, 'results', '06_structure_metrics');
ensure_folder(procDir); ensure_folder(outDir);

files = list_dat_files(rawDir);
time_index = reshape(arrayfun(@(f) parse_time_index(f.name), files), [], 1);
filename = reshape(string({files.name}), [], 1);
N = numel(files);

V0 = read_nyx_dat(fullfile(files(1).folder, files(1).name));
baseP = local_prctile(double(V0(:)), [5 95]);
baseP05 = baseP(1); baseP95 = baseP(2);

spread_p99_p01 = zeros(N, 1);
tail_amplification = zeros(N, 1);
void_fraction_vs_t0000_p05 = zeros(N, 1);
dense_fraction_vs_t0000_p95 = zeros(N, 1);
log_density_entropy = zeros(N, 1);
gini_density = zeros(N, 1);
high_density_component_count = nan(N, 1);
high_density_largest_component_size = nan(N, 1);
high_density_mean_component_size = nan(N, 1);

hasCC = exist('bwconncomp', 'file') == 2;
if ~hasCC
    warning('未检测到 bwconncomp，跳过 P99 mask 连通域分析。');
end

for i = 1:N
    V = read_nyx_dat(fullfile(files(i).folder, files(i).name));
    x = double(V(:));
    logx = log10(max(x, eps));
    pct = local_prctile(x, [1 95 99]);
    p01 = pct(1); p99 = pct(3);
    meanDensity = mean(x, 'omitnan');

    spread_p99_p01(i) = p99 - p01;
    tail_amplification(i) = p99 / max(meanDensity, eps);
    void_fraction_vs_t0000_p05(i) = mean(x < baseP05);
    dense_fraction_vs_t0000_p95(i) = mean(x > baseP95);
    log_density_entropy(i) = entropy_from_hist(logx, 120);
    gini_density(i) = gini_coefficient(x);

    if hasCC
        try
            mask = V >= p99;
            CC = bwconncomp(mask, 26);
            sizes = cellfun(@numel, CC.PixelIdxList);
            high_density_component_count(i) = CC.NumObjects;
            if isempty(sizes)
                high_density_largest_component_size(i) = 0;
                high_density_mean_component_size(i) = 0;
            else
                high_density_largest_component_size(i) = max(sizes);
                high_density_mean_component_size(i) = mean(sizes);
            end
        catch ME
            warning('连通域分析失败于 %s：%s', files(i).name, ME.message);
        end
    end
    fprintf('结构指标完成：%s (%d/%d)\n', files(i).name, i, N);
end

T = table(time_index, filename, spread_p99_p01, tail_amplification, ...
    void_fraction_vs_t0000_p05, dense_fraction_vs_t0000_p95, ...
    log_density_entropy, gini_density, ...
    high_density_component_count, high_density_largest_component_size, high_density_mean_component_size);
writetable(T, fullfile(procDir, 'structure_metrics.csv'));
save(fullfile(procDir, 'structure_metrics.mat'), 'T');

t = time_index;
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
yyaxis left; plot(t, spread_p99_p01, 'LineWidth', 1.6); ylabel('P99 - P01');
yyaxis right; plot(t, tail_amplification, 'LineWidth', 1.6); ylabel('P99 / mean density');
grid on; xlabel('time step'); title('Density spread and tail amplification');
legend({'P99-P01','P99/mean'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'spread_tail_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
plot(t, void_fraction_vs_t0000_p05, 'LineWidth', 1.6); hold on;
plot(t, dense_fraction_vs_t0000_p95, 'LineWidth', 1.6);
grid on; xlabel('time step'); ylabel('voxel fraction');
title('Void and dense fractions using t0000 thresholds');
legend({'density < t0000 P05','density > t0000 P95'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'void_dense_fraction_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
yyaxis left; plot(t, log_density_entropy, 'LineWidth', 1.6); ylabel('log-density entropy');
yyaxis right; plot(t, gini_density, 'LineWidth', 1.6); ylabel('density Gini');
grid on; xlabel('time step'); title('Entropy and Gini coefficient');
legend({'entropy','Gini'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'entropy_gini_curve.png')); close(fig);

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 520]);
plot(t, high_density_component_count, 'LineWidth', 1.5); hold on;
plot(t, high_density_largest_component_size, 'LineWidth', 1.5);
plot(t, high_density_mean_component_size, 'LineWidth', 1.5);
grid on; xlabel('time step'); ylabel('component metric');
title('P99 high-density connected components');
legend({'count','largest size','mean size'}, 'Location', 'best');
save_figure(fig, fullfile(outDir, 'high_density_components_curve.png')); close(fig);

draw_difference_mip(files, time_index, outDir);
end

function draw_difference_mip(files, time_index, outDir)
Vfirst = read_nyx_dat(fullfile(files(1).folder, files(1).name));
Vlast = read_nyx_dat(fullfile(files(end).folder, files(end).name));
D = log10(max(Vlast, eps('single'))) - log10(max(Vfirst, eps('single')));
mipX = signed_abs_mip(D, 1);
mipY = signed_abs_mip(D, 2);
mipZ = signed_abs_mip(D, 3);
lim = max(abs(D(:)));
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1200 430]);
tiledlayout(1, 3, 'Padding', 'compact', 'TileSpacing', 'compact');
nexttile; imagesc(mipX'); axis image off; title('X signed MIP'); clim([-lim lim]); colorbar;
nexttile; imagesc(mipY'); axis image off; title('Y signed MIP'); clim([-lim lim]); colorbar;
nexttile; imagesc(mipZ'); axis image off; title('Z signed MIP'); clim([-lim lim]); colorbar;
colormap(redblue_colormap(256));
sgtitle(sprintf('log-density difference MIP: t%04d - t%04d', time_index(end), time_index(1)), 'FontWeight', 'bold');
save_figure(fig, fullfile(outDir, 'difference_mip_first_last.png')); close(fig);
end

function M = signed_abs_mip(D, dim)
[~, idx] = max(abs(D), [], dim);
switch dim
    case 1
        M = zeros(size(D, 2), size(D, 3));
        for y = 1:size(D, 2), for z = 1:size(D, 3), M(y, z) = D(idx(1, y, z), y, z); end, end
    case 2
        M = zeros(size(D, 1), size(D, 3));
        for x = 1:size(D, 1), for z = 1:size(D, 3), M(x, z) = D(x, idx(x, 1, z), z); end, end
    otherwise
        M = zeros(size(D, 1), size(D, 2));
        for x = 1:size(D, 1), for y = 1:size(D, 2), M(x, y) = D(x, y, idx(x, y, 1)); end, end
end
end

function H = entropy_from_hist(x, nbins)
counts = histcounts(x(isfinite(x)), nbins, 'Normalization', 'probability');
p = counts(counts > 0);
H = -sum(p .* log2(p));
end

function cmap = redblue_colormap(n)
if nargin < 1, n = 256; end
half = floor(n / 2);
blue = [linspace(0.08,1,half)' linspace(0.20,1,half)' linspace(0.75,1,half)'];
red = [linspace(1,0.70,n-half)' linspace(1,0.05,n-half)' linspace(1,0.08,n-half)'];
cmap = [blue; red];
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
