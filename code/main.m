clear; clc; close all;

projectRoot = fileparts(fileparts(mfilename("fullpath")));
addpath(fullfile(projectRoot, "code"));
addpath(fullfile(projectRoot, "code", "utils"));

rawDir = fullfile(projectRoot, "data", "raw");
processedDir = fullfile(projectRoot, "data", "processed");
resultsDir = fullfile(projectRoot, "results");

if ~exist(processedDir, "dir")
    mkdir(processedDir);
end

rawFiles = dir(fullfile(rawDir, "*.dat"));
rawFiles = rawFiles([rawFiles.bytes] > 0);
if isempty(rawFiles)
    warning("main:MissingRawData", ...
        "No non-empty Nyx .dat files found in %s. Put 0000.dat to 0099.dat there before rerunning the MATLAB pipeline.", rawDir);
    disp("Existing processed CSV files, figures, reports, and video can still be reviewed without the raw data.");
    return;
end

step1_check_data(rawDir, resultsDir);
stats = step2_density_statistics(rawDir, processedDir);
step3_draw_histograms(rawDir, resultsDir);
step4_volume_render(rawDir, resultsDir);
step5_high_density_selection(rawDir, processedDir, resultsDir, stats);

disp("Nyx visualization pipeline finished.");
disp("Run interactive_dashboard(rawDir) to open the linked phase-space dashboard.");
