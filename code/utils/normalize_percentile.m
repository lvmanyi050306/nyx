function Vn = normalize_percentile(V, lowerPct, upperPct)
%NORMALIZE_PERCENTILE 百分位裁剪并归一化到 [0,1]。

if nargin < 2, lowerPct = 5; end
if nargin < 3, upperPct = 99.7; end
if lowerPct >= upperPct
    error('lowerPct 必须小于 upperPct。');
end

vals = double(V(isfinite(V)));
if isempty(vals)
    Vn = zeros(size(V), 'single');
    return;
end

thr = local_prctile(vals, [lowerPct upperPct]);
lo = thr(1); hi = thr(2);
if hi <= lo
    Vn = zeros(size(V), 'single');
    return;
end

Vclip = min(max(double(V), lo), hi);
Vn = single((Vclip - lo) ./ (hi - lo));
Vn(~isfinite(Vn)) = 0;
end

function q = local_prctile(x, p)
x = sort(x(:));
pos = 1 + (numel(x) - 1) .* p(:)' ./ 100;
lo = floor(pos); hi = ceil(pos);
w = pos - lo;
q = (1 - w) .* x(lo)' + w .* x(hi)';
end
