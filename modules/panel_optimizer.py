import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.affinity import translate

def optimizar_paneles(zonas_habilitadas, zonas_inhabilitadas, module_specs, panels_x_module, pitch,
modulos_entre_calles=float('inf'),
ancho_calle=0
):
    """
    Optimize solar panel placement based on enabled and restricted zones.
    """
    print("\n=== STARTING LINE-BASED MODULE OPTIMIZATION ===")
    
    # Prepare restricted zones union
    zona_restringida_union = None
    if not zonas_inhabilitadas.empty:
        zona_restringida_union = zonas_inhabilitadas.geometry.unary_union
    
    # Lists to store results
    lineas_paneles = []
    total_modulos = 0
    total_panels = 0
    total_energy = 0
    
    # Calculate module dimensions
    module_width = module_specs['length']  # X-axis length (panel length)
    module_length = module_specs['width'] * panels_x_module  # Y-axis length (multiple panels)
    stc = module_specs['stc'] * panels_x_module  # Total power per module
    
    # Process each enabled zone
    for i, zona in enumerate(zonas_habilitadas.geometry):
        print(f"\nProcessing zone {i+1}")
        print(f"Zone area: {zona.area} sq meters")
        print(f"Zone bounds: {zona.bounds}")
        
        if not zona.is_valid:
            print(f"Zone {i+1} is invalid, skipping...")
            continue
        
        # Get zone bounds
        minx, miny, maxx, maxy = zona.bounds
        
        # Debug print zone dimensions
        print(f"Zone bounds: Min X={minx}, Min Y={miny}, Max X={maxx}, Max Y={maxy}")
        print(f"Module dimensions: Length={module_length}, Width={module_width}")
        print(f"Module between streets: {modulos_entre_calles}")
        print(f"Street width: {ancho_calle}")
        
        # Adjust start and end points to ensure modules fit
        current_x = minx  # Start X position
        modules_in_zone = 0
        column_count=0
        
        while current_x + module_width <= maxx:
            current_y = miny  # Reset Y position for each column
            column_modules=0
            
            while current_y + module_length <= maxy:
                # Create a polygon representing the module
                module_polygon = Polygon([
                    (current_x, current_y),
                    (current_x + module_width, current_y),
                    (current_x + module_width, current_y + module_length),
                    (current_x, current_y + module_length)
                ])
                
                # Check if module is entirely within enabled zone and not intersecting restricted zones
                if (zona.contains(module_polygon) and 
                    (zona_restringida_union is None or not module_polygon.intersects(zona_restringida_union))):
                    
                    # Use module's center line for visualization
                    module_line = LineString([
                        (current_x + module_width/2, current_y),
                        (current_x + module_width/2, current_y + module_length)
                    ])
                    
                    lineas_paneles.append(module_line)
                    total_modulos += 1
                    modules_in_zone += 1
                    column_modules +=1
                
                # Move to next placement position along Y-axis
                current_y += module_length
            
            # Move to next column along X-axis
            current_x += module_width + pitch

        column_count += 1    

         # Decide whether to add a street
        if column_count == modulos_entre_calles:
            #add street width to x movement
            current_x += module_width + ancho_calle
            column_count = 0
        else:
            #normal column movement
            current_x += module_width + pitch     
        
    print(f"Zone {i+1}: {modules_in_zone} modules placed")
    
    # Calculate total panels and energy
    total_panels = total_modulos * panels_x_module
    total_energy = total_panels * (module_specs['stc'])
    
    print("\nSUMMARY:")
    print(f"Total modules: {total_modulos}")
    print(f"Total panels: {total_panels}")
    print(f"Total energy generated: {total_energy:.2f} W")
    
    return lineas_paneles, total_modulos, total_energy