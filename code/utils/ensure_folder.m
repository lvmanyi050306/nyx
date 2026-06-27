function ensure_folder(folder)
%ENSURE_FOLDER 如果目录不存在则创建。

if ~isfolder(folder)
    mkdir(folder);
end
end
