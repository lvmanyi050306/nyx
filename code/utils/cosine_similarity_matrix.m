function S = cosine_similarity_matrix(H)
%COSINE_SIMILARITY_MATRIX 计算行向量之间的余弦相似性矩阵。
%   H 的每一行表示一个时间步的 log-density histogram probability 向量。

H = double(H);
H(~isfinite(H)) = 0;
norms = sqrt(sum(H.^2, 2));
norms(norms == 0) = eps;
Hn = H ./ norms;
S = Hn * Hn';
S = max(min(S, 1), -1);
end
