# File plot_utils.py Functions to plot variable as in world3 graphics.
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
from matplotlib.image import imread

# Taken from pyworld3
def plot_world_variables(time, var_data, var_names, var_lims,
                         img_background=None,
                         title=None,
                         figsize=None,
                         dist_spines=0.09,
                         grid=False,
                         colors=None):
    """
    Plots world state from an instance of World3 or any single sector.

    """
    if not colors:
        prop_cycle = plt.rcParams['axes.prop_cycle']
        colors = prop_cycle.by_key()['color']
    else:
        colors = [colors[i] for i in var_names]
        
    var_number = len(var_data)
    
    fig, hosts = plt.subplots(1, 1, figsize=figsize)
    if not isinstance(hosts,list):
        hosts = [hosts]
    for host in hosts:
        axs = [host, ]
        for i in range(var_number-1):
            axs.append(host.twinx())

        fig.subplots_adjust(left=dist_spines*2)
        for i, ax in enumerate(axs[1:]):
            ax.spines["left"].set_position(("axes", -(i + 1)*dist_spines))
            ax.spines["left"].set_visible(True)
            ax.yaxis.set_label_position('left')
            ax.yaxis.set_ticks_position('left')

        if img_background is not None:
            im = imread(img_background)
            axs[0].imshow(im, aspect="auto",
                          extent=[time[0], time[-1],
                                  var_lims[0][0], var_lims[0][1]], cmap="gray")

        ps = []
        for ax, label, ydata, color in zip(axs, var_names, var_data, colors):
            ps.append(ax.plot(time, ydata, label=label, color=color)[0])
            axs[0].grid(grid)
            axs[0].set_xlim(time[0], time[-1])

        for ax, lim in zip(axs, var_lims):
            ax.set_ylim(lim[0], lim[1])

        for ax_ in axs:
            formatter_ = EngFormatter(places=0, sep="\N{THIN SPACE}")
            ax_.tick_params(axis='y', rotation=90)
            ax_.yaxis.set_major_locator(plt.MaxNLocator(5))
            ax_.yaxis.set_major_formatter(formatter_)

        tkw = dict(size=4, width=1.5)
        axs[0].set_xlabel("time [years]")
        axs[0].tick_params(axis='x', **tkw)
        for i, (ax, p) in enumerate(zip(axs, ps)):
            ax.set_ylabel(p.get_label(), rotation="horizontal")
            ax.yaxis.label.set_color(p.get_color())
            ax.tick_params(axis='y', colors=p.get_color(), **tkw)
            ax.yaxis.set_label_coords(-i*dist_spines, 1.01)

    if title is not None:
        fig.suptitle(title, x=0.95, ha="right", fontsize=10)

    plt.tight_layout()

# Default scales of variables
default_plot_variables_scales = {"nrfr": [0,1],
                          "iopc": [0,1e3],
                          "fpc": [0,1e3],
                          "pop": [0,16e9],
                          "ppolx": [0,32]
                         }

def plot_world_with_scales(w, variable_scales=None, title="W3 run"):
    """
    Plot world3 variables, with potentially new scales.

    Parameters
    ----------
    w: world3
        Instance to plot
    variables: dict(str, [float, float])
        Dict of Variable name and range
    title: str
        Plot title

    Returns
    -------
    """

    if not variable_scales:
        variable_scales = default_plot_variables_scales

    plot_world_variables(w.get_time(),
                    list(map(w.get_var,
                             variable_scales.keys())),
                    variable_scales.keys(),
                    variable_scales.values(),
                    figsize = (7,5),
                    grid = 1,
                    title = title)

# New scales for 03 version (p456)
colors_03 = {
    'pop':'#d62728',
    'f': '#2ca02c',
    'io': '#ff7f0e',
    'ppolx': '#9467bd',
    'nr': '#1f77b4',
    'fpc': '#2ca02c',
    'ciopc': '#ff7f0e',
    'isopc': '#bcbd22',
    'le': '#d62728',
    'hwi': '#d62728',
    'hef': '#2ca02c'
    }
