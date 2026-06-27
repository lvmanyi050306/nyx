function save_figure(fig, filename)
%SAVE_FIGURE 稳定保存报告用图片，兼容新旧 MATLAB。

[folder, ~, ~] = fileparts(filename);
ensure_folder(folder);

try
    exportgraphics(fig, filename, 'Resolution', 180);
catch
    set(fig, 'PaperPositionMode', 'auto');
    print(fig, filename, '-dpng', '-r180');
end
end
