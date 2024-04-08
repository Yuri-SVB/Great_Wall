from greatwall.resources.greatwall import GreatWall
from greatwall.resources import constants

def test_memory_file_system():

    greatwall = GreatWall()

    properties = dir(greatwall)
    assert('memory_file_system' in properties)
    assert('memory_file_system_data_load' in properties)
    assert('memory_file_system_data_name' in properties)
    assert('memory_file_system_data_save' in properties)

    key_fractal = '0,0,1,0'
    name_fractal = greatwall.memory_file_system_data_name(
        key_fractal,
        constants.EXTENSION_FRACTAL,
    )

    blob_fractal = greatwall.memory_file_system_data_load(name_fractal)
    assert(blob_fractal is None)

    blob_fractal = b'ABCDEFG'
    greatwall.memory_file_system_data_save(name_fractal, blob_fractal)

    load_fractal = blob_fractal = greatwall.memory_file_system_data_load(name_fractal)
    assert(blob_fractal == load_fractal)



