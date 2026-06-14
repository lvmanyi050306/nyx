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

step1_check_data(rawDir, resultsDir);
stats = step2_density_statistics(rawDir, processedDir);
step3_draw_histograms(rawDir, resultsDir);
step4_volume_render(rawDir, resultsDir);
step5_high_density_selection(rawDir, processedDir, resultsDir, stats);

disp("Nyx visualization pipeline finished.");
disp("Run interactive_dashboard(rawDir) to open the linked phase-space dashboard.");
