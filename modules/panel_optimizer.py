import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.affinity import translate

def optimizar_paneles(zonas_habilitadas, zonas_inhabilitadas, module_specs, 
                     panels_x_module, pitch_min, pitch_max, pitch_step,
                     modulos_entre_calles=float('inf'), ancho_calle=0,
                     fenced_distance=0):
    """
    Optimize solar PV module placement with multiple enhancements:
    - Fenced area creation
    - Pitch range optimization
    - Street placement between module groups
    """
    print("\n=== STARTING ENHANCED MODULE OPTIMIZATION ===")

    pitch_results = []
    current_pitch = pitch_min

    while current_pitch <= pitch_max:
        # Apply fenced area reduction
        zonas_habilitadas_fenced = zonas_habilitadas.copy()
        zonas_habilitadas_fenced.geometry = zonas_habilitadas_fenced.geometry.buffer(-fenced_distance)

        # Prepare restricted zones union
        zona_restringida_union = zonas_inhabilitadas.geometry.unary_union if not zonas_inhabilitadas.empty else None

        lineas_paneles = []
        total_modulos = 0
        total_panels = 0
        total_energy = 0
        calles = []

        # Calculate module dimensions
        module_width = module_specs['length']
        module_length = module_specs['width'] * panels_x_module
        stc = module_specs['stc'] * panels_x_module

        for i, zona in enumerate(zonas_habilitadas_fenced.geometry):
            print(f"\nProcessing zone {i+1} with pitch {current_pitch}")
            print(f"Zone area: {zona.area} sq meters")
            print(f"Zone bounds: {zona.bounds}")

            if not zona.is_valid:
                print(f"Zone {i+1} is invalid, skipping...")
                continue

            minx, miny, maxx, maxy = zona.bounds
            current_x = minx
            modules_in_zone = 0
            column_count = 0

            while current_x + module_width <= maxx:
                current_y = miny
                column_modules = 0

                while current_y + module_length <= maxy:
                    module_polygon = Polygon([
                        (current_x, current_y),
                        (current_x + module_width, current_y),
                        (current_x + module_width, current_y + module_length),
                        (current_x, current_y + module_length)
                    ])

                    # Check if module is within enabled zone and not in restricted zones
                    if (zona.contains(module_polygon) and
                        (zona_restringida_union is None or not module_polygon.intersects(zona_restringida_union))):
                        module_line = LineString([
                            (current_x + module_width/2, current_y),
                            (current_x + module_width/2, current_y + module_length)
                        ])
                        lineas_paneles.append(module_line)
                        total_modulos += 1
                        modules_in_zone += 1
                        column_modules += 1
                        current_y += module_length
                    else:
                        # Skip placing module if it intersects with a restricted zone
                        current_y += module_length

                # Increment column count
                column_count += 1

                if column_count == modulos_entre_calles:
                    # Add street boundary lines
                    street_left_line = LineString([
                        (current_x + module_width, miny),
                        (current_x + module_width, maxy)
                    ])
                    street_right_line = LineString([
                        (current_x + module_width + ancho_calle, miny),
                        (current_x + module_width + ancho_calle, maxy)
                    ])
                    calles.append({
                        'left_boundary': street_left_line,
                        'right_boundary': street_right_line,
                        'width': ancho_calle
                    })
                    current_x += module_width + ancho_calle
                    column_count = 0
                else:
                    current_x += module_width + current_pitch

            total_panels = total_modulos * panels_x_module
            total_energy = total_panels * module_specs['stc']

            print(f"\nPitch {current_pitch} Summary:")
            print(f"Total modules: {total_modulos}")
            print(f"Total panels: {total_panels}")
            print(f"Total energy generated: {total_energy:.2f} W")

            pitch_results.append({
                'pitch': current_pitch,
                'total_modules': total_modulos,
                'total_panels': total_panels,
                'total_energy': total_energy,
                'lineas_paneles': lineas_paneles,
                'calles': calles
            })

            current_pitch += pitch_step

    best_result = max(pitch_results, key=lambda x: x['total_energy'])
    print("\n=== OPTIMIZATION COMPLETE ===")
    print(f"Best Pitch: {best_result['pitch']}")
    print(f"Maximum Energy: {best_result['total_energy']:.2f} W")

    return (
        best_result['lineas_paneles'],
        best_result['total_modules'],
        best_result['total_energy'],
        best_result['pitch'],
        best_result.get('calles', [])
    )