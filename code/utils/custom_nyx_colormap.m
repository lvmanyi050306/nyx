function cmap = custom_nyx_colormap(n)
%CUSTOM_NYX_COLORMAP Nyx 体绘制与投影使用的深色宇宙网色图。

if nargin < 1, n = 256; end
anchors = [ ...
    0.00 0.01 0.02
    0.03 0.07 0.18
    0.18 0.08 0.38
    0.58 0.18 0.45
    0.93 0.42 0.16
    1.00 0.82 0.25
    1.00 1.00 0.96];
x = linspace(0, 1, size(anchors, 1));
xi = linspace(0, 1, n);
cmap = interp1(x, anchors, xi, 'pchip');
cmap = min(max(cmap, 0), 1);
end
