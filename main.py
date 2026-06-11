import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.widgets import Button, Slider

from solve import generate_system, gen_tableaux, newton
from test_method import Config, testall, ODEs

import pretty

def test():
    s = 2

    config = Config(300, -1.0, 1.0)

    symbols, equations = generate_system(s)
    tableaux = gen_tableaux(symbols, equations, s, config)

    fig, axs = plt.subplots(len(ODEs))
    if len(ODEs) == 1:
        axs = [axs]
    for j in range(len(ODEs)):
        config.dt = 0.01
        config.startt = config.dt
        config.endt = config.startt + config.dt

        c_vals = []
        errors = []
        while config.startt < np.pi * 2:

            sols = np.zeros(len(tableaux))
            for i, t in enumerate(tableaux):
                if t is not None:
                    err = testall(t, config)[j]
                    # sols.T[i] = np.abs(err)
                    sols.T[i] = err
                else:
                    sols.T[i] = np.nan
            
            m = np.nanmin(np.abs(sols))
            index = np.where(np.abs(sols) == m)[0][0]
            c_val = config.lbound + ((config.ubound - config.lbound) * index) / config.l
            c_vals.append(c_val)
            errors.append(sols[index])
            # print(index)

            config.startt += config.dt
            config.endt = config.startt + config.dt
        
        ran = np.arange(start=config.dt, stop=np.pi * 2, step=config.dt)
        axs[j].plot(ran, c_vals, label="c_2")
        axs[j].plot(ran, ODEs[j][0](ran, ODEs[j][1](ran)), label="ode")
        axs[j].plot(ran, ODEs[j][1](ran), label="exact")
        ax2 = axs[j].twinx()
        ax2.plot(ran, errors, label="err", color="gray", linestyle="--")
        ax2.set_ylabel("error")
        ax2.tick_params(axis="y")
        # ax2.set_yscale("symlog", linthresh=1e-10)
        axs[j].set_title(ODEs[j][2])
        axs[j].grid(which="both")

    plt.legend()
    plt.suptitle("[RK2] c_2 value with the lowest error")
    plt.show()

def nd_rotate(n, i, j, theta):
    R = np.eye(n)
    c, s = np.cos(theta), np.sin(theta)
    R[i, i] = c
    R[j, j] = c
    R[i, j] = -s
    R[j, i] = s
    return R

def explore():
    s = 9

    config = Config(100, -1, 1)
    config.dt = 0.01
    config.startt = 0
    config.endt = config.startt + config.dt

    symbols, equations = generate_system(s)
    pretty.add_system(symbols, equations)

    tableaux = newton(symbols, equations, s, config, guesses=50, max_steps=1000000, cap=5000)
    for t in tableaux:
        pretty.add_tableau(t)

    n = len(tableaux[0].to_array())
    errors = np.zeros((len(tableaux)))
    u = np.random.randn(n, 3)
    # u = np.zeros((n, 3))
    # u[6][0] = 1
    # u[7][1] = 1
    # u[2][2] = 1
    # u[-1][0] = 1
    # u[-2][1] = 1
    # u[-3][2] = 1
    u, _ = np.linalg.qr(u)
    def get_proj(R=None):
        if R is None:
            R = np.eye(n)
        proj = np.zeros((len(tableaux), 3))
        for i, t in enumerate(tableaux):
            proj[i,:] = (t.to_array() @ R.T) @ np.stack(u)
        
        return proj

    for i, t in enumerate(tableaux):
        errors[i] = testall(t, config)[0]
    proj = get_proj()

    errors = np.abs(errors)
    print(np.nanmin(errors))
    print(np.nanmax(errors))

    counter = [0]
    def on_press(event):
        s.set_val(s.val + 0.5)
        test(0)
        # fig.savefig(f"out/{counter[0]}.png", dpi=150)
        counter[0] += 1

    fig = plt.figure()
    fig.canvas.mpl_connect("key_press_event", on_press)
    ax = fig.add_subplot(projection="3d")
    p = ax.scatter(proj[:, 0], proj[:, 1], proj[:, 2], s=n, c=errors, norm=colors.LogNorm())
    plt.colorbar(p)

    def update(val):
        angles = [[np.deg2rad(s.val) if s is not None else 0 for s in ss] for ss in sliders]
        R = np.eye(n)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                R = nd_rotate(n, i, j, angles[i][j]) @ R
        proj = get_proj(R)
        p._offsets3d = proj.T

    sliders = [[None for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i >= j:
                continue
            sliders[i][j] = Slider(
                ax=fig.add_axes([0.15 + 0.12 * i, 0.15 - 0.02 * j, 0.05, 0.02]),
                label=f"{list(tableaux[0].dict.keys())[i]}*{list(tableaux[0].dict.keys())[j]}",
                valmin=-360,
                valmax= 360,
                valinit=0
            )
            sliders[i][j].on_changed(update)
    def test(val):
        sliders[4][5].set_val(s.val)
        sliders[0][3].set_val(s.val)
        sliders[2][6].set_val(s.val)
        update(0)

    s = Slider(
        ax=fig.add_axes([0.01, 0.5, 0.2, 0.02]),
        label=f"haha",
        valmin=-360,
        valmax= 360,
        valinit=0
    )
    s.on_changed(test)

    reset = fig.add_axes([0.6, 0.1, 0.05, 0.02])
    button = Button(reset, "Reset", hovercolor="0.975")
    def reset(event):
        for ss in sliders:
            for s in ss:
                if s is not None:
                    s.reset()
    button.on_clicked(reset)

    plt.show()
    pretty.render()

if __name__ == "__main__":
    # test()
    explore()