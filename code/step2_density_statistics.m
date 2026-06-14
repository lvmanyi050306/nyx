function stats = step2_density_statistics(rawDir, processedDir)
%STEP2_DENSITY_STATISTICS Compute density statistics for all raw files.

files = dir(fullfile(rawDir, "*.dat"));
files = files([files.bytes] > 0);
[~, order] = sort({files.name});
files = files(order);

resultRoot = fileparts(fileparts(processedDir));
outDir = fullfile(resultRoot, "results", "04_statistics");
if ~exist(outDir, "dir")
    mkdir(outDir);
end

n = numel(files);
timestep = strings(n, 1);
timeIndex = zeros(n, 1);
meanDensity = zeros(n, 1);
stdDensity = zeros(n, 1);
minDensity = zeros(n, 1);
maxDensity = zeros(n, 1);
p01Density = zeros(n, 1);
p05Density = zeros(n, 1);
p95Density = zeros(n, 1);
p99Density = zeros(n, 1);

for i = 1:n
    filePath = fullfile(files(i).folder, files(i).name);
    timestep(i) = erase(files(i).name, ".dat");
    timeIndex(i) = str2double(timestep(i));

    volume = read_nyx_dat(filePath);
    values = double(volume(:));

    meanDensity(i) = mean(values);
    stdDensity(i) = std(values);
    minDensity(i) = min(values);
    maxDensity(i) = max(values);
    p01Density(i) = prctile(values, 1);
    p05Density(i) = prctile(values, 5);
    p95Density(i) = prctile(values, 95);
    p99Density(i) = prctile(values, 99);
end

stats = table(timestep, timeIndex, meanDensity, stdDensity, ...
    minDensity, maxDensity, p01Density, p05Density, p95Density, p99Density);
stats.Properties.VariableNames = {'timestep', 'time_index', 'mean_density', ...
    'std_density', 'min_density', 'max_density', 'p01_density', ...
    'p05_density', 'p95_density', 'p99_density'};

if ~exist(processedDir, "dir")
    mkdir(processedDir);
end

writetable(stats, fullfile(processedDir, "density_stats.csv"));
save(fullfile(processedDir, "statistics.mat"), "stats");

threshold = table(stats.timestep, stats.p99_density);
threshold.Properties.VariableNames = {'timestep', 'top1_percent_threshold'};
writetable(threshold, fullfile(processedDir, "high_density_threshold.csv"));

draw_statistic_curves(stats, outDir);
end

function draw_statistic_curves(stats, outDir)
fig = figure("Visible", "off");
plot(stats.time_index, stats.mean_density, "LineWidth", 1.8);
hold on;
plot(stats.time_index, stats.mean_density + stats.std_density, "--", "LineWidth", 1.1);
plot(stats.time_index, stats.mean_density - stats.std_density, "--", "LineWidth", 1.1);
grid on;
xlabel("Time step");
ylabel("Density");
legend("Mean", "Mean + std", "Mean - std", "Location", "best");
title("Mean and standard deviation over time");
save_figure(fig, fullfile(outDir, "mean_std_curve.png"));
close(fig);

fig = figure("Visible", "off");
plot(stats.time_index, stats.max_density, "LineWidth", 1.8);
grid on;
xlabel("Time step");
ylabel("Maximum density");
title("Maximum density over time");
save_figure(fig, fullfile(outDir, "max_density_curve.png"));
close(fig);

fig = figure("Visible", "off");
plot(stats.time_index, stats.p01_density, "LineWidth", 1.2);
hold on;
plot(stats.time_index, stats.p05_density, "LineWidth", 1.2);
plot(stats.time_index, stats.p95_density, "LineWidth", 1.2);
plot(stats.time_index, stats.p99_density, "LineWidth", 1.2);
grid on;
xlabel("Time step");
ylabel("Density percentile");
legend("P01", "P05", "P95", "P99", "Location", "best");
title("Density percentile evolution");
save_figure(fig, fullfile(outDir, "percentile_curve.png"));
close(fig);
end
