function gradMag = compute_gradient_magnitude(V)
%COMPUTE_GRADIENT_MAGNITUDE 计算三维标量场的梯度幅值。
%   输入 V 通常为归一化后的 log-density 三维体数据。
%   输出 gradMag 与 V 尺寸一致，表示局部数值变化强度。

V = single(V);
V(~isfinite(V)) = 0;

[gx, gy, gz] = gradient(V);
gradMag = sqrt(gx.^2 + gy.^2 + gz.^2);
gradMag(~isfinite(gradMag)) = 0;
gradMag = single(gradMag);
end
