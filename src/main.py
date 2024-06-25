#!/bin/python
try:
    import usb
    from usb import _lookup as _lu
except Exception as e:
    print(f"Unable load modules: {e}")
    quit(5)

devices = usb.core.find(find_all=True)


def usb_get_string(device, code):
    try:
        value = usb.util.get_string(device, code)
    except Exception as e:
        value = str(e)


class Device:
    def __init__(self, device: usb.core.Device):
        self.device = device

    @property
    def Product(self):
        key = self.device.bDeviceClass
        table = _lu.device_classes
        default = "---"
        try:
            value = usb.util.get_string(self.device, self.device.iProduct)
        except ValueError:
            value = table[key]
        if value is None:
            value = default
        return value

    @property
    def speed(self):
        return self.device.speed

    @property
    def info(self):
        retval = {}
        for key in "idVendor", "idProduct", "bDeviceClass", "iProduct", "speed", "bus", "address", "port":
            try:
                retval[key] = getattr(self.device, key)
            except Exception as e:
                print(e)
        retval["Product"] = self.Product
        return retval



for dev in devices:
    # info = dev.get_info(dev)
    device = Device(dev)
    # dev_class = usb.core._try_lookup(usb.core._lu.device_classes, dev.bDeviceClass)

    # print(f"{dev.bDeviceClass} {dev_class}: {dev.idVendor:04X}:{dev.idProduct:04X} - {dev.bcdUSB}")
    print(device.info)
    print(f"speed: {device.speed}")
