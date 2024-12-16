from modules.kml_loader import cargar_kml
from modules.data_loader import load_module_data
from modules.panel_optimizer import optimizar_paneles
from modules.visualizer import visualizar_paneles
from modules.export_results import export_results

def main():
    # Input parameters
    module_id = float(input("Enter module ID: ")) or '2'
    panels_x_module = int(input("Enter panels per module (per table): ")) or '56'

    # Street configuration
    modulos_entre_calles = float(input("Enter number of tables between streets: ")) or '30'
    ancho_calle = float(input("Enter street width (in meters): ")) or '8'

    # Pitch optimization parameters
    pitch_min = float(input("Enter minimum pitch value: ")) or '2'
    pitch_max = float(input("Enter maximum pitch value: ")) or '4'
    pitch_step = float(input("Enter pitch step value: ")) or '2.5'

    # Fenced area distance
    fenced_distance = float(input("Enter fenced distance (offset in meters): ")) or '10'

    # Project and racking details
    project_name = input("Enter project name: ") or 'Default'
    racking = input("Enter racking type (Fix Tilt/Tracker): ") or 'FixTilt'
    modules_per_string = int(input("Enter modules per string: ")) or '26'

    kml_path = input("Enter KML file path: ") or 'D:\FIDgate\ScopeGis\1\ScopeGis1\data\Zona1.kml'

    # Coordinate Reference System inputs
    input_crs = input("Enter input CRS (default: EPSG:4326): ") or 'EPSG:4326'
    output_crs = input("Enter output CRS (default: EPSG:25833): ") or 'EPSG:25833'

    module_specs = load_module_data(module_id)
    if not module_specs:
        return

    # Load KML zones with specified CRS
    zonas_habilitadas, zonas_inhabilitadas = cargar_kml(
        kml_path,
        input_crs=input_crs,
        output_crs=output_crs
    )
    if zonas_habilitadas is None or zonas_inhabilitadas is None:
        return

    # Optimize PV module placement
    lineas_paneles, total_modulos, total_energia, optimal_pitch, calles = optimizar_paneles(
        zonas_habilitadas,
        zonas_inhabilitadas,
        module_specs,
        panels_x_module,
        pitch_min,
        pitch_max,
        pitch_step,
        modulos_entre_calles=modulos_entre_calles,
        ancho_calle=ancho_calle,
        fenced_distance=fenced_distance
    )

    proyecto_extra_info = {
        'project_name': project_name,
        'racking': racking,
        'module_model': module_specs.get('PV Module Model', 'Unknown'),
        'fenced_distance': fenced_distance,
    }

    # Visualize results
    visualizar_paneles(
        zonas_habilitadas,
        zonas_inhabilitadas,
        lineas_paneles,
        total_modulos,
        total_energia,
        module_specs,
        panels_x_module,
        optimal_pitch,
        proyecto_extra_info=proyecto_extra_info,
        calles=calles
    )

    # Export results
    export_results(
        zonas_habilitadas,
        zonas_inhabilitadas,
        lineas_paneles,
        total_modulos,
        total_energia,
        module_specs,
        panels_x_module,
        optimal_pitch,
        racking,
        modules_per_string,
        project_name
    )

if __name__ == "__main__":
    main()