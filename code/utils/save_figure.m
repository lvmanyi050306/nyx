function save_figure(fig, outputPath)
%SAVE_FIGURE Save a MATLAB figure and create parent folders when needed.

outDir = fileparts(outputPath);
if ~exist(outDir, "dir")
    mkdir(outDir);
end

exportgraphics(fig, outputPath, "Resolution", 200);
end

