function step7_interactive_dashboard(projectRoot)
%STEP7_INTERACTIVE_DASHBOARD 传统 figure/uicontrol 联动刷选仪表盘。
% 不依赖 App Designer；运行本函数会打开可交互窗口，并保存默认截图。

if nargin < 1, projectRoot = fileparts(fileparts(mfilename('fullpath'))); end
rawDir = fullfile(projectRoot, 'data', 'raw');
outDir = fullfile(projectRoot, 'results', '07_dashboard');
ensure_folder(outDir);

files = list_dat_files(rawDir);
timeIdx = arrayfun(@(f) parse_time_index(f.name), files);

state.frame = 1;
state.lowPct = 5;
state.highPct = 99;
state.direction = 'Z';
state.mode = 'MIP';
state.V = [];
state.logV = [];
state.currentFile = '';

fig = figure('Name', 'Nyx Density Linked Brushing Dashboard', ...
    'NumberTitle', 'off', 'Color', 'w', 'Position', [80 80 1280 760]);
axHist = axes('Parent', fig, 'Position', [0.07 0.23 0.40 0.67]);
axView = axes('Parent', fig, 'Position', [0.55 0.23 0.40 0.67]);
txtInfo = uicontrol(fig, 'Style', 'text', 'Units', 'normalized', 'Position', [0.55 0.12 0.40 0.05], ...
    'BackgroundColor', 'w', 'FontSize', 11, 'HorizontalAlignment', 'left');

uicontrol(fig, 'Style', 'text', 'Units', 'normalized', 'Position', [0.07 0.13 0.12 0.03], ...
    'String', 'time step', 'BackgroundColor', 'w');
sFrame = uicontrol(fig, 'Style', 'slider', 'Units', 'normalized', 'Position', [0.18 0.135 0.29 0.025], ...
    'Min', 1, 'Max', numel(files), 'Value', 1, 'SliderStep', slider_step(numel(files)), 'Callback', @onChange);

uicontrol(fig, 'Style', 'text', 'Units', 'normalized', 'Position', [0.07 0.08 0.12 0.03], ...
    'String', 'lower pct', 'BackgroundColor', 'w');
sLow = uicontrol(fig, 'Style', 'slider', 'Units', 'normalized', 'Position', [0.18 0.085 0.29 0.025], ...
    'Min', 0, 'Max', 99, 'Value', 5, 'SliderStep', [0.01 0.10], 'Callback', @onChange);

uicontrol(fig, 'Style', 'text', 'Units', 'normalized', 'Position', [0.07 0.03 0.12 0.03], ...
    'String', 'upper pct', 'BackgroundColor', 'w');
sHigh = uicontrol(fig, 'Style', 'slider', 'Units', 'normalized', 'Position', [0.18 0.035 0.29 0.025], ...
    'Min', 1, 'Max', 100, 'Value', 99, 'SliderStep', [0.01 0.10], 'Callback', @onChange);

uicontrol(fig, 'Style', 'popupmenu', 'Units', 'normalized', 'Position', [0.55 0.055 0.15 0.05], ...
    'String', {'X','Y','Z'}, 'Value', 3, 'Callback', @onChange);
popupDir = findobj(fig, 'Style', 'popupmenu');
uicontrol(fig, 'Style', 'popupmenu', 'Units', 'normalized', 'Position', [0.72 0.055 0.18 0.05], ...
    'String', {'MIP','Mask','LogDensity'}, 'Value', 1, 'Callback', @onChange);
popups = findobj(fig, 'Style', 'popupmenu');
popupMode = popups(popups ~= popupDir);

updateDashboard(true);
drawnow;
previewFile = fullfile(outDir, 'dashboard_preview.png');
try
    frame = getframe(fig);
    imwrite(frame.cdata, previewFile);
catch
    save_figure(fig, previewFile);
end

    function onChange(~, ~)
        updateDashboard(false);
    end

    function updateDashboard(forceReload)
        frame = round(get(sFrame, 'Value'));
        low = get(sLow, 'Value');
        high = get(sHigh, 'Value');
        if low >= high
            if low >= 99
                low = high - 1;
            else
                high = low + 1;
            end
            set(sLow, 'Value', low); set(sHigh, 'Value', high);
        end
        dirOptions = get(popupDir, 'String');
        modeOptions = get(popupMode, 'String');
        state.direction = dirOptions{get(popupDir, 'Value')};
        state.mode = modeOptions{get(popupMode, 'Value')};
        state.lowPct = low; state.highPct = high;

        if forceReload || frame ~= state.frame || isempty(state.V)
            state.frame = frame;
            f = files(frame);
            state.currentFile = f.name;
            state.V = read_nyx_dat(fullfile(f.folder, f.name));
            state.logV = log10(max(state.V, eps('single')));
        end

        vals = double(state.V(:));
        thr = local_prctile(vals, [state.lowPct state.highPct]);
        mask = state.V >= thr(1) & state.V <= thr(2);
        ratio = nnz(mask) / numel(mask);

        axes(axHist); cla(axHist);
        histogram(axHist, double(state.logV(:)), 100, 'Normalization', 'probability', ...
            'FaceColor', [0.28 0.34 0.68], 'EdgeColor', 'none'); hold(axHist, 'on');
        xline(axHist, log10(max(thr(1), eps)), 'r-', 'LineWidth', 1.4);
        xline(axHist, log10(max(thr(2), eps)), 'r-', 'LineWidth', 1.4);
        grid(axHist, 'on');
        xlabel(axHist, 'log10(density)'); ylabel(axHist, 'probability');
        title(axHist, sprintf('Histogram %s  [%0.1f%%, %0.1f%%]', state.currentFile, state.lowPct, state.highPct));

        axes(axView); cla(axView);
        switch state.mode
            case 'Mask'
                vol = single(mask);
            case 'LogDensity'
                vol = normalize_percentile(state.logV, 5, 99.7);
            otherwise
                vol = state.logV; vol(~mask) = min(state.logV(:));
        end
        img = projection(vol, state.direction, state.mode);
        imagesc(axView, img'); axis(axView, 'image'); axis(axView, 'off');
        colormap(axView, custom_nyx_colormap(256)); colorbar(axView);
        title(axView, sprintf('%s projection - %s', state.direction, state.mode));

        set(txtInfo, 'String', sprintf('time=%04d    selected voxels=%d / %d    ratio=%.3f%%', ...
            timeIdx(state.frame), nnz(mask), numel(mask), ratio * 100));
        drawnow;
    end
end

function img = projection(vol, direction, modeName)
% 三种显示模式都使用最大强度投影；区别在传入的 vol 已由上层决定。
fun = @max;
switch direction
    case 'X'
        img = squeeze(fun(vol, [], 1));
    case 'Y'
        img = squeeze(fun(vol, [], 2));
    otherwise
        img = squeeze(fun(vol, [], 3));
end
end

function ss = slider_step(n)
if n <= 1
    ss = [1 1];
else
    ss = [1/(n-1) min(10/(n-1), 1)];
end
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
