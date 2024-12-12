import geopandas as gpd
from shapely.geometry import shape
import pyproj
from shapely.ops import transform

def cargar_kml(ruta_kml, input_crs='EPSG:4326', output_crs='EPSG:25833'):
    """
    Load and process KML file with flexible coordinate system transformation
    
    Args:
    ruta_kml (str): Path to KML file
    input_crs (str): Input coordinate reference system (default: WGS84)
    output_crs (str): Output coordinate reference system (default: UTM zone 33N)
    
    Returns:
    tuple: Enabled and restricted zones as GeoDataFrames in the output CRS
    """
    print("\n=== STARTING KML FILE LOAD ===")
    print(f"Trying to load file: {ruta_kml}")
    print(f"Input CRS: {input_crs}")
    print(f"Output CRS: {output_crs}")
    
    try:
        # Read KML file
        gdf = gpd.read_file(ruta_kml, driver='KML')
        
        # Define coordinate transformations
        input_proj = pyproj.CRS(input_crs)
        output_proj = pyproj.CRS(output_crs)
        
        # Create transformer
        project = pyproj.Transformer.from_crs(input_proj, output_proj, always_xy=True).transform

        # Transform geometries
        def transform_geometry(geometry):
            try:
                # Convert to Shapely geometry if not already
                poly = shape(geometry) if hasattr(geometry, '__geo_interface__') else geometry
                
                # Transform geometry
                transformed_poly = transform(project, poly)
                
                # Ensure it's a valid polygon
                if not transformed_poly.is_valid:
                    transformed_poly = transformed_poly.buffer(0)
                return transformed_poly
            except Exception as e:
                print(f"Error processing geometry: {e}")
                return None

        # Normalize column names
        gdf['Name'] = gdf['Name'].str.lower().str.strip()

        # Filter zones
        zonas_habilitadas = gdf[gdf['Name'] == 'enabled'].copy()
        zonas_inhabilitadas = gdf[gdf['Name'] == 'restricted'].copy()

        # Apply coordinate transformation
        zonas_habilitadas['geometry'] = zonas_habilitadas['geometry'].apply(transform_geometry)
        zonas_inhabilitadas['geometry'] = zonas_inhabilitadas['geometry'].apply(transform_geometry)

        # Remove any None geometries
        zonas_habilitadas = zonas_habilitadas[zonas_habilitadas['geometry'].notna()]
        zonas_inhabilitadas = zonas_inhabilitadas[zonas_inhabilitadas['geometry'].notna()]

        return zonas_habilitadas, zonas_inhabilitadas
    except Exception as e:
        print(f"Error loading KML: {e}")
        return None, None