function interactive_dashboard(rawDir, timestep)
%INTERACTIVE_DASHBOARD Linked histogram and spatial selection dashboard.
%
% Example:
%   interactive_dashboard(fullfile(pwd, "data", "raw"), "0099")

if nargin < 1 || strlength(string(rawDir)) == 0
    projectRoot = fileparts(fileparts(mfilename("fullpath")));
    rawDir = fullfile(projectRoot, "data", "raw");
end

if nargin < 2
    timestep = "0099";
end

filePath = fullfile(rawDir, string(timestep) + ".dat");
info = dir(filePath);
if isempty(info) || info.bytes == 0
    error("interactive_dashboard:MissingRawData", ...
        "Cannot open %s. Place the Nyx raw files in data/raw before using the linked brushing dashboard.", filePath);
end

volume = read_nyx_dat(filePath);
logDensity = log10(max(volume, eps("single")));
values = logDensity(:);

fig = uifigure("Name", "Nyx phase-space linked selection", "Position", [100, 100, 1180, 620]);
grid = uigridlayout(fig, [2, 3]);
grid.RowHeight = {"1x", 54};
grid.ColumnWidth = {"1x", "1x", 280};

histAx = uiaxes(grid);
histAx.Layout.Row = 1;
histAx.Layout.Column = 1;
histogram(histAx, values, 120, "Normalization", "probability");
title(histAx, "Log density phase space");
xlabel(histAx, "log10(density)");
ylabel(histAx, "Probability");
grid(histAx, "on");

spaceAx = uiaxes(grid);
spaceAx.Layout.Row = 1;
spaceAx.Layout.Column = 2;

infoPanel = uipanel(grid, "Title", "Selection");
infoPanel.Layout.Row = 1;
infoPanel.Layout.Column = 3;
infoLayout = uigridlayout(infoPanel, [6, 1]);
infoLayout.RowHeight = {28, 28, 28, 28, 28, "1x"};

labelT = uilabel(infoLayout, "Text", "Timestep: " + string(timestep));
labelLow = uilabel(infoLayout);
labelHigh = uilabel(infoLayout);
labelRatio = uilabel(infoLayout);
labelHint = uilabel(infoLayout, "Text", "Move sliders to brush a density range.");

lowSlider = uislider(grid, "Limits", [0, 100], "Value", 99);
lowSlider.Layout.Row = 2;
lowSlider.Layout.Column = 1;
highSlider = uislider(grid, "Limits", [0, 100], "Value", 100);
highSlider.Layout.Row = 2;
highSlider.Layout.Column = 2;

updateSelection();
lowSlider.ValueChangingFcn = @(~, event) updateSelection(event.Value, highSlider.Value);
highSlider.ValueChangingFcn = @(~, event) updateSelection(lowSlider.Value, event.Value);
lowSlider.ValueChangedFcn = @(~, ~) updateSelection();
highSlider.ValueChangedFcn = @(~, ~) updateSelection();

    function updateSelection(lowPct, highPct)
        if nargin < 1
            lowPct = lowSlider.Value;
            highPct = highSlider.Value;
        end

        lowPct = min(lowPct, highPct - 0.1);
        highPct = max(highPct, lowPct + 0.1);
        low = prctile(values, lowPct);
        high = prctile(values, highPct);
        mask = logDensity >= low & logDensity <= high;
        projection = squeeze(max(logDensity .* single(mask), [], 3));

        imagesc(spaceAx, rot90(projection));
        axis(spaceAx, "image");
        axis(spaceAx, "off");
        colormap(spaceAx, turbo);
        title(spaceAx, "Linked 3D projection");

        labelLow.Text = sprintf("Lower percentile: %.1f%%", lowPct);
        labelHigh.Text = sprintf("Upper percentile: %.1f%%", highPct);
        labelRatio.Text = sprintf("Selected cells: %.3f%%", 100 * nnz(mask) / numel(mask));

        delete(findobj(histAx, "Tag", "SelectionRange"));
        xline(histAx, low, "r", "LineWidth", 1.4, "Tag", "SelectionRange");
        xline(histAx, high, "r", "LineWidth", 1.4, "Tag", "SelectionRange");
    end
end
