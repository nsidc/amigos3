import __builtin__ as _mod___builtin__
import exceptions as _mod_exceptions

xmlparser = _mod___builtin__.type
EXPAT_VERSION = 'expat_2.2.5'
def ErrorString(errno):
    'ErrorString(errno) -> string\nReturns string error for given number.'
    return ''

class ExpatError(_mod_exceptions.Exception):
    __class__ = ExpatError
    __dict__ = {}
    def __init__(self):
        'x.__init__(...) initializes x; see help(type(x)) for signature'
        pass
    
    __module__ = 'xml.parsers.expat'
    @classmethod
    def __subclasshook__(cls, subclass):
        'Abstract classes can override this to customize issubclass().\n\nThis is invoked early on by abc.ABCMeta.__subclasscheck__().\nIt should return True, False or NotImplemented.  If it returns\nNotImplemented, the normal algorithm is used.  Otherwise, it\noverrides the normal algorithm (and the outcome is cached).\n'
        return False
    
    @property
    def __weakref__(self):
        'list of weak references to the object (if defined)'
        pass
    

def ParserCreate(encoding=None, namespace_separator=None):
    'ParserCreate([encoding[, namespace_separator]]) -> parser\nReturn a new XML parser object.'
    pass

XMLParserType = xmlparser()
XML_PARAM_ENTITY_PARSING_ALWAYS = 2
XML_PARAM_ENTITY_PARSING_NEVER = 0
XML_PARAM_ENTITY_PARSING_UNLESS_STANDALONE = 1
__doc__ = 'Python wrapper for Expat parser.'
__file__ = '/usr/lib/python2.7/lib-dynload/pyexpat.x86_64-linux-gnu.so'
__name__ = 'pyexpat'
__package__ = None
__version__ = '2.7.15+'
error = ExpatError()
expat_CAPI = _mod___builtin__.PyCapsule()
features = _mod___builtin__.list()
native_encoding = 'UTF-8'
version_info = _mod___builtin__.tuple()
