function n = infer_grid_size(numVals)
%INFER_GRID_SIZE 根据体素总数自动推断 n，使 numVals = n^3。

if numVals <= 0 || fix(numVals) ~= numVals
    error('体素数量必须为正整数，当前为：%g', numVals);
end

n = round(double(numVals)^(1/3));
if n^3 ~= double(numVals)
    error('文件尺寸异常：体素总数 %d 不能组成 n×n×n 立方体网格。', numVals);
end
end
