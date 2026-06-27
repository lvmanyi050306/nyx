function [lambda1, lambda2, lambda3] = compute_hessian_eigenvalues_3d(V)
%COMPUTE_HESSIAN_EIGENVALUES_3D 计算三维标量场 Hessian 特征值。
%   本函数通过两次 gradient 近似二阶导数，并使用 3x3 对称矩阵特征值
%   解析公式进行向量化计算。输出 lambda1/lambda2/lambda3 按数值从小到大排序。
%
%   注意：Hessian 对噪声敏感，建议调用前先对 log-density 做平滑和降采样。

V = single(V);
V(~isfinite(V)) = 0;

[Vx, Vy, Vz] = gradient(V);
[Hxx, Hxy, Hxz] = gradient(Vx);
[Hyx, Hyy, Hyz] = gradient(Vy);
[Hzx, Hzy, Hzz] = gradient(Vz);

% 混合偏导使用对称平均，减小数值差异带来的不稳定。
Hxy = 0.5 .* (Hxy + Hyx);
Hxz = 0.5 .* (Hxz + Hzx);
Hyz = 0.5 .* (Hyz + Hzy);

Hxx = double(Hxx); Hyy = double(Hyy); Hzz = double(Hzz);
Hxy = double(Hxy); Hxz = double(Hxz); Hyz = double(Hyz);

% 解析式参考对称 3x3 矩阵的稳定特征值分解。
m = (Hxx + Hyy + Hzz) ./ 3;
Bxx = Hxx - m; Byy = Hyy - m; Bzz = Hzz - m;
p2 = (Bxx.^2 + Byy.^2 + Bzz.^2 + 2 .* (Hxy.^2 + Hxz.^2 + Hyz.^2)) ./ 6;
p = sqrt(max(p2, 0));

detB = Bxx .* (Byy .* Bzz - Hyz .* Hyz) ...
     - Hxy .* (Hxy .* Bzz - Hyz .* Hxz) ...
     + Hxz .* (Hxy .* Hyz - Byy .* Hxz);
r = detB ./ max(2 .* p.^3, eps);
r = max(min(r, 1), -1);
phi = acos(r) ./ 3;

eHigh = m + 2 .* p .* cos(phi);
eLow = m + 2 .* p .* cos(phi + 2 .* pi ./ 3);
eMid = 3 .* m - eHigh - eLow;

lambda1 = single(min(min(eLow, eMid), eHigh));
lambda3 = single(max(max(eLow, eMid), eHigh));
lambda2 = single(eLow + eMid + eHigh - double(lambda1) - double(lambda3));

flatMask = p < eps;
lambda1(flatMask) = single(m(flatMask));
lambda2(flatMask) = single(m(flatMask));
lambda3(flatMask) = single(m(flatMask));

lambda1(~isfinite(lambda1)) = 0;
lambda2(~isfinite(lambda2)) = 0;
lambda3(~isfinite(lambda3)) = 0;
end
