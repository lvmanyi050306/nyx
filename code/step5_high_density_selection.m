function step5_high_density_selection(rawDir, processedDir, resultsDir, stats)
%STEP5_HIGH_DENSITY_SELECTION Visualize top 1 percent high-density regions.

outDir = fullfile(resultsDir, "05_interaction_selection");
if ~exist(outDir, "dir")
    mkdir(outDir);
end

if nargin < 4 || isempty(stats)
    statsPath = fullfile(processedDir, "density_stats.csv");
    if ~isfile(statsPath)
        return;
    end
    stats = readtable(statsPath, "TextType", "string");
end

timesteps = ["0000", "0060", "0099"];

for t = timesteps
    filePath = fullfile(rawDir, t + ".dat");
    if ~isfile(filePath) || dir(filePath).bytes == 0
        continue;
    end

    row = stats(stats.timestep == t, :);
    if isempty(row)
        continue;
    end

    volume = read_nyx_dat(filePath);
    mask = volume >= row.p99_density(1);
    projection = squeeze(max(log10(max(volume, eps("single"))) .* single(mask), [], 3));

    fig = figure("Visible", "off");
    imagesc(projection);
    axis image off;
    colorbar;
    set_nyx_colormap();
    title("Top 1 percent density t" + t);
    save_figure(fig, fullfile(outDir, "top1_percent_t" + t + ".png"));
    close(fig);
end
end
