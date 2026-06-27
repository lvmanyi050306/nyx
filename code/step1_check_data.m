function step1_check_data(projectRoot)
%STEP1_CHECK_DATA 检查原始数据完整性并绘制中心切片。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '01_data_check');
ensure_folder(outDir);

files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
if isempty(files), error('data/raw 下没有非空 .dat 文件。'); end
[~, idx] = sort({files.name});
files = files(idx);

names = {files.name};
idx0000 = find(strcmp(names, '0000.dat'), 1);
if isempty(idx0000), idx0000 = 1; end
f = files(idx0000);
V = read_nyx_dat(fullfile(f.folder, f.name));

stats.file = f.name;
stats.size = size(V);
stats.min = min(V(:));
stats.max = max(V(:));
stats.mean = mean(double(V(:)), 'omitnan');
stats.std = std(double(V(:)), 'omitnan');
stats.nan_count = sum(isnan(V(:)));
stats.inf_count = sum(isinf(V(:)));
stats.negative_count = sum(V(:) < 0);

fprintf('检查文件：%s\n', stats.file);
fprintf('尺寸：%d × %d × %d\n', stats.size(1), stats.size(2), stats.size(3));
fprintf('min=%g, max=%g, mean=%g, std=%g\n', stats.min, stats.max, stats.mean, stats.std);
fprintf('NaN=%d, Inf=%d, Negative=%d\n', stats.nan_count, stats.inf_count, stats.negative_count);

n = size(V, 1);
c = round(n / 2);
logV = log10(max(V, eps('single')));

fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 1200 420]);
tiledlayout(1, 3, 'Padding', 'compact', 'TileSpacing', 'compact');
nexttile; imagesc(squeeze(logV(:, :, c))'); axis image off; title('XY 中心切片'); colormap hot; colorbar;
nexttile; imagesc(squeeze(logV(:, c, :))'); axis image off; title('XZ 中心切片'); colormap hot; colorbar;
nexttile; imagesc(squeeze(logV(c, :, :))'); axis image off; title('YZ 中心切片'); colormap hot; colorbar;
sgtitle(sprintf('Nyx log10 density center slices: %s', f.name), 'FontWeight', 'bold');
save_figure(fig, fullfile(outDir, 'center_slices_0000.png'));
close(fig);

sizes = double([files.bytes]);
fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 900 420]);
plot(0:numel(files)-1, sizes, 'o-', 'LineWidth', 1.2, 'MarkerSize', 4);
grid on;
xlabel('time step');
ylabel('file size (bytes)');
title('Nyx .dat 文件尺寸一致性检查');
ylim([min(sizes) * 0.98, max(sizes) * 1.02]);
save_figure(fig, fullfile(outDir, 'file_size_check.png'));
close(fig);

save(fullfile(outDir, 'data_check_stats.mat'), 'stats');
end
