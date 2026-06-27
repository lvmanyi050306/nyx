%% Nyx 宇宙密度演化可视分析主入口
% 运行方式：在项目根目录执行 run('code/main.m')，或直接运行本文件。

clear; clc; close all;

thisFile = mfilename('fullpath');
projectRoot = fileparts(fileparts(thisFile));
if isempty(projectRoot)
    projectRoot = pwd;
end

addpath(fullfile(projectRoot, 'code'));
addpath(fullfile(projectRoot, 'code', 'utils'));

fprintf('Nyx 可视分析项目根目录：%s\n', projectRoot);

rawDir = fullfile(projectRoot, 'data', 'raw');
if ~isfolder(rawDir)
    error('未找到 data/raw 目录，请先创建目录并放入 .dat 文件。');
end

files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
if isempty(files)
    error('data/raw 下没有非空 .dat 文件。');
end

make_project_folders(projectRoot);

steps = { ...
    @step1_check_data, ...
    @step2_statistics_all_frames, ...
    @step3_histogram_analysis, ...
    @step4_volume_render_keyframes, ...
    @step5_high_density_selection, ...
    @step6_structure_metrics};

stepNames = { ...
    'Step 1 数据完整性检查', ...
    'Step 2 全时间步统计', ...
    'Step 3 对数密度直方图分析', ...
    'Step 4 代表时间步体绘制', ...
    'Step 5 高密度区域筛选', ...
    'Step 6 结构指标与时间差分'};

for k = 1:numel(steps)
    fprintf('\n===== %s 开始 =====\n', stepNames{k});
    try
        steps{k}(projectRoot);
        fprintf('===== %s 完成 =====\n', stepNames{k});
    catch ME
        warning('%s 失败：%s', stepNames{k}, ME.message);
        fprintf('主流程继续执行后续步骤。\n');
    end
end

advancedSteps = { ...
    @step8_density_gradient_phase_space, ...
    @step9_hessian_cosmic_web_classification, ...
    @step10_time_similarity_stage_analysis};

advancedNames = { ...
    'Step 8 density-gradient phase space', ...
    'Step 9 Hessian cosmic web classification', ...
    'Step 10 time similarity stage analysis'};

for k = 1:numel(advancedSteps)
    fprintf('\n===== %s start =====\n', advancedNames{k});
    try
        advancedSteps{k}(projectRoot);
        fprintf('===== %s done =====\n', advancedNames{k});
    catch ME
        warning('%s failed: %s', advancedNames{k}, ME.message);
        fprintf('Advanced module failed, base workflow results are kept.\n');
    end
end

try
    generate_video_frames(projectRoot);
    fprintf('\n视频帧已生成到 results/frames/。\n');
catch ME
    warning('视频帧生成失败：%s', ME.message);
end

fprintf('\n交互式仪表盘不在主流程中阻塞启动。\n');
fprintf('需要查看时请运行：step7_interactive_dashboard(projectRoot)\n');
fprintf('全部主流程结束。\n');

function make_project_folders(projectRoot)
% 创建项目要求的所有输出目录。
folders = { ...
    fullfile(projectRoot, 'data', 'processed'), ...
    fullfile(projectRoot, 'results', '01_data_check'), ...
    fullfile(projectRoot, 'results', '02_histograms'), ...
    fullfile(projectRoot, 'results', '03_statistics'), ...
    fullfile(projectRoot, 'results', '04_volume_render'), ...
    fullfile(projectRoot, 'results', '05_high_density'), ...
    fullfile(projectRoot, 'results', '06_structure_metrics'), ...
    fullfile(projectRoot, 'results', '07_dashboard'), ...
    fullfile(projectRoot, 'results', '08_density_gradient_phase_space'), ...
    fullfile(projectRoot, 'results', '09_hessian_cosmic_web'), ...
    fullfile(projectRoot, 'results', '10_time_similarity'), ...
    fullfile(projectRoot, 'results', 'report_figures'), ...
    fullfile(projectRoot, 'results', 'frames'), ...
    fullfile(projectRoot, 'report_assets')};
for i = 1:numel(folders)
    ensure_folder(folders{i});
end
end

function generate_video_frames(projectRoot)
% 生成所有时间步的 MIP 视频帧。MIP 比体绘制更快，适合一键主流程。
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', 'frames');
ensure_folder(outDir);

files = dir(fullfile(rawDir, '*.dat'));
files = files([files.bytes] > 0);
[~, idx] = sort({files.name});
files = files(idx);

for i = 1:numel(files)
    fpath = fullfile(files(i).folder, files(i).name);
    V = read_nyx_dat(fpath);
    logV = log10(max(V, eps('single')));
    Vn = normalize_percentile(logV, 5, 99.7);
    mip = squeeze(max(Vn, [], 3));

    fig = figure('Visible', 'off', 'Color', 'w', 'Position', [100 100 720 620]);
    imagesc(mip');
    axis image off;
    colormap(custom_nyx_colormap(256));
    colorbar;
    title(sprintf('Nyx log-density MIP   time step %04d', i - 1), 'FontWeight', 'bold');
    save_figure(fig, fullfile(outDir, sprintf('frame_%04d.png', i - 1)));
    close(fig);
end
end
