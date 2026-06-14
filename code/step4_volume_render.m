function step4_volume_render(rawDir, resultsDir)
%STEP4_VOLUME_RENDER Render selected timesteps with transfer function and lighting.

outDir = fullfile(resultsDir, "02_volume_render");
if ~exist(outDir, "dir")
    mkdir(outDir);
end

timesteps = ["0000", "0030", "0060", "0099"];

for t = timesteps
    filePath = fullfile(rawDir, t + ".dat");
    if ~isfile(filePath) || dir(filePath).bytes == 0
        continue;
    end

    volume = read_nyx_dat(filePath);
    imageRgb = render_density_volume(volume);

    fig = figure("Visible", "off");
    image(imageRgb);
    axis image off;
    title("Volume rendering t" + t);
    save_figure(fig, fullfile(outDir, "volume_t" + t + ".png"));
    close(fig);
end
end

function imageRgb = render_density_volume(volume)
v = log10(max(single(volume), eps("single")));
lo = prctile(v(:), 5);
hi = prctile(v(:), 99.7);
v = min(max((v - lo) / max(hi - lo, eps), 0), 1);

[gx, gy, gz] = gradient(v);
gradMag = sqrt(gx.^2 + gy.^2 + gz.^2);
gradMag = gradMag / max(gradMag(:) + eps);

alpha = 0.02 * smoothstep(v, 0.20, 0.55) + 0.20 * smoothstep(v, 0.62, 0.95);
alpha = min(alpha .* (0.7 + 1.7 * gradMag), 0.85);

lut = nyx_lut(256);
[nx, ny, nz] = size(v);
rgb = zeros(nx, ny, 3, "single");
accAlpha = zeros(nx, ny, "single");

for k = 1:nz
    slice = v(:, :, k);
    a = alpha(:, :, k) .* (1 - accAlpha);
    idx = max(1, min(256, round(slice * 255) + 1));
    shade = 0.55 + 0.45 * gradMag(:, :, k);

    for c = 1:3
        color = reshape(lut(idx, c), nx, ny) .* shade;
        rgb(:, :, c) = rgb(:, :, c) + a .* color;
    end
    accAlpha = accAlpha + a;
end

background = reshape(single([0.015, 0.018, 0.030]), 1, 1, 3);
imageRgb = rgb + (1 - accAlpha) .* background;
imageRgb = rot90(gather(imageRgb));
end

function y = smoothstep(x, edge0, edge1)
t = min(max((x - edge0) / (edge1 - edge0), 0), 1);
y = t .* t .* (3 - 2 .* t);
end

function lut = nyx_lut(n)
anchorX = [0, 0.22, 0.48, 0.72, 1];
anchorC = [ ...
    0.03, 0.04, 0.10; ...
    0.08, 0.24, 0.44; ...
    0.16, 0.55, 0.72; ...
    0.95, 0.72, 0.32; ...
    1.00, 0.96, 0.82];
x = linspace(0, 1, n);
lut = zeros(n, 3, "single");
for c = 1:3
    lut(:, c) = interp1(anchorX, anchorC(:, c), x, "pchip");
end
lut = min(max(lut, 0), 1);
end
