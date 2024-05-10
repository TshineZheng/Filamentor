


def test_get_first_fila_from_gcode_file():
    from impl.bambu_client import BambuClient
    url = 'https://raw.githubusercontent.com/TshineZheng/Filamentor/main/test/test.3mf'
    path = 'Metadata/plate_1.gcode'
    fila_channel = BambuClient.get_first_fila_from_gcode(url, path)
    assert fila_channel == 0
