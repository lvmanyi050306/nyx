function step3_draw_histograms(rawDir, resultsDir)
%STEP3_DRAW_HISTOGRAMS Draw density histograms for selected timesteps.

outDir = fullfile(resultsDir, "03_histograms");
if ~exist(outDir, "dir")
    mkdir(outDir);
end

timesteps = ["0000", "0030", "0060", "0099"];

for t = timesteps
    filePath = fullfile(rawDir, t + ".dat");
    if ~isfile(filePath) || dir(filePath).bytes == 0
        continue;
    end

    volume = read_nyx_dat(filePath);
    values = log10(max(volume(:), eps("single")));

    fig = figure("Visible", "off");
    histogram(values, 120, "Normalization", "probability");
    grid on;
    xlabel("log10(density)");
    ylabel("Count");
    title("Log density histogram t" + t);
    save_figure(fig, fullfile(outDir, "histogram_t" + t + ".png"));
    close(fig);
end
end
