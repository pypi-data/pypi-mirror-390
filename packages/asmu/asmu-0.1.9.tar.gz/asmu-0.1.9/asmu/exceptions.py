

class UnitError(Exception):
    """Used if the physical unit is unknown or does not match."""
    pass


class DeviceError(Exception):
    """Device unknown or not specified."""
    pass
