function set_nyx_colormap()
%SET_NYX_COLORMAP Apply a perceptual colormap suitable for density fields.

try
    colormap(turbo);
catch
    colormap(parula);
end
end
