import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import numpy as np

def dibujar_geometria(geometria, ax, color="blue", label=None):
    """
    Draw geometry on matplotlib axis
    """
    from shapely.geometry import LineString, MultiLineString, GeometryCollection, Polygon
    
    if isinstance(geometria, LineString):
        x, y = geometria.coords.xy
        ax.plot(x, y, color=color, linewidth=2, label=label)
    elif isinstance(geometria, Polygon):
        # Extract exterior coordinates
        x, y = geometria.exterior.xy
        polygon = MplPolygon(list(zip(x, y)), closed=True, 
                              edgecolor=color, facecolor='none', 
                              linewidth=1, label=label)
        ax.add_patch(polygon)
    elif isinstance(geometria, MultiLineString):
        for linea in geometria.geoms:
            x, y = linea.coords.xy
            ax.plot(x, y, color=color, linewidth=1, label=label)
    elif isinstance(geometria, GeometryCollection):
        for geom in geometria.geoms:
            dibujar_geometria(geom, ax, color, label)

def visualizar_paneles(zonas_habilitadas, zonas_inhabilitadas,
                       lineas_paneles, total_modulos, total_energia,
                       module_specs, panels_x_module, pitch):
    """
    Create visualization of solar panel placement
    """
    print("\n=== GENERATING VISUALIZATION ===")
    
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot enabled zones
    if not zonas_habilitadas.empty:
        for _, zona in zonas_habilitadas.iterrows():
            dibujar_geometria(zona.geometry, ax, color='green', label='Enabled Zone')
    
    # Plot restricted zones
    if not zonas_inhabilitadas.empty:
        for _, zona in zonas_inhabilitadas.iterrows():
            dibujar_geometria(zona.geometry, ax, color='red', label='Restricted Zone')
    
    # Plot panel lines
    for i, panel in enumerate(lineas_paneles):
        dibujar_geometria(panel, ax, color='blue', label='Panel Lines' if i == 0 else None)
    
    plt.title("Solar Panel Placement")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    module_width = module_specs['width'] * panels_x_module
    
    # Create legend
    legend_text = (
        f"Panel Width: {module_specs['width']} m\n"
        f"Panel Length: {module_specs['length']} m\n"
        f"Panels per Module: {panels_x_module}\n"
        f"Module Width: {module_specs['length']} m\n"
        f"Module Length: {module_width} m\n"
        f"STC per Panel: {module_specs['stc']} W\n"
        f"Pitch: {pitch} m\n"
        f"Total Modules: {total_modulos}\n"
        f"Total Energy: {total_energia:.2f} W"
    )
    
    plt.text(1.05, 0.5, legend_text, transform=ax.transAxes,
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.legend()
    plt.grid(True)
    plt.axis('equal')  # This ensures the aspect ratio is 1:1
    plt.tight_layout()
    plt.show()