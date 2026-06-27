function RGB = volume_render_alpha_composite(Vn, modeName)
%VOLUME_RENDER_ALPHA_COMPOSITE 自定义 z 方向 alpha compositing 体绘制。
% Vn 必须为 [0,1] 的三维数组，modeName 控制传递函数风格。

if nargin < 2, modeName = 'filament'; end
Vn = single(min(max(Vn, 0), 1));
[nx, ny, nz] = size(Vn);

% 梯度增强：突出丝状结构边界与团块边缘。
[gx, gy, gz] = gradient(Vn);
gradMag = sqrt(gx.^2 + gy.^2 + gz.^2);
gradMag = normalize_percentile(gradMag, 5, 99);

lut = custom_nyx_colormap(256);
RGB = zeros(nx, ny, 3, 'single');
A = zeros(nx, ny, 'single');

for z = nz:-1:1
    s = Vn(:, :, z);
    g = gradMag(:, :, z);
    idx = max(1, min(256, round(double(s) * 255) + 1));
    C = reshape(lut(idx, :), [nx, ny, 3]);

    switch lower(modeName)
        case {'void', 'voids'}
            alpha = 0.035 + 0.12 * smoothstep(0.02, 0.30, 1 - s) + 0.06 * smoothstep(0.20, 0.55, s);
        case {'node', 'nodes', 'dense'}
            alpha = 0.02 * smoothstep(0.20, 0.50, s) + 0.34 * smoothstep(0.72, 0.98, s);
        otherwise
            alpha = 0.02 * smoothstep(0.08, 0.34, s) + 0.18 * smoothstep(0.34, 0.82, s);
    end

    alpha = single(alpha .* (0.75 + 0.95 * g));
    alpha = min(max(alpha, 0), 0.55);

    shade = single(0.72 + 0.58 * g);
    C = single(C) .* shade;
    C = min(C, 1);

    oneMinusA = 1 - A;
    for ch = 1:3
        RGB(:, :, ch) = RGB(:, :, ch) + oneMinusA .* alpha .* C(:, :, ch);
    end
    A = A + oneMinusA .* alpha;
end

% 温和曝光控制，避免高密度核心过曝。
RGB = 1 - exp(-1.15 * RGB);
RGB = min(max(RGB, 0), 1);
RGB = permute(RGB, [2 1 3]);
end
