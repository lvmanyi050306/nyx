function classVol = classify_cosmic_web_hessian(lambda1, lambda2, lambda3, tau)
%CLASSIFY_COSMIC_WEB_HESSIAN 基于 Hessian 特征值符号进行简化宇宙网分类。
%   classVol 取值：
%       1 = Void
%       2 = Sheet
%       3 = Filament
%       4 = Node
%
%   分类规则：统计小于 -tau 的特征值数量 collapseDim。
%   collapseDim 为 0/1/2/3 时分别对应 Void/Sheet/Filament/Node。
%   这是课程可视化实验中的近似结构识别方法，不代表严格天体物理结论。

if nargin < 4 || isempty(tau)
    vals = abs(double([lambda1(:); lambda2(:); lambda3(:)]));
    vals = vals(isfinite(vals));
    if isempty(vals)
        tau = 0.03;
    else
        tau = local_prctile(vals, 70);
    end
end

collapseDim = int8(lambda1 < -tau) + int8(lambda2 < -tau) + int8(lambda3 < -tau);
classVol = uint8(collapseDim + 1);
end

function q = local_prctile(x, p)
x = sort(x(:));
if isempty(x), q = NaN; return; end
pos = 1 + (numel(x) - 1) .* p ./ 100;
lo = floor(pos); hi = ceil(pos); w = pos - lo;
q = (1 - w) .* x(lo) + w .* x(hi);
end
