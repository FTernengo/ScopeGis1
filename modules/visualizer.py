import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle
from matplotlib.patches import Arrow
import numpy as np
from shapely.geometry import LineString, MultiLineString, GeometryCollection, Polygon

def dibujar_geometria(geometria, ax, color="blue", label=None):
    """
    Draw geometry on matplotlib axis
    """
    if isinstance(geometria, LineString):
        x, y = geometria.coords.xy
        ax.plot(x, y, color=color, linewidth=2, label=label)
    elif isinstance(geometria, Polygon):
        x, y = geometria.exterior.xy
        polygon = MplPolygon(list(zip(x, y)), closed=True,
                            edgecolor=color, facecolor=color,
                            linewidth=1, label=label, alpha=0.7)
        ax.add_patch(polygon)
    elif isinstance(geometria, MultiLineString):
        for linea in geometria.geoms:
            x, y = linea.coords.xy
            ax.plot(x, y, color=color, linewidth=1, label=label)
    elif isinstance(geometria, GeometryCollection):
        for geom in geometria.geoms:
            dibujar_geometria(geom, ax, color, label)

def agregar_norte(ax, x_offset=0.02, y_offset=0.94, arrow_length=0.03):
    """
    Add North arrow to the plot
    """
    arrow = Arrow(x_offset, y_offset, 0, arrow_length,
                  width=0.005, color='black', transform=ax.transAxes)
    ax.add_patch(arrow)
    ax.text(x_offset, y_offset + arrow_length * 1.2, 'N',
            transform=ax.transAxes, ha='center', va='bottom')

def agregar_escala(ax, zonas_habilitadas):
    """
    Add scale bar to the plot
    """
    zone_bounds = zonas_habilitadas.geometry.total_bounds
    zone_width = zone_bounds[2] - zone_bounds[0]
    scale_length = zone_width * 0.25
    scale_text = f'{scale_length:.2f} m'
    x_min, y_min = zone_bounds[0], zone_bounds[1]
    ax.plot([x_min, x_min + scale_length],
            [y_min, y_min],
            color='black', linewidth=2)
    ax.text(x_min + scale_length/2, y_min - zone_width*0.01,
            scale_text, ha='center', va='top')

def visualizar_paneles(zonas_habilitadas, zonas_inhabilitadas,
                      lineas_paneles, total_modulos, total_energia,
                      module_specs, panels_x_module, pitch,
                      proyecto_extra_info=None, calles=None):
    """
    Create visualization of solar panel placement
    """
    print("\n=== GENERATING VISUALIZATION ===")
    fig, ax = plt.subplots(figsize=(20, 15))

    # Plot enabled zones
    if not zonas_habilitadas.empty:
        for _, zona in zonas_habilitadas.iterrows():
            zona_geom = zona.geometry
            dibujar_geometria(zona_geom, ax, color='yellow', label='PV Area')

    # Plot restricted zones
    if not zonas_inhabilitadas.empty:
        for _, zona in zonas_inhabilitadas.iterrows():
            zona_geom = zona.geometry
            dibujar_geometria(zona_geom, ax, color='red', label='Restricted Area')

    # Plot fenced area
    fenced_area = zonas_habilitadas.geometry.unary_union.buffer(-proyecto_extra_info['fenced_distance'])
    dibujar_geometria(fenced_area, ax, color='#FFFF00', label='Fenced Area')

    # Plot panel lines as polygons
    module_width = module_specs['length']
    module_length = module_specs['width'] * panels_x_module
    for panel in lineas_paneles:
        center_x, center_y = panel.centroid.coords[0]
        panel_poly = Polygon([
            (center_x - module_width/2, center_y),
            (center_x + module_width/2, center_y),
            (center_x + module_width/2, center_y + module_length),
            (center_x - module_width/2, center_y + module_length)
        ])
        dibujar_geometria(panel_poly, ax, color='#AEF66A')

    # Plot streets
    if calles:
        for calle in calles:
            dibujar_geometria(calle['left_boundary'], ax, color='brown')
            dibujar_geometria(calle['right_boundary'], ax, color='brown')

    plt.title(f"Layout: {proyecto_extra_info.get('project_name', 'Project Example')} - DK")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.axis('equal')

    # Create new custom legends
    legend_props = dict(facecolor='#AEF66A', alpha=0.5, boxstyle='round')

    # Technology Legend
    tech_text = (
        "Technology\n"
        f"PV Module Model: {proyecto_extra_info.get('module_model', 'Unknown')}\n"
        f"Racking: {proyecto_extra_info.get('racking', 'Unknown')}"
    )
    plt.text(1.02, 0.9, tech_text, transform=ax.transAxes, fontsize=10,
             verticalalignment='top', bbox=legend_props)

    # Capacity Legend
    capacity_text = (
        "Capacity, Quantities & Dimensions\n"
        f"DC Capacity: {total_energia/1_000_000:.2f} MWp\n"
        f"Module Power: {module_specs['stc']} Wp\n"
        f"Total Module Qty: {total_modulos * panels_x_module}\n"
        f"Module Width: {module_specs['width']:.2f} m\n"
        f"Module Length: {module_specs['length']:.2f} m"
    )
    plt.text(1.02, 0.6, capacity_text, transform=ax.transAxes, fontsize=10,
             verticalalignment='top', bbox=legend_props)

    # Assumptions Legend
    total_area_ha = zonas_habilitadas.geometry.area.sum() / 10_000
    assumptions_text = (
        "Assumptions\n"
        f"Fenced Area: {total_area_ha:.2f} Ha\n"
        f"Pitch: {pitch:.2f} m\n"
        f"Structure Conf.: {'1P' if proyecto_extra_info.get('racking') == 'Tracker' else '2P'}\n"
        f"Modules per String: {proyecto_extra_info.get('modules_per_string', 26)}\n"
        f"Modules per Table: {panels_x_module}\n"
        f"Total Table Qty: {total_modulos:.2f}"
    )
    plt.text(1.02, 0.3, assumptions_text, transform=ax.transAxes, fontsize=10,
             verticalalignment='top', bbox=legend_props)

    agregar_norte(ax)
    agregar_escala(ax, zonas_habilitadas)
    plt.tight_layout()
    plt.show()