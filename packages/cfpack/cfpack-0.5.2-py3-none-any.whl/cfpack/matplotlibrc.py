# legacy support (will be removed later)
from . import load_plot_style, print
print("deprecated and will be removed soon; use cfp.load_plot_style() instead.", warn=True)
load_plot_style()
