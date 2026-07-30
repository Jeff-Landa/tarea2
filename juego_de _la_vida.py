import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
#Configuración
FILAS = 60
COLUMNAS = 90
PROB_VIVA = 0.25
INTERVALO_MS = 80

grid = (np.random.rand(FILAS, COLUMNAS) < PROB_VIVA).astype(int)

def siguiente_generacion(grid):
    vecinos = (
        np.roll(grid,  1, axis=0) +
        np.roll(grid, -1, axis=0) +
        np.roll(grid,  1, axis=1) +
        np.roll(grid, -1, axis=1) +
        np.roll(np.roll(grid,  1, axis=0),  1, axis=1) +
        np.roll(np.roll(grid,  1, axis=0), -1, axis=1) +
        np.roll(np.roll(grid, -1, axis=0),  1, axis=1) +
        np.roll(np.roll(grid, -1, axis=0), -1, axis=1)
    )

    nueva = np.where(
        (grid == 1) & ((vecinos == 2) | (vecinos == 3)), 1,
        np.where((grid == 0) & (vecinos == 3), 1, 0)
    )
    return nueva
#Visualización
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_title("Juego de la Vida (clic para editar celdas)")
ax.axis("off")

im = ax.imshow(grid, cmap="Greens", interpolation="nearest", vmin=0, vmax=1)

def update(_):
    global grid
    grid = siguiente_generacion(grid)
    im.set_data(grid)
    return (im,)
#Edición con mouse
def on_click(event):
    #Ignora clics fuera del área del heatmap
    if event.inaxes != ax:
        return

    #Convertir coordenadas del clic a índice de celda
    #im se dibuja con extent implícito de [0..COLUMNAS) y [0..FILAS)
    x = int(event.xdata)
    y = int(event.ydata)

    if 0 <= y < FILAS and 0 <= x < COLUMNAS:
        if event.button == 1:      # ⬅️ botón izquierdo
            grid[y, x] = 1
        elif event.button == 3:    # ➡️ botón derecho
            grid[y, x] = 0
        im.set_data(grid)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', on_click)

ani = FuncAnimation(fig, update, interval=INTERVALO_MS, blit=True)
plt.show()