scale_03_state = {
    'pop': [0, 12e9],
    'f': [0, 6e12],
    'io': [0, 4e12],
    'ppolx': [0, 40],
    'nr': [0, 2e12]
    }
scale_03_life = {
    'fpc': [0, 1000],
    'ciopc': [0, 250],
    'isopc': [0, 1000],
    'le': [0, 90],
    }
scale_03_indices = {
    'hwi': [0, 1],
    'hef': [0, 4]
    }
def plot_03_state(s, title='State'):
    plot_world_variables(s.get_time(),
                         list(map(s.get_var,
                                  scale_03_state.keys())),
                         scale_03_state.keys(),
                         scale_03_state.values(),
                         figsize = (7,5),
                         grid = 1,
                         title = title,
                         colors=colors_03)
def plot_03_life(s, title='Life level'):
    plot_world_variables(s.get_time(),
                         list(map(s.get_var,
                                  scale_03_life.keys())),
                         scale_03_life.keys(),
                         scale_03_life.values(),
                         figsize = (7,5),
                         grid = 1,
                         title = title,
                         colors=colors_03)
def plot_03_indices(s, title='Indices level'):
    plot_world_variables(s.get_time(),
                         list(map(s.get_var,
                                  scale_03_indices.keys())),
                         scale_03_indices.keys(),
                         scale_03_indices.values(),
                         figsize = (7,5),
                         grid = 1,
                         title = title,
                         colors=colors_03)
    
def plot_world_03(s, title=None, with_legend=False):
    """
    Plots world variables with 2003 way.

    """
    
    
    scales = [scale_03_state, scale_03_life, scale_03_indices]
    try:
        time = s.time
    except AttributeError as e:
        raise Exception("System must be run before plot !") from e

    
    if with_legend:
        figsize = (8,12)
    else:
        figsize = (7, 12)

    dist_spines=0.09
    grid=1
    img_background=None
    fig, hosts = plt.subplots(3, 1, figsize=figsize)
    pretitles = ['World state', 'Material life level', 'Welfare and footprint']
    for nn, (host, scale, pretitle) in enumerate(zip(hosts, scales, pretitles)):
        var_number = len(scale)
        var_names = scale.keys()
        var_data = [getattr(s,i) for i in scale]
        var_lims = scale.values()
        colors = [colors_03[i] for i in var_names]
        
        axs = [host, ]
        for i in range(var_number-1):
            axs.append(host.twinx())

        fig.subplots_adjust(left=dist_spines*2)
        for i, ax in enumerate(axs[1:]):
            ax.spines["left"].set_position(("axes", -(i + 1)*dist_spines))
            ax.spines["left"].set_visible(True)
            ax.yaxis.set_label_position('left')
            ax.yaxis.set_ticks_position('left')

        ps = []
        for ax, label, ydata, color in zip(axs, var_names, var_data, colors):
            ps.append(ax.plot(time, ydata, label=label, color=color)[0])
            axs[0].grid(grid)
            axs[0].set_xlim(time[0], time[-1])

        for ax, lim in zip(axs, var_lims):
            ax.set_ylim(lim[0], lim[1])

        for ax_ in axs:
            formatter_ = EngFormatter(places=0, sep="\N{THIN SPACE}")
            ax_.tick_params(axis='y', rotation=90)
            ax_.yaxis.set_major_locator(plt.MaxNLocator(5))
            ax_.yaxis.set_major_formatter(formatter_)
            
        tkw = dict(size=4, width=1.5)
        axs[0].set_xlabel("time [years]")
        axs[0].tick_params(axis='x', **tkw)
        for i, (ax, p) in enumerate(zip(axs, ps)):
            ax.set_ylabel(p.get_label(), rotation="horizontal")
            ax.yaxis.label.set_color(p.get_color())
            ax.tick_params(axis='y', colors=p.get_color(), **tkw)
            ax.yaxis.set_label_coords(-i*dist_spines, 1.01)
        
        axs[0].set_xticks([1900, 1950, 2000, 2050, 2100])
        axs[0].set_yticks([i*max(list(var_lims)[0])/4 for i in range(5)])
        if with_legend:
            fig.legend(ps, [s.definition(name).capitalize() for name in var_names], bbox_to_anchor = (0.97, 0.96 - nn/3), loc='upper left')
        
        if pretitle is not None:
            host.set_title(pretitle, x=0.95, ha="right", fontsize=10)
    if title is not None:
            fig.suptitle(title, fontsize=15)
    plt.tight_layout()


