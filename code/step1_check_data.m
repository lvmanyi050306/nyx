function step1_check_data(rawDir, resultsDir)
%STEP1_CHECK_DATA Load the first volume and save a central slice preview.

outDir = fullfile(resultsDir, "01_data_check");
if ~exist(outDir, "dir")
    mkdir(outDir);
end

filePath = fullfile(rawDir, "0000.dat");
if ~isfile(filePath) || dir(filePath).bytes == 0
    warning("step1_check_data:MissingData", "Placeholder or missing file: %s", filePath);
    return;
end

volume = read_nyx_dat(filePath);
sliceIndex = round(size(volume, 3) / 2);

fig = figure("Visible", "off");
imagesc(volume(:, :, sliceIndex));
axis image off;
colorbar;
title("Density slice t0000");
set_nyx_colormap();
save_figure(fig, fullfile(outDir, "slice_0000.png"));
close(fig);
end

