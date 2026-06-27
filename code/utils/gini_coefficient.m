function g = gini_coefficient(x)
%GINI_COEFFICIENT 计算非负密度数组的 Gini 系数。

x = double(x(:));
x = x(isfinite(x));
x = x - min(0, min(x));
if isempty(x) || sum(x) == 0
    g = 0;
    return;
end
x = sort(x);
n = numel(x);
g = (2 * sum((1:n)' .* x) / (n * sum(x))) - (n + 1) / n;
end
