function V = read_nyx_dat(filename)
%READ_NYX_DAT 读取 Nyx little-endian float32 三维密度场。
% 原始线性存储顺序为 z 最快、y 其次、x 最慢。
% 输出 V 的维度为 [x, y, z]，便于 MATLAB 中按空间轴理解。

if nargin < 1 || ~isfile(filename)
    error('输入文件不存在：%s', string(filename));
end

fid = fopen(filename, 'r', 'ieee-le');
if fid < 0
    error('无法打开文件：%s', filename);
end

cleaner = onCleanup(@() fclose(fid));
data = fread(fid, inf, 'single=>single');
numVals = numel(data);
n = infer_grid_size(numVals);

% Nyx 原始数据：data(z, y, x)，先按 [z,y,x] 重排，再转为 [x,y,z]。
Vz_y_x = reshape(data, [n, n, n]);
V = permute(Vz_y_x, [3, 2, 1]);
V = single(V);
end
