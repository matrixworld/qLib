"""
        @file       qlibutils.py
        @author     xy
        @since      2019-11-13

        @brief      Functions for building attribute popup menus.
"""

import hou

import re
import traceback



def buildAttribLabel(a, showClass=True):
    """Build an informative attrib label.

    TODO:
        - show unique values for ints too? not just strings?
    """
    assert type(a) is hou.Attrib
    csh = { "global": "detail", "point": "pt", "vertex": "vtx" }
    had=hou.attribData

    td = { had.String:'s', had.Int:'i', had.Float:'f' }
    t = a.dataType()
    ts = a.size()

    ty = '?'
    if t in td: ty = td[t]
    if ts==3: ty='v'
    if ts==4: ty='p'

    ax=[]
    if showClass:
        c = re.search('[^.]+$', str(a.type()) ).group(0).lower()
        if c in csh: c = csh[c]
        ax.append(c)

    q = a.qualifier()
    if q and q!='':
        ax.append(str(q).lower())

    s = len(a.strings())
    if s>0: ax.append('strings:%d' % s)

    ax = ' (%s)' % ', '.join(ax) if len(ax) else ''
    R = '%s@  %s%s' % (ty, a.name(), ax, )
    return R



def buildAttribMenu(
        kwargs,         # regular hou kwargs
        attribClass,    # string or tuple
        inputGeo=None,  # either a hou.Geometry or None means function will try its best
        filter=None,    # filter function, taking a hou.Attrib object
        showClass=None, # None, True or False, to override default decision
                        # if attribute class should be shown
    ):
    """Build an attribute popup menu based on various criteria.

    """
    assert type(kwargs) is dict, "expected a valid kwargs dict"
    assert type(attribClass) in (str, tuple, list, ), "invalid attribClass argument"

    # auto-detect geometry input if necessary
    #
    if not inputGeo and kwargs and kwargs.has_key("node"):
        i = kwargs["node"].inputs()
        if len(i):
            inputGeo = i[0].geometry()

    # process attribClass input
    #
    if type(attribClass) is str:
        # support plain strings like "point primitive"
        attribClass = tuple(attribClass.split())

    if "all" in attribClass:
        attribClass = ("point", "primitive", "vertex", "detail", )

    if "comp" in attribClass or "component" in attribClass:
        attribClass = ("point", "primitive", "vertex", )

    if type(attribClass) is not tuple:
        # this is intended for lists
        attribClass = tuple(attribClass)

    attribClass = tuple(sorted(attribClass))

    #print "inputGeo:", str(inputGeo)
    #print "attribClass:", str(attribClass)

    if not inputGeo:
        raise hou.OperationFailed("Couldn't determine input geometry")

    # collect attributes, filter and sort them
    #
    get_funcs = {"point": "pointAttribs",
        "primitive": "primAttribs",
        "prim": "primAttribs",
        "vertex": "vertexAttribs",
        "detail": "globalAttribs",
        "global": "globalAttribs" }

    show_class = len(attribClass)>1
    if showClass:
        show_class = showClass

    R = []
    for c in attribClass:

        # get them attributes
        attribs = ()
        if c in get_funcs:
            attribs = inputGeo.__getattribute__(get_funcs[c])()

        # filter them if required
        if filter:
            attribs = [ a for a in attribs if filter(a) ]

        # sort 'em alphabetically
        attribs = sorted(attribs, key = lambda a: a.name().lower())

        for a in attribs:
            R.append(a.name())
            R.append(buildAttribLabel(a, showClass=show_class))

        # add menu separator between classes
        if c!=attribClass[-1]:
            R.append("_separator_")
            R.append("")

    return R



def isNumeric(hou_attrib):
    """Convenience filter function for numeric (int/float of size 1) attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()!=hou.attribData.String


def isNumber(hou_attrib):
    """Convenience filter function for numeric (int/float of size 1) attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()!=hou.attribData.String and \
        hou_attrib.size()==1


def isInt(hou_attrib):
    """Convenience filter function for numeric (int/float of size 1) attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()==hou.attribData.Int and \
        hou_attrib.size()==1


def isString(hou_attrib):
    """Convenience filter function for string attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()==hou.attribData.String and \
        hou_attrib.size()==1


def isVector(hou_attrib):
    """Convenience filter function for numeric (int/float of size 3) attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()!=hou.attribData.String and \
        hou_attrib.size()==3


def isVector4(hou_attrib):
    """Convenience filter function for numeric (int/float of size 3) attributes.
    """
    assert type(hou_attrib) is hou.Attrib, "invalid argument"

    return \
        hou_attrib.dataType()!=hou.attribData.String and \
        hou_attrib.size()==3


