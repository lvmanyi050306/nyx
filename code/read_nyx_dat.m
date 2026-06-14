function volume = read_nyx_dat(filePath, gridSize, precision)
%READ_NYX_DAT Read one Nyx density volume from a binary .dat file.
%
% Files are little-endian float32. Linear order is z first, then y, then x.

if nargin < 3 || isempty(precision)
    precision = "single";
end

info = dir(filePath);
if isempty(info)
    error("read_nyx_dat:FileMissing", "File does not exist: %s", filePath);
end

bytesPerValue = bytes_per_value(precision);
valueCount = info.bytes / bytesPerValue;
if nargin < 2 || isempty(gridSize)
    n = round(valueCount^(1 / 3));
    if n^3 ~= valueCount
        error("read_nyx_dat:CannotInferGrid", ...
            "Cannot infer cubic grid size from %d values in %s.", valueCount, filePath);
    end
    gridSize = [n, n, n];
end

fid = fopen(filePath, "rb", "ieee-le");
if fid < 0
    error("read_nyx_dat:FileOpenFailed", "Cannot open file: %s", filePath);
end

cleanup = onCleanup(@() fclose(fid));
raw = fread(fid, prod(gridSize), char("*" + precision));

if numel(raw) ~= prod(gridSize)
    error("read_nyx_dat:SizeMismatch", ...
        "Expected %d values, got %d in %s.", prod(gridSize), numel(raw), filePath);
end

zyx = reshape(raw, [gridSize(3), gridSize(2), gridSize(1)]);
volume = permute(zyx, [3, 2, 1]);
end

function bytes = bytes_per_value(precision)
switch string(precision)
    case {"single", "float32"}
        bytes = 4;
    case {"double", "float64"}
        bytes = 8;
    otherwise
        error("read_nyx_dat:UnsupportedPrecision", "Unsupported precision: %s", precision);
end
end
