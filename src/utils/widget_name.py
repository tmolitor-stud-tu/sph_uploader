import logging
logger = logging.getLogger(__name__)

def widget_name(widget):
    names = []
    obj = widget
    while obj != None:
        names.append(obj.objectName())
        obj = obj.parent()
    name = ".".join(names[::-1])
    logger.debug("full widget name: '%s'" % name)
    return name
