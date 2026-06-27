function [stageLabel, splitIdx] = simple_stage_segmentation(distFromStart)
%SIMPLE_STAGE_SEGMENTATION 基于距初始分布距离的简单四阶段划分。
%   将 distance_from_start 归一化后按 25%、50%、75% 分位划分为：
%   Early、Transition、Structure enhancement、Late。
%   若数据过少或分位数不稳定，则退化为按时间均分四段。

N = numel(distFromStart);
names = ["Early stage"; "Transition stage"; "Structure enhancement stage"; "Late stage"];
stageLabel = strings(N, 1);

if N == 0
    splitIdx = [];
    return;
end

d = double(distFromStart(:));
d(~isfinite(d)) = 0;
d = d - min(d);
if max(d) > 0
    d = d ./ max(d);
end

q = local_prctile(d, [25 50 75]);
useQuantile = numel(unique(round(q, 6))) == 3 && all(isfinite(q));

if useQuantile
    for i = 1:N
        if d(i) <= q(1)
            stageLabel(i) = names(1);
        elseif d(i) <= q(2)
            stageLabel(i) = names(2);
        elseif d(i) <= q(3)
            stageLabel(i) = names(3);
        else
            stageLabel(i) = names(4);
        end
    end
else
    edges = round(linspace(0, N, 5));
    for s = 1:4
        a = edges(s) + 1;
        b = max(edges(s + 1), a);
        stageLabel(a:b) = names(s);
    end
end

splitIdx = zeros(1, 3);
for s = 1:3
    idx = find(stageLabel == names(s), 1, 'last');
    if isempty(idx), idx = max(1, round(N * s / 4)); end
    splitIdx(s) = idx;
end
end

function q = local_prctile(x, p)
x = sort(x(:));
if isempty(x), q = nan(size(p)); return; end
pos = 1 + (numel(x) - 1) .* p(:)' ./ 100;
lo = floor(pos); hi = ceil(pos); w = pos - lo;
q = (1 - w) .* x(lo)' + w .* x(hi)';
end
