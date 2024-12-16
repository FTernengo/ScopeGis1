# export_results.py
import os
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString, Polygon
import xml.etree.ElementTree as ET
import zipfile
import warnings

def export_results(
    zonas_habilitadas,
    zonas_inhabilitadas,
    lineas_paneles,
    total_modulos,
    total_energia,
    module_specs,
    panels_x_module,
    pitch,
    racking,
    modules_per_string,
    project_name,
    input_crs='EPSG:4326'
):
    """
    Export solar PV layout results to KML/KMZ and Excel
    """
    print("\n=== EXPORTING RESULTS ===")

    # Suppress UserWarning about geographic CRS
    warnings.filterwarnings('ignore', category=UserWarning)

    # Convert panel lines to polygons
    panel_polygons = []
    for line in lineas_paneles:
        # Approximate panel polygon from line
        width = module_specs['length']
        height = module_specs['width'] * panels_x_module
        panel_poly = Polygon([
            (line.coords[0][0] - width/2, line.coords[0][1]),
            (line.coords[0][0] + width/2, line.coords[0][1]),
            (line.coords[1][0] + width/2, line.coords[1][1]),
            (line.coords[1][0] - width/2, line.coords[1][1])
        ])
        panel_polygons.append(panel_poly)

    # Create GeoDataFrame of panels
    gdf_panels = gpd.GeoDataFrame(geometry=panel_polygons, crs=zonas_habilitadas.crs)

    # Export KML/KMZ
    kml_filename = f"Layout_{project_name}.kmz"

    # Temporary files
    temp_kml = "temp_layout.kml"
    with zipfile.ZipFile(kml_filename, 'w', zipfile.ZIP_DEFLATED) as kmzfile:
        # Ensure panels are in WGS84 for KML
        gdf_panels_wgs84 = gdf_panels.to_crs('EPSG:4326')

        # Create KML content
        kml_content = create_kml_content(gdf_panels_wgs84, project_name, zonas_habilitadas, zonas_inhabilitadas)

        with open(temp_kml, 'w') as f:
            f.write(kml_content)
        kmzfile.write(temp_kml, arcname='doc.kml')
        os.remove(temp_kml)

    
    # Export Excel
    excel_filename = f"Layout_{project_name}_tables.xlsx"
    
    # Prepare Excel sheets
    with pd.ExcelWriter(excel_filename) as writer:
        # Technology Sheet
        tech_data = {
            'Parameter': ['PV Module Model', 'Racking'],
            'Value': [module_specs.get('model', 'Unknown'), racking]
        }
        pd.DataFrame(tech_data).to_excel(writer, sheet_name='Technology', index=False)
        
        # Capacity Sheet
        capacity_data = {
            'Parameter': [
                'DC Capacity', 
                'Module Power', 
                'Total Module Qty', 
                'Module Width', 
                'Module Length'
            ],
            'Value': [
                f"{total_energia/1_000_000:.2f} MWp",
                f"{module_specs['stc']} Wp",
                total_modulos * panels_x_module,
                module_specs['width'],
                module_specs['length']
            ]
        }
        pd.DataFrame(capacity_data).to_excel(writer, sheet_name='Capacity', index=False)
        
        # Assumptions Sheet
        total_area_ha = zonas_habilitadas.geometry.area.sum() / 10_000
        structure_conf = "1P" if racking == "Tracker" else "2P"
        assumptions_data = {
            'Parameter': [
                'Fenced Area', 
                'Pitch', 
                'Structure Conf.', 
                'Modules per String', 
                'Modules per Table', 
                'Total Table Qty'
            ],
            'Value': [
                f"{total_area_ha:.2f} Ha",
                pitch,
                structure_conf,
                modules_per_string,
                panels_x_module,
                total_modulos
            ]
        }
        pd.DataFrame(assumptions_data).to_excel(writer, sheet_name='Assumptions', index=False)
    
    print(f"Results exported to {kml_filename} and {excel_filename}")
    return kml_filename, excel_filename

def create_kml_content(gdf, project_name, zonas_habilitadas, zonas_inhabilitadas):
    """Create KML content from GeoDataFrame"""
    kml_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{project_name} Layout</name>
    <Folder>
        <name>PV Modules</name>
        {_generate_placemark_elements(gdf)}
    </Folder>
</Document>
</kml>'''
    return kml_template

def _generate_placemark_elements(gdf):
    """Generate KML placemark elements"""
    placemarks = []
    for idx, row in gdf.iterrows():
        coords = list(row.geometry.exterior.coords)
        coord_string = ' '.join([f"{lon},{lat},0" for lon, lat in coords])
        placemark = f'''
        <Placemark>
            <name>Panel {idx+1}</name>
            <Polygon>
                <outerBoundaryIs>
                    <LinearRing>
                        <coordinates>{coord_string}</coordinates>
                    </LinearRing>
                </outerBoundaryIs>
            </Polygon>
        </Placemark>'''
        placemarks.append(placemark)
    return ''.join(placemarks)