from modules.kml_loader import cargar_kml
from modules.data_loader import load_module_data
from modules.panel_optimizer import optimizar_paneles
from modules.visualizer import visualizar_paneles

def main():
    # Input parameters
    module_id = float(input("Enter module ID: "))
    panels_x_module = int(input("Enter panels per module: "))
    pitch = float(input("Enter pitch value (separacion): "))
    kml_path = input("Enter KML file path: ")
    modulos_entre_calles = int(input("Ingrese numero de modulos entre calles= "))
    ancho_calle= int(input("Ingrese ancho de calle: "))
    
    # Coordinate Reference System inputs
    input_crs = input("Enter input CRS (default: EPSG:4326): ") or 'EPSG:4326'
    output_crs = input("Enter output CRS (default: EPSG:25833): ") or 'EPSG:25833'

    # Load module data
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

    # Optimize panel placement
    lineas_paneles, total_modulos, total_energia = optimizar_paneles(
        zonas_habilitadas,
        zonas_inhabilitadas,
        module_specs,
        panels_x_module,
        pitch
    )

    # Visualize results
    visualizar_paneles(
        zonas_habilitadas,
        zonas_inhabilitadas,
        lineas_paneles,
        total_modulos,
        total_energia,
        module_specs,
        panels_x_module,
        pitch
    )

if __name__ == "__main__":
    main()