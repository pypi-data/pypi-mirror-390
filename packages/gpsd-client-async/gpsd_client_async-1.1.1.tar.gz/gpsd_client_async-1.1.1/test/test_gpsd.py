from gpsd_client_async import messages

def test_parse():
    with open("test/gpsd.log") as log:
        for line in log:
            print(messages.parse(line))


def test_parse_version():
    version_message = messages.parse('{"class":"VERSION","release":"3.25","rev":"3.25","proto_major":3,"proto_minor":15}')
    assert isinstance(version_message, messages.Version) 

def test_parse_devices():
    version_devices = messages.parse('{"class":"DEVICES","devices":[{"class":"DEVICE","path":"/dev/dtmux/0/ubl0","activated":"2025-04-07T10:36:58.805Z","native":0,"bps":38400,"parity":"N","stopbits":1,"cycle":1.00}]}')
    assert isinstance(version_devices, messages.Devices) 

def test_parse_watch():
    version_watch = messages.parse('{"class":"WATCH","enable":true,"json":true,"nmea":false,"raw":0,"scaled":false,"timing":false,"split24":false,"pps":false}')
    assert isinstance(version_watch, messages.Watch) 

def test_parse_device():
    version_device = messages.parse('{"class":"DEVICE","path":"/dev/dtmux/0/ubl0","driver":"u-blox","activated":"2025-04-07T10:37:19.631Z","native":1,"bps":38400,"parity":"N","stopbits":1,"cycle":1.00,"mincycle":0.02}')
    assert isinstance(version_device, messages.Device) 

def test_parse_tpv():
    version_tpv = messages.parse('{"class":"TPV","device":"/dev/dtmux/0/ubl0","mode":3,"time":"2025-04-07T10:37:20.000Z","ept":0.005,"lat":52.341913900,"lon":11.477318100,"altHAE":265.4160,"altMSL":220.9210,"alt":220.9210,"epv":1092.100,"track":0.0000,"magtrack":3.4864,"magvar":3.5,"speed":0.575,"eps":12.60,"geoidSep":43.030,"eph":400.355,"sep":169.290}')
    assert isinstance(version_tpv, messages.TPV) 

def test_parse_sky():
    version_sky = messages.parse('{"class":"SKY","device":"/dev/dtmux/0/ubl0","gdop":10.58,"hdop":3.89,"pdop":8.91,"tdop":5.71,"vdop":8.02}')
    assert isinstance(version_sky, messages.Sky) 