def plot_world_03_compare(s, s2, title=None, with_legend=False, *args, **kwargs):
    """Compare in the main variables of the worlds, plotted in the "Limits To Growth: the 30th year update" way.
    
    Parameters
    ----------
    s : 
        World3 object (with simulation already run).
    s2 :
        World3 object to compare (with simulation already run).
    
    args, kwargs :
        See pydynmao.core.plot_utils.plot_world arguments.
    """

    scales = [scale_03_state, scale_03_life, scale_03_indices]
    try:
        time = s.time
        time2 = s2.time
    except AttributeError as e:
        raise Exception("System must be run before plot !") from e

    
    if with_legend:
        figsize = (8,12)
    else:
        figsize = (7, 12)

    dist_spines=0.09
    grid=1
    img_background=None
    fig, hosts = plt.subplots(3, 1, figsize=figsize)
    pretitles = ['World state', 'Material life level', 'Welfare and footprint']
    for nn, (host, scale, pretitle) in enumerate(zip(hosts, scales, pretitles)):
        var_number = len(scale)
        var_names = scale.keys()
        var_data = [getattr(s,i) for i in scale]
        var_data_2 = [getattr(s2,i) for i in scale]
        var_lims = scale.values()
        colors = [colors_03[i] for i in var_names]
        
        axs = [host, ]
        for i in range(var_number-1):
            axs.append(host.twinx())

        fig.subplots_adjust(left=dist_spines*2)
        for i, ax in enumerate(axs[1:]):
            ax.spines["left"].set_position(("axes", -(i + 1)*dist_spines))
            ax.spines["left"].set_visible(True)
            ax.yaxis.set_label_position('left')
            ax.yaxis.set_ticks_position('left')

        ps = []
        for ax, label, ydata, ydata2, color in zip(axs, var_names, var_data, var_data_2, colors):
            ps.append(ax.plot(time, ydata, label=label, color=color)[0])
            ps.append(ax.plot(time, ydata2, label=label, color=color, linestyle='--')[0])
            axs[0].grid(grid)
            axs[0].set_xlim(time[0], time[-1])

        # Axes
        for ax, lim in zip(axs, var_lims):
            ax.set_ylim(lim[0], lim[1])

        for ax_ in axs:
            formatter_ = EngFormatter(places=0, sep="\N{THIN SPACE}")
            ax_.tick_params(axis='y', rotation=90)
            ax_.yaxis.set_major_locator(plt.MaxNLocator(5))
            ax_.yaxis.set_major_formatter(formatter_)

        # Legends & ticks
        tkw = dict(size=4, width=1.5)
        axs[0].set_xlabel("time [years]")
        axs[0].tick_params(axis='x', **tkw)
        for i, (ax, p) in enumerate(zip(axs, ps)):
            ax.set_ylabel(p.get_label(), rotation="horizontal")
            ax.yaxis.label.set_color(p.get_color())
            ax.tick_params(axis='y', colors=p.get_color(), **tkw)
            ax.yaxis.set_label_coords(-i*dist_spines, 1.01)
        
        axs[0].set_xticks([1900, 1950, 2000, 2050, 2100])
        axs[0].set_yticks([i*max(list(var_lims)[0])/4 for i in range(5)])

        
        if with_legend:
            fig.legend(ps[::2], [s.definition(name).capitalize() for name in var_names], bbox_to_anchor = (0.97, 0.96 - nn/3), loc='upper left')

        # Title
        if pretitle is not None:
            host.set_title(pretitle, x=0.95, ha="right", fontsize=10)
    if title is not None:
            fig.suptitle(title, fontsize=15)
    plt.tight_layout()
