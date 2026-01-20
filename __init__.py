
def classFactory(iface):
    from .bbox_coords_plugin import BBoxCoordsPlugin
    return BBoxCoordsPlugin(iface)
