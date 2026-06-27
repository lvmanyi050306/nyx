function y = smoothstep(edge0, edge1, x)
%SMOOTHSTEP 平滑阶跃函数，用于透明度传递函数。

if edge1 == edge0
    y = double(x >= edge1);
    return;
end
t = (x - edge0) ./ (edge1 - edge0);
t = min(max(t, 0), 1);
y = t .* t .* (3 - 2 .* t);
end
