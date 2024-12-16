import pandas as pd

def load_module_data(module_id):
    """
    Load module data from CSV based on module ID
    
    Args:
        module_id (str): Unique identifier for the module
    
    Returns:
        dict: Module specifications or None if not found
    """
    print(f"\n=== LOADING MODULE DATA FOR ID {module_id} ===")
    
    try:
        # Load CSV file
        df = pd.read_csv('./Data/cec_module_test_fermin.csv')
        
        # Find module by ID
        module_data = df[df['ID'].astype(float) == module_id]

        
        if module_data.empty:
            print(f"ERROR: Module with ID {module_id} not found")
            return None
        
        # Extract module specifications
        module_spec = {
            'PV Module Model': module_data['Modelo'].values[0],
            'length': module_data['Length'].values[0],
            'width': module_data['Width'].values[0],
            'stc': module_data['STC'].values[0]
        
        }
        
        print("Module data found:")
        print(f"PV Module Model: {module_spec['PV Module Model']} m" )
        print(f"Length: {module_spec['length']} m")
        print(f"Width: {module_spec['width']} m")
        print(f"STC: {module_spec['stc']} W")
        
        return module_spec
    
    except FileNotFoundError:
        print("ERROR: CSV file not found")
        return None
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return None