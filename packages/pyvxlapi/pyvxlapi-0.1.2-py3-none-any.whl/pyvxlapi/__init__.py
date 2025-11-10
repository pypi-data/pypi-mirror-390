r"""Wrapper for vxlapi.h

Generated with:
C:\pyvxlapi\.venv\Scripts\ctypesgen -lvxlapi64 -o src/pyvxlapi/__init__.py assets/vxlapi.h

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
_libdirs = []

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries
_libs["vxlapi64"] = load_library("vxlapi64")

# 1 libraries
# End libraries

# No modules

enum_e_XLevent_type = c_int# vxlapi.h: 399

XL_NO_COMMAND = 0# vxlapi.h: 399

XL_RECEIVE_MSG = 1# vxlapi.h: 399

XL_CHIP_STATE = 4# vxlapi.h: 399

XL_TRANSCEIVER = 6# vxlapi.h: 399

XL_TIMER = 8# vxlapi.h: 399

XL_TRANSMIT_MSG = 10# vxlapi.h: 399

XL_SYNC_PULSE = 11# vxlapi.h: 399

XL_APPLICATION_NOTIFICATION = 15# vxlapi.h: 399

XL_LIN_MSG = 20# vxlapi.h: 399

XL_LIN_ERRMSG = 21# vxlapi.h: 399

XL_LIN_SYNCERR = 22# vxlapi.h: 399

XL_LIN_NOANS = 23# vxlapi.h: 399

XL_LIN_WAKEUP = 24# vxlapi.h: 399

XL_LIN_SLEEP = 25# vxlapi.h: 399

XL_LIN_CRCINFO = 26# vxlapi.h: 399

XL_RECEIVE_DAIO_DATA = 32# vxlapi.h: 399

XL_RECEIVE_DAIO_PIGGY = 34# vxlapi.h: 399

XL_KLINE_MSG = 36# vxlapi.h: 399

XLuint64 = c_ulonglong# vxlapi.h: 630

XLint64 = c_longlong# vxlapi.h: 631

XLlong = c_long# vxlapi.h: 636

XLulong = c_ulong# vxlapi.h: 637

# vxlapi.h: 650
class struct_s_xl_application_notification(Structure):
    pass

struct_s_xl_application_notification._pack_ = 8
struct_s_xl_application_notification.__slots__ = [
    'notifyReason',
    'reserved',
]
struct_s_xl_application_notification._fields_ = [
    ('notifyReason', c_uint),
    ('reserved', c_uint * int(7)),
]

XL_APPLICATION_NOTIFICATION_EV = struct_s_xl_application_notification# vxlapi.h: 650

# vxlapi.h: 664
class struct_s_xl_sync_pulse_ev(Structure):
    pass

struct_s_xl_sync_pulse_ev._pack_ = 8
struct_s_xl_sync_pulse_ev.__slots__ = [
    'triggerSource',
    'reserved',
    'time',
]
struct_s_xl_sync_pulse_ev._fields_ = [
    ('triggerSource', c_uint),
    ('reserved', c_uint),
    ('time', XLuint64),
]

XL_SYNC_PULSE_EV = struct_s_xl_sync_pulse_ev# vxlapi.h: 664

# vxlapi.h: 670
class struct_s_xl_sync_pulse(Structure):
    pass

struct_s_xl_sync_pulse._pack_ = 1
struct_s_xl_sync_pulse.__slots__ = [
    'pulseCode',
    'time',
]
struct_s_xl_sync_pulse._fields_ = [
    ('pulseCode', c_ubyte),
    ('time', XLuint64),
]

XLstringType = String# vxlapi.h: 758

XLaccess = XLuint64# vxlapi.h: 762

XLindex = XLuint64# vxlapi.h: 763

XLhandle = POINTER(None)# vxlapi.h: 771

# vxlapi.h: 827
class struct_anon_1(Structure):
    pass

struct_anon_1._pack_ = 1
struct_anon_1.__slots__ = [
    'LINMode',
    'baudrate',
    'LINVersion',
    'reserved',
]
struct_anon_1._fields_ = [
    ('LINMode', c_uint),
    ('baudrate', c_int),
    ('LINVersion', c_uint),
    ('reserved', c_uint),
]

XLlinStatPar = struct_anon_1# vxlapi.h: 827

# vxlapi.h: 866
class struct_s_xl_can_msg(Structure):
    pass

struct_s_xl_can_msg._pack_ = 1
struct_s_xl_can_msg.__slots__ = [
    'id',
    'flags',
    'dlc',
    'res1',
    'data',
    'res2',
]
struct_s_xl_can_msg._fields_ = [
    ('id', c_uint),
    ('flags', c_ushort),
    ('dlc', c_ushort),
    ('res1', XLuint64),
    ('data', c_ubyte * int(8)),
    ('res2', XLuint64),
]

# vxlapi.h: 888
class struct_s_xl_daio_data(Structure):
    pass

struct_s_xl_daio_data._pack_ = 1
struct_s_xl_daio_data.__slots__ = [
    'flags',
    'timestamp_correction',
    'mask_digital',
    'value_digital',
    'mask_analog',
    'reserved0',
    'value_analog',
    'pwm_frequency',
    'pwm_value',
    'reserved1',
    'reserved2',
]
struct_s_xl_daio_data._fields_ = [
    ('flags', c_ushort),
    ('timestamp_correction', c_uint),
    ('mask_digital', c_ubyte),
    ('value_digital', c_ubyte),
    ('mask_analog', c_ubyte),
    ('reserved0', c_ubyte),
    ('value_analog', c_ushort * int(4)),
    ('pwm_frequency', c_uint),
    ('pwm_value', c_ushort),
    ('reserved1', c_uint),
    ('reserved2', c_uint),
]

# vxlapi.h: 905
class struct_s_xl_io_digital_data(Structure):
    pass

struct_s_xl_io_digital_data._pack_ = 1
struct_s_xl_io_digital_data.__slots__ = [
    'digitalInputData',
]
struct_s_xl_io_digital_data._fields_ = [
    ('digitalInputData', c_uint),
]

XL_IO_DIGITAL_DATA = struct_s_xl_io_digital_data# vxlapi.h: 905

# vxlapi.h: 912
class struct_s_xl_io_analog_data(Structure):
    pass

struct_s_xl_io_analog_data._pack_ = 1
struct_s_xl_io_analog_data.__slots__ = [
    'measuredAnalogData0',
    'measuredAnalogData1',
    'measuredAnalogData2',
    'measuredAnalogData3',
]
struct_s_xl_io_analog_data._fields_ = [
    ('measuredAnalogData0', c_uint),
    ('measuredAnalogData1', c_uint),
    ('measuredAnalogData2', c_uint),
    ('measuredAnalogData3', c_uint),
]

XL_IO_ANALOG_DATA = struct_s_xl_io_analog_data# vxlapi.h: 912

# vxlapi.h: 919
class union_anon_2(Union):
    pass

union_anon_2._pack_ = 1
union_anon_2.__slots__ = [
    'digital',
    'analog',
]
union_anon_2._fields_ = [
    ('digital', XL_IO_DIGITAL_DATA),
    ('analog', XL_IO_ANALOG_DATA),
]

# vxlapi.h: 915
class struct_s_xl_daio_piggy_data(Structure):
    pass

struct_s_xl_daio_piggy_data._pack_ = 1
struct_s_xl_daio_piggy_data.__slots__ = [
    'daioEvtTag',
    'triggerType',
    'data',
]
struct_s_xl_daio_piggy_data._fields_ = [
    ('daioEvtTag', c_uint),
    ('triggerType', c_uint),
    ('data', union_anon_2),
]

# vxlapi.h: 934
class struct_s_xl_chip_state(Structure):
    pass

struct_s_xl_chip_state._pack_ = 1
struct_s_xl_chip_state.__slots__ = [
    'busStatus',
    'txErrorCounter',
    'rxErrorCounter',
]
struct_s_xl_chip_state._fields_ = [
    ('busStatus', c_ubyte),
    ('txErrorCounter', c_ubyte),
    ('rxErrorCounter', c_ubyte),
]

# vxlapi.h: 947
class struct_s_xl_transceiver(Structure):
    pass

struct_s_xl_transceiver._pack_ = 1
struct_s_xl_transceiver.__slots__ = [
    'event_reason',
    'is_present',
]
struct_s_xl_transceiver._fields_ = [
    ('event_reason', c_ubyte),
    ('is_present', c_ubyte),
]

# vxlapi.h: 968
class struct_s_xl_lin_msg(Structure):
    pass

struct_s_xl_lin_msg._pack_ = 1
struct_s_xl_lin_msg.__slots__ = [
    'id',
    'dlc',
    'flags',
    'data',
    'crc',
]
struct_s_xl_lin_msg._fields_ = [
    ('id', c_ubyte),
    ('dlc', c_ubyte),
    ('flags', c_ushort),
    ('data', c_ubyte * int(8)),
    ('crc', c_ubyte),
]

# vxlapi.h: 976
class struct_s_xl_lin_sleep(Structure):
    pass

struct_s_xl_lin_sleep._pack_ = 1
struct_s_xl_lin_sleep.__slots__ = [
    'flag',
]
struct_s_xl_lin_sleep._fields_ = [
    ('flag', c_ubyte),
]

# vxlapi.h: 980
class struct_s_xl_lin_no_ans(Structure):
    pass

struct_s_xl_lin_no_ans._pack_ = 1
struct_s_xl_lin_no_ans.__slots__ = [
    'id',
]
struct_s_xl_lin_no_ans._fields_ = [
    ('id', c_ubyte),
]

# vxlapi.h: 984
class struct_s_xl_lin_wake_up(Structure):
    pass

struct_s_xl_lin_wake_up._pack_ = 1
struct_s_xl_lin_wake_up.__slots__ = [
    'flag',
    'unused',
    'startOffs',
    'width',
]
struct_s_xl_lin_wake_up._fields_ = [
    ('flag', c_ubyte),
    ('unused', c_ubyte * int(3)),
    ('startOffs', c_uint),
    ('width', c_uint),
]

# vxlapi.h: 991
class struct_s_xl_lin_crc_info(Structure):
    pass

struct_s_xl_lin_crc_info._pack_ = 1
struct_s_xl_lin_crc_info.__slots__ = [
    'id',
    'flags',
]
struct_s_xl_lin_crc_info._fields_ = [
    ('id', c_ubyte),
    ('flags', c_ubyte),
]

# vxlapi.h: 998
class union_s_xl_lin_msg_api(Union):
    pass

union_s_xl_lin_msg_api._pack_ = 1
union_s_xl_lin_msg_api.__slots__ = [
    'linMsg',
    'linNoAns',
    'linWakeUp',
    'linSleep',
    'linCRCinfo',
]
union_s_xl_lin_msg_api._fields_ = [
    ('linMsg', struct_s_xl_lin_msg),
    ('linNoAns', struct_s_xl_lin_no_ans),
    ('linWakeUp', struct_s_xl_lin_wake_up),
    ('linSleep', struct_s_xl_lin_sleep),
    ('linCRCinfo', struct_s_xl_lin_crc_info),
]

# vxlapi.h: 1012
class struct_s_xl_kline_rx_data(Structure):
    pass

struct_s_xl_kline_rx_data._pack_ = 1
struct_s_xl_kline_rx_data.__slots__ = [
    'timeDiff',
    'data',
    'error',
]
struct_s_xl_kline_rx_data._fields_ = [
    ('timeDiff', c_uint),
    ('data', c_uint),
    ('error', c_uint),
]

XL_KLINE_RX_DATA = struct_s_xl_kline_rx_data# vxlapi.h: 1012

# vxlapi.h: 1018
class struct_s_xl_kline_tx_data(Structure):
    pass

struct_s_xl_kline_tx_data._pack_ = 1
struct_s_xl_kline_tx_data.__slots__ = [
    'timeDiff',
    'data',
    'error',
]
struct_s_xl_kline_tx_data._fields_ = [
    ('timeDiff', c_uint),
    ('data', c_uint),
    ('error', c_uint),
]

XL_KLINE_TX_DATA = struct_s_xl_kline_tx_data# vxlapi.h: 1018

# vxlapi.h: 1024
class struct_s_xl_kline_tester_5bd(Structure):
    pass

struct_s_xl_kline_tester_5bd._pack_ = 1
struct_s_xl_kline_tester_5bd.__slots__ = [
    'tag5bd',
    'timeDiff',
    'data',
]
struct_s_xl_kline_tester_5bd._fields_ = [
    ('tag5bd', c_uint),
    ('timeDiff', c_uint),
    ('data', c_uint),
]

XL_KLINE_TESTER_5BD = struct_s_xl_kline_tester_5bd# vxlapi.h: 1024

# vxlapi.h: 1030
class struct_s_xl_kline_ecu_5bd(Structure):
    pass

struct_s_xl_kline_ecu_5bd._pack_ = 1
struct_s_xl_kline_ecu_5bd.__slots__ = [
    'tag5bd',
    'timeDiff',
    'data',
]
struct_s_xl_kline_ecu_5bd._fields_ = [
    ('tag5bd', c_uint),
    ('timeDiff', c_uint),
    ('data', c_uint),
]

XL_KLINE_ECU_5BD = struct_s_xl_kline_ecu_5bd# vxlapi.h: 1030

# vxlapi.h: 1035
class struct_s_xl_kline_tester_fastinit_wu_pattern(Structure):
    pass

struct_s_xl_kline_tester_fastinit_wu_pattern._pack_ = 1
struct_s_xl_kline_tester_fastinit_wu_pattern.__slots__ = [
    'timeDiff',
    'fastInitEdgeTimeDiff',
]
struct_s_xl_kline_tester_fastinit_wu_pattern._fields_ = [
    ('timeDiff', c_uint),
    ('fastInitEdgeTimeDiff', c_uint),
]

XL_KLINE_TESTER_FI_WU_PATTERN = struct_s_xl_kline_tester_fastinit_wu_pattern# vxlapi.h: 1035

# vxlapi.h: 1040
class struct_s_xl_kline_ecu_fastinit_wu_pattern(Structure):
    pass

struct_s_xl_kline_ecu_fastinit_wu_pattern._pack_ = 1
struct_s_xl_kline_ecu_fastinit_wu_pattern.__slots__ = [
    'timeDiff',
    'fastInitEdgeTimeDiff',
]
struct_s_xl_kline_ecu_fastinit_wu_pattern._fields_ = [
    ('timeDiff', c_uint),
    ('fastInitEdgeTimeDiff', c_uint),
]

XL_KLINE_ECU_FI_WU_PATTERN = struct_s_xl_kline_ecu_fastinit_wu_pattern# vxlapi.h: 1040

# vxlapi.h: 1046
class struct_s_xl_kline_confirmation(Structure):
    pass

struct_s_xl_kline_confirmation._pack_ = 1
struct_s_xl_kline_confirmation.__slots__ = [
    'channel',
    'confTag',
    'result',
]
struct_s_xl_kline_confirmation._fields_ = [
    ('channel', c_uint),
    ('confTag', c_uint),
    ('result', c_uint),
]

XL_KLINE_CONFIRMATION = struct_s_xl_kline_confirmation# vxlapi.h: 1046

# vxlapi.h: 1050
class struct_s_xl_kline_error_rxtx(Structure):
    pass

struct_s_xl_kline_error_rxtx._pack_ = 1
struct_s_xl_kline_error_rxtx.__slots__ = [
    'rxtxErrData',
]
struct_s_xl_kline_error_rxtx._fields_ = [
    ('rxtxErrData', c_uint),
]

XL_KLINE_ERROR_RXTX = struct_s_xl_kline_error_rxtx# vxlapi.h: 1050

# vxlapi.h: 1054
class struct_s_xl_kline_error_5bd_tester(Structure):
    pass

struct_s_xl_kline_error_5bd_tester._pack_ = 1
struct_s_xl_kline_error_5bd_tester.__slots__ = [
    'tester5BdErr',
]
struct_s_xl_kline_error_5bd_tester._fields_ = [
    ('tester5BdErr', c_uint),
]

XL_KLINE_ERROR_TESTER_5BD = struct_s_xl_kline_error_5bd_tester# vxlapi.h: 1054

# vxlapi.h: 1058
class struct_s_xl_kline_error_5bd_ecu(Structure):
    pass

struct_s_xl_kline_error_5bd_ecu._pack_ = 1
struct_s_xl_kline_error_5bd_ecu.__slots__ = [
    'ecu5BdErr',
]
struct_s_xl_kline_error_5bd_ecu._fields_ = [
    ('ecu5BdErr', c_uint),
]

XL_KLINE_ERROR_ECU_5BD = struct_s_xl_kline_error_5bd_ecu# vxlapi.h: 1058

# vxlapi.h: 1063
class struct_s_xl_kline_error_ibs(Structure):
    pass

struct_s_xl_kline_error_ibs._pack_ = 1
struct_s_xl_kline_error_ibs.__slots__ = [
    'ibsErr',
    'rxtxErrData',
]
struct_s_xl_kline_error_ibs._fields_ = [
    ('ibsErr', c_uint),
    ('rxtxErrData', c_uint),
]

XL_KLINE_ERROR_IBS = struct_s_xl_kline_error_ibs# vxlapi.h: 1063

# vxlapi.h: 1069
class union_anon_3(Union):
    pass

union_anon_3._pack_ = 1
union_anon_3.__slots__ = [
    'rxtxErr',
    'tester5BdErr',
    'ecu5BdErr',
    'ibsErr',
    'reserved',
]
union_anon_3._fields_ = [
    ('rxtxErr', XL_KLINE_ERROR_RXTX),
    ('tester5BdErr', XL_KLINE_ERROR_TESTER_5BD),
    ('ecu5BdErr', XL_KLINE_ERROR_ECU_5BD),
    ('ibsErr', XL_KLINE_ERROR_IBS),
    ('reserved', c_uint * int(4)),
]

# vxlapi.h: 1078
class struct_s_xl_kline_error(Structure):
    pass

struct_s_xl_kline_error._pack_ = 1
struct_s_xl_kline_error.__slots__ = [
    'klineErrorTag',
    'reserved',
    'data',
]
struct_s_xl_kline_error._fields_ = [
    ('klineErrorTag', c_uint),
    ('reserved', c_uint),
    ('data', union_anon_3),
]

XL_KLINE_ERROR = struct_s_xl_kline_error# vxlapi.h: 1078

# vxlapi.h: 1087
class union_anon_4(Union):
    pass

union_anon_4._pack_ = 1
union_anon_4.__slots__ = [
    'klineRx',
    'klineTx',
    'klineTester5Bd',
    'klineEcu5Bd',
    'klineTesterFiWu',
    'klineEcuFiWu',
    'klineConfirmation',
    'klineError',
]
union_anon_4._fields_ = [
    ('klineRx', XL_KLINE_RX_DATA),
    ('klineTx', XL_KLINE_TX_DATA),
    ('klineTester5Bd', XL_KLINE_TESTER_5BD),
    ('klineEcu5Bd', XL_KLINE_ECU_5BD),
    ('klineTesterFiWu', XL_KLINE_TESTER_FI_WU_PATTERN),
    ('klineEcuFiWu', XL_KLINE_ECU_FI_WU_PATTERN),
    ('klineConfirmation', XL_KLINE_CONFIRMATION),
    ('klineError', XL_KLINE_ERROR),
]

# vxlapi.h: 1101
class struct_s_xl_kline_data(Structure):
    pass

struct_s_xl_kline_data._pack_ = 1
struct_s_xl_kline_data.__slots__ = [
    'klineEvtTag',
    'reserved',
    'data',
]
struct_s_xl_kline_data._fields_ = [
    ('klineEvtTag', c_uint),
    ('reserved', c_uint),
    ('data', union_anon_4),
]

XL_KLINE_DATA = struct_s_xl_kline_data# vxlapi.h: 1101

# vxlapi.h: 1106
class union_s_xl_tag_data(Union):
    pass

union_s_xl_tag_data._pack_ = 1
union_s_xl_tag_data.__slots__ = [
    'msg',
    'chipState',
    'linMsgApi',
    'syncPulse',
    'daioData',
    'transceiver',
    'daioPiggyData',
    'klineData',
]
union_s_xl_tag_data._fields_ = [
    ('msg', struct_s_xl_can_msg),
    ('chipState', struct_s_xl_chip_state),
    ('linMsgApi', union_s_xl_lin_msg_api),
    ('syncPulse', struct_s_xl_sync_pulse),
    ('daioData', struct_s_xl_daio_data),
    ('transceiver', struct_s_xl_transceiver),
    ('daioPiggyData', struct_s_xl_daio_piggy_data),
    ('klineData', struct_s_xl_kline_data),
]

XLeventTag = c_ubyte# vxlapi.h: 1117

# vxlapi.h: 1123
class struct_s_xl_event(Structure):
    pass

struct_s_xl_event._pack_ = 1
struct_s_xl_event.__slots__ = [
    'tag',
    'chanIndex',
    'transId',
    'portHandle',
    'flags',
    'reserved',
    'timeStamp',
    'tagData',
]
struct_s_xl_event._fields_ = [
    ('tag', XLeventTag),
    ('chanIndex', c_ubyte),
    ('transId', c_ushort),
    ('portHandle', c_ushort),
    ('flags', c_ubyte),
    ('reserved', c_ubyte),
    ('timeStamp', XLuint64),
    ('tagData', union_s_xl_tag_data),
]

XLevent = struct_s_xl_event# vxlapi.h: 1136

XLstatus = c_short# vxlapi.h: 1148

# vxlapi.h: 1226
class struct_anon_5(Structure):
    pass

struct_anon_5._pack_ = 1
struct_anon_5.__slots__ = [
    'arbitrationBitRate',
    'sjwAbr',
    'tseg1Abr',
    'tseg2Abr',
    'dataBitRate',
    'sjwDbr',
    'tseg1Dbr',
    'tseg2Dbr',
    'reserved',
    'options',
    'reserved1',
    'reserved2',
]
struct_anon_5._fields_ = [
    ('arbitrationBitRate', c_uint),
    ('sjwAbr', c_uint),
    ('tseg1Abr', c_uint),
    ('tseg2Abr', c_uint),
    ('dataBitRate', c_uint),
    ('sjwDbr', c_uint),
    ('tseg1Dbr', c_uint),
    ('tseg2Dbr', c_uint),
    ('reserved', c_ubyte),
    ('options', c_ubyte),
    ('reserved1', c_ubyte * int(2)),
    ('reserved2', c_uint),
]

XLcanFdConf = struct_anon_5# vxlapi.h: 1226

# vxlapi.h: 1235
class struct_anon_6(Structure):
    pass

struct_anon_6._pack_ = 1
struct_anon_6.__slots__ = [
    'bitRate',
    'sjw',
    'tseg1',
    'tseg2',
    'sam',
]
struct_anon_6._fields_ = [
    ('bitRate', c_uint),
    ('sjw', c_ubyte),
    ('tseg1', c_ubyte),
    ('tseg2', c_ubyte),
    ('sam', c_ubyte),
]

XLchipParams = struct_anon_6# vxlapi.h: 1235

# vxlapi.h: 1250
class struct_anon_7(Structure):
    pass

struct_anon_7._pack_ = 1
struct_anon_7.__slots__ = [
    'bitRate',
    'sjw',
    'tseg1',
    'tseg2',
    'sam',
    'outputMode',
    'reserved1',
    'canOpMode',
]
struct_anon_7._fields_ = [
    ('bitRate', c_uint),
    ('sjw', c_ubyte),
    ('tseg1', c_ubyte),
    ('tseg2', c_ubyte),
    ('sam', c_ubyte),
    ('outputMode', c_ubyte),
    ('reserved1', c_ubyte * int(7)),
    ('canOpMode', c_ubyte),
]

# vxlapi.h: 1261
class struct_anon_8(Structure):
    pass

struct_anon_8._pack_ = 1
struct_anon_8.__slots__ = [
    'arbitrationBitRate',
    'sjwAbr',
    'tseg1Abr',
    'tseg2Abr',
    'samAbr',
    'outputMode',
    'sjwDbr',
    'tseg1Dbr',
    'tseg2Dbr',
    'dataBitRate',
    'canOpMode',
]
struct_anon_8._fields_ = [
    ('arbitrationBitRate', c_uint),
    ('sjwAbr', c_ubyte),
    ('tseg1Abr', c_ubyte),
    ('tseg2Abr', c_ubyte),
    ('samAbr', c_ubyte),
    ('outputMode', c_ubyte),
    ('sjwDbr', c_ubyte),
    ('tseg1Dbr', c_ubyte),
    ('tseg2Dbr', c_ubyte),
    ('dataBitRate', c_uint),
    ('canOpMode', c_ubyte),
]

# vxlapi.h: 1276
class struct_anon_9(Structure):
    pass

struct_anon_9._pack_ = 1
struct_anon_9.__slots__ = [
    'activeSpeedGrade',
    'compatibleSpeedGrade',
    'inicFwVersion',
]
struct_anon_9._fields_ = [
    ('activeSpeedGrade', c_uint),
    ('compatibleSpeedGrade', c_uint),
    ('inicFwVersion', c_uint),
]

# vxlapi.h: 1282
class struct_anon_10(Structure):
    pass

struct_anon_10._pack_ = 1
struct_anon_10.__slots__ = [
    'status',
    'cfgMode',
    'baudrate',
]
struct_anon_10._fields_ = [
    ('status', c_uint),
    ('cfgMode', c_uint),
    ('baudrate', c_uint),
]

# vxlapi.h: 1289
class struct_anon_11(Structure):
    pass

struct_anon_11._pack_ = 1
struct_anon_11.__slots__ = [
    'macAddr',
    'connector',
    'phy',
    'link',
    'speed',
    'clockMode',
    'bypass',
]
struct_anon_11._fields_ = [
    ('macAddr', c_ubyte * int(6)),
    ('connector', c_ubyte),
    ('phy', c_ubyte),
    ('link', c_ubyte),
    ('speed', c_ubyte),
    ('clockMode', c_ubyte),
    ('bypass', c_ubyte),
]

# vxlapi.h: 1304
class struct_anon_12(Structure):
    pass

struct_anon_12._pack_ = 1
struct_anon_12.__slots__ = [
    'bitrate',
    'parity',
    'minGap',
]
struct_anon_12._fields_ = [
    ('bitrate', c_uint),
    ('parity', c_uint),
    ('minGap', c_uint),
]

# vxlapi.h: 1310
class struct_anon_13(Structure):
    pass

struct_anon_13._pack_ = 1
struct_anon_13.__slots__ = [
    'bitrate',
    'minBitrate',
    'maxBitrate',
    'parity',
    'minGap',
    'autoBaudrate',
]
struct_anon_13._fields_ = [
    ('bitrate', c_uint),
    ('minBitrate', c_uint),
    ('maxBitrate', c_uint),
    ('parity', c_uint),
    ('minGap', c_uint),
    ('autoBaudrate', c_uint),
]

# vxlapi.h: 1303
class union_anon_14(Union):
    pass

union_anon_14._pack_ = 1
union_anon_14.__slots__ = [
    'tx',
    'rx',
    'raw',
]
union_anon_14._fields_ = [
    ('tx', struct_anon_12),
    ('rx', struct_anon_13),
    ('raw', c_ubyte * int(24)),
]

# vxlapi.h: 1299
class struct_anon_15(Structure):
    pass

struct_anon_15._pack_ = 1
struct_anon_15.__slots__ = [
    'channelDirection',
    'res1',
    'dir',
]
struct_anon_15._fields_ = [
    ('channelDirection', c_ushort),
    ('res1', c_ushort),
    ('dir', union_anon_14),
]

# vxlapi.h: 1249
class union_anon_16(Union):
    pass

union_anon_16._pack_ = 1
union_anon_16.__slots__ = [
    'can',
    'canFD',
    'most',
    'flexray',
    'ethernet',
    'a429',
    'raw',
]
union_anon_16._fields_ = [
    ('can', struct_anon_7),
    ('canFD', struct_anon_8),
    ('most', struct_anon_9),
    ('flexray', struct_anon_10),
    ('ethernet', struct_anon_11),
    ('a429', struct_anon_15),
    ('raw', c_ubyte * int(28)),
]

# vxlapi.h: 1325
class struct_anon_17(Structure):
    pass

struct_anon_17._pack_ = 1
struct_anon_17.__slots__ = [
    'busType',
    'data',
]
struct_anon_17._fields_ = [
    ('busType', c_uint),
    ('data', union_anon_16),
]

XLbusParams = struct_anon_17# vxlapi.h: 1325

XLportHandle = XLlong# vxlapi.h: 1330

pXLportHandle = POINTER(XLlong)# vxlapi.h: 1330

# vxlapi.h: 1361
class struct_s_xl_license_info(Structure):
    pass

struct_s_xl_license_info._pack_ = 1
struct_s_xl_license_info.__slots__ = [
    'bAvailable',
    'licName',
]
struct_s_xl_license_info._fields_ = [
    ('bAvailable', c_ubyte),
    ('licName', c_char * int(65)),
]

XL_LICENSE_INFO = struct_s_xl_license_info# vxlapi.h: 1361

XLlicenseInfo = XL_LICENSE_INFO# vxlapi.h: 1363

# vxlapi.h: 1410
class struct_s_xl_channel_config(Structure):
    pass

struct_s_xl_channel_config._pack_ = 1
struct_s_xl_channel_config.__slots__ = [
    'name',
    'hwType',
    'hwIndex',
    'hwChannel',
    'transceiverType',
    'transceiverState',
    'configError',
    'channelIndex',
    'channelMask',
    'channelCapabilities',
    'channelBusCapabilities',
    'isOnBus',
    'connectedBusType',
    'busParams',
    '_doNotUse',
    'driverVersion',
    'interfaceVersion',
    'raw_data',
    'serialNumber',
    'articleNumber',
    'transceiverName',
    'specialCabFlags',
    'dominantTimeout',
    'dominantRecessiveDelay',
    'recessiveDominantDelay',
    'connectionInfo',
    'currentlyAvailableTimestamps',
    'minimalSupplyVoltage',
    'maximalSupplyVoltage',
    'maximalBaudrate',
    'fpgaCoreCapabilities',
    'specialDeviceStatus',
    'channelBusActiveCapabilities',
    'breakOffset',
    'delimiterOffset',
    'reserved',
]
struct_s_xl_channel_config._fields_ = [
    ('name', c_char * int((31 + 1))),
    ('hwType', c_ubyte),
    ('hwIndex', c_ubyte),
    ('hwChannel', c_ubyte),
    ('transceiverType', c_ushort),
    ('transceiverState', c_ushort),
    ('configError', c_ushort),
    ('channelIndex', c_ubyte),
    ('channelMask', XLuint64),
    ('channelCapabilities', c_uint),
    ('channelBusCapabilities', c_uint),
    ('isOnBus', c_ubyte),
    ('connectedBusType', c_uint),
    ('busParams', XLbusParams),
    ('_doNotUse', c_uint),
    ('driverVersion', c_uint),
    ('interfaceVersion', c_uint),
    ('raw_data', c_uint * int(10)),
    ('serialNumber', c_uint),
    ('articleNumber', c_uint),
    ('transceiverName', c_char * int((31 + 1))),
    ('specialCabFlags', c_uint),
    ('dominantTimeout', c_uint),
    ('dominantRecessiveDelay', c_ubyte),
    ('recessiveDominantDelay', c_ubyte),
    ('connectionInfo', c_ubyte),
    ('currentlyAvailableTimestamps', c_ubyte),
    ('minimalSupplyVoltage', c_ushort),
    ('maximalSupplyVoltage', c_ushort),
    ('maximalBaudrate', c_uint),
    ('fpgaCoreCapabilities', c_ubyte),
    ('specialDeviceStatus', c_ubyte),
    ('channelBusActiveCapabilities', c_ushort),
    ('breakOffset', c_ushort),
    ('delimiterOffset', c_ushort),
    ('reserved', c_uint * int(3)),
]

XL_CHANNEL_CONFIG = struct_s_xl_channel_config# vxlapi.h: 1410

XLchannelConfig = XL_CHANNEL_CONFIG# vxlapi.h: 1412

pXLchannelConfig = POINTER(XL_CHANNEL_CONFIG)# vxlapi.h: 1413

# vxlapi.h: 1420
class struct_s_xl_driver_config(Structure):
    pass

struct_s_xl_driver_config._pack_ = 1
struct_s_xl_driver_config.__slots__ = [
    'dllVersion',
    'channelCount',
    'reserved',
    'channel',
]
struct_s_xl_driver_config._fields_ = [
    ('dllVersion', c_uint),
    ('channelCount', c_uint),
    ('reserved', c_uint * int(10)),
    ('channel', XLchannelConfig * int(64)),
]

XL_DRIVER_CONFIG = struct_s_xl_driver_config# vxlapi.h: 1420

XLdriverConfig = XL_DRIVER_CONFIG# vxlapi.h: 1422

pXLdriverConfig = POINTER(XL_DRIVER_CONFIG)# vxlapi.h: 1423

# vxlapi.h: 1453
class struct__XLacc_filt(Structure):
    pass

struct__XLacc_filt._pack_ = 1
struct__XLacc_filt.__slots__ = [
    'isSet',
    'code',
    'mask',
]
struct__XLacc_filt._fields_ = [
    ('isSet', c_ubyte),
    ('code', c_uint),
    ('mask', c_uint),
]

XLaccFilt = struct__XLacc_filt# vxlapi.h: 1458

# vxlapi.h: 1461
class struct__XLacceptance(Structure):
    pass

struct__XLacceptance._pack_ = 1
struct__XLacceptance.__slots__ = [
    'std',
    'xtd',
]
struct__XLacceptance._fields_ = [
    ('std', XLaccFilt),
    ('xtd', XLaccFilt),
]

XLacceptance = struct__XLacceptance# vxlapi.h: 1465

XLremoteHandle = c_uint# vxlapi.h: 1533

XLdeviceAccess = c_uint# vxlapi.h: 1534

XLremoteStatus = c_uint# vxlapi.h: 1535

# vxlapi.h: 1543
class union_anon_18(Union):
    pass

union_anon_18._pack_ = 8
union_anon_18.__slots__ = [
    'v4',
    'v6',
]
union_anon_18._fields_ = [
    ('v4', c_uint),
    ('v6', c_uint * int(4)),
]

# vxlapi.h: 1552
class struct_s_xl_ip_address(Structure):
    pass

struct_s_xl_ip_address._pack_ = 8
struct_s_xl_ip_address.__slots__ = [
    'ip',
    'prefixLength',
    'ipVersion',
    'configPort',
    'eventPort',
]
struct_s_xl_ip_address._fields_ = [
    ('ip', union_anon_18),
    ('prefixLength', c_uint),
    ('ipVersion', c_uint),
    ('configPort', c_uint),
    ('eventPort', c_uint),
]

XLipAddress = struct_s_xl_ip_address# vxlapi.h: 1552

# vxlapi.h: 1563
class struct_s_xl_remote_location_config(Structure):
    pass

struct_s_xl_remote_location_config._pack_ = 8
struct_s_xl_remote_location_config.__slots__ = [
    'hostName',
    'alias',
    'ipAddress',
    'userIpAddress',
    'deviceType',
    'serialNumber',
    'articleNumber',
    'remoteHandle',
]
struct_s_xl_remote_location_config._fields_ = [
    ('hostName', c_char * int(64)),
    ('alias', c_char * int(64)),
    ('ipAddress', XLipAddress),
    ('userIpAddress', XLipAddress),
    ('deviceType', c_uint),
    ('serialNumber', c_uint),
    ('articleNumber', c_uint),
    ('remoteHandle', XLremoteHandle),
]

XLremoteLocationConfig = struct_s_xl_remote_location_config# vxlapi.h: 1563

# vxlapi.h: 1571
class struct_s_xl_remote_device(Structure):
    pass

struct_s_xl_remote_device._pack_ = 8
struct_s_xl_remote_device.__slots__ = [
    'deviceName',
    'hwType',
    'articleNumber',
    'serialNumber',
    'reserved',
]
struct_s_xl_remote_device._fields_ = [
    ('deviceName', c_char * int(32)),
    ('hwType', c_uint),
    ('articleNumber', c_uint),
    ('serialNumber', c_uint),
    ('reserved', c_uint),
]

XLremoteDevice = struct_s_xl_remote_device# vxlapi.h: 1571

# vxlapi.h: 1579
class struct_s_xl_remote_device_info(Structure):
    pass

struct_s_xl_remote_device_info._pack_ = 8
struct_s_xl_remote_device_info.__slots__ = [
    'locationConfig',
    'flags',
    'reserved',
    'nbrOfDevices',
    'deviceInfo',
]
struct_s_xl_remote_device_info._fields_ = [
    ('locationConfig', XLremoteLocationConfig),
    ('flags', c_uint),
    ('reserved', c_uint),
    ('nbrOfDevices', c_uint),
    ('deviceInfo', XLremoteDevice * int(16)),
]

XLremoteDeviceInfo = struct_s_xl_remote_device_info# vxlapi.h: 1579

# vxlapi.h: 1883
class struct_s_xl_most_ctrl_spy(Structure):
    pass

struct_s_xl_most_ctrl_spy._pack_ = 8
struct_s_xl_most_ctrl_spy.__slots__ = [
    'arbitration',
    'targetAddress',
    'sourceAddress',
    'ctrlType',
    'ctrlData',
    'crc',
    'txStatus',
    'ctrlRes',
    'spyRxStatus',
]
struct_s_xl_most_ctrl_spy._fields_ = [
    ('arbitration', c_uint),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('ctrlType', c_ubyte),
    ('ctrlData', c_ubyte * int(17)),
    ('crc', c_ushort),
    ('txStatus', c_ushort),
    ('ctrlRes', c_ushort),
    ('spyRxStatus', c_uint),
]

XL_MOST_CTRL_SPY_EV = struct_s_xl_most_ctrl_spy# vxlapi.h: 1883

# vxlapi.h: 1893
class struct_s_xl_most_ctrl_msg(Structure):
    pass

struct_s_xl_most_ctrl_msg._pack_ = 8
struct_s_xl_most_ctrl_msg.__slots__ = [
    'ctrlPrio',
    'ctrlType',
    'targetAddress',
    'sourceAddress',
    'ctrlData',
    'direction',
    'status',
]
struct_s_xl_most_ctrl_msg._fields_ = [
    ('ctrlPrio', c_ubyte),
    ('ctrlType', c_ubyte),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('ctrlData', c_ubyte * int(17)),
    ('direction', c_ubyte),
    ('status', c_uint),
]

XL_MOST_CTRL_MSG_EV = struct_s_xl_most_ctrl_msg# vxlapi.h: 1893

# vxlapi.h: 1903
class struct_s_xl_most_async_msg(Structure):
    pass

struct_s_xl_most_async_msg._pack_ = 8
struct_s_xl_most_async_msg.__slots__ = [
    'status',
    'crc',
    'arbitration',
    'length',
    'targetAddress',
    'sourceAddress',
    'asyncData',
]
struct_s_xl_most_async_msg._fields_ = [
    ('status', c_uint),
    ('crc', c_uint),
    ('arbitration', c_ubyte),
    ('length', c_ubyte),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('asyncData', c_ubyte * int(1018)),
]

XL_MOST_ASYNC_MSG_EV = struct_s_xl_most_async_msg# vxlapi.h: 1903

# vxlapi.h: 1911
class struct_s_xl_most_async_tx(Structure):
    pass

struct_s_xl_most_async_tx._pack_ = 8
struct_s_xl_most_async_tx.__slots__ = [
    'arbitration',
    'length',
    'targetAddress',
    'sourceAddress',
    'asyncData',
]
struct_s_xl_most_async_tx._fields_ = [
    ('arbitration', c_ubyte),
    ('length', c_ubyte),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('asyncData', c_ubyte * int(1014)),
]

XL_MOST_ASYNC_TX_EV = struct_s_xl_most_async_tx# vxlapi.h: 1911

# vxlapi.h: 1928
class struct_s_xl_most_special_register(Structure):
    pass

struct_s_xl_most_special_register._pack_ = 8
struct_s_xl_most_special_register.__slots__ = [
    'changeMask',
    'lockStatus',
    'register_bNAH',
    'register_bNAL',
    'register_bGA',
    'register_bAPAH',
    'register_bAPAL',
    'register_bNPR',
    'register_bMPR',
    'register_bNDR',
    'register_bMDR',
    'register_bSBC',
    'register_bXTIM',
    'register_bXRTY',
]
struct_s_xl_most_special_register._fields_ = [
    ('changeMask', c_uint),
    ('lockStatus', c_uint),
    ('register_bNAH', c_ubyte),
    ('register_bNAL', c_ubyte),
    ('register_bGA', c_ubyte),
    ('register_bAPAH', c_ubyte),
    ('register_bAPAL', c_ubyte),
    ('register_bNPR', c_ubyte),
    ('register_bMPR', c_ubyte),
    ('register_bNDR', c_ubyte),
    ('register_bMDR', c_ubyte),
    ('register_bSBC', c_ubyte),
    ('register_bXTIM', c_ubyte),
    ('register_bXRTY', c_ubyte),
]

XL_MOST_SPECIAL_REGISTER_EV = struct_s_xl_most_special_register# vxlapi.h: 1928

# vxlapi.h: 1933
class struct_s_xl_most_event_source(Structure):
    pass

struct_s_xl_most_event_source._pack_ = 8
struct_s_xl_most_event_source.__slots__ = [
    'mask',
    'state',
]
struct_s_xl_most_event_source._fields_ = [
    ('mask', c_uint),
    ('state', c_uint),
]

XL_MOST_EVENT_SOURCE_EV = struct_s_xl_most_event_source# vxlapi.h: 1933

# vxlapi.h: 1937
class struct_s_xl_most_all_bypass(Structure):
    pass

struct_s_xl_most_all_bypass._pack_ = 8
struct_s_xl_most_all_bypass.__slots__ = [
    'bypassState',
]
struct_s_xl_most_all_bypass._fields_ = [
    ('bypassState', c_uint),
]

XL_MOST_ALL_BYPASS_EV = struct_s_xl_most_all_bypass# vxlapi.h: 1937

# vxlapi.h: 1941
class struct_s_xl_most_timing_mode(Structure):
    pass

struct_s_xl_most_timing_mode._pack_ = 8
struct_s_xl_most_timing_mode.__slots__ = [
    'timingmode',
]
struct_s_xl_most_timing_mode._fields_ = [
    ('timingmode', c_uint),
]

XL_MOST_TIMING_MODE_EV = struct_s_xl_most_timing_mode# vxlapi.h: 1941

# vxlapi.h: 1945
class struct_s_xl_most_timing_mode_spdif(Structure):
    pass

struct_s_xl_most_timing_mode_spdif._pack_ = 8
struct_s_xl_most_timing_mode_spdif.__slots__ = [
    'timingmode',
]
struct_s_xl_most_timing_mode_spdif._fields_ = [
    ('timingmode', c_uint),
]

XL_MOST_TIMING_MODE_SPDIF_EV = struct_s_xl_most_timing_mode_spdif# vxlapi.h: 1945

# vxlapi.h: 1949
class struct_s_xl_most_frequency(Structure):
    pass

struct_s_xl_most_frequency._pack_ = 8
struct_s_xl_most_frequency.__slots__ = [
    'frequency',
]
struct_s_xl_most_frequency._fields_ = [
    ('frequency', c_uint),
]

XL_MOST_FREQUENCY_EV = struct_s_xl_most_frequency# vxlapi.h: 1949

# vxlapi.h: 1955
class struct_s_xl_most_register_bytes(Structure):
    pass

struct_s_xl_most_register_bytes._pack_ = 8
struct_s_xl_most_register_bytes.__slots__ = [
    'number',
    'address',
    'value',
]
struct_s_xl_most_register_bytes._fields_ = [
    ('number', c_uint),
    ('address', c_uint),
    ('value', c_ubyte * int(16)),
]

XL_MOST_REGISTER_BYTES_EV = struct_s_xl_most_register_bytes# vxlapi.h: 1955

# vxlapi.h: 1961
class struct_s_xl_most_register_bits(Structure):
    pass

struct_s_xl_most_register_bits._pack_ = 8
struct_s_xl_most_register_bits.__slots__ = [
    'address',
    'value',
    'mask',
]
struct_s_xl_most_register_bits._fields_ = [
    ('address', c_uint),
    ('value', c_uint),
    ('mask', c_uint),
]

XL_MOST_REGISTER_BITS_EV = struct_s_xl_most_register_bits# vxlapi.h: 1961

# vxlapi.h: 1965
class struct_s_xl_most_sync_alloc(Structure):
    pass

struct_s_xl_most_sync_alloc._pack_ = 8
struct_s_xl_most_sync_alloc.__slots__ = [
    'allocTable',
]
struct_s_xl_most_sync_alloc._fields_ = [
    ('allocTable', c_ubyte * int(64)),
]

XL_MOST_SYNC_ALLOC_EV = struct_s_xl_most_sync_alloc# vxlapi.h: 1965

# vxlapi.h: 1971
class struct_s_xl_most_ctrl_sync_audio(Structure):
    pass

struct_s_xl_most_ctrl_sync_audio._pack_ = 8
struct_s_xl_most_ctrl_sync_audio.__slots__ = [
    'channelMask',
    'device',
    'mode',
]
struct_s_xl_most_ctrl_sync_audio._fields_ = [
    ('channelMask', c_uint * int(4)),
    ('device', c_uint),
    ('mode', c_uint),
]

XL_MOST_CTRL_SYNC_AUDIO_EV = struct_s_xl_most_ctrl_sync_audio# vxlapi.h: 1971

# vxlapi.h: 1977
class struct_s_xl_most_ctrl_sync_audio_ex(Structure):
    pass

struct_s_xl_most_ctrl_sync_audio_ex._pack_ = 8
struct_s_xl_most_ctrl_sync_audio_ex.__slots__ = [
    'channelMask',
    'device',
    'mode',
]
struct_s_xl_most_ctrl_sync_audio_ex._fields_ = [
    ('channelMask', c_uint * int(16)),
    ('device', c_uint),
    ('mode', c_uint),
]

XL_MOST_CTRL_SYNC_AUDIO_EX_EV = struct_s_xl_most_ctrl_sync_audio_ex# vxlapi.h: 1977

# vxlapi.h: 1982
class struct_s_xl_most_sync_volume_status(Structure):
    pass

struct_s_xl_most_sync_volume_status._pack_ = 8
struct_s_xl_most_sync_volume_status.__slots__ = [
    'device',
    'volume',
]
struct_s_xl_most_sync_volume_status._fields_ = [
    ('device', c_uint),
    ('volume', c_uint),
]

XL_MOST_SYNC_VOLUME_STATUS_EV = struct_s_xl_most_sync_volume_status# vxlapi.h: 1982

# vxlapi.h: 1987
class struct_s_xl_most_sync_mutes_status(Structure):
    pass

struct_s_xl_most_sync_mutes_status._pack_ = 8
struct_s_xl_most_sync_mutes_status.__slots__ = [
    'device',
    'mute',
]
struct_s_xl_most_sync_mutes_status._fields_ = [
    ('device', c_uint),
    ('mute', c_uint),
]

XL_MOST_SYNC_MUTES_STATUS_EV = struct_s_xl_most_sync_mutes_status# vxlapi.h: 1987

# vxlapi.h: 1991
class struct_s_xl_most_rx_light(Structure):
    pass

struct_s_xl_most_rx_light._pack_ = 8
struct_s_xl_most_rx_light.__slots__ = [
    'light',
]
struct_s_xl_most_rx_light._fields_ = [
    ('light', c_uint),
]

XL_MOST_RX_LIGHT_EV = struct_s_xl_most_rx_light# vxlapi.h: 1991

# vxlapi.h: 1995
class struct_s_xl_most_tx_light(Structure):
    pass

struct_s_xl_most_tx_light._pack_ = 8
struct_s_xl_most_tx_light.__slots__ = [
    'light',
]
struct_s_xl_most_tx_light._fields_ = [
    ('light', c_uint),
]

XL_MOST_TX_LIGHT_EV = struct_s_xl_most_tx_light# vxlapi.h: 1995

# vxlapi.h: 1999
class struct_s_xl_most_light_power(Structure):
    pass

struct_s_xl_most_light_power._pack_ = 8
struct_s_xl_most_light_power.__slots__ = [
    'lightPower',
]
struct_s_xl_most_light_power._fields_ = [
    ('lightPower', c_uint),
]

XL_MOST_LIGHT_POWER_EV = struct_s_xl_most_light_power# vxlapi.h: 1999

# vxlapi.h: 2003
class struct_s_xl_most_lock_status(Structure):
    pass

struct_s_xl_most_lock_status._pack_ = 8
struct_s_xl_most_lock_status.__slots__ = [
    'lockStatus',
]
struct_s_xl_most_lock_status._fields_ = [
    ('lockStatus', c_uint),
]

XL_MOST_LOCK_STATUS_EV = struct_s_xl_most_lock_status# vxlapi.h: 2003

# vxlapi.h: 2007
class struct_s_xl_most_supervisor_lock_status(Structure):
    pass

struct_s_xl_most_supervisor_lock_status._pack_ = 8
struct_s_xl_most_supervisor_lock_status.__slots__ = [
    'supervisorLockStatus',
]
struct_s_xl_most_supervisor_lock_status._fields_ = [
    ('supervisorLockStatus', c_uint),
]

XL_MOST_SUPERVISOR_LOCK_STATUS_EV = struct_s_xl_most_supervisor_lock_status# vxlapi.h: 2007

# vxlapi.h: 2013
class struct_s_xl_most_gen_light_error(Structure):
    pass

struct_s_xl_most_gen_light_error._pack_ = 8
struct_s_xl_most_gen_light_error.__slots__ = [
    'lightOnTime',
    'lightOffTime',
    'repeat',
]
struct_s_xl_most_gen_light_error._fields_ = [
    ('lightOnTime', c_uint),
    ('lightOffTime', c_uint),
    ('repeat', c_uint),
]

XL_MOST_GEN_LIGHT_ERROR_EV = struct_s_xl_most_gen_light_error# vxlapi.h: 2013

# vxlapi.h: 2019
class struct_s_xl_most_gen_lock_error(Structure):
    pass

struct_s_xl_most_gen_lock_error._pack_ = 8
struct_s_xl_most_gen_lock_error.__slots__ = [
    'lockOnTime',
    'lockOffTime',
    'repeat',
]
struct_s_xl_most_gen_lock_error._fields_ = [
    ('lockOnTime', c_uint),
    ('lockOffTime', c_uint),
    ('repeat', c_uint),
]

XL_MOST_GEN_LOCK_ERROR_EV = struct_s_xl_most_gen_lock_error# vxlapi.h: 2019

# vxlapi.h: 2023
class struct_s_xl_most_rx_buffer(Structure):
    pass

struct_s_xl_most_rx_buffer._pack_ = 8
struct_s_xl_most_rx_buffer.__slots__ = [
    'mode',
]
struct_s_xl_most_rx_buffer._fields_ = [
    ('mode', c_uint),
]

XL_MOST_RX_BUFFER_EV = struct_s_xl_most_rx_buffer# vxlapi.h: 2023

# vxlapi.h: 2028
class struct_s_xl_most_error(Structure):
    pass

struct_s_xl_most_error._pack_ = 8
struct_s_xl_most_error.__slots__ = [
    'errorCode',
    'parameter',
]
struct_s_xl_most_error._fields_ = [
    ('errorCode', c_uint),
    ('parameter', c_uint * int(3)),
]

XL_MOST_ERROR_EV = struct_s_xl_most_error# vxlapi.h: 2028

XL_MOST_SYNC_PULSE_EV = XL_SYNC_PULSE_EV# vxlapi.h: 2030

# vxlapi.h: 2034
class struct_s_xl_most_ctrl_busload(Structure):
    pass

struct_s_xl_most_ctrl_busload._pack_ = 8
struct_s_xl_most_ctrl_busload.__slots__ = [
    'busloadCtrlStarted',
]
struct_s_xl_most_ctrl_busload._fields_ = [
    ('busloadCtrlStarted', c_uint),
]

XL_MOST_CTRL_BUSLOAD_EV = struct_s_xl_most_ctrl_busload# vxlapi.h: 2034

# vxlapi.h: 2038
class struct_s_xl_most_async_busload(Structure):
    pass

struct_s_xl_most_async_busload._pack_ = 8
struct_s_xl_most_async_busload.__slots__ = [
    'busloadAsyncStarted',
]
struct_s_xl_most_async_busload._fields_ = [
    ('busloadAsyncStarted', c_uint),
]

XL_MOST_ASYNC_BUSLOAD_EV = struct_s_xl_most_async_busload# vxlapi.h: 2038

# vxlapi.h: 2045
class struct_s_xl_most_stream_state(Structure):
    pass

struct_s_xl_most_stream_state._pack_ = 8
struct_s_xl_most_stream_state.__slots__ = [
    'streamHandle',
    'streamState',
    'streamError',
    'reserved',
]
struct_s_xl_most_stream_state._fields_ = [
    ('streamHandle', c_uint),
    ('streamState', c_uint),
    ('streamError', c_uint),
    ('reserved', c_uint),
]

XL_MOST_STREAM_STATE_EV = struct_s_xl_most_stream_state# vxlapi.h: 2045

# vxlapi.h: 2057
class struct_s_xl_most_stream_buffer(Structure):
    pass

struct_s_xl_most_stream_buffer._pack_ = 8
struct_s_xl_most_stream_buffer.__slots__ = [
    'streamHandle',
    'pBuffer',
    'validBytes',
    'status',
    'pBuffer_highpart',
]
struct_s_xl_most_stream_buffer._fields_ = [
    ('streamHandle', c_uint),
    ('pBuffer', c_uint),
    ('validBytes', c_uint),
    ('status', c_uint),
    ('pBuffer_highpart', c_uint),
]

XL_MOST_STREAM_BUFFER_EV = struct_s_xl_most_stream_buffer# vxlapi.h: 2057

# vxlapi.h: 2063
class struct_s_xl_most_sync_tx_underflow(Structure):
    pass

struct_s_xl_most_sync_tx_underflow._pack_ = 8
struct_s_xl_most_sync_tx_underflow.__slots__ = [
    'streamHandle',
    'reserved',
]
struct_s_xl_most_sync_tx_underflow._fields_ = [
    ('streamHandle', c_uint),
    ('reserved', c_uint),
]

XL_MOST_SYNC_TX_UNDERFLOW_EV = struct_s_xl_most_sync_tx_underflow# vxlapi.h: 2063

# vxlapi.h: 2068
class struct_s_xl_most_sync_rx_overflow(Structure):
    pass

struct_s_xl_most_sync_rx_overflow._pack_ = 8
struct_s_xl_most_sync_rx_overflow.__slots__ = [
    'streamHandle',
    'reserved',
]
struct_s_xl_most_sync_rx_overflow._fields_ = [
    ('streamHandle', c_uint),
    ('reserved', c_uint),
]

XL_MOST_SYNC_RX_OVERFLOW_EV = struct_s_xl_most_sync_rx_overflow# vxlapi.h: 2068

# vxlapi.h: 2075
class union_s_xl_most_tag_data(Union):
    pass

union_s_xl_most_tag_data._pack_ = 8
union_s_xl_most_tag_data.__slots__ = [
    'mostCtrlSpy',
    'mostCtrlMsg',
    'mostAsyncMsg',
    'mostAsyncTx',
    'mostSpecialRegister',
    'mostEventSource',
    'mostAllBypass',
    'mostTimingMode',
    'mostTimingModeSpdif',
    'mostFrequency',
    'mostRegisterBytes',
    'mostRegisterBits',
    'mostSyncAlloc',
    'mostCtrlSyncAudio',
    'mostCtrlSyncAudioEx',
    'mostSyncVolumeStatus',
    'mostSyncMuteStatus',
    'mostRxLight',
    'mostTxLight',
    'mostLightPower',
    'mostLockStatus',
    'mostGenLightError',
    'mostGenLockError',
    'mostRxBuffer',
    'mostError',
    'mostSyncPulse',
    'mostCtrlBusload',
    'mostAsyncBusload',
    'mostStreamState',
    'mostStreamBuffer',
    'mostSyncTxUnderflow',
    'mostSyncRxOverflow',
]
union_s_xl_most_tag_data._fields_ = [
    ('mostCtrlSpy', XL_MOST_CTRL_SPY_EV),
    ('mostCtrlMsg', XL_MOST_CTRL_MSG_EV),
    ('mostAsyncMsg', XL_MOST_ASYNC_MSG_EV),
    ('mostAsyncTx', XL_MOST_ASYNC_TX_EV),
    ('mostSpecialRegister', XL_MOST_SPECIAL_REGISTER_EV),
    ('mostEventSource', XL_MOST_EVENT_SOURCE_EV),
    ('mostAllBypass', XL_MOST_ALL_BYPASS_EV),
    ('mostTimingMode', XL_MOST_TIMING_MODE_EV),
    ('mostTimingModeSpdif', XL_MOST_TIMING_MODE_SPDIF_EV),
    ('mostFrequency', XL_MOST_FREQUENCY_EV),
    ('mostRegisterBytes', XL_MOST_REGISTER_BYTES_EV),
    ('mostRegisterBits', XL_MOST_REGISTER_BITS_EV),
    ('mostSyncAlloc', XL_MOST_SYNC_ALLOC_EV),
    ('mostCtrlSyncAudio', XL_MOST_CTRL_SYNC_AUDIO_EV),
    ('mostCtrlSyncAudioEx', XL_MOST_CTRL_SYNC_AUDIO_EX_EV),
    ('mostSyncVolumeStatus', XL_MOST_SYNC_VOLUME_STATUS_EV),
    ('mostSyncMuteStatus', XL_MOST_SYNC_MUTES_STATUS_EV),
    ('mostRxLight', XL_MOST_RX_LIGHT_EV),
    ('mostTxLight', XL_MOST_TX_LIGHT_EV),
    ('mostLightPower', XL_MOST_LIGHT_POWER_EV),
    ('mostLockStatus', XL_MOST_LOCK_STATUS_EV),
    ('mostGenLightError', XL_MOST_GEN_LIGHT_ERROR_EV),
    ('mostGenLockError', XL_MOST_GEN_LOCK_ERROR_EV),
    ('mostRxBuffer', XL_MOST_RX_BUFFER_EV),
    ('mostError', XL_MOST_ERROR_EV),
    ('mostSyncPulse', XL_MOST_SYNC_PULSE_EV),
    ('mostCtrlBusload', XL_MOST_CTRL_BUSLOAD_EV),
    ('mostAsyncBusload', XL_MOST_ASYNC_BUSLOAD_EV),
    ('mostStreamState', XL_MOST_STREAM_STATE_EV),
    ('mostStreamBuffer', XL_MOST_STREAM_BUFFER_EV),
    ('mostSyncTxUnderflow', XL_MOST_SYNC_TX_UNDERFLOW_EV),
    ('mostSyncRxOverflow', XL_MOST_SYNC_RX_OVERFLOW_EV),
]

XLmostEventTag = c_ushort# vxlapi.h: 2110

# vxlapi.h: 2112
class struct_s_xl_most_event(Structure):
    pass

struct_s_xl_most_event._pack_ = 8
struct_s_xl_most_event.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved',
    'timeStamp',
    'timeStampSync',
    'tagData',
]
struct_s_xl_most_event._fields_ = [
    ('size', c_uint),
    ('tag', XLmostEventTag),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved', c_ushort),
    ('timeStamp', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_s_xl_most_tag_data),
]

XLmostEvent = struct_s_xl_most_event# vxlapi.h: 2126

XLmostCtrlMsg = XL_MOST_CTRL_MSG_EV# vxlapi.h: 2128

XLmostAsyncMsg = XL_MOST_ASYNC_TX_EV# vxlapi.h: 2129

# vxlapi.h: 2136
class struct_s_xl_most_ctrl_busload_configuration(Structure):
    pass

struct_s_xl_most_ctrl_busload_configuration._pack_ = 8
struct_s_xl_most_ctrl_busload_configuration.__slots__ = [
    'transmissionRate',
    'counterType',
    'counterPosition',
    'busloadCtrlMsg',
]
struct_s_xl_most_ctrl_busload_configuration._fields_ = [
    ('transmissionRate', c_uint),
    ('counterType', c_uint),
    ('counterPosition', c_uint),
    ('busloadCtrlMsg', XL_MOST_CTRL_MSG_EV),
]

XL_MOST_CTRL_BUSLOAD_CONFIGURATION = struct_s_xl_most_ctrl_busload_configuration# vxlapi.h: 2136

# vxlapi.h: 2143
class struct_s_xl_most_async_busload_configuration(Structure):
    pass

struct_s_xl_most_async_busload_configuration._pack_ = 8
struct_s_xl_most_async_busload_configuration.__slots__ = [
    'transmissionRate',
    'counterType',
    'counterPosition',
    'busloadAsyncMsg',
]
struct_s_xl_most_async_busload_configuration._fields_ = [
    ('transmissionRate', c_uint),
    ('counterType', c_uint),
    ('counterPosition', c_uint),
    ('busloadAsyncMsg', XL_MOST_ASYNC_TX_EV),
]

XL_MOST_ASYNC_BUSLOAD_CONFIGURATION = struct_s_xl_most_async_busload_configuration# vxlapi.h: 2143

XLmostCtrlBusloadConfiguration = XL_MOST_CTRL_BUSLOAD_CONFIGURATION# vxlapi.h: 2145

XLmostAsyncBusloadConfiguration = XL_MOST_ASYNC_BUSLOAD_CONFIGURATION# vxlapi.h: 2146

# vxlapi.h: 2180
class struct_s_xl_most_device_state(Structure):
    pass

struct_s_xl_most_device_state._pack_ = 8
struct_s_xl_most_device_state.__slots__ = [
    'selectionMask',
    'lockState',
    'rxLight',
    'txLight',
    'txLightPower',
    'registerBunch1',
    'bypassState',
    'timingMode',
    'frequency',
    'registerBunch2',
    'registerBunch3',
    'volume',
    'mute',
    'eventSource',
    'rxBufferMode',
    'allocTable',
    'supervisorLockStatus',
    'broadcastedConfigStatus',
    'adrNetworkMaster',
    'abilityToWake',
]
struct_s_xl_most_device_state._fields_ = [
    ('selectionMask', c_uint),
    ('lockState', c_uint),
    ('rxLight', c_uint),
    ('txLight', c_uint),
    ('txLightPower', c_uint),
    ('registerBunch1', c_ubyte * int(16)),
    ('bypassState', c_uint),
    ('timingMode', c_uint),
    ('frequency', c_uint),
    ('registerBunch2', c_ubyte * int(2)),
    ('registerBunch3', c_ubyte * int(2)),
    ('volume', c_uint * int(2)),
    ('mute', c_uint * int(2)),
    ('eventSource', c_uint),
    ('rxBufferMode', c_uint),
    ('allocTable', c_ubyte * int(64)),
    ('supervisorLockStatus', c_uint),
    ('broadcastedConfigStatus', c_uint),
    ('adrNetworkMaster', c_uint),
    ('abilityToWake', c_uint),
]

XL_MOST_DEVICE_STATE = struct_s_xl_most_device_state# vxlapi.h: 2180

XLmostDeviceState = XL_MOST_DEVICE_STATE# vxlapi.h: 2182

# vxlapi.h: 2190
class struct_s_xl_most_stream_open(Structure):
    pass

struct_s_xl_most_stream_open._pack_ = 8
struct_s_xl_most_stream_open.__slots__ = [
    'pStreamHandle',
    'numSyncChannels',
    'direction',
    'options',
    'latency',
]
struct_s_xl_most_stream_open._fields_ = [
    ('pStreamHandle', POINTER(c_uint)),
    ('numSyncChannels', c_uint),
    ('direction', c_uint),
    ('options', c_uint),
    ('latency', c_uint),
]

XL_MOST_STREAM_OPEN = struct_s_xl_most_stream_open# vxlapi.h: 2190

XLmostStreamOpen = XL_MOST_STREAM_OPEN# vxlapi.h: 2192

# vxlapi.h: 2203
class struct_s_xl_most_stream_info(Structure):
    pass

struct_s_xl_most_stream_info._pack_ = 8
struct_s_xl_most_stream_info.__slots__ = [
    'streamHandle',
    'numSyncChannels',
    'direction',
    'options',
    'latency',
    'streamState',
    'reserved',
    'syncChannels',
]
struct_s_xl_most_stream_info._fields_ = [
    ('streamHandle', c_uint),
    ('numSyncChannels', c_uint),
    ('direction', c_uint),
    ('options', c_uint),
    ('latency', c_uint),
    ('streamState', c_uint),
    ('reserved', c_uint),
    ('syncChannels', c_ubyte * int(60)),
]

XL_MOST_STREAM_INFO = struct_s_xl_most_stream_info# vxlapi.h: 2203

XLmostStreamInfo = XL_MOST_STREAM_INFO# vxlapi.h: 2205

# vxlapi.h: 2290
class struct_s_xl_fr_cluster_configuration(Structure):
    pass

struct_s_xl_fr_cluster_configuration._pack_ = 4
struct_s_xl_fr_cluster_configuration.__slots__ = [
    'busGuardianEnable',
    'baudrate',
    'busGuardianTick',
    'externalClockCorrectionMode',
    'gColdStartAttempts',
    'gListenNoise',
    'gMacroPerCycle',
    'gMaxWithoutClockCorrectionFatal',
    'gMaxWithoutClockCorrectionPassive',
    'gNetworkManagementVectorLength',
    'gNumberOfMinislots',
    'gNumberOfStaticSlots',
    'gOffsetCorrectionStart',
    'gPayloadLengthStatic',
    'gSyncNodeMax',
    'gdActionPointOffset',
    'gdDynamicSlotIdlePhase',
    'gdMacrotick',
    'gdMinislot',
    'gdMiniSlotActionPointOffset',
    'gdNIT',
    'gdStaticSlot',
    'gdSymbolWindow',
    'gdTSSTransmitter',
    'gdWakeupSymbolRxIdle',
    'gdWakeupSymbolRxLow',
    'gdWakeupSymbolRxWindow',
    'gdWakeupSymbolTxIdle',
    'gdWakeupSymbolTxLow',
    'pAllowHaltDueToClock',
    'pAllowPassiveToActive',
    'pChannels',
    'pClusterDriftDamping',
    'pDecodingCorrection',
    'pDelayCompensationA',
    'pDelayCompensationB',
    'pExternOffsetCorrection',
    'pExternRateCorrection',
    'pKeySlotUsedForStartup',
    'pKeySlotUsedForSync',
    'pLatestTx',
    'pMacroInitialOffsetA',
    'pMacroInitialOffsetB',
    'pMaxPayloadLengthDynamic',
    'pMicroInitialOffsetA',
    'pMicroInitialOffsetB',
    'pMicroPerCycle',
    'pMicroPerMacroNom',
    'pOffsetCorrectionOut',
    'pRateCorrectionOut',
    'pSamplesPerMicrotick',
    'pSingleSlotEnabled',
    'pWakeupChannel',
    'pWakeupPattern',
    'pdAcceptedStartupRange',
    'pdListenTimeout',
    'pdMaxDrift',
    'pdMicrotick',
    'gdCASRxLowMax',
    'gChannels',
    'vExternOffsetControl',
    'vExternRateControl',
    'pChannelsMTS',
    'framePresetData',
    'reserved',
]
struct_s_xl_fr_cluster_configuration._fields_ = [
    ('busGuardianEnable', c_uint),
    ('baudrate', c_uint),
    ('busGuardianTick', c_uint),
    ('externalClockCorrectionMode', c_uint),
    ('gColdStartAttempts', c_uint),
    ('gListenNoise', c_uint),
    ('gMacroPerCycle', c_uint),
    ('gMaxWithoutClockCorrectionFatal', c_uint),
    ('gMaxWithoutClockCorrectionPassive', c_uint),
    ('gNetworkManagementVectorLength', c_uint),
    ('gNumberOfMinislots', c_uint),
    ('gNumberOfStaticSlots', c_uint),
    ('gOffsetCorrectionStart', c_uint),
    ('gPayloadLengthStatic', c_uint),
    ('gSyncNodeMax', c_uint),
    ('gdActionPointOffset', c_uint),
    ('gdDynamicSlotIdlePhase', c_uint),
    ('gdMacrotick', c_uint),
    ('gdMinislot', c_uint),
    ('gdMiniSlotActionPointOffset', c_uint),
    ('gdNIT', c_uint),
    ('gdStaticSlot', c_uint),
    ('gdSymbolWindow', c_uint),
    ('gdTSSTransmitter', c_uint),
    ('gdWakeupSymbolRxIdle', c_uint),
    ('gdWakeupSymbolRxLow', c_uint),
    ('gdWakeupSymbolRxWindow', c_uint),
    ('gdWakeupSymbolTxIdle', c_uint),
    ('gdWakeupSymbolTxLow', c_uint),
    ('pAllowHaltDueToClock', c_uint),
    ('pAllowPassiveToActive', c_uint),
    ('pChannels', c_uint),
    ('pClusterDriftDamping', c_uint),
    ('pDecodingCorrection', c_uint),
    ('pDelayCompensationA', c_uint),
    ('pDelayCompensationB', c_uint),
    ('pExternOffsetCorrection', c_uint),
    ('pExternRateCorrection', c_uint),
    ('pKeySlotUsedForStartup', c_uint),
    ('pKeySlotUsedForSync', c_uint),
    ('pLatestTx', c_uint),
    ('pMacroInitialOffsetA', c_uint),
    ('pMacroInitialOffsetB', c_uint),
    ('pMaxPayloadLengthDynamic', c_uint),
    ('pMicroInitialOffsetA', c_uint),
    ('pMicroInitialOffsetB', c_uint),
    ('pMicroPerCycle', c_uint),
    ('pMicroPerMacroNom', c_uint),
    ('pOffsetCorrectionOut', c_uint),
    ('pRateCorrectionOut', c_uint),
    ('pSamplesPerMicrotick', c_uint),
    ('pSingleSlotEnabled', c_uint),
    ('pWakeupChannel', c_uint),
    ('pWakeupPattern', c_uint),
    ('pdAcceptedStartupRange', c_uint),
    ('pdListenTimeout', c_uint),
    ('pdMaxDrift', c_uint),
    ('pdMicrotick', c_uint),
    ('gdCASRxLowMax', c_uint),
    ('gChannels', c_uint),
    ('vExternOffsetControl', c_uint),
    ('vExternRateControl', c_uint),
    ('pChannelsMTS', c_uint),
    ('framePresetData', c_uint),
    ('reserved', c_uint * int(15)),
]

XLfrClusterConfig = struct_s_xl_fr_cluster_configuration# vxlapi.h: 2290

# vxlapi.h: 2299
class struct_s_xl_fr_channel_config(Structure):
    pass

struct_s_xl_fr_channel_config._pack_ = 4
struct_s_xl_fr_channel_config.__slots__ = [
    'status',
    'cfgMode',
    'reserved',
    'xlFrClusterConfig',
]
struct_s_xl_fr_channel_config._fields_ = [
    ('status', c_uint),
    ('cfgMode', c_uint),
    ('reserved', c_uint * int(6)),
    ('xlFrClusterConfig', XLfrClusterConfig),
]

XLfrChannelConfig = struct_s_xl_fr_channel_config# vxlapi.h: 2299

# vxlapi.h: 2332
class struct_s_xl_fr_set_modes(Structure):
    pass

struct_s_xl_fr_set_modes._pack_ = 4
struct_s_xl_fr_set_modes.__slots__ = [
    'frMode',
    'frStartupAttributes',
    'useSelCycle',
    'selCycle',
    'reserved',
]
struct_s_xl_fr_set_modes._fields_ = [
    ('frMode', c_uint),
    ('frStartupAttributes', c_uint),
    ('useSelCycle', c_ushort),
    ('selCycle', c_ushort),
    ('reserved', c_uint * int(29)),
]

XLfrMode = struct_s_xl_fr_set_modes# vxlapi.h: 2332

# vxlapi.h: 2376
class struct_s_xl_fr_acceptance_filter(Structure):
    pass

struct_s_xl_fr_acceptance_filter._pack_ = 8
struct_s_xl_fr_acceptance_filter.__slots__ = [
    'filterStatus',
    'filterTypeMask',
    'filterFirstSlot',
    'filterLastSlot',
    'filterChannelMask',
]
struct_s_xl_fr_acceptance_filter._fields_ = [
    ('filterStatus', c_uint),
    ('filterTypeMask', c_uint),
    ('filterFirstSlot', c_uint),
    ('filterLastSlot', c_uint),
    ('filterChannelMask', c_uint),
]

XLfrAcceptanceFilter = struct_s_xl_fr_acceptance_filter# vxlapi.h: 2376

# vxlapi.h: 2537
class struct_s_xl_fr_start_cycle(Structure):
    pass

struct_s_xl_fr_start_cycle._pack_ = 8
struct_s_xl_fr_start_cycle.__slots__ = [
    'cycleCount',
    'vRateCorrection',
    'vOffsetCorrection',
    'vClockCorrectionFailed',
    'vAllowPassivToActive',
    'reserved',
]
struct_s_xl_fr_start_cycle._fields_ = [
    ('cycleCount', c_uint),
    ('vRateCorrection', c_int),
    ('vOffsetCorrection', c_int),
    ('vClockCorrectionFailed', c_uint),
    ('vAllowPassivToActive', c_uint),
    ('reserved', c_uint * int(3)),
]

XL_FR_START_CYCLE_EV = struct_s_xl_fr_start_cycle# vxlapi.h: 2537

# vxlapi.h: 2546
class struct_s_xl_fr_rx_frame(Structure):
    pass

struct_s_xl_fr_rx_frame._pack_ = 8
struct_s_xl_fr_rx_frame.__slots__ = [
    'flags',
    'headerCRC',
    'slotID',
    'cycleCount',
    'payloadLength',
    'data',
]
struct_s_xl_fr_rx_frame._fields_ = [
    ('flags', c_ushort),
    ('headerCRC', c_ushort),
    ('slotID', c_ushort),
    ('cycleCount', c_ubyte),
    ('payloadLength', c_ubyte),
    ('data', c_ubyte * int(254)),
]

XL_FR_RX_FRAME_EV = struct_s_xl_fr_rx_frame# vxlapi.h: 2546

# vxlapi.h: 2560
class struct_s_xl_fr_tx_frame(Structure):
    pass

struct_s_xl_fr_tx_frame._pack_ = 8
struct_s_xl_fr_tx_frame.__slots__ = [
    'flags',
    'slotID',
    'offset',
    'repetition',
    'payloadLength',
    'txMode',
    'incrementSize',
    'incrementOffset',
    'reserved0',
    'reserved1',
    'data',
]
struct_s_xl_fr_tx_frame._fields_ = [
    ('flags', c_ushort),
    ('slotID', c_ushort),
    ('offset', c_ubyte),
    ('repetition', c_ubyte),
    ('payloadLength', c_ubyte),
    ('txMode', c_ubyte),
    ('incrementSize', c_ubyte),
    ('incrementOffset', c_ubyte),
    ('reserved0', c_ubyte),
    ('reserved1', c_ubyte),
    ('data', c_ubyte * int(254)),
]

XL_FR_TX_FRAME_EV = struct_s_xl_fr_tx_frame# vxlapi.h: 2560

# vxlapi.h: 2566
class struct_s_xl_fr_wakeup(Structure):
    pass

struct_s_xl_fr_wakeup._pack_ = 8
struct_s_xl_fr_wakeup.__slots__ = [
    'cycleCount',
    'wakeupStatus',
    'reserved',
]
struct_s_xl_fr_wakeup._fields_ = [
    ('cycleCount', c_ubyte),
    ('wakeupStatus', c_ubyte),
    ('reserved', c_ubyte * int(6)),
]

XL_FR_WAKEUP_EV = struct_s_xl_fr_wakeup# vxlapi.h: 2566

# vxlapi.h: 2573
class struct_s_xl_fr_symbol_window(Structure):
    pass

struct_s_xl_fr_symbol_window._pack_ = 8
struct_s_xl_fr_symbol_window.__slots__ = [
    'symbol',
    'flags',
    'cycleCount',
    'reserved',
]
struct_s_xl_fr_symbol_window._fields_ = [
    ('symbol', c_uint),
    ('flags', c_uint),
    ('cycleCount', c_ubyte),
    ('reserved', c_ubyte * int(7)),
]

XL_FR_SYMBOL_WINDOW_EV = struct_s_xl_fr_symbol_window# vxlapi.h: 2573

# vxlapi.h: 2578
class struct_s_xl_fr_status(Structure):
    pass

struct_s_xl_fr_status._pack_ = 8
struct_s_xl_fr_status.__slots__ = [
    'statusType',
    'reserved',
]
struct_s_xl_fr_status._fields_ = [
    ('statusType', c_uint),
    ('reserved', c_uint),
]

XL_FR_STATUS_EV = struct_s_xl_fr_status# vxlapi.h: 2578

# vxlapi.h: 2584
class struct_s_xl_fr_nm_vector(Structure):
    pass

struct_s_xl_fr_nm_vector._pack_ = 8
struct_s_xl_fr_nm_vector.__slots__ = [
    'nmVector',
    'cycleCount',
    'reserved',
]
struct_s_xl_fr_nm_vector._fields_ = [
    ('nmVector', c_ubyte * int(12)),
    ('cycleCount', c_ubyte),
    ('reserved', c_ubyte * int(3)),
]

XL_FR_NM_VECTOR_EV = struct_s_xl_fr_nm_vector# vxlapi.h: 2584

XL_FR_SYNC_PULSE_EV = XL_SYNC_PULSE_EV# vxlapi.h: 2586

# vxlapi.h: 2591
class struct_s_xl_fr_error_poc_mode(Structure):
    pass

struct_s_xl_fr_error_poc_mode._pack_ = 8
struct_s_xl_fr_error_poc_mode.__slots__ = [
    'errorMode',
    'reserved',
]
struct_s_xl_fr_error_poc_mode._fields_ = [
    ('errorMode', c_ubyte),
    ('reserved', c_ubyte * int(3)),
]

XL_FR_ERROR_POC_MODE_EV = struct_s_xl_fr_error_poc_mode# vxlapi.h: 2591

# vxlapi.h: 2599
class struct_s_xl_fr_error_sync_frames(Structure):
    pass

struct_s_xl_fr_error_sync_frames._pack_ = 8
struct_s_xl_fr_error_sync_frames.__slots__ = [
    'evenSyncFramesA',
    'oddSyncFramesA',
    'evenSyncFramesB',
    'oddSyncFramesB',
    'reserved',
]
struct_s_xl_fr_error_sync_frames._fields_ = [
    ('evenSyncFramesA', c_ushort),
    ('oddSyncFramesA', c_ushort),
    ('evenSyncFramesB', c_ushort),
    ('oddSyncFramesB', c_ushort),
    ('reserved', c_uint),
]

XL_FR_ERROR_SYNC_FRAMES_EV = struct_s_xl_fr_error_sync_frames# vxlapi.h: 2599

# vxlapi.h: 2609
class struct_s_xl_fr_error_clock_corr_failure(Structure):
    pass

struct_s_xl_fr_error_clock_corr_failure._pack_ = 8
struct_s_xl_fr_error_clock_corr_failure.__slots__ = [
    'evenSyncFramesA',
    'oddSyncFramesA',
    'evenSyncFramesB',
    'oddSyncFramesB',
    'flags',
    'clockCorrFailedCounter',
    'reserved',
]
struct_s_xl_fr_error_clock_corr_failure._fields_ = [
    ('evenSyncFramesA', c_ushort),
    ('oddSyncFramesA', c_ushort),
    ('evenSyncFramesB', c_ushort),
    ('oddSyncFramesB', c_ushort),
    ('flags', c_uint),
    ('clockCorrFailedCounter', c_uint),
    ('reserved', c_uint),
]

XL_FR_ERROR_CLOCK_CORR_FAILURE_EV = struct_s_xl_fr_error_clock_corr_failure# vxlapi.h: 2609

# vxlapi.h: 2614
class struct_s_xl_fr_error_nit_failure(Structure):
    pass

struct_s_xl_fr_error_nit_failure._pack_ = 8
struct_s_xl_fr_error_nit_failure.__slots__ = [
    'flags',
    'reserved',
]
struct_s_xl_fr_error_nit_failure._fields_ = [
    ('flags', c_uint),
    ('reserved', c_uint),
]

XL_FR_ERROR_NIT_FAILURE_EV = struct_s_xl_fr_error_nit_failure# vxlapi.h: 2614

# vxlapi.h: 2619
class struct_s_xl_fr_error_cc_error(Structure):
    pass

struct_s_xl_fr_error_cc_error._pack_ = 8
struct_s_xl_fr_error_cc_error.__slots__ = [
    'ccError',
    'reserved',
]
struct_s_xl_fr_error_cc_error._fields_ = [
    ('ccError', c_uint),
    ('reserved', c_uint),
]

XL_FR_ERROR_CC_ERROR_EV = struct_s_xl_fr_error_cc_error# vxlapi.h: 2619

# vxlapi.h: 2621
class union_s_xl_fr_error_info(Union):
    pass

union_s_xl_fr_error_info._pack_ = 8
union_s_xl_fr_error_info.__slots__ = [
    'frPocMode',
    'frSyncFramesBelowMin',
    'frSyncFramesOverload',
    'frClockCorrectionFailure',
    'frNitFailure',
    'frCCError',
]
union_s_xl_fr_error_info._fields_ = [
    ('frPocMode', XL_FR_ERROR_POC_MODE_EV),
    ('frSyncFramesBelowMin', XL_FR_ERROR_SYNC_FRAMES_EV),
    ('frSyncFramesOverload', XL_FR_ERROR_SYNC_FRAMES_EV),
    ('frClockCorrectionFailure', XL_FR_ERROR_CLOCK_CORR_FAILURE_EV),
    ('frNitFailure', XL_FR_ERROR_NIT_FAILURE_EV),
    ('frCCError', XL_FR_ERROR_CC_ERROR_EV),
]

# vxlapi.h: 2635
class struct_s_xl_fr_error(Structure):
    pass

struct_s_xl_fr_error._pack_ = 8
struct_s_xl_fr_error.__slots__ = [
    'tag',
    'cycleCount',
    'reserved',
    'errorInfo',
]
struct_s_xl_fr_error._fields_ = [
    ('tag', c_ubyte),
    ('cycleCount', c_ubyte),
    ('reserved', c_ubyte * int(6)),
    ('errorInfo', union_s_xl_fr_error_info),
]

XL_FR_ERROR_EV = struct_s_xl_fr_error# vxlapi.h: 2635

# vxlapi.h: 2650
class struct_s_xl_fr_spy_frame(Structure):
    pass

struct_s_xl_fr_spy_frame._pack_ = 8
struct_s_xl_fr_spy_frame.__slots__ = [
    'frameLength',
    'frameError',
    'tssLength',
    'headerFlags',
    'slotID',
    'headerCRC',
    'payloadLength',
    'cycleCount',
    'frameFlags',
    'reserved',
    'frameCRC',
    'data',
]
struct_s_xl_fr_spy_frame._fields_ = [
    ('frameLength', c_uint),
    ('frameError', c_ubyte),
    ('tssLength', c_ubyte),
    ('headerFlags', c_ushort),
    ('slotID', c_ushort),
    ('headerCRC', c_ushort),
    ('payloadLength', c_ubyte),
    ('cycleCount', c_ubyte),
    ('frameFlags', c_ubyte),
    ('reserved', c_ubyte),
    ('frameCRC', c_uint),
    ('data', c_ubyte * int(254)),
]

XL_FR_SPY_FRAME_EV = struct_s_xl_fr_spy_frame# vxlapi.h: 2650

# vxlapi.h: 2655
class struct_s_xl_fr_spy_symbol(Structure):
    pass

struct_s_xl_fr_spy_symbol._pack_ = 8
struct_s_xl_fr_spy_symbol.__slots__ = [
    'lowLength',
    'reserved',
]
struct_s_xl_fr_spy_symbol._fields_ = [
    ('lowLength', c_ushort),
    ('reserved', c_ushort),
]

XL_FR_SPY_SYMBOL_EV = struct_s_xl_fr_spy_symbol# vxlapi.h: 2655

# vxlapi.h: 2662
class union_s_xl_fr_tag_data(Union):
    pass

union_s_xl_fr_tag_data._pack_ = 8
union_s_xl_fr_tag_data.__slots__ = [
    'frStartCycle',
    'frRxFrame',
    'frTxFrame',
    'frWakeup',
    'frSymbolWindow',
    'frError',
    'frStatus',
    'frNmVector',
    'frSyncPulse',
    'frSpyFrame',
    'frSpySymbol',
    'applicationNotification',
    'raw',
]
union_s_xl_fr_tag_data._fields_ = [
    ('frStartCycle', XL_FR_START_CYCLE_EV),
    ('frRxFrame', XL_FR_RX_FRAME_EV),
    ('frTxFrame', XL_FR_TX_FRAME_EV),
    ('frWakeup', XL_FR_WAKEUP_EV),
    ('frSymbolWindow', XL_FR_SYMBOL_WINDOW_EV),
    ('frError', XL_FR_ERROR_EV),
    ('frStatus', XL_FR_STATUS_EV),
    ('frNmVector', XL_FR_NM_VECTOR_EV),
    ('frSyncPulse', XL_FR_SYNC_PULSE_EV),
    ('frSpyFrame', XL_FR_SPY_FRAME_EV),
    ('frSpySymbol', XL_FR_SPY_SYMBOL_EV),
    ('applicationNotification', XL_APPLICATION_NOTIFICATION_EV),
    ('raw', c_ubyte * int((512 - 32))),
]

XLfrEventTag = c_ushort# vxlapi.h: 2680

# vxlapi.h: 2682
class struct_s_xl_fr_event(Structure):
    pass

struct_s_xl_fr_event._pack_ = 8
struct_s_xl_fr_event.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved',
    'timeStamp',
    'timeStampSync',
    'tagData',
]
struct_s_xl_fr_event._fields_ = [
    ('size', c_uint),
    ('tag', XLfrEventTag),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved', c_ushort),
    ('timeStamp', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_s_xl_fr_tag_data),
]

XLfrEvent = struct_s_xl_fr_event# vxlapi.h: 2696

# vxlapi.h: 2722
class struct_anon_19(Structure):
    pass

struct_anon_19._pack_ = 8
struct_anon_19.__slots__ = [
    'portMask',
    'type',
]
struct_anon_19._fields_ = [
    ('portMask', c_uint),
    ('type', c_uint),
]

# vxlapi.h: 2719
class union_triggerTypeParams(Union):
    pass

union_triggerTypeParams._pack_ = 8
union_triggerTypeParams.__slots__ = [
    'cycleTime',
    'digital',
]
union_triggerTypeParams._fields_ = [
    ('cycleTime', c_uint),
    ('digital', struct_anon_19),
]

# vxlapi.h: 2729
class struct_s_xl_daio_trigger_mode(Structure):
    pass

struct_s_xl_daio_trigger_mode._pack_ = 8
struct_s_xl_daio_trigger_mode.__slots__ = [
    'portTypeMask',
    'triggerType',
    'param',
]
struct_s_xl_daio_trigger_mode._fields_ = [
    ('portTypeMask', c_uint),
    ('triggerType', c_uint),
    ('param', union_triggerTypeParams),
]

XLdaioTriggerMode = struct_s_xl_daio_trigger_mode# vxlapi.h: 2729

# vxlapi.h: 2742
class struct_xl_daio_set_port(Structure):
    pass

struct_xl_daio_set_port._pack_ = 8
struct_xl_daio_set_port.__slots__ = [
    'portType',
    'portMask',
    'portFunction',
    'reserved',
]
struct_xl_daio_set_port._fields_ = [
    ('portType', c_uint),
    ('portMask', c_uint),
    ('portFunction', c_uint * int(8)),
    ('reserved', c_uint * int(8)),
]

XLdaioSetPort = struct_xl_daio_set_port# vxlapi.h: 2742

# vxlapi.h: 2769
class struct_xl_daio_digital_params(Structure):
    pass

struct_xl_daio_digital_params._pack_ = 8
struct_xl_daio_digital_params.__slots__ = [
    'portMask',
    'valueMask',
]
struct_xl_daio_digital_params._fields_ = [
    ('portMask', c_uint),
    ('valueMask', c_uint),
]

XLdaioDigitalParams = struct_xl_daio_digital_params# vxlapi.h: 2769

# vxlapi.h: 2786
class struct_xl_daio_analog_params(Structure):
    pass

struct_xl_daio_analog_params._pack_ = 8
struct_xl_daio_analog_params.__slots__ = [
    'portMask',
    'value',
]
struct_xl_daio_analog_params._fields_ = [
    ('portMask', c_uint),
    ('value', c_uint * int(8)),
]

XLdaioAnalogParams = struct_xl_daio_analog_params# vxlapi.h: 2786

# vxlapi.h: 2825
class struct_s_xl_kline_uart_params(Structure):
    pass

struct_s_xl_kline_uart_params._pack_ = 8
struct_s_xl_kline_uart_params.__slots__ = [
    'databits',
    'stopbits',
    'parity',
]
struct_s_xl_kline_uart_params._fields_ = [
    ('databits', c_uint),
    ('stopbits', c_uint),
    ('parity', c_uint),
]

XLklineUartParameter = struct_s_xl_kline_uart_params# vxlapi.h: 2825

# vxlapi.h: 2833
class struct_s_xl_kline_init_tester(Structure):
    pass

struct_s_xl_kline_init_tester._pack_ = 8
struct_s_xl_kline_init_tester.__slots__ = [
    'TiniL',
    'Twup',
    'reserved',
]
struct_s_xl_kline_init_tester._fields_ = [
    ('TiniL', c_uint),
    ('Twup', c_uint),
    ('reserved', c_uint),
]

XLklineInitTester = struct_s_xl_kline_init_tester# vxlapi.h: 2833

# vxlapi.h: 2851
class struct_s_xl_kline_init_5BdTester(Structure):
    pass

struct_s_xl_kline_init_5BdTester._pack_ = 8
struct_s_xl_kline_init_5BdTester.__slots__ = [
    'addr',
    'rate5bd',
    'W1min',
    'W1max',
    'W2min',
    'W2max',
    'W3min',
    'W3max',
    'W4',
    'W4min',
    'W4max',
    'kb2Not',
    'reserved',
]
struct_s_xl_kline_init_5BdTester._fields_ = [
    ('addr', c_uint),
    ('rate5bd', c_uint),
    ('W1min', c_uint),
    ('W1max', c_uint),
    ('W2min', c_uint),
    ('W2max', c_uint),
    ('W3min', c_uint),
    ('W3max', c_uint),
    ('W4', c_uint),
    ('W4min', c_uint),
    ('W4max', c_uint),
    ('kb2Not', c_uint),
    ('reserved', c_uint),
]

XLkline5BdTester = struct_s_xl_kline_init_5BdTester# vxlapi.h: 2851

# vxlapi.h: 2870
class struct_s_xl_kline_init_5BdEcu(Structure):
    pass

struct_s_xl_kline_init_5BdEcu._pack_ = 8
struct_s_xl_kline_init_5BdEcu.__slots__ = [
    'configure',
    'addr',
    'rate5bd',
    'syncPattern',
    'W1',
    'W2',
    'W3',
    'W4',
    'W4min',
    'W4max',
    'kb1',
    'kb2',
    'addrNot',
    'reserved',
]
struct_s_xl_kline_init_5BdEcu._fields_ = [
    ('configure', c_uint),
    ('addr', c_uint),
    ('rate5bd', c_uint),
    ('syncPattern', c_uint),
    ('W1', c_uint),
    ('W2', c_uint),
    ('W3', c_uint),
    ('W4', c_uint),
    ('W4min', c_uint),
    ('W4max', c_uint),
    ('kb1', c_uint),
    ('kb2', c_uint),
    ('addrNot', c_uint),
    ('reserved', c_uint),
]

XLkline5BdEcu = struct_s_xl_kline_init_5BdEcu# vxlapi.h: 2870

# vxlapi.h: 2878
class struct_s_xl_kline_set_com_tester(Structure):
    pass

struct_s_xl_kline_set_com_tester._pack_ = 8
struct_s_xl_kline_set_com_tester.__slots__ = [
    'P1min',
    'P4',
    'reserved',
]
struct_s_xl_kline_set_com_tester._fields_ = [
    ('P1min', c_uint),
    ('P4', c_uint),
    ('reserved', c_uint),
]

XLklineSetComTester = struct_s_xl_kline_set_com_tester# vxlapi.h: 2878

# vxlapi.h: 2890
class struct_s_xl_kline_set_com_ecu(Structure):
    pass

struct_s_xl_kline_set_com_ecu._pack_ = 8
struct_s_xl_kline_set_com_ecu.__slots__ = [
    'P1',
    'P4min',
    'TinilMin',
    'TinilMax',
    'TwupMin',
    'TwupMax',
    'reserved',
]
struct_s_xl_kline_set_com_ecu._fields_ = [
    ('P1', c_uint),
    ('P4min', c_uint),
    ('TinilMin', c_uint),
    ('TinilMax', c_uint),
    ('TwupMin', c_uint),
    ('TwupMax', c_uint),
    ('reserved', c_uint),
]

XLklineSetComEcu = struct_s_xl_kline_set_com_ecu# vxlapi.h: 2890

XLnetworkId = c_int# vxlapi.h: 3195

pXLnetworkId = POINTER(c_int)# vxlapi.h: 3195

XLswitchId = c_int# vxlapi.h: 3197

pXLswitchId = POINTER(c_int)# vxlapi.h: 3197

XLnetworkHandle = XLlong# vxlapi.h: 3199

pXLnetworkHandle = POINTER(XLlong)# vxlapi.h: 3199

XLethPortHandle = XLlong# vxlapi.h: 3201

pXLethPortHandle = POINTER(XLlong)# vxlapi.h: 3201

XLrxHandle = XLlong# vxlapi.h: 3203

pXLrxHandle = POINTER(XLlong)# vxlapi.h: 3203

enum_e_xl_timesync_clock_uuid_format = c_int# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_UNDEFINED = 0# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_VECTOR_DEV = (XL_TS_CLK_UUID_FORMAT_UNDEFINED + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_EUI64 = (XL_TS_CLK_UUID_FORMAT_VECTOR_DEV + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_LOCAL_PC = (XL_TS_CLK_UUID_FORMAT_EUI64 + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_VECTOR_PC = (XL_TS_CLK_UUID_FORMAT_LOCAL_PC + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_STANDARD_PC = (XL_TS_CLK_UUID_FORMAT_VECTOR_PC + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_PERFORMANCE_CNT = (XL_TS_CLK_UUID_FORMAT_STANDARD_PC + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_EXTERNAL = (XL_TS_CLK_UUID_FORMAT_PERFORMANCE_CNT + 1)# vxlapi.h: 3228

XL_TS_CLK_UUID_FORMAT_GPTP = (XL_TS_CLK_UUID_FORMAT_EXTERNAL + 1)# vxlapi.h: 3228

T_XL_TIMESYNC_CLK_UUID_FORMAT = enum_e_xl_timesync_clock_uuid_format# vxlapi.h: 3228

XLtsClkUuidFormat = T_XL_TIMESYNC_CLK_UUID_FORMAT# vxlapi.h: 3230

enum_e_xl_timesync_time_scale = c_int# vxlapi.h: 3239

XL_TS_TIMESCALE_UNDEFINED = 0# vxlapi.h: 3239

XL_TS_TIMESCALE_UTC = (XL_TS_TIMESCALE_UNDEFINED + 1)# vxlapi.h: 3239

XL_TS_TIMESCALE_TAI = (XL_TS_TIMESCALE_UTC + 1)# vxlapi.h: 3239

XL_TS_TIMESCALE_PERFORMANCE_COUNTER = (XL_TS_TIMESCALE_TAI + 1)# vxlapi.h: 3239

XL_TS_TIMESCALE_ARBITRARY = (XL_TS_TIMESCALE_PERFORMANCE_COUNTER + 1)# vxlapi.h: 3239

XL_TS_TIMESCALE_RTC = (XL_TS_TIMESCALE_ARBITRARY + 1)# vxlapi.h: 3239

XLtsTimeScale = enum_e_xl_timesync_time_scale# vxlapi.h: 3239

enum_e_xl_timesync_clk_external_type = c_int# vxlapi.h: 3244

XL_TS_CLK_EXTTYPE_NONE = 0# vxlapi.h: 3244

XL_TS_CLK_EXTTYPE_DOMAIN = 4# vxlapi.h: 3244

XLtsClkExternalType = enum_e_xl_timesync_clk_external_type# vxlapi.h: 3244

# vxlapi.h: 3249
class struct_s_xl_timesync_leap_seconds(Structure):
    pass

struct_s_xl_timesync_leap_seconds._pack_ = 4
struct_s_xl_timesync_leap_seconds.__slots__ = [
    'leapSecondsFlags',
    'leapSecondsValue',
]
struct_s_xl_timesync_leap_seconds._fields_ = [
    ('leapSecondsFlags', c_uint),
    ('leapSecondsValue', c_int),
]

XLtsLeapSeconds = struct_s_xl_timesync_leap_seconds# vxlapi.h: 3249

# vxlapi.h: 3255
class struct_anon_20(Structure):
    pass

struct_anon_20._pack_ = 4
struct_anon_20.__slots__ = [
    'articleNumber',
    'serialNumber',
    'clkId',
]
struct_anon_20._fields_ = [
    ('articleNumber', c_uint),
    ('serialNumber', c_uint),
    ('clkId', c_uint),
]

# vxlapi.h: 3261
class struct_anon_21(Structure):
    pass

struct_anon_21._pack_ = 4
struct_anon_21.__slots__ = [
    'oui',
    'extensionId',
]
struct_anon_21._fields_ = [
    ('oui', c_ubyte * int(3)),
    ('extensionId', c_ubyte * int(5)),
]

# vxlapi.h: 3254
class union_anon_22(Union):
    pass

union_anon_22._pack_ = 4
union_anon_22.__slots__ = [
    'vectorDevUuid',
    'eui64Uuid',
    'raw',
]
union_anon_22._fields_ = [
    ('vectorDevUuid', struct_anon_20),
    ('eui64Uuid', struct_anon_21),
    ('raw', c_uint * int(6)),
]

# vxlapi.h: 3270
class struct_s_xl_timesync_clock_uuid_(Structure):
    pass

struct_s_xl_timesync_clock_uuid_._pack_ = 4
struct_s_xl_timesync_clock_uuid_.__slots__ = [
    'uuidFormat',
    'uuid',
    'reserved',
]
struct_s_xl_timesync_clock_uuid_._fields_ = [
    ('uuidFormat', XLtsClkUuidFormat),
    ('uuid', union_anon_22),
    ('reserved', c_uint * int(4)),
]

XLtsClkUuid = struct_s_xl_timesync_clock_uuid_# vxlapi.h: 3270

# vxlapi.h: 3278
class struct_s_xl_ts_domain_time(Structure):
    pass

struct_s_xl_ts_domain_time._pack_ = 4
struct_s_xl_ts_domain_time.__slots__ = [
    'domainTime',
    'timeScale',
    'leapSeconds',
    'clusterMaster',
    'syncStatus',
]
struct_s_xl_ts_domain_time._fields_ = [
    ('domainTime', XLuint64),
    ('timeScale', XLtsTimeScale),
    ('leapSeconds', XLtsLeapSeconds),
    ('clusterMaster', XLtsClkUuid),
    ('syncStatus', c_uint),
]

XLtsDomainTime = struct_s_xl_ts_domain_time# vxlapi.h: 3278

XLtsClockHandle = c_int# vxlapi.h: 3280

enum_e_xl_timesync_interface_version = c_int# vxlapi.h: 3282

XL_TS_INTERFACE_VERSION_INVL = 0# vxlapi.h: 3282

XL_TS_INTERFACE_VERSION_1 = 1# vxlapi.h: 3282

XLtsInterfaceVersion = enum_e_xl_timesync_interface_version# vxlapi.h: 3282

XLethEventTag = c_ushort# vxlapi.h: 3291

# vxlapi.h: 3297
class struct_s_xl_eth_frame(Structure):
    pass

struct_s_xl_eth_frame._pack_ = 1
struct_s_xl_eth_frame.__slots__ = [
    'etherType',
    'payload',
]
struct_s_xl_eth_frame._fields_ = [
    ('etherType', c_ushort),
    ('payload', c_ubyte * int(1500)),
]

T_XL_ETH_FRAME = struct_s_xl_eth_frame# vxlapi.h: 3297

# vxlapi.h: 3302
class union_s_xl_eth_framedata(Union):
    pass

union_s_xl_eth_framedata._pack_ = 1
union_s_xl_eth_framedata.__slots__ = [
    'rawData',
    'ethFrame',
]
union_s_xl_eth_framedata._fields_ = [
    ('rawData', c_ubyte * int(1600)),
    ('ethFrame', T_XL_ETH_FRAME),
]

T_XL_ETH_FRAMEDATA = union_s_xl_eth_framedata# vxlapi.h: 3302

# vxlapi.h: 3314
class struct_s_xl_eth_dataframe_rx(Structure):
    pass

struct_s_xl_eth_dataframe_rx._pack_ = 1
struct_s_xl_eth_dataframe_rx.__slots__ = [
    'frameIdentifier',
    'frameDuration',
    'dataLen',
    'reserved',
    'reserved2',
    'fcs',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_eth_dataframe_rx._fields_ = [
    ('frameIdentifier', c_uint),
    ('frameDuration', c_uint),
    ('dataLen', c_ushort),
    ('reserved', c_ushort),
    ('reserved2', c_uint * int(3)),
    ('fcs', c_uint),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_ETH_DATAFRAME_RX = struct_s_xl_eth_dataframe_rx# vxlapi.h: 3314

# vxlapi.h: 3327
class struct_s_xl_eth_dataframe_rxerror(Structure):
    pass

struct_s_xl_eth_dataframe_rxerror._pack_ = 1
struct_s_xl_eth_dataframe_rxerror.__slots__ = [
    'frameIdentifier',
    'frameDuration',
    'errorFlags',
    'dataLen',
    'reserved',
    'reserved2',
    'fcs',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_eth_dataframe_rxerror._fields_ = [
    ('frameIdentifier', c_uint),
    ('frameDuration', c_uint),
    ('errorFlags', c_uint),
    ('dataLen', c_ushort),
    ('reserved', c_ushort),
    ('reserved2', c_uint * int(3)),
    ('fcs', c_uint),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_ETH_DATAFRAME_RX_ERROR = struct_s_xl_eth_dataframe_rxerror# vxlapi.h: 3327

# vxlapi.h: 3338
class struct_s_xl_eth_dataframe_tx(Structure):
    pass

struct_s_xl_eth_dataframe_tx._pack_ = 1
struct_s_xl_eth_dataframe_tx.__slots__ = [
    'frameIdentifier',
    'flags',
    'dataLen',
    'reserved',
    'reserved2',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_eth_dataframe_tx._fields_ = [
    ('frameIdentifier', c_uint),
    ('flags', c_uint),
    ('dataLen', c_ushort),
    ('reserved', c_ushort),
    ('reserved2', c_uint * int(4)),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_ETH_DATAFRAME_TX = struct_s_xl_eth_dataframe_tx# vxlapi.h: 3338

# vxlapi.h: 3352
class struct_s_xl_eth_dataframe_tx_event(Structure):
    pass

struct_s_xl_eth_dataframe_tx_event._pack_ = 1
struct_s_xl_eth_dataframe_tx_event.__slots__ = [
    'frameIdentifier',
    'flags',
    'dataLen',
    'reserved',
    'frameDuration',
    'reserved2',
    'fcs',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_eth_dataframe_tx_event._fields_ = [
    ('frameIdentifier', c_uint),
    ('flags', c_uint),
    ('dataLen', c_ushort),
    ('reserved', c_ushort),
    ('frameDuration', c_uint),
    ('reserved2', c_uint * int(2)),
    ('fcs', c_uint),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_ETH_DATAFRAME_TX_EVENT = struct_s_xl_eth_dataframe_tx_event# vxlapi.h: 3352

T_XL_ETH_DATAFRAME_TXACK = T_XL_ETH_DATAFRAME_TX_EVENT# vxlapi.h: 3354

T_XL_ETH_DATAFRAME_TXACK_SW = T_XL_ETH_DATAFRAME_TX_EVENT# vxlapi.h: 3355

T_XL_ETH_DATAFRAME_TXACK_OTHERAPP = T_XL_ETH_DATAFRAME_TX_EVENT# vxlapi.h: 3356

# vxlapi.h: 3361
class struct_s_xl_eth_dataframe_txerror(Structure):
    pass

struct_s_xl_eth_dataframe_txerror._pack_ = 1
struct_s_xl_eth_dataframe_txerror.__slots__ = [
    'errorType',
    'txFrame',
]
struct_s_xl_eth_dataframe_txerror._fields_ = [
    ('errorType', c_uint),
    ('txFrame', T_XL_ETH_DATAFRAME_TX_EVENT),
]

T_XL_ETH_DATAFRAME_TX_ERROR = struct_s_xl_eth_dataframe_txerror# vxlapi.h: 3361

T_XL_ETH_DATAFRAME_TX_ERR_SW = T_XL_ETH_DATAFRAME_TX_ERROR# vxlapi.h: 3363

T_XL_ETH_DATAFRAME_TX_ERR_OTHERAPP = T_XL_ETH_DATAFRAME_TX_ERROR# vxlapi.h: 3364

# vxlapi.h: 3372
class struct_s_xl_eth_config_result(Structure):
    pass

struct_s_xl_eth_config_result._pack_ = 4
struct_s_xl_eth_config_result.__slots__ = [
    'result',
]
struct_s_xl_eth_config_result._fields_ = [
    ('result', c_uint),
]

T_XL_ETH_CONFIG_RESULT = struct_s_xl_eth_config_result# vxlapi.h: 3372

# vxlapi.h: 3383
class struct_s_xl_eth_channel_status(Structure):
    pass

struct_s_xl_eth_channel_status._pack_ = 4
struct_s_xl_eth_channel_status.__slots__ = [
    'link',
    'speed',
    'duplex',
    'mdiType',
    'activeConnector',
    'activePhy',
    'clockMode',
    'brPairs',
]
struct_s_xl_eth_channel_status._fields_ = [
    ('link', c_uint),
    ('speed', c_uint),
    ('duplex', c_uint),
    ('mdiType', c_uint),
    ('activeConnector', c_uint),
    ('activePhy', c_uint),
    ('clockMode', c_uint),
    ('brPairs', c_uint),
]

T_XL_ETH_CHANNEL_STATUS = struct_s_xl_eth_channel_status# vxlapi.h: 3383

# vxlapi.h: 3391
class struct_anon_23(Structure):
    pass

struct_anon_23._pack_ = 4
struct_anon_23.__slots__ = [
    'frameIdentifier',
    'fcs',
    'sourceMAC',
    'reserved',
]
struct_anon_23._fields_ = [
    ('frameIdentifier', c_uint),
    ('fcs', c_uint),
    ('sourceMAC', c_ubyte * int(6)),
    ('reserved', c_ubyte * int(2)),
]

# vxlapi.h: 3398
class struct_anon_24(Structure):
    pass

struct_anon_24._pack_ = 4
struct_anon_24.__slots__ = [
    'errorType',
    'frameIdentifier',
    'fcs',
    'sourceMAC',
    'reserved',
]
struct_anon_24._fields_ = [
    ('errorType', c_uint),
    ('frameIdentifier', c_uint),
    ('fcs', c_uint),
    ('sourceMAC', c_ubyte * int(6)),
    ('reserved', c_ubyte * int(2)),
]

# vxlapi.h: 3390
class union_anon_25(Union):
    pass

union_anon_25._pack_ = 4
union_anon_25.__slots__ = [
    'txAck',
    'txAckSw',
    'txError',
    'txErrorSw',
    'reserved',
]
union_anon_25._fields_ = [
    ('txAck', struct_anon_23),
    ('txAckSw', struct_anon_23),
    ('txError', struct_anon_24),
    ('txErrorSw', struct_anon_24),
    ('reserved', c_uint * int(20)),
]

# vxlapi.h: 3408
class struct_s_xl_eth_lostevent(Structure):
    pass

struct_s_xl_eth_lostevent._pack_ = 4
struct_s_xl_eth_lostevent.__slots__ = [
    'eventTypeLost',
    'reserved',
    'reason',
    'eventInfo',
]
struct_s_xl_eth_lostevent._fields_ = [
    ('eventTypeLost', XLethEventTag),
    ('reserved', c_ushort),
    ('reason', c_uint),
    ('eventInfo', union_anon_25),
]

T_XL_ETH_LOSTEVENT = struct_s_xl_eth_lostevent# vxlapi.h: 3408

# vxlapi.h: 3422
class union_s_xl_eth_tag_data(Union):
    pass

union_s_xl_eth_tag_data._pack_ = 4
union_s_xl_eth_tag_data.__slots__ = [
    'rawData',
    'frameRxOk',
    'frameRxError',
    'frameTxAck',
    'frameTxAckSw',
    'frameTxAckOtherApp',
    'frameTxError',
    'frameTxErrorSw',
    'frameTxErrorOtherApp',
    'configResult',
    'channelStatus',
    'syncPulse',
    'lostEvent',
]
union_s_xl_eth_tag_data._fields_ = [
    ('rawData', c_ubyte * int(2048)),
    ('frameRxOk', T_XL_ETH_DATAFRAME_RX),
    ('frameRxError', T_XL_ETH_DATAFRAME_RX_ERROR),
    ('frameTxAck', T_XL_ETH_DATAFRAME_TXACK),
    ('frameTxAckSw', T_XL_ETH_DATAFRAME_TXACK_SW),
    ('frameTxAckOtherApp', T_XL_ETH_DATAFRAME_TXACK_OTHERAPP),
    ('frameTxError', T_XL_ETH_DATAFRAME_TX_ERROR),
    ('frameTxErrorSw', T_XL_ETH_DATAFRAME_TX_ERR_SW),
    ('frameTxErrorOtherApp', T_XL_ETH_DATAFRAME_TX_ERR_OTHERAPP),
    ('configResult', T_XL_ETH_CONFIG_RESULT),
    ('channelStatus', T_XL_ETH_CHANNEL_STATUS),
    ('syncPulse', XL_SYNC_PULSE_EV),
    ('lostEvent', T_XL_ETH_LOSTEVENT),
]

# vxlapi.h: 3442
class struct_s_xl_eth_event(Structure):
    pass

struct_s_xl_eth_event._pack_ = 4
struct_s_xl_eth_event.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved',
    'reserved1',
    'timeStampSync',
    'tagData',
]
struct_s_xl_eth_event._fields_ = [
    ('size', c_uint),
    ('tag', XLethEventTag),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved', c_ushort),
    ('reserved1', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_s_xl_eth_tag_data),
]

T_XL_ETH_EVENT = struct_s_xl_eth_event# vxlapi.h: 3442

# vxlapi.h: 3459
class struct_s_xl_net_eth_dataframe_rx(Structure):
    pass

struct_s_xl_net_eth_dataframe_rx._pack_ = 4
struct_s_xl_net_eth_dataframe_rx.__slots__ = [
    'frameDuration',
    'dataLen',
    'reserved1',
    'reserved2',
    'errorFlags',
    'reserved3',
    'fcs',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_net_eth_dataframe_rx._fields_ = [
    ('frameDuration', c_uint),
    ('dataLen', c_ushort),
    ('reserved1', c_ubyte),
    ('reserved2', c_ubyte),
    ('errorFlags', c_uint),
    ('reserved3', c_uint),
    ('fcs', c_uint),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_NET_ETH_DATAFRAME_RX = struct_s_xl_net_eth_dataframe_rx# vxlapi.h: 3459

# vxlapi.h: 3472
class struct_s_xl_net_eth_dataframe_rx_error(Structure):
    pass

struct_s_xl_net_eth_dataframe_rx_error._pack_ = 4
struct_s_xl_net_eth_dataframe_rx_error.__slots__ = [
    'frameDuration',
    'errorFlags',
    'dataLen',
    'reserved1',
    'reserved2',
    'reserved3',
    'fcs',
    'destMAC',
    'sourceMAC',
    'frameData',
]
struct_s_xl_net_eth_dataframe_rx_error._fields_ = [
    ('frameDuration', c_uint),
    ('errorFlags', c_uint),
    ('dataLen', c_ushort),
    ('reserved1', c_ubyte),
    ('reserved2', c_ubyte),
    ('reserved3', c_uint * int(2)),
    ('fcs', c_uint),
    ('destMAC', c_ubyte * int(6)),
    ('sourceMAC', c_ubyte * int(6)),
    ('frameData', T_XL_ETH_FRAMEDATA),
]

T_XL_NET_ETH_DATAFRAME_RX_ERROR = struct_s_xl_net_eth_dataframe_rx_error# vxlapi.h: 3472

T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ACK = T_XL_NET_ETH_DATAFRAME_RX# vxlapi.h: 3476

T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ERROR = T_XL_NET_ETH_DATAFRAME_RX_ERROR# vxlapi.h: 3477

T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX = T_XL_NET_ETH_DATAFRAME_RX# vxlapi.h: 3478

T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX_ERROR = T_XL_NET_ETH_DATAFRAME_RX_ERROR# vxlapi.h: 3479

T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX = T_XL_NET_ETH_DATAFRAME_RX# vxlapi.h: 3480

T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX_ERROR = T_XL_NET_ETH_DATAFRAME_RX_ERROR# vxlapi.h: 3481

T_XL_NET_ETH_DATAFRAME_TX = T_XL_ETH_DATAFRAME_TX# vxlapi.h: 3484

T_XL_NET_ETH_CHANNEL_STATUS = T_XL_ETH_CHANNEL_STATUS# vxlapi.h: 3487

# vxlapi.h: 3504
class union_s_xl_eth_net_tag_data(Union):
    pass

union_s_xl_eth_net_tag_data._pack_ = 4
union_s_xl_eth_net_tag_data.__slots__ = [
    'rawData',
    'frameSimRx',
    'frameSimRxError',
    'frameSimTxAck',
    'frameSimTxError',
    'frameMeasureRx',
    'frameMeasureRxError',
    'frameMeasureTx',
    'frameMeasureTxError',
    'channelStatus',
]
union_s_xl_eth_net_tag_data._fields_ = [
    ('rawData', c_ubyte * int(2048)),
    ('frameSimRx', T_XL_NET_ETH_DATAFRAME_RX),
    ('frameSimRxError', T_XL_NET_ETH_DATAFRAME_RX_ERROR),
    ('frameSimTxAck', T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ACK),
    ('frameSimTxError', T_XL_NET_ETH_DATAFRAME_SIMULATION_TX_ERROR),
    ('frameMeasureRx', T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX),
    ('frameMeasureRxError', T_XL_NET_ETH_DATAFRAME_MEASUREMENT_RX_ERROR),
    ('frameMeasureTx', T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX),
    ('frameMeasureTxError', T_XL_NET_ETH_DATAFRAME_MEASUREMENT_TX_ERROR),
    ('channelStatus', T_XL_NET_ETH_CHANNEL_STATUS),
]

# vxlapi.h: 3516
class struct_s_xl_net_eth_event(Structure):
    pass

struct_s_xl_net_eth_event._pack_ = 4
struct_s_xl_net_eth_event.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved',
    'reserved1',
    'timeStampSync',
    'tagData',
]
struct_s_xl_net_eth_event._fields_ = [
    ('size', c_uint),
    ('tag', XLethEventTag),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved', c_ushort),
    ('reserved1', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_s_xl_eth_net_tag_data),
]

T_XL_NET_ETH_EVENT = struct_s_xl_net_eth_event# vxlapi.h: 3516

# vxlapi.h: 3527
class struct_anon_26(Structure):
    pass

struct_anon_26._pack_ = 4
struct_anon_26.__slots__ = [
    'speed',
    'duplex',
    'connector',
    'phy',
    'clockMode',
    'mdiMode',
    'brPairs',
]
struct_anon_26._fields_ = [
    ('speed', c_uint),
    ('duplex', c_uint),
    ('connector', c_uint),
    ('phy', c_uint),
    ('clockMode', c_uint),
    ('mdiMode', c_uint),
    ('brPairs', c_uint),
]

T_XL_ETH_CONFIG = struct_anon_26# vxlapi.h: 3527

# vxlapi.h: 3535
class struct_anon_27(Structure):
    pass

struct_anon_27._pack_ = 4
struct_anon_27.__slots__ = [
    'address',
]
struct_anon_27._fields_ = [
    ('address', c_ubyte * int(6)),
]

T_XL_ETH_MAC_ADDRESS = struct_anon_27# vxlapi.h: 3535

XLmostEventTag = c_ushort# vxlapi.h: 3893

# vxlapi.h: 3898
class struct_s_xl_most150_event_source(Structure):
    pass

struct_s_xl_most150_event_source._pack_ = 1
struct_s_xl_most150_event_source.__slots__ = [
    'sourceMask',
]
struct_s_xl_most150_event_source._fields_ = [
    ('sourceMask', c_uint),
]

XL_MOST150_EVENT_SOURCE_EV = struct_s_xl_most150_event_source# vxlapi.h: 3898

# vxlapi.h: 3902
class struct_s_xl_most150_device_mode(Structure):
    pass

struct_s_xl_most150_device_mode._pack_ = 1
struct_s_xl_most150_device_mode.__slots__ = [
    'deviceMode',
]
struct_s_xl_most150_device_mode._fields_ = [
    ('deviceMode', c_uint),
]

XL_MOST150_DEVICE_MODE_EV = struct_s_xl_most150_device_mode# vxlapi.h: 3902

# vxlapi.h: 3906
class struct_s_xl_most150_frequency(Structure):
    pass

struct_s_xl_most150_frequency._pack_ = 1
struct_s_xl_most150_frequency.__slots__ = [
    'frequency',
]
struct_s_xl_most150_frequency._fields_ = [
    ('frequency', c_uint),
]

XL_MOST150_FREQUENCY_EV = struct_s_xl_most150_frequency# vxlapi.h: 3906

# vxlapi.h: 3926
class struct_s_xl_most150_special_node_info(Structure):
    pass

struct_s_xl_most150_special_node_info._pack_ = 1
struct_s_xl_most150_special_node_info.__slots__ = [
    'changeMask',
    'nodeAddress',
    'groupAddress',
    'npr',
    'mpr',
    'sbc',
    'ctrlRetryTime',
    'ctrlSendAttempts',
    'asyncRetryTime',
    'asyncSendAttempts',
    'macAddr',
    'nprSpy',
    'mprSpy',
    'sbcSpy',
    'inicNIState',
    'reserved1',
    'reserved2',
]
struct_s_xl_most150_special_node_info._fields_ = [
    ('changeMask', c_uint),
    ('nodeAddress', c_ushort),
    ('groupAddress', c_ushort),
    ('npr', c_ubyte),
    ('mpr', c_ubyte),
    ('sbc', c_ubyte),
    ('ctrlRetryTime', c_ubyte),
    ('ctrlSendAttempts', c_ubyte),
    ('asyncRetryTime', c_ubyte),
    ('asyncSendAttempts', c_ubyte),
    ('macAddr', c_ubyte * int(6)),
    ('nprSpy', c_ubyte),
    ('mprSpy', c_ubyte),
    ('sbcSpy', c_ubyte),
    ('inicNIState', c_ubyte),
    ('reserved1', c_ubyte * int(3)),
    ('reserved2', c_uint * int(3)),
]

XL_MOST150_SPECIAL_NODE_INFO_EV = struct_s_xl_most150_special_node_info# vxlapi.h: 3926

# vxlapi.h: 3938
class struct_s_xl_most150_ctrl_rx(Structure):
    pass

struct_s_xl_most150_ctrl_rx._pack_ = 1
struct_s_xl_most150_ctrl_rx.__slots__ = [
    'targetAddress',
    'sourceAddress',
    'fblockId',
    'instId',
    'functionId',
    'opType',
    'telId',
    'telLen',
    'ctrlData',
]
struct_s_xl_most150_ctrl_rx._fields_ = [
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('fblockId', c_ubyte),
    ('instId', c_ubyte),
    ('functionId', c_ushort),
    ('opType', c_ubyte),
    ('telId', c_ubyte),
    ('telLen', c_ushort),
    ('ctrlData', c_ubyte * int(45)),
]

XL_MOST150_CTRL_RX_EV = struct_s_xl_most150_ctrl_rx# vxlapi.h: 3938

# vxlapi.h: 3959
class struct_s_xl_most150_ctrl_spy(Structure):
    pass

struct_s_xl_most150_ctrl_spy._pack_ = 1
struct_s_xl_most150_ctrl_spy.__slots__ = [
    'frameCount',
    'msgDuration',
    'priority',
    'targetAddress',
    'pAck',
    'ctrlDataLenAnnounced',
    'reserved0',
    'pIndex',
    'sourceAddress',
    'reserved1',
    'crc',
    'crcCalculated',
    'cAck',
    'ctrlDataLen',
    'reserved2',
    'status',
    'validMask',
    'ctrlData',
]
struct_s_xl_most150_ctrl_spy._fields_ = [
    ('frameCount', c_uint),
    ('msgDuration', c_uint),
    ('priority', c_ubyte),
    ('targetAddress', c_ushort),
    ('pAck', c_ubyte),
    ('ctrlDataLenAnnounced', c_ushort),
    ('reserved0', c_ubyte),
    ('pIndex', c_ubyte),
    ('sourceAddress', c_ushort),
    ('reserved1', c_ushort),
    ('crc', c_ushort),
    ('crcCalculated', c_ushort),
    ('cAck', c_ubyte),
    ('ctrlDataLen', c_ushort),
    ('reserved2', c_ubyte),
    ('status', c_uint),
    ('validMask', c_uint),
    ('ctrlData', c_ubyte * int(51)),
]

XL_MOST150_CTRL_SPY_EV = struct_s_xl_most150_ctrl_spy# vxlapi.h: 3959

# vxlapi.h: 3966
class struct_s_xl_most150_async_rx_msg(Structure):
    pass

struct_s_xl_most150_async_rx_msg._pack_ = 1
struct_s_xl_most150_async_rx_msg.__slots__ = [
    'length',
    'targetAddress',
    'sourceAddress',
    'asyncData',
]
struct_s_xl_most150_async_rx_msg._fields_ = [
    ('length', c_ushort),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('asyncData', c_ubyte * int(1524)),
]

XL_MOST150_ASYNC_RX_EV = struct_s_xl_most150_async_rx_msg# vxlapi.h: 3966

# vxlapi.h: 3984
class struct_s_xl_most150_async_spy_msg(Structure):
    pass

struct_s_xl_most150_async_spy_msg._pack_ = 1
struct_s_xl_most150_async_spy_msg.__slots__ = [
    'frameCount',
    'pktDuration',
    'asyncDataLenAnnounced',
    'targetAddress',
    'pAck',
    'pIndex',
    'sourceAddress',
    'crc',
    'crcCalculated',
    'cAck',
    'asyncDataLen',
    'reserved',
    'status',
    'validMask',
    'asyncData',
]
struct_s_xl_most150_async_spy_msg._fields_ = [
    ('frameCount', c_uint),
    ('pktDuration', c_uint),
    ('asyncDataLenAnnounced', c_ushort),
    ('targetAddress', c_ushort),
    ('pAck', c_ubyte),
    ('pIndex', c_ubyte),
    ('sourceAddress', c_ushort),
    ('crc', c_uint),
    ('crcCalculated', c_uint),
    ('cAck', c_ubyte),
    ('asyncDataLen', c_ushort),
    ('reserved', c_ubyte),
    ('status', c_uint),
    ('validMask', c_uint),
    ('asyncData', c_ubyte * int(1524)),
]

XL_MOST150_ASYNC_SPY_EV = struct_s_xl_most150_async_spy_msg# vxlapi.h: 3984

# vxlapi.h: 3991
class struct_s_xl_most150_ethernet_rx(Structure):
    pass

struct_s_xl_most150_ethernet_rx._pack_ = 1
struct_s_xl_most150_ethernet_rx.__slots__ = [
    'sourceAddress',
    'targetAddress',
    'length',
    'ethernetData',
]
struct_s_xl_most150_ethernet_rx._fields_ = [
    ('sourceAddress', c_ubyte * int(6)),
    ('targetAddress', c_ubyte * int(6)),
    ('length', c_uint),
    ('ethernetData', c_ubyte * int(1510)),
]

XL_MOST150_ETHERNET_RX_EV = struct_s_xl_most150_ethernet_rx# vxlapi.h: 3991

# vxlapi.h: 4009
class struct_s_xl_most150_ethernet_spy(Structure):
    pass

struct_s_xl_most150_ethernet_spy._pack_ = 1
struct_s_xl_most150_ethernet_spy.__slots__ = [
    'frameCount',
    'pktDuration',
    'ethernetDataLenAnnounced',
    'targetAddress',
    'pAck',
    'sourceAddress',
    'reserved0',
    'crc',
    'crcCalculated',
    'cAck',
    'ethernetDataLen',
    'reserved1',
    'status',
    'validMask',
    'ethernetData',
]
struct_s_xl_most150_ethernet_spy._fields_ = [
    ('frameCount', c_uint),
    ('pktDuration', c_uint),
    ('ethernetDataLenAnnounced', c_ushort),
    ('targetAddress', c_ubyte * int(6)),
    ('pAck', c_ubyte),
    ('sourceAddress', c_ubyte * int(6)),
    ('reserved0', c_ubyte),
    ('crc', c_uint),
    ('crcCalculated', c_uint),
    ('cAck', c_ubyte),
    ('ethernetDataLen', c_ushort),
    ('reserved1', c_ubyte),
    ('status', c_uint),
    ('validMask', c_uint),
    ('ethernetData', c_ubyte * int(1506)),
]

XL_MOST150_ETHERNET_SPY_EV = struct_s_xl_most150_ethernet_spy# vxlapi.h: 4009

# vxlapi.h: 4014
class struct_s_xl_most150_cl_info(Structure):
    pass

struct_s_xl_most150_cl_info._pack_ = 1
struct_s_xl_most150_cl_info.__slots__ = [
    'label',
    'channelWidth',
]
struct_s_xl_most150_cl_info._fields_ = [
    ('label', c_ushort),
    ('channelWidth', c_ushort),
]

XL_MOST150_CL_INFO = struct_s_xl_most150_cl_info# vxlapi.h: 4014

# vxlapi.h: 4018
class struct_s_xl_most150_sync_alloc_info(Structure):
    pass

struct_s_xl_most150_sync_alloc_info._pack_ = 1
struct_s_xl_most150_sync_alloc_info.__slots__ = [
    'allocTable',
]
struct_s_xl_most150_sync_alloc_info._fields_ = [
    ('allocTable', XL_MOST150_CL_INFO * int(372)),
]

XL_MOST150_SYNC_ALLOC_INFO_EV = struct_s_xl_most150_sync_alloc_info# vxlapi.h: 4018

# vxlapi.h: 4024
class struct_s_xl_most150_sync_volume_status(Structure):
    pass

struct_s_xl_most150_sync_volume_status._pack_ = 1
struct_s_xl_most150_sync_volume_status.__slots__ = [
    'device',
    'volume',
]
struct_s_xl_most150_sync_volume_status._fields_ = [
    ('device', c_uint),
    ('volume', c_uint),
]

XL_MOST150_SYNC_VOLUME_STATUS_EV = struct_s_xl_most150_sync_volume_status# vxlapi.h: 4024

# vxlapi.h: 4028
class struct_s_xl_most150_tx_light(Structure):
    pass

struct_s_xl_most150_tx_light._pack_ = 1
struct_s_xl_most150_tx_light.__slots__ = [
    'light',
]
struct_s_xl_most150_tx_light._fields_ = [
    ('light', c_uint),
]

XL_MOST150_TX_LIGHT_EV = struct_s_xl_most150_tx_light# vxlapi.h: 4028

# vxlapi.h: 4032
class struct_s_xl_most150_rx_light_lock_status(Structure):
    pass

struct_s_xl_most150_rx_light_lock_status._pack_ = 1
struct_s_xl_most150_rx_light_lock_status.__slots__ = [
    'status',
]
struct_s_xl_most150_rx_light_lock_status._fields_ = [
    ('status', c_uint),
]

XL_MOST150_RXLIGHT_LOCKSTATUS_EV = struct_s_xl_most150_rx_light_lock_status# vxlapi.h: 4032

# vxlapi.h: 4037
class struct_s_xl_most150_error(Structure):
    pass

struct_s_xl_most150_error._pack_ = 1
struct_s_xl_most150_error.__slots__ = [
    'errorCode',
    'parameter',
]
struct_s_xl_most150_error._fields_ = [
    ('errorCode', c_uint),
    ('parameter', c_uint * int(3)),
]

XL_MOST150_ERROR_EV = struct_s_xl_most150_error# vxlapi.h: 4037

# vxlapi.h: 4042
class struct_s_xl_most150_configure_rx_buffer(Structure):
    pass

struct_s_xl_most150_configure_rx_buffer._pack_ = 1
struct_s_xl_most150_configure_rx_buffer.__slots__ = [
    'bufferType',
    'bufferMode',
]
struct_s_xl_most150_configure_rx_buffer._fields_ = [
    ('bufferType', c_uint),
    ('bufferMode', c_uint),
]

XL_MOST150_CONFIGURE_RX_BUFFER_EV = struct_s_xl_most150_configure_rx_buffer# vxlapi.h: 4042

# vxlapi.h: 4049
class struct_s_xl_most150_ctrl_sync_audio(Structure):
    pass

struct_s_xl_most150_ctrl_sync_audio._pack_ = 1
struct_s_xl_most150_ctrl_sync_audio.__slots__ = [
    'label',
    'width',
    'device',
    'mode',
]
struct_s_xl_most150_ctrl_sync_audio._fields_ = [
    ('label', c_uint),
    ('width', c_uint),
    ('device', c_uint),
    ('mode', c_uint),
]

XL_MOST150_CTRL_SYNC_AUDIO_EV = struct_s_xl_most150_ctrl_sync_audio# vxlapi.h: 4049

# vxlapi.h: 4054
class struct_s_xl_most150_sync_mute_status(Structure):
    pass

struct_s_xl_most150_sync_mute_status._pack_ = 1
struct_s_xl_most150_sync_mute_status.__slots__ = [
    'device',
    'mute',
]
struct_s_xl_most150_sync_mute_status._fields_ = [
    ('device', c_uint),
    ('mute', c_uint),
]

XL_MOST150_SYNC_MUTE_STATUS_EV = struct_s_xl_most150_sync_mute_status# vxlapi.h: 4054

# vxlapi.h: 4058
class struct_s_xl_most150_tx_light_power(Structure):
    pass

struct_s_xl_most150_tx_light_power._pack_ = 1
struct_s_xl_most150_tx_light_power.__slots__ = [
    'lightPower',
]
struct_s_xl_most150_tx_light_power._fields_ = [
    ('lightPower', c_uint),
]

XL_MOST150_LIGHT_POWER_EV = struct_s_xl_most150_tx_light_power# vxlapi.h: 4058

# vxlapi.h: 4062
class struct_s_xl_most150_gen_light_error(Structure):
    pass

struct_s_xl_most150_gen_light_error._pack_ = 1
struct_s_xl_most150_gen_light_error.__slots__ = [
    'stressStarted',
]
struct_s_xl_most150_gen_light_error._fields_ = [
    ('stressStarted', c_uint),
]

XL_MOST150_GEN_LIGHT_ERROR_EV = struct_s_xl_most150_gen_light_error# vxlapi.h: 4062

# vxlapi.h: 4066
class struct_s_xl_most150_gen_lock_error(Structure):
    pass

struct_s_xl_most150_gen_lock_error._pack_ = 1
struct_s_xl_most150_gen_lock_error.__slots__ = [
    'stressStarted',
]
struct_s_xl_most150_gen_lock_error._fields_ = [
    ('stressStarted', c_uint),
]

XL_MOST150_GEN_LOCK_ERROR_EV = struct_s_xl_most150_gen_lock_error# vxlapi.h: 4066

# vxlapi.h: 4070
class struct_s_xl_most150_ctrl_busload(Structure):
    pass

struct_s_xl_most150_ctrl_busload._pack_ = 1
struct_s_xl_most150_ctrl_busload.__slots__ = [
    'busloadStarted',
]
struct_s_xl_most150_ctrl_busload._fields_ = [
    ('busloadStarted', c_uint),
]

XL_MOST150_CTRL_BUSLOAD_EV = struct_s_xl_most150_ctrl_busload# vxlapi.h: 4070

# vxlapi.h: 4074
class struct_s_xl_most150_async_busload(Structure):
    pass

struct_s_xl_most150_async_busload._pack_ = 1
struct_s_xl_most150_async_busload.__slots__ = [
    'busloadStarted',
]
struct_s_xl_most150_async_busload._fields_ = [
    ('busloadStarted', c_uint),
]

XL_MOST150_ASYNC_BUSLOAD_EV = struct_s_xl_most150_async_busload# vxlapi.h: 4074

# vxlapi.h: 4078
class struct_s_xl_most150_systemlock_flag(Structure):
    pass

struct_s_xl_most150_systemlock_flag._pack_ = 1
struct_s_xl_most150_systemlock_flag.__slots__ = [
    'state',
]
struct_s_xl_most150_systemlock_flag._fields_ = [
    ('state', c_uint),
]

XL_MOST150_SYSTEMLOCK_FLAG_EV = struct_s_xl_most150_systemlock_flag# vxlapi.h: 4078

# vxlapi.h: 4082
class struct_s_xl_most150_shutdown_flag(Structure):
    pass

struct_s_xl_most150_shutdown_flag._pack_ = 1
struct_s_xl_most150_shutdown_flag.__slots__ = [
    'state',
]
struct_s_xl_most150_shutdown_flag._fields_ = [
    ('state', c_uint),
]

XL_MOST150_SHUTDOWN_FLAG_EV = struct_s_xl_most150_shutdown_flag# vxlapi.h: 4082

# vxlapi.h: 4087
class struct_s_xl_most150_spdif_mode(Structure):
    pass

struct_s_xl_most150_spdif_mode._pack_ = 1
struct_s_xl_most150_spdif_mode.__slots__ = [
    'spdifMode',
    'spdifError',
]
struct_s_xl_most150_spdif_mode._fields_ = [
    ('spdifMode', c_uint),
    ('spdifError', c_uint),
]

XL_MOST150_SPDIF_MODE_EV = struct_s_xl_most150_spdif_mode# vxlapi.h: 4087

# vxlapi.h: 4091
class struct_s_xl_most150_ecl(Structure):
    pass

struct_s_xl_most150_ecl._pack_ = 1
struct_s_xl_most150_ecl.__slots__ = [
    'eclLineState',
]
struct_s_xl_most150_ecl._fields_ = [
    ('eclLineState', c_uint),
]

XL_MOST150_ECL_EV = struct_s_xl_most150_ecl# vxlapi.h: 4091

# vxlapi.h: 4095
class struct_s_xl_most150_ecl_termination(Structure):
    pass

struct_s_xl_most150_ecl_termination._pack_ = 1
struct_s_xl_most150_ecl_termination.__slots__ = [
    'resistorEnabled',
]
struct_s_xl_most150_ecl_termination._fields_ = [
    ('resistorEnabled', c_uint),
]

XL_MOST150_ECL_TERMINATION_EV = struct_s_xl_most150_ecl_termination# vxlapi.h: 4095

# vxlapi.h: 4100
class struct_s_xl_most150_nw_startup(Structure):
    pass

struct_s_xl_most150_nw_startup._pack_ = 1
struct_s_xl_most150_nw_startup.__slots__ = [
    'error',
    'errorInfo',
]
struct_s_xl_most150_nw_startup._fields_ = [
    ('error', c_uint),
    ('errorInfo', c_uint),
]

XL_MOST150_NW_STARTUP_EV = struct_s_xl_most150_nw_startup# vxlapi.h: 4100

# vxlapi.h: 4105
class struct_s_xl_most150_nw_shutdown(Structure):
    pass

struct_s_xl_most150_nw_shutdown._pack_ = 1
struct_s_xl_most150_nw_shutdown.__slots__ = [
    'error',
    'errorInfo',
]
struct_s_xl_most150_nw_shutdown._fields_ = [
    ('error', c_uint),
    ('errorInfo', c_uint),
]

XL_MOST150_NW_SHUTDOWN_EV = struct_s_xl_most150_nw_shutdown# vxlapi.h: 4105

# vxlapi.h: 4111
class struct_s_xl_most150_stream_state(Structure):
    pass

struct_s_xl_most150_stream_state._pack_ = 1
struct_s_xl_most150_stream_state.__slots__ = [
    'streamHandle',
    'streamState',
    'streamError',
]
struct_s_xl_most150_stream_state._fields_ = [
    ('streamHandle', c_uint),
    ('streamState', c_uint),
    ('streamError', c_uint),
]

XL_MOST150_STREAM_STATE_EV = struct_s_xl_most150_stream_state# vxlapi.h: 4111

# vxlapi.h: 4117
class struct_s_xl_most150_stream_tx_buffer(Structure):
    pass

struct_s_xl_most150_stream_tx_buffer._pack_ = 1
struct_s_xl_most150_stream_tx_buffer.__slots__ = [
    'streamHandle',
    'numberOfBytes',
    'status',
]
struct_s_xl_most150_stream_tx_buffer._fields_ = [
    ('streamHandle', c_uint),
    ('numberOfBytes', c_uint),
    ('status', c_uint),
]

XL_MOST150_STREAM_TX_BUFFER_EV = struct_s_xl_most150_stream_tx_buffer# vxlapi.h: 4117

# vxlapi.h: 4124
class struct_s_xl_most150_stream_rx_buffer(Structure):
    pass

struct_s_xl_most150_stream_rx_buffer._pack_ = 1
struct_s_xl_most150_stream_rx_buffer.__slots__ = [
    'streamHandle',
    'numberOfBytes',
    'status',
    'labelInfo',
]
struct_s_xl_most150_stream_rx_buffer._fields_ = [
    ('streamHandle', c_uint),
    ('numberOfBytes', c_uint),
    ('status', c_uint),
    ('labelInfo', c_uint),
]

XL_MOST150_STREAM_RX_BUFFER_EV = struct_s_xl_most150_stream_rx_buffer# vxlapi.h: 4124

# vxlapi.h: 4129
class struct_s_xl_most150_stream_tx_underflow(Structure):
    pass

struct_s_xl_most150_stream_tx_underflow._pack_ = 1
struct_s_xl_most150_stream_tx_underflow.__slots__ = [
    'streamHandle',
    'reserved',
]
struct_s_xl_most150_stream_tx_underflow._fields_ = [
    ('streamHandle', c_uint),
    ('reserved', c_uint),
]

XL_MOST150_STREAM_TX_UNDERFLOW_EV = struct_s_xl_most150_stream_tx_underflow# vxlapi.h: 4129

# vxlapi.h: 4136
class struct_s_xl_most150_stream_tx_label(Structure):
    pass

struct_s_xl_most150_stream_tx_label._pack_ = 1
struct_s_xl_most150_stream_tx_label.__slots__ = [
    'streamHandle',
    'errorInfo',
    'connLabel',
    'width',
]
struct_s_xl_most150_stream_tx_label._fields_ = [
    ('streamHandle', c_uint),
    ('errorInfo', c_uint),
    ('connLabel', c_uint),
    ('width', c_uint),
]

XL_MOST150_STREAM_TX_LABEL_EV = struct_s_xl_most150_stream_tx_label# vxlapi.h: 4136

# vxlapi.h: 4140
class struct_s_xl_most150_gen_bypass_stress(Structure):
    pass

struct_s_xl_most150_gen_bypass_stress._pack_ = 1
struct_s_xl_most150_gen_bypass_stress.__slots__ = [
    'stressStarted',
]
struct_s_xl_most150_gen_bypass_stress._fields_ = [
    ('stressStarted', c_uint),
]

XL_MOST150_GEN_BYPASS_STRESS_EV = struct_s_xl_most150_gen_bypass_stress# vxlapi.h: 4140

# vxlapi.h: 4144
class struct_s_xl_most150_ecl_sequence(Structure):
    pass

struct_s_xl_most150_ecl_sequence._pack_ = 1
struct_s_xl_most150_ecl_sequence.__slots__ = [
    'sequenceStarted',
]
struct_s_xl_most150_ecl_sequence._fields_ = [
    ('sequenceStarted', c_uint),
]

XL_MOST150_ECL_SEQUENCE_EV = struct_s_xl_most150_ecl_sequence# vxlapi.h: 4144

# vxlapi.h: 4148
class struct_s_xl_most150_ecl_glitch_filter(Structure):
    pass

struct_s_xl_most150_ecl_glitch_filter._pack_ = 1
struct_s_xl_most150_ecl_glitch_filter.__slots__ = [
    'duration',
]
struct_s_xl_most150_ecl_glitch_filter._fields_ = [
    ('duration', c_uint),
]

XL_MOST150_ECL_GLITCH_FILTER_EV = struct_s_xl_most150_ecl_glitch_filter# vxlapi.h: 4148

# vxlapi.h: 4152
class struct_s_xl_most150_sso_result(Structure):
    pass

struct_s_xl_most150_sso_result._pack_ = 1
struct_s_xl_most150_sso_result.__slots__ = [
    'status',
]
struct_s_xl_most150_sso_result._fields_ = [
    ('status', c_uint),
]

XL_MOST150_SSO_RESULT_EV = struct_s_xl_most150_sso_result# vxlapi.h: 4152

# vxlapi.h: 4177
class struct_s_xl_most150_ctrl_tx_ack(Structure):
    pass

struct_s_xl_most150_ctrl_tx_ack._pack_ = 1
struct_s_xl_most150_ctrl_tx_ack.__slots__ = [
    'targetAddress',
    'sourceAddress',
    'ctrlPrio',
    'ctrlSendAttempts',
    'reserved',
    'status',
    'ctrlData',
]
struct_s_xl_most150_ctrl_tx_ack._fields_ = [
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('ctrlPrio', c_ubyte),
    ('ctrlSendAttempts', c_ubyte),
    ('reserved', c_ubyte * int(2)),
    ('status', c_uint),
    ('ctrlData', c_ubyte * int(51)),
]

XL_MOST150_CTRL_TX_ACK_EV = struct_s_xl_most150_ctrl_tx_ack# vxlapi.h: 4177

# vxlapi.h: 4187
class struct_s_xl_most150_async_tx_ack(Structure):
    pass

struct_s_xl_most150_async_tx_ack._pack_ = 1
struct_s_xl_most150_async_tx_ack.__slots__ = [
    'priority',
    'asyncSendAttempts',
    'length',
    'targetAddress',
    'sourceAddress',
    'status',
    'asyncData',
]
struct_s_xl_most150_async_tx_ack._fields_ = [
    ('priority', c_ubyte),
    ('asyncSendAttempts', c_ubyte),
    ('length', c_ushort),
    ('targetAddress', c_ushort),
    ('sourceAddress', c_ushort),
    ('status', c_uint),
    ('asyncData', c_ubyte * int(1524)),
]

XL_MOST150_ASYNC_TX_ACK_EV = struct_s_xl_most150_async_tx_ack# vxlapi.h: 4187

# vxlapi.h: 4197
class struct_s_xl_most150_ethernet_tx(Structure):
    pass

struct_s_xl_most150_ethernet_tx._pack_ = 1
struct_s_xl_most150_ethernet_tx.__slots__ = [
    'priority',
    'ethSendAttempts',
    'sourceAddress',
    'targetAddress',
    'reserved',
    'length',
    'ethernetData',
]
struct_s_xl_most150_ethernet_tx._fields_ = [
    ('priority', c_ubyte),
    ('ethSendAttempts', c_ubyte),
    ('sourceAddress', c_ubyte * int(6)),
    ('targetAddress', c_ubyte * int(6)),
    ('reserved', c_ubyte * int(2)),
    ('length', c_uint),
    ('ethernetData', c_ubyte * int(1510)),
]

XL_MOST150_ETHERNET_TX_ACK_EV = struct_s_xl_most150_ethernet_tx# vxlapi.h: 4197

# vxlapi.h: 4201
class struct_s_xl_most150_hw_sync(Structure):
    pass

struct_s_xl_most150_hw_sync._pack_ = 1
struct_s_xl_most150_hw_sync.__slots__ = [
    'pulseCode',
]
struct_s_xl_most150_hw_sync._fields_ = [
    ('pulseCode', c_uint),
]

XL_MOST150_HW_SYNC_EV = struct_s_xl_most150_hw_sync# vxlapi.h: 4201

# vxlapi.h: 4215
class union_anon_28(Union):
    pass

union_anon_28._pack_ = 1
union_anon_28.__slots__ = [
    'rawData',
    'mostEventSource',
    'mostDeviceMode',
    'mostFrequency',
    'mostSpecialNodeInfo',
    'mostCtrlRx',
    'mostCtrlTxAck',
    'mostAsyncSpy',
    'mostAsyncRx',
    'mostSyncAllocInfo',
    'mostSyncVolumeStatus',
    'mostTxLight',
    'mostRxLightLockStatus',
    'mostError',
    'mostConfigureRxBuffer',
    'mostCtrlSyncAudio',
    'mostSyncMuteStatus',
    'mostLightPower',
    'mostGenLightError',
    'mostGenLockError',
    'mostCtrlBusload',
    'mostAsyncBusload',
    'mostEthernetRx',
    'mostSystemLockFlag',
    'mostShutdownFlag',
    'mostSpdifMode',
    'mostEclEvent',
    'mostEclTermination',
    'mostCtrlSpy',
    'mostAsyncTxAck',
    'mostEthernetSpy',
    'mostEthernetTxAck',
    'mostHWSync',
    'mostStartup',
    'mostShutdown',
    'mostStreamState',
    'mostStreamTxBuffer',
    'mostStreamRxBuffer',
    'mostStreamTxUnderflow',
    'mostStreamTxLabel',
    'mostGenBypassStress',
    'mostEclSequence',
    'mostEclGlitchFilter',
    'mostSsoResult',
]
union_anon_28._fields_ = [
    ('rawData', c_ubyte * int(2048)),
    ('mostEventSource', XL_MOST150_EVENT_SOURCE_EV),
    ('mostDeviceMode', XL_MOST150_DEVICE_MODE_EV),
    ('mostFrequency', XL_MOST150_FREQUENCY_EV),
    ('mostSpecialNodeInfo', XL_MOST150_SPECIAL_NODE_INFO_EV),
    ('mostCtrlRx', XL_MOST150_CTRL_RX_EV),
    ('mostCtrlTxAck', XL_MOST150_CTRL_TX_ACK_EV),
    ('mostAsyncSpy', XL_MOST150_ASYNC_SPY_EV),
    ('mostAsyncRx', XL_MOST150_ASYNC_RX_EV),
    ('mostSyncAllocInfo', XL_MOST150_SYNC_ALLOC_INFO_EV),
    ('mostSyncVolumeStatus', XL_MOST150_SYNC_VOLUME_STATUS_EV),
    ('mostTxLight', XL_MOST150_TX_LIGHT_EV),
    ('mostRxLightLockStatus', XL_MOST150_RXLIGHT_LOCKSTATUS_EV),
    ('mostError', XL_MOST150_ERROR_EV),
    ('mostConfigureRxBuffer', XL_MOST150_CONFIGURE_RX_BUFFER_EV),
    ('mostCtrlSyncAudio', XL_MOST150_CTRL_SYNC_AUDIO_EV),
    ('mostSyncMuteStatus', XL_MOST150_SYNC_MUTE_STATUS_EV),
    ('mostLightPower', XL_MOST150_LIGHT_POWER_EV),
    ('mostGenLightError', XL_MOST150_GEN_LIGHT_ERROR_EV),
    ('mostGenLockError', XL_MOST150_GEN_LOCK_ERROR_EV),
    ('mostCtrlBusload', XL_MOST150_CTRL_BUSLOAD_EV),
    ('mostAsyncBusload', XL_MOST150_ASYNC_BUSLOAD_EV),
    ('mostEthernetRx', XL_MOST150_ETHERNET_RX_EV),
    ('mostSystemLockFlag', XL_MOST150_SYSTEMLOCK_FLAG_EV),
    ('mostShutdownFlag', XL_MOST150_SHUTDOWN_FLAG_EV),
    ('mostSpdifMode', XL_MOST150_SPDIF_MODE_EV),
    ('mostEclEvent', XL_MOST150_ECL_EV),
    ('mostEclTermination', XL_MOST150_ECL_TERMINATION_EV),
    ('mostCtrlSpy', XL_MOST150_CTRL_SPY_EV),
    ('mostAsyncTxAck', XL_MOST150_ASYNC_TX_ACK_EV),
    ('mostEthernetSpy', XL_MOST150_ETHERNET_SPY_EV),
    ('mostEthernetTxAck', XL_MOST150_ETHERNET_TX_ACK_EV),
    ('mostHWSync', XL_MOST150_HW_SYNC_EV),
    ('mostStartup', XL_MOST150_NW_STARTUP_EV),
    ('mostShutdown', XL_MOST150_NW_SHUTDOWN_EV),
    ('mostStreamState', XL_MOST150_STREAM_STATE_EV),
    ('mostStreamTxBuffer', XL_MOST150_STREAM_TX_BUFFER_EV),
    ('mostStreamRxBuffer', XL_MOST150_STREAM_RX_BUFFER_EV),
    ('mostStreamTxUnderflow', XL_MOST150_STREAM_TX_UNDERFLOW_EV),
    ('mostStreamTxLabel', XL_MOST150_STREAM_TX_LABEL_EV),
    ('mostGenBypassStress', XL_MOST150_GEN_BYPASS_STRESS_EV),
    ('mostEclSequence', XL_MOST150_ECL_SEQUENCE_EV),
    ('mostEclGlitchFilter', XL_MOST150_ECL_GLITCH_FILTER_EV),
    ('mostSsoResult', XL_MOST150_SSO_RESULT_EV),
]

# vxlapi.h: 4261
class struct_s_xl_event_most150(Structure):
    pass

struct_s_xl_event_most150._pack_ = 1
struct_s_xl_event_most150.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved',
    'timeStamp',
    'timeStampSync',
    'tagData',
]
struct_s_xl_event_most150._fields_ = [
    ('size', c_uint),
    ('tag', XLmostEventTag),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved', c_ushort),
    ('timeStamp', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_anon_28),
]

XLmost150event = struct_s_xl_event_most150# vxlapi.h: 4261

# vxlapi.h: 4278
class struct_s_xl_set_most150_special_node_info(Structure):
    pass

struct_s_xl_set_most150_special_node_info._pack_ = 1
struct_s_xl_set_most150_special_node_info.__slots__ = [
    'changeMask',
    'nodeAddress',
    'groupAddress',
    'sbc',
    'ctrlRetryTime',
    'ctrlSendAttempts',
    'asyncRetryTime',
    'asyncSendAttempts',
    'macAddr',
]
struct_s_xl_set_most150_special_node_info._fields_ = [
    ('changeMask', c_uint),
    ('nodeAddress', c_uint),
    ('groupAddress', c_uint),
    ('sbc', c_uint),
    ('ctrlRetryTime', c_uint),
    ('ctrlSendAttempts', c_uint),
    ('asyncRetryTime', c_uint),
    ('asyncSendAttempts', c_uint),
    ('macAddr', c_ubyte * int(6)),
]

XLmost150SetSpecialNodeInfo = struct_s_xl_set_most150_special_node_info# vxlapi.h: 4278

# vxlapi.h: 4300
class struct_s_xl_most150_ctrl_tx_msg(Structure):
    pass

struct_s_xl_most150_ctrl_tx_msg._pack_ = 1
struct_s_xl_most150_ctrl_tx_msg.__slots__ = [
    'ctrlPrio',
    'ctrlSendAttempts',
    'targetAddress',
    'ctrlData',
]
struct_s_xl_most150_ctrl_tx_msg._fields_ = [
    ('ctrlPrio', c_uint),
    ('ctrlSendAttempts', c_uint),
    ('targetAddress', c_uint),
    ('ctrlData', c_ubyte * int(51)),
]

XLmost150CtrlTxMsg = struct_s_xl_most150_ctrl_tx_msg# vxlapi.h: 4300

# vxlapi.h: 4309
class struct_s_xl_most150_async_tx_msg(Structure):
    pass

struct_s_xl_most150_async_tx_msg._pack_ = 1
struct_s_xl_most150_async_tx_msg.__slots__ = [
    'priority',
    'asyncSendAttempts',
    'length',
    'targetAddress',
    'asyncData',
]
struct_s_xl_most150_async_tx_msg._fields_ = [
    ('priority', c_uint),
    ('asyncSendAttempts', c_uint),
    ('length', c_uint),
    ('targetAddress', c_uint),
    ('asyncData', c_ubyte * int(1600)),
]

XLmost150AsyncTxMsg = struct_s_xl_most150_async_tx_msg# vxlapi.h: 4309

# vxlapi.h: 4319
class struct_s_xl_most150_ethernet_tx_msg(Structure):
    pass

struct_s_xl_most150_ethernet_tx_msg._pack_ = 1
struct_s_xl_most150_ethernet_tx_msg.__slots__ = [
    'priority',
    'ethSendAttempts',
    'sourceAddress',
    'targetAddress',
    'length',
    'ethernetData',
]
struct_s_xl_most150_ethernet_tx_msg._fields_ = [
    ('priority', c_uint),
    ('ethSendAttempts', c_uint),
    ('sourceAddress', c_ubyte * int(6)),
    ('targetAddress', c_ubyte * int(6)),
    ('length', c_uint),
    ('ethernetData', c_ubyte * int(1600)),
]

XLmost150EthernetTxMsg = struct_s_xl_most150_ethernet_tx_msg# vxlapi.h: 4319

# vxlapi.h: 4327
class struct_s_xl_most150_sync_audio_parameter(Structure):
    pass

struct_s_xl_most150_sync_audio_parameter._pack_ = 1
struct_s_xl_most150_sync_audio_parameter.__slots__ = [
    'label',
    'width',
    'device',
    'mode',
]
struct_s_xl_most150_sync_audio_parameter._fields_ = [
    ('label', c_uint),
    ('width', c_uint),
    ('device', c_uint),
    ('mode', c_uint),
]

XLmost150SyncAudioParameter = struct_s_xl_most150_sync_audio_parameter# vxlapi.h: 4327

# vxlapi.h: 4335
class struct_s_xl_most150_ctrl_busload_config(Structure):
    pass

struct_s_xl_most150_ctrl_busload_config._pack_ = 1
struct_s_xl_most150_ctrl_busload_config.__slots__ = [
    'transmissionRate',
    'counterType',
    'counterPosition',
    'busloadCtrlMsg',
]
struct_s_xl_most150_ctrl_busload_config._fields_ = [
    ('transmissionRate', c_uint),
    ('counterType', c_uint),
    ('counterPosition', c_uint),
    ('busloadCtrlMsg', XLmost150CtrlTxMsg),
]

XLmost150CtrlBusloadConfig = struct_s_xl_most150_ctrl_busload_config# vxlapi.h: 4335

# vxlapi.h: 4344
class union_anon_29(Union):
    pass

union_anon_29._pack_ = 1
union_anon_29.__slots__ = [
    'rawBusloadPkt',
    'busloadAsyncPkt',
    'busloadEthernetPkt',
]
union_anon_29._fields_ = [
    ('rawBusloadPkt', c_ubyte * int(1540)),
    ('busloadAsyncPkt', XLmost150AsyncTxMsg),
    ('busloadEthernetPkt', XLmost150EthernetTxMsg),
]

# vxlapi.h: 4349
class struct_s_xl_most150_async_busload_config(Structure):
    pass

struct_s_xl_most150_async_busload_config._pack_ = 1
struct_s_xl_most150_async_busload_config.__slots__ = [
    'busloadType',
    'transmissionRate',
    'counterType',
    'counterPosition',
    'busloadPkt',
]
struct_s_xl_most150_async_busload_config._fields_ = [
    ('busloadType', c_uint),
    ('transmissionRate', c_uint),
    ('counterType', c_uint),
    ('counterPosition', c_uint),
    ('busloadPkt', union_anon_29),
]

XLmost150AsyncBusloadConfig = struct_s_xl_most150_async_busload_config# vxlapi.h: 4349

# vxlapi.h: 4358
class struct_s_xl_most150_stream_open(Structure):
    pass

struct_s_xl_most150_stream_open._pack_ = 1
struct_s_xl_most150_stream_open.__slots__ = [
    'pStreamHandle',
    'direction',
    'numBytesPerFrame',
    'reserved',
    'latency',
]
struct_s_xl_most150_stream_open._fields_ = [
    ('pStreamHandle', POINTER(c_uint)),
    ('direction', c_uint),
    ('numBytesPerFrame', c_uint),
    ('reserved', c_uint),
    ('latency', c_uint),
]

XLmost150StreamOpen = struct_s_xl_most150_stream_open# vxlapi.h: 4358

# vxlapi.h: 4369
class struct_s_xl_most150_stream_get_info(Structure):
    pass

struct_s_xl_most150_stream_get_info._pack_ = 1
struct_s_xl_most150_stream_get_info.__slots__ = [
    'streamHandle',
    'numBytesPerFrame',
    'direction',
    'reserved',
    'latency',
    'streamState',
    'connLabels',
]
struct_s_xl_most150_stream_get_info._fields_ = [
    ('streamHandle', c_uint),
    ('numBytesPerFrame', c_uint),
    ('direction', c_uint),
    ('reserved', c_uint),
    ('latency', c_uint),
    ('streamState', c_uint),
    ('connLabels', c_uint * int(8)),
]

XLmost150StreamInfo = struct_s_xl_most150_stream_get_info# vxlapi.h: 4369

# vxlapi.h: 4418
class struct_anon_30(Structure):
    pass

struct_anon_30._pack_ = 8
struct_anon_30.__slots__ = [
    'canId',
    'msgFlags',
    'dlc',
    'reserved',
    'data',
]
struct_anon_30._fields_ = [
    ('canId', c_uint),
    ('msgFlags', c_uint),
    ('dlc', c_ubyte),
    ('reserved', c_ubyte * int(7)),
    ('data', c_ubyte * int(64)),
]

XL_CAN_TX_MSG = struct_anon_30# vxlapi.h: 4418

# vxlapi.h: 4426
class union_anon_31(Union):
    pass

union_anon_31._pack_ = 8
union_anon_31.__slots__ = [
    'canMsg',
]
union_anon_31._fields_ = [
    ('canMsg', XL_CAN_TX_MSG),
]

# vxlapi.h: 4429
class struct_anon_32(Structure):
    pass

struct_anon_32._pack_ = 8
struct_anon_32.__slots__ = [
    'tag',
    'transId',
    'channelIndex',
    'reserved',
    'tagData',
]
struct_anon_32._fields_ = [
    ('tag', c_ushort),
    ('transId', c_ushort),
    ('channelIndex', c_ubyte),
    ('reserved', c_ubyte * int(3)),
    ('tagData', union_anon_31),
]

XLcanTxEvent = struct_anon_32# vxlapi.h: 4429

# vxlapi.h: 4445
class struct_anon_33(Structure):
    pass

struct_anon_33._pack_ = 8
struct_anon_33.__slots__ = [
    'canId',
    'msgFlags',
    'crc',
    'reserved1',
    'totalBitCnt',
    'dlc',
    'reserved',
    'data',
]
struct_anon_33._fields_ = [
    ('canId', c_uint),
    ('msgFlags', c_uint),
    ('crc', c_uint),
    ('reserved1', c_ubyte * int(12)),
    ('totalBitCnt', c_ushort),
    ('dlc', c_ubyte),
    ('reserved', c_ubyte * int(5)),
    ('data', c_ubyte * int(64)),
]

XL_CAN_EV_RX_MSG = struct_anon_33# vxlapi.h: 4445

# vxlapi.h: 4454
class struct_anon_34(Structure):
    pass

struct_anon_34._pack_ = 8
struct_anon_34.__slots__ = [
    'canId',
    'msgFlags',
    'dlc',
    'reserved1',
    'reserved',
    'data',
]
struct_anon_34._fields_ = [
    ('canId', c_uint),
    ('msgFlags', c_uint),
    ('dlc', c_ubyte),
    ('reserved1', c_ubyte),
    ('reserved', c_ushort),
    ('data', c_ubyte * int(64)),
]

XL_CAN_EV_TX_REQUEST = struct_anon_34# vxlapi.h: 4454

# vxlapi.h: 4464
class struct_anon_35(Structure):
    pass

struct_anon_35._pack_ = 8
struct_anon_35.__slots__ = [
    'busStatus',
    'txErrorCounter',
    'rxErrorCounter',
    'reserved',
    'reserved0',
]
struct_anon_35._fields_ = [
    ('busStatus', c_ubyte),
    ('txErrorCounter', c_ubyte),
    ('rxErrorCounter', c_ubyte),
    ('reserved', c_ubyte),
    ('reserved0', c_uint),
]

XL_CAN_EV_CHIP_STATE = struct_anon_35# vxlapi.h: 4464

XL_CAN_EV_SYNC_PULSE = XL_SYNC_PULSE_EV# vxlapi.h: 4467

# vxlapi.h: 4484
class struct_anon_36(Structure):
    pass

struct_anon_36._pack_ = 8
struct_anon_36.__slots__ = [
    'errorCode',
    'reserved',
]
struct_anon_36._fields_ = [
    ('errorCode', c_ubyte),
    ('reserved', c_ubyte * int(95)),
]

XL_CAN_EV_ERROR = struct_anon_36# vxlapi.h: 4484

# vxlapi.h: 4506
class union_u_tagData(Union):
    pass

union_u_tagData._pack_ = 8
union_u_tagData.__slots__ = [
    'raw',
    'canRxOkMsg',
    'canTxOkMsg',
    'canTxRequest',
    'canError',
    'canChipState',
    'canSyncPulse',
]
union_u_tagData._fields_ = [
    ('raw', c_ubyte * int((128 - 32))),
    ('canRxOkMsg', XL_CAN_EV_RX_MSG),
    ('canTxOkMsg', XL_CAN_EV_RX_MSG),
    ('canTxRequest', XL_CAN_EV_TX_REQUEST),
    ('canError', XL_CAN_EV_ERROR),
    ('canChipState', XL_CAN_EV_CHIP_STATE),
    ('canSyncPulse', XL_CAN_EV_SYNC_PULSE),
]

# vxlapi.h: 4516
class struct_anon_37(Structure):
    pass

struct_anon_37._pack_ = 8
struct_anon_37.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'userHandle',
    'flagsChip',
    'reserved0',
    'reserved1',
    'timeStampSync',
    'tagData',
]
struct_anon_37._fields_ = [
    ('size', c_uint),
    ('tag', c_ushort),
    ('channelIndex', c_ushort),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved0', c_ushort),
    ('reserved1', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_u_tagData),
]

XLcanRxEvent = struct_anon_37# vxlapi.h: 4516

# vxlapi.h: 4612
class struct_anon_38(Structure):
    pass

struct_anon_38._pack_ = 8
struct_anon_38.__slots__ = [
    'bitrate',
    'parity',
    'minGap',
]
struct_anon_38._fields_ = [
    ('bitrate', c_uint),
    ('parity', c_uint),
    ('minGap', c_uint),
]

# vxlapi.h: 4618
class struct_anon_39(Structure):
    pass

struct_anon_39._pack_ = 8
struct_anon_39.__slots__ = [
    'bitrate',
    'minBitrate',
    'maxBitrate',
    'parity',
    'minGap',
    'autoBaudrate',
]
struct_anon_39._fields_ = [
    ('bitrate', c_uint),
    ('minBitrate', c_uint),
    ('maxBitrate', c_uint),
    ('parity', c_uint),
    ('minGap', c_uint),
    ('autoBaudrate', c_uint),
]

# vxlapi.h: 4611
class union_anon_40(Union):
    pass

union_anon_40._pack_ = 8
union_anon_40.__slots__ = [
    'tx',
    'rx',
    'raw',
]
union_anon_40._fields_ = [
    ('tx', struct_anon_38),
    ('rx', struct_anon_39),
    ('raw', c_ubyte * int(28)),
]

# vxlapi.h: 4629
class struct_s_xl_a429_params(Structure):
    pass

struct_s_xl_a429_params._pack_ = 8
struct_s_xl_a429_params.__slots__ = [
    'channelDirection',
    'res1',
    'data',
]
struct_s_xl_a429_params._fields_ = [
    ('channelDirection', c_ushort),
    ('res1', c_ushort),
    ('data', union_anon_40),
]

XL_A429_PARAMS = struct_s_xl_a429_params# vxlapi.h: 4629

# vxlapi.h: 4645
class struct_s_xl_a429_msg_tx(Structure):
    pass

struct_s_xl_a429_msg_tx._pack_ = 8
struct_s_xl_a429_msg_tx.__slots__ = [
    'userHandle',
    'res1',
    'flags',
    'cycleTime',
    'gap',
    'label',
    'parity',
    'res2',
    'data',
]
struct_s_xl_a429_msg_tx._fields_ = [
    ('userHandle', c_ushort),
    ('res1', c_ushort),
    ('flags', c_uint),
    ('cycleTime', c_uint),
    ('gap', c_uint),
    ('label', c_ubyte),
    ('parity', c_ubyte),
    ('res2', c_ushort),
    ('data', c_uint),
]

XL_A429_MSG_TX = struct_s_xl_a429_msg_tx# vxlapi.h: 4645

# vxlapi.h: 4659
class struct_s_xl_a429_ev_tx_ok(Structure):
    pass

struct_s_xl_a429_ev_tx_ok._pack_ = 8
struct_s_xl_a429_ev_tx_ok.__slots__ = [
    'frameLength',
    'bitrate',
    'label',
    'msgCtrl',
    'res1',
    'data',
]
struct_s_xl_a429_ev_tx_ok._fields_ = [
    ('frameLength', c_uint),
    ('bitrate', c_uint),
    ('label', c_ubyte),
    ('msgCtrl', c_ubyte),
    ('res1', c_ushort),
    ('data', c_uint),
]

XL_A429_EV_TX_OK = struct_s_xl_a429_ev_tx_ok# vxlapi.h: 4659

# vxlapi.h: 4670
class struct_s_xl_a429_ev_tx_err(Structure):
    pass

struct_s_xl_a429_ev_tx_err._pack_ = 8
struct_s_xl_a429_ev_tx_err.__slots__ = [
    'frameLength',
    'bitrate',
    'errorPosition',
    'errorReason',
    'label',
    'res1',
    'data',
]
struct_s_xl_a429_ev_tx_err._fields_ = [
    ('frameLength', c_uint),
    ('bitrate', c_uint),
    ('errorPosition', c_ubyte),
    ('errorReason', c_ubyte),
    ('label', c_ubyte),
    ('res1', c_ubyte),
    ('data', c_uint),
]

XL_A429_EV_TX_ERR = struct_s_xl_a429_ev_tx_err# vxlapi.h: 4670

# vxlapi.h: 4679
class struct_s_xl_a429_ev_rx_ok(Structure):
    pass

struct_s_xl_a429_ev_rx_ok._pack_ = 8
struct_s_xl_a429_ev_rx_ok.__slots__ = [
    'frameLength',
    'bitrate',
    'label',
    'res1',
    'data',
]
struct_s_xl_a429_ev_rx_ok._fields_ = [
    ('frameLength', c_uint),
    ('bitrate', c_uint),
    ('label', c_ubyte),
    ('res1', c_ubyte * int(3)),
    ('data', c_uint),
]

XL_A429_EV_RX_OK = struct_s_xl_a429_ev_rx_ok# vxlapi.h: 4679

# vxlapi.h: 4691
class struct_s_xl_a429_ev_rx_err(Structure):
    pass

struct_s_xl_a429_ev_rx_err._pack_ = 8
struct_s_xl_a429_ev_rx_err.__slots__ = [
    'frameLength',
    'bitrate',
    'bitLengthOfLastBit',
    'errorPosition',
    'errorReason',
    'label',
    'res1',
    'data',
]
struct_s_xl_a429_ev_rx_err._fields_ = [
    ('frameLength', c_uint),
    ('bitrate', c_uint),
    ('bitLengthOfLastBit', c_uint),
    ('errorPosition', c_ubyte),
    ('errorReason', c_ubyte),
    ('label', c_ubyte),
    ('res1', c_ubyte),
    ('data', c_uint),
]

XL_A429_EV_RX_ERR = struct_s_xl_a429_ev_rx_err# vxlapi.h: 4691

# vxlapi.h: 4697
class struct_s_xl_a429_ev_bus_statistic(Structure):
    pass

struct_s_xl_a429_ev_bus_statistic._pack_ = 8
struct_s_xl_a429_ev_bus_statistic.__slots__ = [
    'busLoad',
    'res1',
]
struct_s_xl_a429_ev_bus_statistic._fields_ = [
    ('busLoad', c_uint),
    ('res1', c_uint * int(3)),
]

XL_A429_EV_BUS_STATISTIC = struct_s_xl_a429_ev_bus_statistic# vxlapi.h: 4697

XL_A429_EV_SYNC_PULSE = XL_SYNC_PULSE_EV# vxlapi.h: 4699

# vxlapi.h: 4712
class union_anon_41(Union):
    pass

union_anon_41._pack_ = 8
union_anon_41.__slots__ = [
    'a429TxOkMsg',
    'a429TxErrMsg',
    'a429RxOkMsg',
    'a429RxErrMsg',
    'a429BusStatistic',
    'a429SyncPulse',
]
union_anon_41._fields_ = [
    ('a429TxOkMsg', XL_A429_EV_TX_OK),
    ('a429TxErrMsg', XL_A429_EV_TX_ERR),
    ('a429RxOkMsg', XL_A429_EV_RX_OK),
    ('a429RxErrMsg', XL_A429_EV_RX_ERR),
    ('a429BusStatistic', XL_A429_EV_BUS_STATISTIC),
    ('a429SyncPulse', XL_A429_EV_SYNC_PULSE),
]

# vxlapi.h: 4720
class struct_anon_42(Structure):
    pass

struct_anon_42._pack_ = 8
struct_anon_42.__slots__ = [
    'size',
    'tag',
    'channelIndex',
    'reserved',
    'userHandle',
    'flagsChip',
    'reserved0',
    'timeStamp',
    'timeStampSync',
    'tagData',
]
struct_anon_42._fields_ = [
    ('size', c_uint),
    ('tag', c_ushort),
    ('channelIndex', c_ubyte),
    ('reserved', c_ubyte),
    ('userHandle', c_uint),
    ('flagsChip', c_ushort),
    ('reserved0', c_ushort),
    ('timeStamp', XLuint64),
    ('timeStampSync', XLuint64),
    ('tagData', union_anon_41),
]

XLa429RxEvent = struct_anon_42# vxlapi.h: 4720

# vxlapi.h: 4726
class struct_XLIDriverConfig(Structure):
    pass

# vxlapi.h: 4729
class struct__XLdriverConfig(Structure):
    pass

XLdrvConfigHandle = POINTER(struct__XLdriverConfig)# vxlapi.h: 4730

# vxlapi.h: 4750
class struct_anon_43(Structure):
    pass

struct_anon_43._pack_ = 8
struct_anon_43.__slots__ = [
    'name',
    'type',
    'configError',
]
struct_anon_43._fields_ = [
    ('name', String),
    ('type', c_uint),
    ('configError', c_uint),
]

# vxlapi.h: 4735
class struct_s_xl_channel_drv_config_v1(Structure):
    pass

struct_s_xl_channel_drv_config_v1._pack_ = 8
struct_s_xl_channel_drv_config_v1.__slots__ = [
    'hwChannel',
    'channelIndex',
    'deviceIndex',
    'interfaceVersion',
    'isOnBus',
    'channelCapabilities',
    'channelCapabilities2',
    'channelBusCapabilities',
    'channelBusActiveCapabilities',
    'connectedBusType',
    'currentlyAvailableTimestamps',
    'busParams',
    'transceiver',
    'remoteChannel',
]
struct_s_xl_channel_drv_config_v1._fields_ = [
    ('hwChannel', c_uint),
    ('channelIndex', c_uint),
    ('deviceIndex', c_uint),
    ('interfaceVersion', c_uint),
    ('isOnBus', c_uint),
    ('channelCapabilities', XLuint64),
    ('channelCapabilities2', XLuint64),
    ('channelBusCapabilities', XLuint64),
    ('channelBusActiveCapabilities', XLuint64),
    ('connectedBusType', XLuint64),
    ('currentlyAvailableTimestamps', c_uint),
    ('busParams', XLbusParams),
    ('transceiver', struct_anon_43),
    ('remoteChannel', POINTER(struct_s_xl_channel_drv_config_v1)),
]

XLchannelDrvConfigV1 = struct_s_xl_channel_drv_config_v1# vxlapi.h: 4756

pXLchannelDrvConfigV1 = POINTER(struct_s_xl_channel_drv_config_v1)# vxlapi.h: 4756

# vxlapi.h: 4762
class struct_s_channel_drv_config_list_v1(Structure):
    pass

struct_s_channel_drv_config_list_v1._pack_ = 8
struct_s_channel_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_channel_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLchannelDrvConfigV1)),
    ('count', c_uint),
]

XLchannelDrvConfigListV1 = struct_s_channel_drv_config_list_v1# vxlapi.h: 4762

pXLchannelDrvConfigListV1 = POINTER(struct_s_channel_drv_config_list_v1)# vxlapi.h: 4762

TP_FCT_XLAPI_GET_CHANNEL_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLchannelDrvConfigListV1))# vxlapi.h: 4765

# vxlapi.h: 4769
class struct_s_xl_device_drv_config_v1(Structure):
    pass

# vxlapi.h: 4779
class struct_anon_44(Structure):
    pass

struct_anon_44._pack_ = 8
struct_anon_44.__slots__ = [
    'item',
    'count',
]
struct_anon_44._fields_ = [
    ('item', POINTER(struct_s_xl_device_drv_config_v1)),
    ('count', c_uint),
]

struct_s_xl_device_drv_config_v1._pack_ = 8
struct_s_xl_device_drv_config_v1.__slots__ = [
    'name',
    'hwType',
    'hwIndex',
    'serialNumber',
    'articleNumber',
    'driverVersion',
    'connectionInfo',
    'isRemoteDevice',
    'remoteDeviceList',
    'channelList',
]
struct_s_xl_device_drv_config_v1._fields_ = [
    ('name', String),
    ('hwType', c_uint),
    ('hwIndex', c_uint),
    ('serialNumber', c_uint),
    ('articleNumber', c_uint),
    ('driverVersion', XLuint64),
    ('connectionInfo', c_uint),
    ('isRemoteDevice', c_uint),
    ('remoteDeviceList', struct_anon_44),
    ('channelList', XLchannelDrvConfigListV1),
]

XLdeviceDrvConfigV1 = struct_s_xl_device_drv_config_v1# vxlapi.h: 4785

pXLdeviceDrvConfigV1 = POINTER(struct_s_xl_device_drv_config_v1)# vxlapi.h: 4785

# vxlapi.h: 4791
class struct_s_device_drv_config_list_v1(Structure):
    pass

struct_s_device_drv_config_list_v1._pack_ = 8
struct_s_device_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_device_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLdeviceDrvConfigV1)),
    ('count', c_uint),
]

XLdeviceDrvConfigListV1 = struct_s_device_drv_config_list_v1# vxlapi.h: 4791

pXLdeviceDrvConfigListV1 = POINTER(struct_s_device_drv_config_list_v1)# vxlapi.h: 4791

TP_FCT_XLAPI_GET_DEVICE_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLdeviceDrvConfigListV1))# vxlapi.h: 4794

# vxlapi.h: 4800
class struct_s_xl_virtual_port_drv_config_v1(Structure):
    pass

struct_s_xl_virtual_port_drv_config_v1._pack_ = 8
struct_s_xl_virtual_port_drv_config_v1.__slots__ = [
    'virtualPortName',
    'networkIdx',
    'switchId',
]
struct_s_xl_virtual_port_drv_config_v1._fields_ = [
    ('virtualPortName', String),
    ('networkIdx', c_uint),
    ('switchId', XLswitchId),
]

XLvirtualportDrvConfigV1 = struct_s_xl_virtual_port_drv_config_v1# vxlapi.h: 4800

pXLvirtualportDrvConfigV1 = POINTER(struct_s_xl_virtual_port_drv_config_v1)# vxlapi.h: 4800

# vxlapi.h: 4806
class struct_s_virtual_port_drv_config_list_v1(Structure):
    pass

struct_s_virtual_port_drv_config_list_v1._pack_ = 8
struct_s_virtual_port_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_virtual_port_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLvirtualportDrvConfigV1)),
    ('count', c_uint),
]

XLvirtualportDrvConfigListV1 = struct_s_virtual_port_drv_config_list_v1# vxlapi.h: 4806

pXLvirtualportDrvConfigListV1 = POINTER(struct_s_virtual_port_drv_config_list_v1)# vxlapi.h: 4806

TP_FCT_XLAPI_GET_VIRTUAL_PORT_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLvirtualportDrvConfigListV1))# vxlapi.h: 4809

# vxlapi.h: 4818
class struct_s_xl_measurement_point_drv_config_v1(Structure):
    pass

struct_s_xl_measurement_point_drv_config_v1._pack_ = 8
struct_s_xl_measurement_point_drv_config_v1.__slots__ = [
    'measurementPointName',
    'networkIdx',
    'switchId',
    'channel',
]
struct_s_xl_measurement_point_drv_config_v1._fields_ = [
    ('measurementPointName', String),
    ('networkIdx', c_uint),
    ('switchId', XLswitchId),
    ('channel', POINTER(XLchannelDrvConfigV1)),
]

XLmeasurementpointDrvConfigV1 = struct_s_xl_measurement_point_drv_config_v1# vxlapi.h: 4818

pXLmeasurementpointDrvConfigV1 = POINTER(struct_s_xl_measurement_point_drv_config_v1)# vxlapi.h: 4818

# vxlapi.h: 4824
class struct_s_xl_measurement_point_drv_config_list_v1(Structure):
    pass

struct_s_xl_measurement_point_drv_config_list_v1._pack_ = 8
struct_s_xl_measurement_point_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_xl_measurement_point_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLmeasurementpointDrvConfigV1)),
    ('count', c_uint),
]

XLmeasurementpointDrvConfigListV1 = struct_s_xl_measurement_point_drv_config_list_v1# vxlapi.h: 4824

pXLmeasurementpointDrvConfigListV1 = POINTER(struct_s_xl_measurement_point_drv_config_list_v1)# vxlapi.h: 4824

TP_FCT_XLAPI_GET_MEASUREMENT_POINT_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLmeasurementpointDrvConfigListV1))# vxlapi.h: 4827

# vxlapi.h: 4839
class struct_s_xl_switch_drv_config_v1(Structure):
    pass

struct_s_xl_switch_drv_config_v1._pack_ = 8
struct_s_xl_switch_drv_config_v1.__slots__ = [
    'switchName',
    'switchId',
    'networkIdx',
    'device',
    'switchCapability',
    'vpList',
    'mpList',
]
struct_s_xl_switch_drv_config_v1._fields_ = [
    ('switchName', String),
    ('switchId', XLswitchId),
    ('networkIdx', c_uint),
    ('device', POINTER(XLdeviceDrvConfigV1)),
    ('switchCapability', c_uint),
    ('vpList', XLvirtualportDrvConfigListV1),
    ('mpList', XLmeasurementpointDrvConfigListV1),
]

XLswitchDrvConfigV1 = struct_s_xl_switch_drv_config_v1# vxlapi.h: 4839

pXLswitchDrvConfigV1 = POINTER(struct_s_xl_switch_drv_config_v1)# vxlapi.h: 4839

# vxlapi.h: 4845
class struct_s_switch_drv_config_list_v1(Structure):
    pass

struct_s_switch_drv_config_list_v1._pack_ = 8
struct_s_switch_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_switch_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLswitchDrvConfigV1)),
    ('count', c_uint),
]

XLswitchDrvConfigListV1 = struct_s_switch_drv_config_list_v1# vxlapi.h: 4845

pXLswitchDrvConfigListV1 = POINTER(struct_s_switch_drv_config_list_v1)# vxlapi.h: 4845

TP_FCT_XLAPI_GET_SWITCH_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLswitchDrvConfigListV1))# vxlapi.h: 4848

enum_anon_45 = c_int# vxlapi.h: 4851

XL_ETH_NETWORK = 1# vxlapi.h: 4851

XLnetworkType = enum_anon_45# vxlapi.h: 4851

# vxlapi.h: 4860
class struct_s_xl_network_drv_config_v1(Structure):
    pass

struct_s_xl_network_drv_config_v1._pack_ = 8
struct_s_xl_network_drv_config_v1.__slots__ = [
    'networkName',
    'statusCode',
    'statusErrorString',
    'networkType',
    'switchList',
]
struct_s_xl_network_drv_config_v1._fields_ = [
    ('networkName', String),
    ('statusCode', c_uint),
    ('statusErrorString', String),
    ('networkType', XLnetworkType),
    ('switchList', XLswitchDrvConfigListV1),
]

XLnetworkDrvConfigV1 = struct_s_xl_network_drv_config_v1# vxlapi.h: 4860

pXLnetworkDrvConfigV1 = POINTER(struct_s_xl_network_drv_config_v1)# vxlapi.h: 4860

# vxlapi.h: 4866
class struct_s_xl_network_drv_config_list_v1(Structure):
    pass

struct_s_xl_network_drv_config_list_v1._pack_ = 8
struct_s_xl_network_drv_config_list_v1.__slots__ = [
    'item',
    'count',
]
struct_s_xl_network_drv_config_list_v1._fields_ = [
    ('item', POINTER(XLnetworkDrvConfigV1)),
    ('count', c_uint),
]

XLnetworkDrvConfigListV1 = struct_s_xl_network_drv_config_list_v1# vxlapi.h: 4866

pXLnetworkDrvConfigListV1 = POINTER(struct_s_xl_network_drv_config_list_v1)# vxlapi.h: 4866

TP_FCT_XLAPI_GET_NETWORK_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLnetworkDrvConfigListV1))# vxlapi.h: 4869

# vxlapi.h: 4875
class struct_s_xl_dll_drv_config_v1(Structure):
    pass

struct_s_xl_dll_drv_config_v1._pack_ = 8
struct_s_xl_dll_drv_config_v1.__slots__ = [
    'dllVersion',
]
struct_s_xl_dll_drv_config_v1._fields_ = [
    ('dllVersion', XLuint64),
]

XLdllDrvConfigV1 = struct_s_xl_dll_drv_config_v1# vxlapi.h: 4875

pXLdllDrvConfigV1 = POINTER(struct_s_xl_dll_drv_config_v1)# vxlapi.h: 4875

TP_FCT_XLAPI_GET_DLL_CONFIG_V1 = CFUNCTYPE(UNCHECKED(XLstatus), XLdrvConfigHandle, POINTER(XLdllDrvConfigV1))# vxlapi.h: 4878

enum_anon_46 = c_int# vxlapi.h: 4883

XL_IDRIVER_CONFIG_VERSION_1 = 0x8001# vxlapi.h: 4883

XLIdriverConfigVersion = enum_anon_46# vxlapi.h: 4883

# vxlapi.h: 4895
class struct_s_xlapi_driver_config_v1(Structure):
    pass

struct_s_xlapi_driver_config_v1._pack_ = 8
struct_s_xlapi_driver_config_v1.__slots__ = [
    'configHandle',
    'fctGetDeviceConfig',
    'fctGetChannelConfig',
    'fctGetNetworkConfig',
    'fctGetSwitchConfig',
    'fctGetVirtualPortConfig',
    'fctGetMeasurementPointConfig',
    'fctGetDllConfig',
]
struct_s_xlapi_driver_config_v1._fields_ = [
    ('configHandle', XLdrvConfigHandle),
    ('fctGetDeviceConfig', TP_FCT_XLAPI_GET_DEVICE_CONFIG_V1),
    ('fctGetChannelConfig', TP_FCT_XLAPI_GET_CHANNEL_CONFIG_V1),
    ('fctGetNetworkConfig', TP_FCT_XLAPI_GET_NETWORK_CONFIG_V1),
    ('fctGetSwitchConfig', TP_FCT_XLAPI_GET_SWITCH_CONFIG_V1),
    ('fctGetVirtualPortConfig', TP_FCT_XLAPI_GET_VIRTUAL_PORT_CONFIG_V1),
    ('fctGetMeasurementPointConfig', TP_FCT_XLAPI_GET_MEASUREMENT_POINT_CONFIG_V1),
    ('fctGetDllConfig', TP_FCT_XLAPI_GET_DLL_CONFIG_V1),
]

XLapiIDriverConfigV1 = struct_s_xlapi_driver_config_v1# vxlapi.h: 4895

pXLapiIDriverConfigV1 = POINTER(struct_s_xlapi_driver_config_v1)# vxlapi.h: 4895

# vxlapi.h: 4908
if _libs["vxlapi64"].has("xlGetErrorString", "cdecl"):
    xlGetErrorString = _libs["vxlapi64"].get("xlGetErrorString", "cdecl")
    xlGetErrorString.argtypes = [XLstatus]
    xlGetErrorString.restype = XLstringType

# vxlapi.h: 4920
if _libs["vxlapi64"].has("xlOpenDriver", "cdecl"):
    xlOpenDriver = _libs["vxlapi64"].get("xlOpenDriver", "cdecl")
    xlOpenDriver.argtypes = []
    xlOpenDriver.restype = XLstatus

# vxlapi.h: 4934
if _libs["vxlapi64"].has("xlCloseDriver", "cdecl"):
    xlCloseDriver = _libs["vxlapi64"].get("xlCloseDriver", "cdecl")
    xlCloseDriver.argtypes = []
    xlCloseDriver.restype = XLstatus

# vxlapi.h: 4954
if _libs["vxlapi64"].has("xlGetApplConfig", "cdecl"):
    xlGetApplConfig = _libs["vxlapi64"].get("xlGetApplConfig", "cdecl")
    xlGetApplConfig.argtypes = [String, c_uint, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), c_uint]
    xlGetApplConfig.restype = XLstatus

# vxlapi.h: 4963
if _libs["vxlapi64"].has("xlSetApplConfig", "cdecl"):
    xlSetApplConfig = _libs["vxlapi64"].get("xlSetApplConfig", "cdecl")
    xlSetApplConfig.argtypes = [String, c_uint, c_uint, c_uint, c_uint, c_uint]
    xlSetApplConfig.restype = XLstatus

# vxlapi.h: 4981
if _libs["vxlapi64"].has("xlGetDriverConfig", "cdecl"):
    xlGetDriverConfig = _libs["vxlapi64"].get("xlGetDriverConfig", "cdecl")
    xlGetDriverConfig.argtypes = [POINTER(XLdriverConfig)]
    xlGetDriverConfig.restype = XLstatus

# vxlapi.h: 4993
for _lib in _libs.values():
    if not _lib.has("xlCreateDriverConfig", "cdecl"):
        continue
    xlCreateDriverConfig = _lib.get("xlCreateDriverConfig", "cdecl")
    xlCreateDriverConfig.argtypes = [XLIdriverConfigVersion, POINTER(struct_XLIDriverConfig)]
    xlCreateDriverConfig.restype = XLstatus
    break

# vxlapi.h: 5003
for _lib in _libs.values():
    if not _lib.has("xlDestroyDriverConfig", "cdecl"):
        continue
    xlDestroyDriverConfig = _lib.get("xlDestroyDriverConfig", "cdecl")
    xlDestroyDriverConfig.argtypes = [XLdrvConfigHandle]
    xlDestroyDriverConfig.restype = XLstatus
    break

# vxlapi.h: 5011
if _libs["vxlapi64"].has("xlGetChannelIndex", "cdecl"):
    xlGetChannelIndex = _libs["vxlapi64"].get("xlGetChannelIndex", "cdecl")
    xlGetChannelIndex.argtypes = [c_int, c_int, c_int]
    xlGetChannelIndex.restype = c_int

# vxlapi.h: 5019
if _libs["vxlapi64"].has("xlGetChannelMask", "cdecl"):
    xlGetChannelMask = _libs["vxlapi64"].get("xlGetChannelMask", "cdecl")
    xlGetChannelMask.argtypes = [c_int, c_int, c_int]
    xlGetChannelMask.restype = XLaccess

# vxlapi.h: 5032
if _libs["vxlapi64"].has("xlOpenPort", "cdecl"):
    xlOpenPort = _libs["vxlapi64"].get("xlOpenPort", "cdecl")
    xlOpenPort.argtypes = [POINTER(XLportHandle), String, XLaccess, POINTER(XLaccess), c_uint, c_uint, c_uint]
    xlOpenPort.restype = XLstatus

# vxlapi.h: 5044
if _libs["vxlapi64"].has("xlCreatePort", "cdecl"):
    xlCreatePort = _libs["vxlapi64"].get("xlCreatePort", "cdecl")
    xlCreatePort.argtypes = [POINTER(XLportHandle), String, c_uint, c_uint, XLuint64]
    xlCreatePort.restype = XLstatus

# vxlapi.h: 5056
if _libs["vxlapi64"].has("xlAddChannelToPort", "cdecl"):
    xlAddChannelToPort = _libs["vxlapi64"].get("xlAddChannelToPort", "cdecl")
    xlAddChannelToPort.argtypes = [XLportHandle, XLaccess, c_uint, POINTER(c_uint), XLuint64]
    xlAddChannelToPort.restype = XLstatus

# vxlapi.h: 5066
if _libs["vxlapi64"].has("xlFinalizePort", "cdecl"):
    xlFinalizePort = _libs["vxlapi64"].get("xlFinalizePort", "cdecl")
    xlFinalizePort.argtypes = [XLportHandle]
    xlFinalizePort.restype = XLstatus

# vxlapi.h: 5078
if _libs["vxlapi64"].has("xlSetTimerRate", "cdecl"):
    xlSetTimerRate = _libs["vxlapi64"].get("xlSetTimerRate", "cdecl")
    xlSetTimerRate.argtypes = [XLportHandle, XLulong]
    xlSetTimerRate.restype = XLstatus

# vxlapi.h: 5105
if _libs["vxlapi64"].has("xlSetTimerRateAndChannel", "cdecl"):
    xlSetTimerRateAndChannel = _libs["vxlapi64"].get("xlSetTimerRateAndChannel", "cdecl")
    xlSetTimerRateAndChannel.argtypes = [XLportHandle, POINTER(XLaccess), POINTER(XLulong)]
    xlSetTimerRateAndChannel.restype = XLstatus

# vxlapi.h: 5115
if _libs["vxlapi64"].has("xlResetClock", "cdecl"):
    xlResetClock = _libs["vxlapi64"].get("xlResetClock", "cdecl")
    xlResetClock.argtypes = [XLportHandle]
    xlResetClock.restype = XLstatus

# vxlapi.h: 5142
for _lib in _libs.values():
    if not _lib.has("xlTsResetClocks", "cdecl"):
        continue
    xlTsResetClocks = _lib.get("xlTsResetClocks", "cdecl")
    xlTsResetClocks.argtypes = [XLportHandle, POINTER(XLtsTimeScale), POINTER(XLtsLeapSeconds), POINTER(XLtsClkUuid), POINTER(XLuint64)]
    xlTsResetClocks.restype = XLstatus
    break

# vxlapi.h: 5171
for _lib in _libs.values():
    if not _lib.has("xlNetTsResetClocks", "cdecl"):
        continue
    xlNetTsResetClocks = _lib.get("xlNetTsResetClocks", "cdecl")
    xlNetTsResetClocks.argtypes = [XLnetworkHandle, POINTER(XLtsTimeScale), POINTER(XLtsLeapSeconds), POINTER(XLtsClkUuid), POINTER(XLuint64)]
    xlNetTsResetClocks.restype = XLstatus
    break

# vxlapi.h: 5200
for _lib in _libs.values():
    if not _lib.has("xlTsGetStatus", "cdecl"):
        continue
    xlTsGetStatus = _lib.get("xlTsGetStatus", "cdecl")
    xlTsGetStatus.argtypes = [XLportHandle, XLaccess, POINTER(XLtsTimeScale), POINTER(XLtsLeapSeconds), POINTER(XLtsClkUuid), POINTER(XLtsClkUuid)]
    xlTsGetStatus.restype = XLstatus
    break

# vxlapi.h: 5227
for _lib in _libs.values():
    if not _lib.has("xlNetTsGetStatus", "cdecl"):
        continue
    xlNetTsGetStatus = _lib.get("xlNetTsGetStatus", "cdecl")
    xlNetTsGetStatus.argtypes = [XLnetworkHandle, XLethPortHandle, POINTER(XLtsTimeScale), POINTER(XLtsLeapSeconds), POINTER(XLtsClkUuid), POINTER(XLtsClkUuid)]
    xlNetTsGetStatus.restype = XLstatus
    break

# vxlapi.h: 5243
if _libs["vxlapi64"].has("xlSetNotification", "cdecl"):
    xlSetNotification = _libs["vxlapi64"].get("xlSetNotification", "cdecl")
    xlSetNotification.argtypes = [XLportHandle, POINTER(XLhandle), c_int]
    xlSetNotification.restype = XLstatus

# vxlapi.h: 5253
if _libs["vxlapi64"].has("xlSetTimerBasedNotify", "cdecl"):
    xlSetTimerBasedNotify = _libs["vxlapi64"].get("xlSetTimerBasedNotify", "cdecl")
    xlSetTimerBasedNotify.argtypes = [XLportHandle, POINTER(XLhandle)]
    xlSetTimerBasedNotify.restype = XLstatus

# vxlapi.h: 5261
if _libs["vxlapi64"].has("xlFlushReceiveQueue", "cdecl"):
    xlFlushReceiveQueue = _libs["vxlapi64"].get("xlFlushReceiveQueue", "cdecl")
    xlFlushReceiveQueue.argtypes = [XLportHandle]
    xlFlushReceiveQueue.restype = XLstatus

# vxlapi.h: 5272
if _libs["vxlapi64"].has("xlGetReceiveQueueLevel", "cdecl"):
    xlGetReceiveQueueLevel = _libs["vxlapi64"].get("xlGetReceiveQueueLevel", "cdecl")
    xlGetReceiveQueueLevel.argtypes = [XLportHandle, POINTER(c_int)]
    xlGetReceiveQueueLevel.restype = XLstatus

# vxlapi.h: 5281
if _libs["vxlapi64"].has("xlActivateChannel", "cdecl"):
    xlActivateChannel = _libs["vxlapi64"].get("xlActivateChannel", "cdecl")
    xlActivateChannel.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlActivateChannel.restype = XLstatus

# vxlapi.h: 5300
if _libs["vxlapi64"].has("xlReceive", "cdecl"):
    xlReceive = _libs["vxlapi64"].get("xlReceive", "cdecl")
    xlReceive.argtypes = [XLportHandle, POINTER(c_uint), POINTER(XLevent)]
    xlReceive.restype = XLstatus

# vxlapi.h: 5309
if _libs["vxlapi64"].has("xlGetEventString", "cdecl"):
    xlGetEventString = _libs["vxlapi64"].get("xlGetEventString", "cdecl")
    xlGetEventString.argtypes = [POINTER(XLevent)]
    xlGetEventString.restype = XLstringType

# vxlapi.h: 5310
if _libs["vxlapi64"].has("xlCanGetEventString", "cdecl"):
    xlCanGetEventString = _libs["vxlapi64"].get("xlCanGetEventString", "cdecl")
    xlCanGetEventString.argtypes = [POINTER(XLcanRxEvent)]
    xlCanGetEventString.restype = XLstringType

# vxlapi.h: 5317
if _libs["vxlapi64"].has("xlOemContact", "cdecl"):
    xlOemContact = _libs["vxlapi64"].get("xlOemContact", "cdecl")
    xlOemContact.argtypes = [XLportHandle, XLulong, XLuint64, POINTER(XLuint64)]
    xlOemContact.restype = XLstatus

# vxlapi.h: 5329
if _libs["vxlapi64"].has("xlGetSyncTime", "cdecl"):
    xlGetSyncTime = _libs["vxlapi64"].get("xlGetSyncTime", "cdecl")
    xlGetSyncTime.argtypes = [XLportHandle, POINTER(XLuint64)]
    xlGetSyncTime.restype = XLstatus

# vxlapi.h: 5337
if _libs["vxlapi64"].has("xlGetChannelTime", "cdecl"):
    xlGetChannelTime = _libs["vxlapi64"].get("xlGetChannelTime", "cdecl")
    xlGetChannelTime.argtypes = [XLportHandle, XLaccess, POINTER(XLuint64)]
    xlGetChannelTime.restype = XLstatus

# vxlapi.h: 5347
if _libs["vxlapi64"].has("xlGenerateSyncPulse", "cdecl"):
    xlGenerateSyncPulse = _libs["vxlapi64"].get("xlGenerateSyncPulse", "cdecl")
    xlGenerateSyncPulse.argtypes = [XLportHandle, XLaccess]
    xlGenerateSyncPulse.restype = XLstatus

# vxlapi.h: 5376
if _libs["vxlapi64"].has("xlPopupHwConfig", "cdecl"):
    xlPopupHwConfig = _libs["vxlapi64"].get("xlPopupHwConfig", "cdecl")
    xlPopupHwConfig.argtypes = [String, c_uint]
    xlPopupHwConfig.restype = XLstatus

# vxlapi.h: 5386
if _libs["vxlapi64"].has("xlDeactivateChannel", "cdecl"):
    xlDeactivateChannel = _libs["vxlapi64"].get("xlDeactivateChannel", "cdecl")
    xlDeactivateChannel.argtypes = [XLportHandle, XLaccess]
    xlDeactivateChannel.restype = XLstatus

# vxlapi.h: 5394
if _libs["vxlapi64"].has("xlClosePort", "cdecl"):
    xlClosePort = _libs["vxlapi64"].get("xlClosePort", "cdecl")
    xlClosePort.argtypes = [XLportHandle]
    xlClosePort.restype = XLstatus

# vxlapi.h: 5406
if _libs["vxlapi64"].has("xlCanFlushTransmitQueue", "cdecl"):
    xlCanFlushTransmitQueue = _libs["vxlapi64"].get("xlCanFlushTransmitQueue", "cdecl")
    xlCanFlushTransmitQueue.argtypes = [XLportHandle, XLaccess]
    xlCanFlushTransmitQueue.restype = XLstatus

# vxlapi.h: 5416
if _libs["vxlapi64"].has("xlCanSetChannelOutput", "cdecl"):
    xlCanSetChannelOutput = _libs["vxlapi64"].get("xlCanSetChannelOutput", "cdecl")
    xlCanSetChannelOutput.argtypes = [XLportHandle, XLaccess, c_int]
    xlCanSetChannelOutput.restype = XLstatus

# vxlapi.h: 5427
if _libs["vxlapi64"].has("xlCanSetChannelMode", "cdecl"):
    xlCanSetChannelMode = _libs["vxlapi64"].get("xlCanSetChannelMode", "cdecl")
    xlCanSetChannelMode.argtypes = [XLportHandle, XLaccess, c_int, c_int]
    xlCanSetChannelMode.restype = XLstatus

# vxlapi.h: 5434
if _libs["vxlapi64"].has("xlCanSetReceiveMode", "cdecl"):
    xlCanSetReceiveMode = _libs["vxlapi64"].get("xlCanSetReceiveMode", "cdecl")
    xlCanSetReceiveMode.argtypes = [XLportHandle, c_ubyte, c_ubyte]
    xlCanSetReceiveMode.restype = XLstatus

# vxlapi.h: 5451
if _libs["vxlapi64"].has("xlCanSetChannelTransceiver", "cdecl"):
    xlCanSetChannelTransceiver = _libs["vxlapi64"].get("xlCanSetChannelTransceiver", "cdecl")
    xlCanSetChannelTransceiver.argtypes = [XLportHandle, XLaccess, c_int, c_int, c_int]
    xlCanSetChannelTransceiver.restype = XLstatus

# vxlapi.h: 5464
if _libs["vxlapi64"].has("xlCanSetChannelParams", "cdecl"):
    xlCanSetChannelParams = _libs["vxlapi64"].get("xlCanSetChannelParams", "cdecl")
    xlCanSetChannelParams.argtypes = [XLportHandle, XLaccess, POINTER(XLchipParams)]
    xlCanSetChannelParams.restype = XLstatus

# vxlapi.h: 5467
if _libs["vxlapi64"].has("xlCanSetChannelParamsC200", "cdecl"):
    xlCanSetChannelParamsC200 = _libs["vxlapi64"].get("xlCanSetChannelParamsC200", "cdecl")
    xlCanSetChannelParamsC200.argtypes = [XLportHandle, XLaccess, c_ubyte, c_ubyte]
    xlCanSetChannelParamsC200.restype = XLstatus

# vxlapi.h: 5470
if _libs["vxlapi64"].has("xlCanSetChannelBitrate", "cdecl"):
    xlCanSetChannelBitrate = _libs["vxlapi64"].get("xlCanSetChannelBitrate", "cdecl")
    xlCanSetChannelBitrate.argtypes = [XLportHandle, XLaccess, XLulong]
    xlCanSetChannelBitrate.restype = XLstatus

# vxlapi.h: 5476
if _libs["vxlapi64"].has("xlCanFdSetConfiguration", "cdecl"):
    xlCanFdSetConfiguration = _libs["vxlapi64"].get("xlCanFdSetConfiguration", "cdecl")
    xlCanFdSetConfiguration.argtypes = [XLportHandle, XLaccess, POINTER(XLcanFdConf)]
    xlCanFdSetConfiguration.restype = XLstatus

# vxlapi.h: 5484
if _libs["vxlapi64"].has("xlCanReceive", "cdecl"):
    xlCanReceive = _libs["vxlapi64"].get("xlCanReceive", "cdecl")
    xlCanReceive.argtypes = [XLportHandle, POINTER(XLcanRxEvent)]
    xlCanReceive.restype = XLstatus

# vxlapi.h: 5491
if _libs["vxlapi64"].has("xlCanTransmitEx", "cdecl"):
    xlCanTransmitEx = _libs["vxlapi64"].get("xlCanTransmitEx", "cdecl")
    xlCanTransmitEx.argtypes = [XLportHandle, XLaccess, c_uint, POINTER(c_uint), POINTER(XLcanTxEvent)]
    xlCanTransmitEx.restype = XLstatus

# vxlapi.h: 5504
if _libs["vxlapi64"].has("xlCanSetChannelAcceptance", "cdecl"):
    xlCanSetChannelAcceptance = _libs["vxlapi64"].get("xlCanSetChannelAcceptance", "cdecl")
    xlCanSetChannelAcceptance.argtypes = [XLportHandle, XLaccess, XLulong, XLulong, c_uint]
    xlCanSetChannelAcceptance.restype = XLstatus

# vxlapi.h: 5514
if _libs["vxlapi64"].has("xlCanAddAcceptanceRange", "cdecl"):
    xlCanAddAcceptanceRange = _libs["vxlapi64"].get("xlCanAddAcceptanceRange", "cdecl")
    xlCanAddAcceptanceRange.argtypes = [XLportHandle, XLaccess, XLulong, XLulong]
    xlCanAddAcceptanceRange.restype = XLstatus

# vxlapi.h: 5516
if _libs["vxlapi64"].has("xlCanRemoveAcceptanceRange", "cdecl"):
    xlCanRemoveAcceptanceRange = _libs["vxlapi64"].get("xlCanRemoveAcceptanceRange", "cdecl")
    xlCanRemoveAcceptanceRange.argtypes = [XLportHandle, XLaccess, XLulong, XLulong]
    xlCanRemoveAcceptanceRange.restype = XLstatus

# vxlapi.h: 5518
if _libs["vxlapi64"].has("xlCanResetAcceptance", "cdecl"):
    xlCanResetAcceptance = _libs["vxlapi64"].get("xlCanResetAcceptance", "cdecl")
    xlCanResetAcceptance.argtypes = [XLportHandle, XLaccess, c_uint]
    xlCanResetAcceptance.restype = XLstatus

# vxlapi.h: 5527
if _libs["vxlapi64"].has("xlCanRequestChipState", "cdecl"):
    xlCanRequestChipState = _libs["vxlapi64"].get("xlCanRequestChipState", "cdecl")
    xlCanRequestChipState.argtypes = [XLportHandle, XLaccess]
    xlCanRequestChipState.restype = XLstatus

# vxlapi.h: 5541
if _libs["vxlapi64"].has("xlCanTransmit", "cdecl"):
    xlCanTransmit = _libs["vxlapi64"].get("xlCanTransmit", "cdecl")
    xlCanTransmit.argtypes = [XLportHandle, XLaccess, POINTER(c_uint), POINTER(None)]
    xlCanTransmit.restype = XLstatus

# vxlapi.h: 5549
if _libs["vxlapi64"].has("xlSetGlobalTimeSync", "cdecl"):
    xlSetGlobalTimeSync = _libs["vxlapi64"].get("xlSetGlobalTimeSync", "cdecl")
    xlSetGlobalTimeSync.argtypes = [XLulong, POINTER(XLulong)]
    xlSetGlobalTimeSync.restype = XLstatus

# vxlapi.h: 5560
if _libs["vxlapi64"].has("xlCheckLicense", "cdecl"):
    xlCheckLicense = _libs["vxlapi64"].get("xlCheckLicense", "cdecl")
    xlCheckLicense.argtypes = [XLportHandle, XLaccess, XLulong]
    xlCheckLicense.restype = XLstatus

# vxlapi.h: 5576
if _libs["vxlapi64"].has("xlGetLicenseInfo", "cdecl"):
    xlGetLicenseInfo = _libs["vxlapi64"].get("xlGetLicenseInfo", "cdecl")
    xlGetLicenseInfo.argtypes = [XLaccess, POINTER(XLlicenseInfo), c_uint]
    xlGetLicenseInfo.restype = XLstatus

# vxlapi.h: 5582
if _libs["vxlapi64"].has("xlLinSetChannelParams", "cdecl"):
    xlLinSetChannelParams = _libs["vxlapi64"].get("xlLinSetChannelParams", "cdecl")
    xlLinSetChannelParams.argtypes = [XLportHandle, XLaccess, XLlinStatPar]
    xlLinSetChannelParams.restype = XLstatus

# vxlapi.h: 5583
if _libs["vxlapi64"].has("xlLinSetDLC", "cdecl"):
    xlLinSetDLC = _libs["vxlapi64"].get("xlLinSetDLC", "cdecl")
    xlLinSetDLC.argtypes = [XLportHandle, XLaccess, String]
    xlLinSetDLC.restype = XLstatus

# vxlapi.h: 5584
if _libs["vxlapi64"].has("xlLinSetSlave", "cdecl"):
    xlLinSetSlave = _libs["vxlapi64"].get("xlLinSetSlave", "cdecl")
    xlLinSetSlave.argtypes = [XLportHandle, XLaccess, c_ubyte, String, c_ubyte, c_ushort]
    xlLinSetSlave.restype = XLstatus

# vxlapi.h: 5587
if _libs["vxlapi64"].has("xlLinSendRequest", "cdecl"):
    xlLinSendRequest = _libs["vxlapi64"].get("xlLinSendRequest", "cdecl")
    xlLinSendRequest.argtypes = [XLportHandle, XLaccess, c_ubyte, c_uint]
    xlLinSendRequest.restype = XLstatus

# vxlapi.h: 5589
if _libs["vxlapi64"].has("xlLinSetSleepMode", "cdecl"):
    xlLinSetSleepMode = _libs["vxlapi64"].get("xlLinSetSleepMode", "cdecl")
    xlLinSetSleepMode.argtypes = [XLportHandle, XLaccess, c_uint, c_ubyte]
    xlLinSetSleepMode.restype = XLstatus

# vxlapi.h: 5591
if _libs["vxlapi64"].has("xlLinWakeUp", "cdecl"):
    xlLinWakeUp = _libs["vxlapi64"].get("xlLinWakeUp", "cdecl")
    xlLinWakeUp.argtypes = [XLportHandle, XLaccess]
    xlLinWakeUp.restype = XLstatus

# vxlapi.h: 5592
if _libs["vxlapi64"].has("xlLinSetChecksum", "cdecl"):
    xlLinSetChecksum = _libs["vxlapi64"].get("xlLinSetChecksum", "cdecl")
    xlLinSetChecksum.argtypes = [XLportHandle, XLaccess, String]
    xlLinSetChecksum.restype = XLstatus

# vxlapi.h: 5593
if _libs["vxlapi64"].has("xlLinSwitchSlave", "cdecl"):
    xlLinSwitchSlave = _libs["vxlapi64"].get("xlLinSwitchSlave", "cdecl")
    xlLinSwitchSlave.argtypes = [XLportHandle, XLaccess, c_ubyte, c_ubyte]
    xlLinSwitchSlave.restype = XLstatus

# vxlapi.h: 5600
if _libs["vxlapi64"].has("xlDAIOSetPWMOutput", "cdecl"):
    xlDAIOSetPWMOutput = _libs["vxlapi64"].get("xlDAIOSetPWMOutput", "cdecl")
    xlDAIOSetPWMOutput.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlDAIOSetPWMOutput.restype = XLstatus

# vxlapi.h: 5602
if _libs["vxlapi64"].has("xlDAIOSetDigitalOutput", "cdecl"):
    xlDAIOSetDigitalOutput = _libs["vxlapi64"].get("xlDAIOSetDigitalOutput", "cdecl")
    xlDAIOSetDigitalOutput.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlDAIOSetDigitalOutput.restype = XLstatus

# vxlapi.h: 5604
if _libs["vxlapi64"].has("xlDAIOSetAnalogOutput", "cdecl"):
    xlDAIOSetAnalogOutput = _libs["vxlapi64"].get("xlDAIOSetAnalogOutput", "cdecl")
    xlDAIOSetAnalogOutput.argtypes = [XLportHandle, XLaccess, c_uint, c_uint, c_uint, c_uint]
    xlDAIOSetAnalogOutput.restype = XLstatus

# vxlapi.h: 5607
if _libs["vxlapi64"].has("xlDAIORequestMeasurement", "cdecl"):
    xlDAIORequestMeasurement = _libs["vxlapi64"].get("xlDAIORequestMeasurement", "cdecl")
    xlDAIORequestMeasurement.argtypes = [XLportHandle, XLaccess]
    xlDAIORequestMeasurement.restype = XLstatus

# vxlapi.h: 5608
if _libs["vxlapi64"].has("xlDAIOSetDigitalParameters", "cdecl"):
    xlDAIOSetDigitalParameters = _libs["vxlapi64"].get("xlDAIOSetDigitalParameters", "cdecl")
    xlDAIOSetDigitalParameters.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlDAIOSetDigitalParameters.restype = XLstatus

# vxlapi.h: 5610
if _libs["vxlapi64"].has("xlDAIOSetAnalogParameters", "cdecl"):
    xlDAIOSetAnalogParameters = _libs["vxlapi64"].get("xlDAIOSetAnalogParameters", "cdecl")
    xlDAIOSetAnalogParameters.argtypes = [XLportHandle, XLaccess, c_uint, c_uint, c_uint]
    xlDAIOSetAnalogParameters.restype = XLstatus

# vxlapi.h: 5613
if _libs["vxlapi64"].has("xlDAIOSetAnalogTrigger", "cdecl"):
    xlDAIOSetAnalogTrigger = _libs["vxlapi64"].get("xlDAIOSetAnalogTrigger", "cdecl")
    xlDAIOSetAnalogTrigger.argtypes = [XLportHandle, XLaccess, c_uint, c_uint, c_uint]
    xlDAIOSetAnalogTrigger.restype = XLstatus

# vxlapi.h: 5616
if _libs["vxlapi64"].has("xlDAIOSetMeasurementFrequency", "cdecl"):
    xlDAIOSetMeasurementFrequency = _libs["vxlapi64"].get("xlDAIOSetMeasurementFrequency", "cdecl")
    xlDAIOSetMeasurementFrequency.argtypes = [XLportHandle, XLaccess, c_uint]
    xlDAIOSetMeasurementFrequency.restype = XLstatus

# vxlapi.h: 5618
if _libs["vxlapi64"].has("xlDAIOSetDigitalTrigger", "cdecl"):
    xlDAIOSetDigitalTrigger = _libs["vxlapi64"].get("xlDAIOSetDigitalTrigger", "cdecl")
    xlDAIOSetDigitalTrigger.argtypes = [XLportHandle, XLaccess, c_uint]
    xlDAIOSetDigitalTrigger.restype = XLstatus

# vxlapi.h: 5624
if _libs["vxlapi64"].has("xlKlineTransmit", "cdecl"):
    xlKlineTransmit = _libs["vxlapi64"].get("xlKlineTransmit", "cdecl")
    xlKlineTransmit.argtypes = [XLportHandle, XLaccess, c_uint, POINTER(c_ubyte)]
    xlKlineTransmit.restype = XLstatus

# vxlapi.h: 5626
if _libs["vxlapi64"].has("xlKlineSetUartParams", "cdecl"):
    xlKlineSetUartParams = _libs["vxlapi64"].get("xlKlineSetUartParams", "cdecl")
    xlKlineSetUartParams.argtypes = [XLportHandle, XLaccess, POINTER(XLklineUartParameter)]
    xlKlineSetUartParams.restype = XLstatus

# vxlapi.h: 5628
if _libs["vxlapi64"].has("xlKlineSwitchHighspeedMode", "cdecl"):
    xlKlineSwitchHighspeedMode = _libs["vxlapi64"].get("xlKlineSwitchHighspeedMode", "cdecl")
    xlKlineSwitchHighspeedMode.argtypes = [XLportHandle, XLaccess, c_uint]
    xlKlineSwitchHighspeedMode.restype = XLstatus

# vxlapi.h: 5630
if _libs["vxlapi64"].has("xlKlineSwitchTesterResistor", "cdecl"):
    xlKlineSwitchTesterResistor = _libs["vxlapi64"].get("xlKlineSwitchTesterResistor", "cdecl")
    xlKlineSwitchTesterResistor.argtypes = [XLportHandle, XLaccess, c_uint]
    xlKlineSwitchTesterResistor.restype = XLstatus

# vxlapi.h: 5632
if _libs["vxlapi64"].has("xlKlineSetBaudrate", "cdecl"):
    xlKlineSetBaudrate = _libs["vxlapi64"].get("xlKlineSetBaudrate", "cdecl")
    xlKlineSetBaudrate.argtypes = [XLportHandle, XLaccess, c_uint]
    xlKlineSetBaudrate.restype = XLstatus

# vxlapi.h: 5634
if _libs["vxlapi64"].has("xlKlineFastInitTester", "cdecl"):
    xlKlineFastInitTester = _libs["vxlapi64"].get("xlKlineFastInitTester", "cdecl")
    xlKlineFastInitTester.argtypes = [XLportHandle, XLaccess, c_uint, POINTER(c_ubyte), POINTER(XLklineInitTester)]
    xlKlineFastInitTester.restype = XLstatus

# vxlapi.h: 5637
if _libs["vxlapi64"].has("xlKlineInit5BdTester", "cdecl"):
    xlKlineInit5BdTester = _libs["vxlapi64"].get("xlKlineInit5BdTester", "cdecl")
    xlKlineInit5BdTester.argtypes = [XLportHandle, XLaccess, POINTER(XLkline5BdTester)]
    xlKlineInit5BdTester.restype = XLstatus

# vxlapi.h: 5639
if _libs["vxlapi64"].has("xlKlineInit5BdEcu", "cdecl"):
    xlKlineInit5BdEcu = _libs["vxlapi64"].get("xlKlineInit5BdEcu", "cdecl")
    xlKlineInit5BdEcu.argtypes = [XLportHandle, XLaccess, POINTER(XLkline5BdEcu)]
    xlKlineInit5BdEcu.restype = XLstatus

# vxlapi.h: 5641
if _libs["vxlapi64"].has("xlKlineSetCommunicationTimingTester", "cdecl"):
    xlKlineSetCommunicationTimingTester = _libs["vxlapi64"].get("xlKlineSetCommunicationTimingTester", "cdecl")
    xlKlineSetCommunicationTimingTester.argtypes = [XLportHandle, XLaccess, POINTER(XLklineSetComTester)]
    xlKlineSetCommunicationTimingTester.restype = XLstatus

# vxlapi.h: 5644
if _libs["vxlapi64"].has("xlKlineSetCommunicationTimingEcu", "cdecl"):
    xlKlineSetCommunicationTimingEcu = _libs["vxlapi64"].get("xlKlineSetCommunicationTimingEcu", "cdecl")
    xlKlineSetCommunicationTimingEcu.argtypes = [XLportHandle, XLaccess, POINTER(XLklineSetComEcu)]
    xlKlineSetCommunicationTimingEcu.restype = XLstatus

# vxlapi.h: 5698
if _libs["vxlapi64"].has("xlMostReceive", "cdecl"):
    xlMostReceive = _libs["vxlapi64"].get("xlMostReceive", "cdecl")
    xlMostReceive.argtypes = [XLportHandle, POINTER(XLmostEvent)]
    xlMostReceive.restype = XLstatus

# vxlapi.h: 5708
if _libs["vxlapi64"].has("xlMostSwitchEventSources", "cdecl"):
    xlMostSwitchEventSources = _libs["vxlapi64"].get("xlMostSwitchEventSources", "cdecl")
    xlMostSwitchEventSources.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort]
    xlMostSwitchEventSources.restype = XLstatus

# vxlapi.h: 5716
if _libs["vxlapi64"].has("xlMostSetAllBypass", "cdecl"):
    xlMostSetAllBypass = _libs["vxlapi64"].get("xlMostSetAllBypass", "cdecl")
    xlMostSetAllBypass.argtypes = [XLportHandle, XLaccess, c_ushort, c_ubyte]
    xlMostSetAllBypass.restype = XLstatus

# vxlapi.h: 5723
if _libs["vxlapi64"].has("xlMostGetAllBypass", "cdecl"):
    xlMostGetAllBypass = _libs["vxlapi64"].get("xlMostGetAllBypass", "cdecl")
    xlMostGetAllBypass.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetAllBypass.restype = XLstatus

# vxlapi.h: 5731
if _libs["vxlapi64"].has("xlMostSetTimingMode", "cdecl"):
    xlMostSetTimingMode = _libs["vxlapi64"].get("xlMostSetTimingMode", "cdecl")
    xlMostSetTimingMode.argtypes = [XLportHandle, XLaccess, c_ushort, c_ubyte]
    xlMostSetTimingMode.restype = XLstatus

# vxlapi.h: 5739
if _libs["vxlapi64"].has("xlMostGetTimingMode", "cdecl"):
    xlMostGetTimingMode = _libs["vxlapi64"].get("xlMostGetTimingMode", "cdecl")
    xlMostGetTimingMode.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetTimingMode.restype = XLstatus

# vxlapi.h: 5748
if _libs["vxlapi64"].has("xlMostSetFrequency", "cdecl"):
    xlMostSetFrequency = _libs["vxlapi64"].get("xlMostSetFrequency", "cdecl")
    xlMostSetFrequency.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort]
    xlMostSetFrequency.restype = XLstatus

# vxlapi.h: 5757
if _libs["vxlapi64"].has("xlMostGetFrequency", "cdecl"):
    xlMostGetFrequency = _libs["vxlapi64"].get("xlMostGetFrequency", "cdecl")
    xlMostGetFrequency.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetFrequency.restype = XLstatus

# vxlapi.h: 5768
if _libs["vxlapi64"].has("xlMostWriteRegister", "cdecl"):
    xlMostWriteRegister = _libs["vxlapi64"].get("xlMostWriteRegister", "cdecl")
    xlMostWriteRegister.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort, c_ubyte, String]
    xlMostWriteRegister.restype = XLstatus

# vxlapi.h: 5779
if _libs["vxlapi64"].has("xlMostReadRegister", "cdecl"):
    xlMostReadRegister = _libs["vxlapi64"].get("xlMostReadRegister", "cdecl")
    xlMostReadRegister.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort, c_ubyte]
    xlMostReadRegister.restype = XLstatus

# vxlapi.h: 5790
if _libs["vxlapi64"].has("xlMostWriteRegisterBit", "cdecl"):
    xlMostWriteRegisterBit = _libs["vxlapi64"].get("xlMostWriteRegisterBit", "cdecl")
    xlMostWriteRegisterBit.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort, c_ubyte, c_ubyte]
    xlMostWriteRegisterBit.restype = XLstatus

# vxlapi.h: 5803
if _libs["vxlapi64"].has("xlMostCtrlTransmit", "cdecl"):
    xlMostCtrlTransmit = _libs["vxlapi64"].get("xlMostCtrlTransmit", "cdecl")
    xlMostCtrlTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostCtrlMsg)]
    xlMostCtrlTransmit.restype = XLstatus

# vxlapi.h: 5816
if _libs["vxlapi64"].has("xlMostAsyncTransmit", "cdecl"):
    xlMostAsyncTransmit = _libs["vxlapi64"].get("xlMostAsyncTransmit", "cdecl")
    xlMostAsyncTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostAsyncMsg)]
    xlMostAsyncTransmit.restype = XLstatus

# vxlapi.h: 5824
if _libs["vxlapi64"].has("xlMostSyncGetAllocTable", "cdecl"):
    xlMostSyncGetAllocTable = _libs["vxlapi64"].get("xlMostSyncGetAllocTable", "cdecl")
    xlMostSyncGetAllocTable.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostSyncGetAllocTable.restype = XLstatus

# vxlapi.h: 5836
if _libs["vxlapi64"].has("xlMostCtrlSyncAudio", "cdecl"):
    xlMostCtrlSyncAudio = _libs["vxlapi64"].get("xlMostCtrlSyncAudio", "cdecl")
    xlMostCtrlSyncAudio.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(c_uint), c_uint, c_uint]
    xlMostCtrlSyncAudio.restype = XLstatus

# vxlapi.h: 5848
if _libs["vxlapi64"].has("xlMostCtrlSyncAudioEx", "cdecl"):
    xlMostCtrlSyncAudioEx = _libs["vxlapi64"].get("xlMostCtrlSyncAudioEx", "cdecl")
    xlMostCtrlSyncAudioEx.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(c_uint), c_uint, c_uint]
    xlMostCtrlSyncAudioEx.restype = XLstatus

# vxlapi.h: 5858
if _libs["vxlapi64"].has("xlMostSyncVolume", "cdecl"):
    xlMostSyncVolume = _libs["vxlapi64"].get("xlMostSyncVolume", "cdecl")
    xlMostSyncVolume.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_ubyte]
    xlMostSyncVolume.restype = XLstatus

# vxlapi.h: 5867
if _libs["vxlapi64"].has("xlMostSyncMute", "cdecl"):
    xlMostSyncMute = _libs["vxlapi64"].get("xlMostSyncMute", "cdecl")
    xlMostSyncMute.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_ubyte]
    xlMostSyncMute.restype = XLstatus

# vxlapi.h: 5876
if _libs["vxlapi64"].has("xlMostSyncGetVolumeStatus", "cdecl"):
    xlMostSyncGetVolumeStatus = _libs["vxlapi64"].get("xlMostSyncGetVolumeStatus", "cdecl")
    xlMostSyncGetVolumeStatus.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostSyncGetVolumeStatus.restype = XLstatus

# vxlapi.h: 5885
if _libs["vxlapi64"].has("xlMostSyncGetMuteStatus", "cdecl"):
    xlMostSyncGetMuteStatus = _libs["vxlapi64"].get("xlMostSyncGetMuteStatus", "cdecl")
    xlMostSyncGetMuteStatus.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostSyncGetMuteStatus.restype = XLstatus

# vxlapi.h: 5893
if _libs["vxlapi64"].has("xlMostGetRxLight", "cdecl"):
    xlMostGetRxLight = _libs["vxlapi64"].get("xlMostGetRxLight", "cdecl")
    xlMostGetRxLight.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetRxLight.restype = XLstatus

# vxlapi.h: 5901
if _libs["vxlapi64"].has("xlMostSetTxLight", "cdecl"):
    xlMostSetTxLight = _libs["vxlapi64"].get("xlMostSetTxLight", "cdecl")
    xlMostSetTxLight.argtypes = [XLportHandle, XLaccess, c_ushort, c_ubyte]
    xlMostSetTxLight.restype = XLstatus

# vxlapi.h: 5909
if _libs["vxlapi64"].has("xlMostGetTxLight", "cdecl"):
    xlMostGetTxLight = _libs["vxlapi64"].get("xlMostGetTxLight", "cdecl")
    xlMostGetTxLight.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetTxLight.restype = XLstatus

# vxlapi.h: 5917
if _libs["vxlapi64"].has("xlMostSetLightPower", "cdecl"):
    xlMostSetLightPower = _libs["vxlapi64"].get("xlMostSetLightPower", "cdecl")
    xlMostSetLightPower.argtypes = [XLportHandle, XLaccess, c_ushort, c_ubyte]
    xlMostSetLightPower.restype = XLstatus

# vxlapi.h: 5927
if _libs["vxlapi64"].has("xlMostGetLockStatus", "cdecl"):
    xlMostGetLockStatus = _libs["vxlapi64"].get("xlMostGetLockStatus", "cdecl")
    xlMostGetLockStatus.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostGetLockStatus.restype = XLstatus

# vxlapi.h: 5938
if _libs["vxlapi64"].has("xlMostGenerateLightError", "cdecl"):
    xlMostGenerateLightError = _libs["vxlapi64"].get("xlMostGenerateLightError", "cdecl")
    xlMostGenerateLightError.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong, XLulong, c_ushort]
    xlMostGenerateLightError.restype = XLstatus

# vxlapi.h: 5950
if _libs["vxlapi64"].has("xlMostGenerateLockError", "cdecl"):
    xlMostGenerateLockError = _libs["vxlapi64"].get("xlMostGenerateLockError", "cdecl")
    xlMostGenerateLockError.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong, XLulong, c_ushort]
    xlMostGenerateLockError.restype = XLstatus

# vxlapi.h: 5961
if _libs["vxlapi64"].has("xlMostCtrlRxBuffer", "cdecl"):
    xlMostCtrlRxBuffer = _libs["vxlapi64"].get("xlMostCtrlRxBuffer", "cdecl")
    xlMostCtrlRxBuffer.argtypes = [XLportHandle, XLaccess, c_ushort, c_ushort]
    xlMostCtrlRxBuffer.restype = XLstatus

# vxlapi.h: 5967
if _libs["vxlapi64"].has("xlMostTwinklePowerLed", "cdecl"):
    xlMostTwinklePowerLed = _libs["vxlapi64"].get("xlMostTwinklePowerLed", "cdecl")
    xlMostTwinklePowerLed.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMostTwinklePowerLed.restype = XLstatus

# vxlapi.h: 5980
if _libs["vxlapi64"].has("xlMostCtrlConfigureBusload", "cdecl"):
    xlMostCtrlConfigureBusload = _libs["vxlapi64"].get("xlMostCtrlConfigureBusload", "cdecl")
    xlMostCtrlConfigureBusload.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostCtrlBusloadConfiguration)]
    xlMostCtrlConfigureBusload.restype = XLstatus

# vxlapi.h: 5993
if _libs["vxlapi64"].has("xlMostCtrlGenerateBusload", "cdecl"):
    xlMostCtrlGenerateBusload = _libs["vxlapi64"].get("xlMostCtrlGenerateBusload", "cdecl")
    xlMostCtrlGenerateBusload.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong]
    xlMostCtrlGenerateBusload.restype = XLstatus

# vxlapi.h: 6006
if _libs["vxlapi64"].has("xlMostAsyncConfigureBusload", "cdecl"):
    xlMostAsyncConfigureBusload = _libs["vxlapi64"].get("xlMostAsyncConfigureBusload", "cdecl")
    xlMostAsyncConfigureBusload.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostAsyncBusloadConfiguration)]
    xlMostAsyncConfigureBusload.restype = XLstatus

# vxlapi.h: 6019
if _libs["vxlapi64"].has("xlMostAsyncGenerateBusload", "cdecl"):
    xlMostAsyncGenerateBusload = _libs["vxlapi64"].get("xlMostAsyncGenerateBusload", "cdecl")
    xlMostAsyncGenerateBusload.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong]
    xlMostAsyncGenerateBusload.restype = XLstatus

# vxlapi.h: 6033
if _libs["vxlapi64"].has("xlMostStreamOpen", "cdecl"):
    xlMostStreamOpen = _libs["vxlapi64"].get("xlMostStreamOpen", "cdecl")
    xlMostStreamOpen.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostStreamOpen)]
    xlMostStreamOpen.restype = XLstatus

# vxlapi.h: 6044
if _libs["vxlapi64"].has("xlMostStreamClose", "cdecl"):
    xlMostStreamClose = _libs["vxlapi64"].get("xlMostStreamClose", "cdecl")
    xlMostStreamClose.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostStreamClose.restype = XLstatus

# vxlapi.h: 6057
if _libs["vxlapi64"].has("xlMostStreamStart", "cdecl"):
    xlMostStreamStart = _libs["vxlapi64"].get("xlMostStreamStart", "cdecl")
    xlMostStreamStart.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, String]
    xlMostStreamStart.restype = XLstatus

# vxlapi.h: 6069
if _libs["vxlapi64"].has("xlMostStreamStop", "cdecl"):
    xlMostStreamStop = _libs["vxlapi64"].get("xlMostStreamStop", "cdecl")
    xlMostStreamStop.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostStreamStop.restype = XLstatus

# vxlapi.h: 6085
if _libs["vxlapi64"].has("xlMostStreamBufferAllocate", "cdecl"):
    xlMostStreamBufferAllocate = _libs["vxlapi64"].get("xlMostStreamBufferAllocate", "cdecl")
    xlMostStreamBufferAllocate.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, POINTER(POINTER(c_ubyte)), POINTER(c_uint)]
    xlMostStreamBufferAllocate.restype = XLstatus

# vxlapi.h: 6098
if _libs["vxlapi64"].has("xlMostStreamBufferDeallocateAll", "cdecl"):
    xlMostStreamBufferDeallocateAll = _libs["vxlapi64"].get("xlMostStreamBufferDeallocateAll", "cdecl")
    xlMostStreamBufferDeallocateAll.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostStreamBufferDeallocateAll.restype = XLstatus

# vxlapi.h: 6111
if _libs["vxlapi64"].has("xlMostStreamBufferSetNext", "cdecl"):
    xlMostStreamBufferSetNext = _libs["vxlapi64"].get("xlMostStreamBufferSetNext", "cdecl")
    xlMostStreamBufferSetNext.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, POINTER(c_ubyte), c_uint]
    xlMostStreamBufferSetNext.restype = XLstatus

# vxlapi.h: 6124
if _libs["vxlapi64"].has("xlMostStreamGetInfo", "cdecl"):
    xlMostStreamGetInfo = _libs["vxlapi64"].get("xlMostStreamGetInfo", "cdecl")
    xlMostStreamGetInfo.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmostStreamInfo)]
    xlMostStreamGetInfo.restype = XLstatus

# vxlapi.h: 6136
if _libs["vxlapi64"].has("xlMostStreamBufferClearAll", "cdecl"):
    xlMostStreamBufferClearAll = _libs["vxlapi64"].get("xlMostStreamBufferClearAll", "cdecl")
    xlMostStreamBufferClearAll.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMostStreamBufferClearAll.restype = XLstatus

# vxlapi.h: 6150
if _libs["vxlapi64"].has("xlFrSetConfiguration", "cdecl"):
    xlFrSetConfiguration = _libs["vxlapi64"].get("xlFrSetConfiguration", "cdecl")
    xlFrSetConfiguration.argtypes = [XLportHandle, XLaccess, POINTER(XLfrClusterConfig)]
    xlFrSetConfiguration.restype = XLstatus

# vxlapi.h: 6161
if _libs["vxlapi64"].has("xlFrGetChannelConfiguration", "cdecl"):
    xlFrGetChannelConfiguration = _libs["vxlapi64"].get("xlFrGetChannelConfiguration", "cdecl")
    xlFrGetChannelConfiguration.argtypes = [XLportHandle, XLaccess, POINTER(XLfrChannelConfig)]
    xlFrGetChannelConfiguration.restype = XLstatus

# vxlapi.h: 6171
if _libs["vxlapi64"].has("xlFrSetMode", "cdecl"):
    xlFrSetMode = _libs["vxlapi64"].get("xlFrSetMode", "cdecl")
    xlFrSetMode.argtypes = [XLportHandle, XLaccess, POINTER(XLfrMode)]
    xlFrSetMode.restype = XLstatus

# vxlapi.h: 6181
if _libs["vxlapi64"].has("xlFrInitStartupAndSync", "cdecl"):
    xlFrInitStartupAndSync = _libs["vxlapi64"].get("xlFrInitStartupAndSync", "cdecl")
    xlFrInitStartupAndSync.argtypes = [XLportHandle, XLaccess, POINTER(XLfrEvent)]
    xlFrInitStartupAndSync.restype = XLstatus

# vxlapi.h: 6192
if _libs["vxlapi64"].has("xlFrSetupSymbolWindow", "cdecl"):
    xlFrSetupSymbolWindow = _libs["vxlapi64"].get("xlFrSetupSymbolWindow", "cdecl")
    xlFrSetupSymbolWindow.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlFrSetupSymbolWindow.restype = XLstatus

# vxlapi.h: 6201
if _libs["vxlapi64"].has("xlFrReceive", "cdecl"):
    xlFrReceive = _libs["vxlapi64"].get("xlFrReceive", "cdecl")
    xlFrReceive.argtypes = [XLportHandle, POINTER(XLfrEvent)]
    xlFrReceive.restype = XLstatus

# vxlapi.h: 6211
if _libs["vxlapi64"].has("xlFrTransmit", "cdecl"):
    xlFrTransmit = _libs["vxlapi64"].get("xlFrTransmit", "cdecl")
    xlFrTransmit.argtypes = [XLportHandle, XLaccess, POINTER(XLfrEvent)]
    xlFrTransmit.restype = XLstatus

# vxlapi.h: 6222
if _libs["vxlapi64"].has("xlFrSetTransceiverMode", "cdecl"):
    xlFrSetTransceiverMode = _libs["vxlapi64"].get("xlFrSetTransceiverMode", "cdecl")
    xlFrSetTransceiverMode.argtypes = [XLportHandle, XLaccess, c_uint, c_uint]
    xlFrSetTransceiverMode.restype = XLstatus

# vxlapi.h: 6232
if _libs["vxlapi64"].has("xlFrSendSymbolWindow", "cdecl"):
    xlFrSendSymbolWindow = _libs["vxlapi64"].get("xlFrSendSymbolWindow", "cdecl")
    xlFrSendSymbolWindow.argtypes = [XLportHandle, XLaccess, c_uint]
    xlFrSendSymbolWindow.restype = XLstatus

# vxlapi.h: 6242
if _libs["vxlapi64"].has("xlFrActivateSpy", "cdecl"):
    xlFrActivateSpy = _libs["vxlapi64"].get("xlFrActivateSpy", "cdecl")
    xlFrActivateSpy.argtypes = [XLportHandle, XLaccess, c_uint]
    xlFrActivateSpy.restype = XLstatus

# vxlapi.h: 6251
if _libs["vxlapi64"].has("xlFrSetAcceptanceFilter", "cdecl"):
    xlFrSetAcceptanceFilter = _libs["vxlapi64"].get("xlFrSetAcceptanceFilter", "cdecl")
    xlFrSetAcceptanceFilter.argtypes = [XLportHandle, XLaccess, POINTER(XLfrAcceptanceFilter)]
    xlFrSetAcceptanceFilter.restype = XLstatus

# vxlapi.h: 6258
if _libs["vxlapi64"].has("xlGetRemoteDriverConfig", "cdecl"):
    xlGetRemoteDriverConfig = _libs["vxlapi64"].get("xlGetRemoteDriverConfig", "cdecl")
    xlGetRemoteDriverConfig.argtypes = [POINTER(XLdriverConfig)]
    xlGetRemoteDriverConfig.restype = XLstatus

# vxlapi.h: 6268
if _libs["vxlapi64"].has("xlGetRemoteDeviceInfo", "cdecl"):
    xlGetRemoteDeviceInfo = _libs["vxlapi64"].get("xlGetRemoteDeviceInfo", "cdecl")
    xlGetRemoteDeviceInfo.argtypes = [POINTER(POINTER(XLremoteDeviceInfo)), POINTER(c_uint), c_uint]
    xlGetRemoteDeviceInfo.restype = XLstatus

# vxlapi.h: 6275
if _libs["vxlapi64"].has("xlReleaseRemoteDeviceInfo", "cdecl"):
    xlReleaseRemoteDeviceInfo = _libs["vxlapi64"].get("xlReleaseRemoteDeviceInfo", "cdecl")
    xlReleaseRemoteDeviceInfo.argtypes = [POINTER(POINTER(XLremoteDeviceInfo))]
    xlReleaseRemoteDeviceInfo.restype = XLstatus

# vxlapi.h: 6285
if _libs["vxlapi64"].has("xlAddRemoteDevice", "cdecl"):
    xlAddRemoteDevice = _libs["vxlapi64"].get("xlAddRemoteDevice", "cdecl")
    xlAddRemoteDevice.argtypes = [XLremoteHandle, XLdeviceAccess, c_uint]
    xlAddRemoteDevice.restype = XLstatus

# vxlapi.h: 6294
if _libs["vxlapi64"].has("xlRemoveRemoteDevice", "cdecl"):
    xlRemoveRemoteDevice = _libs["vxlapi64"].get("xlRemoveRemoteDevice", "cdecl")
    xlRemoveRemoteDevice.argtypes = [XLremoteHandle, XLdeviceAccess, c_uint]
    xlRemoveRemoteDevice.restype = XLstatus

# vxlapi.h: 6303
if _libs["vxlapi64"].has("xlUpdateRemoteDeviceInfo", "cdecl"):
    xlUpdateRemoteDeviceInfo = _libs["vxlapi64"].get("xlUpdateRemoteDeviceInfo", "cdecl")
    xlUpdateRemoteDeviceInfo.argtypes = [POINTER(XLremoteDeviceInfo), c_uint]
    xlUpdateRemoteDeviceInfo.restype = XLstatus

# vxlapi.h: 6313
if _libs["vxlapi64"].has("xlGetRemoteHwInfo", "cdecl"):
    xlGetRemoteHwInfo = _libs["vxlapi64"].get("xlGetRemoteHwInfo", "cdecl")
    xlGetRemoteHwInfo.argtypes = [XLremoteHandle, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    xlGetRemoteHwInfo.restype = XLstatus

# vxlapi.h: 6324
if _libs["vxlapi64"].has("xlRegisterRemoteDevice", "cdecl"):
    xlRegisterRemoteDevice = _libs["vxlapi64"].get("xlRegisterRemoteDevice", "cdecl")
    xlRegisterRemoteDevice.argtypes = [c_int, POINTER(XLipAddress), c_uint]
    xlRegisterRemoteDevice.restype = XLstatus

# vxlapi.h: 6337
if _libs["vxlapi64"].has("xlIoSetTriggerMode", "cdecl"):
    xlIoSetTriggerMode = _libs["vxlapi64"].get("xlIoSetTriggerMode", "cdecl")
    xlIoSetTriggerMode.argtypes = [XLportHandle, XLaccess, POINTER(XLdaioTriggerMode)]
    xlIoSetTriggerMode.restype = XLstatus

# vxlapi.h: 6344
if _libs["vxlapi64"].has("xlIoSetDigitalOutput", "cdecl"):
    xlIoSetDigitalOutput = _libs["vxlapi64"].get("xlIoSetDigitalOutput", "cdecl")
    xlIoSetDigitalOutput.argtypes = [XLportHandle, XLaccess, POINTER(XLdaioDigitalParams)]
    xlIoSetDigitalOutput.restype = XLstatus

# vxlapi.h: 6351
if _libs["vxlapi64"].has("xlIoConfigurePorts", "cdecl"):
    xlIoConfigurePorts = _libs["vxlapi64"].get("xlIoConfigurePorts", "cdecl")
    xlIoConfigurePorts.argtypes = [XLportHandle, XLaccess, POINTER(XLdaioSetPort)]
    xlIoConfigurePorts.restype = XLstatus

# vxlapi.h: 6358
if _libs["vxlapi64"].has("xlIoSetDigInThreshold", "cdecl"):
    xlIoSetDigInThreshold = _libs["vxlapi64"].get("xlIoSetDigInThreshold", "cdecl")
    xlIoSetDigInThreshold.argtypes = [XLportHandle, XLaccess, c_uint]
    xlIoSetDigInThreshold.restype = XLstatus

# vxlapi.h: 6365
if _libs["vxlapi64"].has("xlIoSetDigOutLevel", "cdecl"):
    xlIoSetDigOutLevel = _libs["vxlapi64"].get("xlIoSetDigOutLevel", "cdecl")
    xlIoSetDigOutLevel.argtypes = [XLportHandle, XLaccess, c_uint]
    xlIoSetDigOutLevel.restype = XLstatus

# vxlapi.h: 6372
if _libs["vxlapi64"].has("xlIoSetAnalogOutput", "cdecl"):
    xlIoSetAnalogOutput = _libs["vxlapi64"].get("xlIoSetAnalogOutput", "cdecl")
    xlIoSetAnalogOutput.argtypes = [XLportHandle, XLaccess, POINTER(XLdaioAnalogParams)]
    xlIoSetAnalogOutput.restype = XLstatus

# vxlapi.h: 6379
if _libs["vxlapi64"].has("xlIoStartSampling", "cdecl"):
    xlIoStartSampling = _libs["vxlapi64"].get("xlIoStartSampling", "cdecl")
    xlIoStartSampling.argtypes = [XLportHandle, XLaccess, c_uint]
    xlIoStartSampling.restype = XLstatus

# vxlapi.h: 6413
if _libs["vxlapi64"].has("xlMost150Receive", "cdecl"):
    xlMost150Receive = _libs["vxlapi64"].get("xlMost150Receive", "cdecl")
    xlMost150Receive.argtypes = [XLportHandle, POINTER(XLmost150event)]
    xlMost150Receive.restype = XLstatus

# vxlapi.h: 6419
if _libs["vxlapi64"].has("xlMost150TwinklePowerLed", "cdecl"):
    xlMost150TwinklePowerLed = _libs["vxlapi64"].get("xlMost150TwinklePowerLed", "cdecl")
    xlMost150TwinklePowerLed.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150TwinklePowerLed.restype = XLstatus

# vxlapi.h: 6428
if _libs["vxlapi64"].has("xlMost150SwitchEventSources", "cdecl"):
    xlMost150SwitchEventSources = _libs["vxlapi64"].get("xlMost150SwitchEventSources", "cdecl")
    xlMost150SwitchEventSources.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SwitchEventSources.restype = XLstatus

# vxlapi.h: 6437
if _libs["vxlapi64"].has("xlMost150SetDeviceMode", "cdecl"):
    xlMost150SetDeviceMode = _libs["vxlapi64"].get("xlMost150SetDeviceMode", "cdecl")
    xlMost150SetDeviceMode.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetDeviceMode.restype = XLstatus

# vxlapi.h: 6444
if _libs["vxlapi64"].has("xlMost150GetDeviceMode", "cdecl"):
    xlMost150GetDeviceMode = _libs["vxlapi64"].get("xlMost150GetDeviceMode", "cdecl")
    xlMost150GetDeviceMode.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetDeviceMode.restype = XLstatus

# vxlapi.h: 6452
if _libs["vxlapi64"].has("xlMost150SetSPDIFMode", "cdecl"):
    xlMost150SetSPDIFMode = _libs["vxlapi64"].get("xlMost150SetSPDIFMode", "cdecl")
    xlMost150SetSPDIFMode.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetSPDIFMode.restype = XLstatus

# vxlapi.h: 6460
if _libs["vxlapi64"].has("xlMost150GetSPDIFMode", "cdecl"):
    xlMost150GetSPDIFMode = _libs["vxlapi64"].get("xlMost150GetSPDIFMode", "cdecl")
    xlMost150GetSPDIFMode.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetSPDIFMode.restype = XLstatus

# vxlapi.h: 6468
if _libs["vxlapi64"].has("xlMost150SetSpecialNodeInfo", "cdecl"):
    xlMost150SetSpecialNodeInfo = _libs["vxlapi64"].get("xlMost150SetSpecialNodeInfo", "cdecl")
    xlMost150SetSpecialNodeInfo.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150SetSpecialNodeInfo)]
    xlMost150SetSpecialNodeInfo.restype = XLstatus

# vxlapi.h: 6475
if _libs["vxlapi64"].has("xlMost150GetSpecialNodeInfo", "cdecl"):
    xlMost150GetSpecialNodeInfo = _libs["vxlapi64"].get("xlMost150GetSpecialNodeInfo", "cdecl")
    xlMost150GetSpecialNodeInfo.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150GetSpecialNodeInfo.restype = XLstatus

# vxlapi.h: 6482
if _libs["vxlapi64"].has("xlMost150SetFrequency", "cdecl"):
    xlMost150SetFrequency = _libs["vxlapi64"].get("xlMost150SetFrequency", "cdecl")
    xlMost150SetFrequency.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetFrequency.restype = XLstatus

# vxlapi.h: 6488
if _libs["vxlapi64"].has("xlMost150GetFrequency", "cdecl"):
    xlMost150GetFrequency = _libs["vxlapi64"].get("xlMost150GetFrequency", "cdecl")
    xlMost150GetFrequency.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetFrequency.restype = XLstatus

# vxlapi.h: 6495
if _libs["vxlapi64"].has("xlMost150CtrlTransmit", "cdecl"):
    xlMost150CtrlTransmit = _libs["vxlapi64"].get("xlMost150CtrlTransmit", "cdecl")
    xlMost150CtrlTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150CtrlTxMsg)]
    xlMost150CtrlTransmit.restype = XLstatus

# vxlapi.h: 6502
if _libs["vxlapi64"].has("xlMost150AsyncTransmit", "cdecl"):
    xlMost150AsyncTransmit = _libs["vxlapi64"].get("xlMost150AsyncTransmit", "cdecl")
    xlMost150AsyncTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150AsyncTxMsg)]
    xlMost150AsyncTransmit.restype = XLstatus

# vxlapi.h: 6509
if _libs["vxlapi64"].has("xlMost150EthernetTransmit", "cdecl"):
    xlMost150EthernetTransmit = _libs["vxlapi64"].get("xlMost150EthernetTransmit", "cdecl")
    xlMost150EthernetTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150EthernetTxMsg)]
    xlMost150EthernetTransmit.restype = XLstatus

# vxlapi.h: 6515
if _libs["vxlapi64"].has("xlMost150GetSystemLockFlag", "cdecl"):
    xlMost150GetSystemLockFlag = _libs["vxlapi64"].get("xlMost150GetSystemLockFlag", "cdecl")
    xlMost150GetSystemLockFlag.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetSystemLockFlag.restype = XLstatus

# vxlapi.h: 6521
if _libs["vxlapi64"].has("xlMost150GetShutdownFlag", "cdecl"):
    xlMost150GetShutdownFlag = _libs["vxlapi64"].get("xlMost150GetShutdownFlag", "cdecl")
    xlMost150GetShutdownFlag.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetShutdownFlag.restype = XLstatus

# vxlapi.h: 6527
if _libs["vxlapi64"].has("xlMost150Shutdown", "cdecl"):
    xlMost150Shutdown = _libs["vxlapi64"].get("xlMost150Shutdown", "cdecl")
    xlMost150Shutdown.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150Shutdown.restype = XLstatus

# vxlapi.h: 6533
if _libs["vxlapi64"].has("xlMost150Startup", "cdecl"):
    xlMost150Startup = _libs["vxlapi64"].get("xlMost150Startup", "cdecl")
    xlMost150Startup.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150Startup.restype = XLstatus

# vxlapi.h: 6540
if _libs["vxlapi64"].has("xlMost150SyncGetAllocTable", "cdecl"):
    xlMost150SyncGetAllocTable = _libs["vxlapi64"].get("xlMost150SyncGetAllocTable", "cdecl")
    xlMost150SyncGetAllocTable.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150SyncGetAllocTable.restype = XLstatus

# vxlapi.h: 6547
if _libs["vxlapi64"].has("xlMost150CtrlSyncAudio", "cdecl"):
    xlMost150CtrlSyncAudio = _libs["vxlapi64"].get("xlMost150CtrlSyncAudio", "cdecl")
    xlMost150CtrlSyncAudio.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150SyncAudioParameter)]
    xlMost150CtrlSyncAudio.restype = XLstatus

# vxlapi.h: 6555
if _libs["vxlapi64"].has("xlMost150SyncSetVolume", "cdecl"):
    xlMost150SyncSetVolume = _libs["vxlapi64"].get("xlMost150SyncSetVolume", "cdecl")
    xlMost150SyncSetVolume.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint]
    xlMost150SyncSetVolume.restype = XLstatus

# vxlapi.h: 6563
if _libs["vxlapi64"].has("xlMost150SyncGetVolume", "cdecl"):
    xlMost150SyncGetVolume = _libs["vxlapi64"].get("xlMost150SyncGetVolume", "cdecl")
    xlMost150SyncGetVolume.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SyncGetVolume.restype = XLstatus

# vxlapi.h: 6571
if _libs["vxlapi64"].has("xlMost150SyncSetMute", "cdecl"):
    xlMost150SyncSetMute = _libs["vxlapi64"].get("xlMost150SyncSetMute", "cdecl")
    xlMost150SyncSetMute.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint]
    xlMost150SyncSetMute.restype = XLstatus

# vxlapi.h: 6578
if _libs["vxlapi64"].has("xlMost150SyncGetMute", "cdecl"):
    xlMost150SyncGetMute = _libs["vxlapi64"].get("xlMost150SyncGetMute", "cdecl")
    xlMost150SyncGetMute.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SyncGetMute.restype = XLstatus

# vxlapi.h: 6585
if _libs["vxlapi64"].has("xlMost150GetRxLightLockStatus", "cdecl"):
    xlMost150GetRxLightLockStatus = _libs["vxlapi64"].get("xlMost150GetRxLightLockStatus", "cdecl")
    xlMost150GetRxLightLockStatus.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150GetRxLightLockStatus.restype = XLstatus

# vxlapi.h: 6593
if _libs["vxlapi64"].has("xlMost150SetTxLight", "cdecl"):
    xlMost150SetTxLight = _libs["vxlapi64"].get("xlMost150SetTxLight", "cdecl")
    xlMost150SetTxLight.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetTxLight.restype = XLstatus

# vxlapi.h: 6599
if _libs["vxlapi64"].has("xlMost150GetTxLight", "cdecl"):
    xlMost150GetTxLight = _libs["vxlapi64"].get("xlMost150GetTxLight", "cdecl")
    xlMost150GetTxLight.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetTxLight.restype = XLstatus

# vxlapi.h: 6607
if _libs["vxlapi64"].has("xlMost150SetTxLightPower", "cdecl"):
    xlMost150SetTxLightPower = _libs["vxlapi64"].get("xlMost150SetTxLightPower", "cdecl")
    xlMost150SetTxLightPower.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetTxLightPower.restype = XLstatus

# vxlapi.h: 6617
if _libs["vxlapi64"].has("xlMost150GenerateLightError", "cdecl"):
    xlMost150GenerateLightError = _libs["vxlapi64"].get("xlMost150GenerateLightError", "cdecl")
    xlMost150GenerateLightError.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint, c_uint]
    xlMost150GenerateLightError.restype = XLstatus

# vxlapi.h: 6628
if _libs["vxlapi64"].has("xlMost150GenerateLockError", "cdecl"):
    xlMost150GenerateLockError = _libs["vxlapi64"].get("xlMost150GenerateLockError", "cdecl")
    xlMost150GenerateLockError.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint, c_uint]
    xlMost150GenerateLockError.restype = XLstatus

# vxlapi.h: 6638
if _libs["vxlapi64"].has("xlMost150ConfigureRxBuffer", "cdecl"):
    xlMost150ConfigureRxBuffer = _libs["vxlapi64"].get("xlMost150ConfigureRxBuffer", "cdecl")
    xlMost150ConfigureRxBuffer.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint]
    xlMost150ConfigureRxBuffer.restype = XLstatus

# vxlapi.h: 6645
if _libs["vxlapi64"].has("xlMost150CtrlConfigureBusload", "cdecl"):
    xlMost150CtrlConfigureBusload = _libs["vxlapi64"].get("xlMost150CtrlConfigureBusload", "cdecl")
    xlMost150CtrlConfigureBusload.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150CtrlBusloadConfig)]
    xlMost150CtrlConfigureBusload.restype = XLstatus

# vxlapi.h: 6655
if _libs["vxlapi64"].has("xlMost150CtrlGenerateBusload", "cdecl"):
    xlMost150CtrlGenerateBusload = _libs["vxlapi64"].get("xlMost150CtrlGenerateBusload", "cdecl")
    xlMost150CtrlGenerateBusload.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong]
    xlMost150CtrlGenerateBusload.restype = XLstatus

# vxlapi.h: 6662
if _libs["vxlapi64"].has("xlMost150AsyncConfigureBusload", "cdecl"):
    xlMost150AsyncConfigureBusload = _libs["vxlapi64"].get("xlMost150AsyncConfigureBusload", "cdecl")
    xlMost150AsyncConfigureBusload.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150AsyncBusloadConfig)]
    xlMost150AsyncConfigureBusload.restype = XLstatus

# vxlapi.h: 6672
if _libs["vxlapi64"].has("xlMost150AsyncGenerateBusload", "cdecl"):
    xlMost150AsyncGenerateBusload = _libs["vxlapi64"].get("xlMost150AsyncGenerateBusload", "cdecl")
    xlMost150AsyncGenerateBusload.argtypes = [XLportHandle, XLaccess, c_ushort, XLulong]
    xlMost150AsyncGenerateBusload.restype = XLstatus

# vxlapi.h: 6680
if _libs["vxlapi64"].has("xlMost150SetECLLine", "cdecl"):
    xlMost150SetECLLine = _libs["vxlapi64"].get("xlMost150SetECLLine", "cdecl")
    xlMost150SetECLLine.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetECLLine.restype = XLstatus

# vxlapi.h: 6688
if _libs["vxlapi64"].has("xlMost150SetECLTermination", "cdecl"):
    xlMost150SetECLTermination = _libs["vxlapi64"].get("xlMost150SetECLTermination", "cdecl")
    xlMost150SetECLTermination.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetECLTermination.restype = XLstatus

# vxlapi.h: 6695
if _libs["vxlapi64"].has("xlMost150GetECLInfo", "cdecl"):
    xlMost150GetECLInfo = _libs["vxlapi64"].get("xlMost150GetECLInfo", "cdecl")
    xlMost150GetECLInfo.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetECLInfo.restype = XLstatus

# vxlapi.h: 6707
if _libs["vxlapi64"].has("xlMost150StreamOpen", "cdecl"):
    xlMost150StreamOpen = _libs["vxlapi64"].get("xlMost150StreamOpen", "cdecl")
    xlMost150StreamOpen.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150StreamOpen)]
    xlMost150StreamOpen.restype = XLstatus

# vxlapi.h: 6718
if _libs["vxlapi64"].has("xlMost150StreamClose", "cdecl"):
    xlMost150StreamClose = _libs["vxlapi64"].get("xlMost150StreamClose", "cdecl")
    xlMost150StreamClose.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150StreamClose.restype = XLstatus

# vxlapi.h: 6732
if _libs["vxlapi64"].has("xlMost150StreamStart", "cdecl"):
    xlMost150StreamStart = _libs["vxlapi64"].get("xlMost150StreamStart", "cdecl")
    xlMost150StreamStart.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint, POINTER(c_uint)]
    xlMost150StreamStart.restype = XLstatus

# vxlapi.h: 6745
if _libs["vxlapi64"].has("xlMost150StreamStop", "cdecl"):
    xlMost150StreamStop = _libs["vxlapi64"].get("xlMost150StreamStop", "cdecl")
    xlMost150StreamStop.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150StreamStop.restype = XLstatus

# vxlapi.h: 6760
if _libs["vxlapi64"].has("xlMost150StreamTransmitData", "cdecl"):
    xlMost150StreamTransmitData = _libs["vxlapi64"].get("xlMost150StreamTransmitData", "cdecl")
    xlMost150StreamTransmitData.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, POINTER(c_ubyte), POINTER(c_uint)]
    xlMost150StreamTransmitData.restype = XLstatus

# vxlapi.h: 6773
if _libs["vxlapi64"].has("xlMost150StreamClearTxFifo", "cdecl"):
    xlMost150StreamClearTxFifo = _libs["vxlapi64"].get("xlMost150StreamClearTxFifo", "cdecl")
    xlMost150StreamClearTxFifo.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150StreamClearTxFifo.restype = XLstatus

# vxlapi.h: 6785
if _libs["vxlapi64"].has("xlMost150StreamGetInfo", "cdecl"):
    xlMost150StreamGetInfo = _libs["vxlapi64"].get("xlMost150StreamGetInfo", "cdecl")
    xlMost150StreamGetInfo.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(XLmost150StreamInfo)]
    xlMost150StreamGetInfo.restype = XLstatus

# vxlapi.h: 6794
if _libs["vxlapi64"].has("xlMost150StreamInitRxFifo", "cdecl"):
    xlMost150StreamInitRxFifo = _libs["vxlapi64"].get("xlMost150StreamInitRxFifo", "cdecl")
    xlMost150StreamInitRxFifo.argtypes = [XLportHandle, XLaccess]
    xlMost150StreamInitRxFifo.restype = XLstatus

# vxlapi.h: 6809
if _libs["vxlapi64"].has("xlMost150StreamReceiveData", "cdecl"):
    xlMost150StreamReceiveData = _libs["vxlapi64"].get("xlMost150StreamReceiveData", "cdecl")
    xlMost150StreamReceiveData.argtypes = [XLportHandle, XLaccess, POINTER(c_ubyte), POINTER(c_uint)]
    xlMost150StreamReceiveData.restype = XLstatus

# vxlapi.h: 6822
if _libs["vxlapi64"].has("xlMost150GenerateBypassStress", "cdecl"):
    xlMost150GenerateBypassStress = _libs["vxlapi64"].get("xlMost150GenerateBypassStress", "cdecl")
    xlMost150GenerateBypassStress.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, c_uint, c_uint]
    xlMost150GenerateBypassStress.restype = XLstatus

# vxlapi.h: 6836
if _libs["vxlapi64"].has("xlMost150EclConfigureSeq", "cdecl"):
    xlMost150EclConfigureSeq = _libs["vxlapi64"].get("xlMost150EclConfigureSeq", "cdecl")
    xlMost150EclConfigureSeq.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint, POINTER(c_uint), POINTER(c_uint)]
    xlMost150EclConfigureSeq.restype = XLstatus

# vxlapi.h: 6847
if _libs["vxlapi64"].has("xlMost150EclGenerateSeq", "cdecl"):
    xlMost150EclGenerateSeq = _libs["vxlapi64"].get("xlMost150EclGenerateSeq", "cdecl")
    xlMost150EclGenerateSeq.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150EclGenerateSeq.restype = XLstatus

# vxlapi.h: 6857
if _libs["vxlapi64"].has("xlMost150SetECLGlitchFilter", "cdecl"):
    xlMost150SetECLGlitchFilter = _libs["vxlapi64"].get("xlMost150SetECLGlitchFilter", "cdecl")
    xlMost150SetECLGlitchFilter.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetECLGlitchFilter.restype = XLstatus

# vxlapi.h: 6869
if _libs["vxlapi64"].has("xlMost150SetSSOResult", "cdecl"):
    xlMost150SetSSOResult = _libs["vxlapi64"].get("xlMost150SetSSOResult", "cdecl")
    xlMost150SetSSOResult.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlMost150SetSSOResult.restype = XLstatus

# vxlapi.h: 6879
if _libs["vxlapi64"].has("xlMost150GetSSOResult", "cdecl"):
    xlMost150GetSSOResult = _libs["vxlapi64"].get("xlMost150GetSSOResult", "cdecl")
    xlMost150GetSSOResult.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlMost150GetSSOResult.restype = XLstatus

# vxlapi.h: 6908
if _libs["vxlapi64"].has("xlEthSetConfig", "cdecl"):
    xlEthSetConfig = _libs["vxlapi64"].get("xlEthSetConfig", "cdecl")
    xlEthSetConfig.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(T_XL_ETH_CONFIG)]
    xlEthSetConfig.restype = XLstatus

# vxlapi.h: 6916
if _libs["vxlapi64"].has("xlEthGetConfig", "cdecl"):
    xlEthGetConfig = _libs["vxlapi64"].get("xlEthGetConfig", "cdecl")
    xlEthGetConfig.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(T_XL_ETH_CONFIG)]
    xlEthGetConfig.restype = XLstatus

# vxlapi.h: 6930
if _libs["vxlapi64"].has("xlEthReceive", "cdecl"):
    xlEthReceive = _libs["vxlapi64"].get("xlEthReceive", "cdecl")
    xlEthReceive.argtypes = [XLportHandle, POINTER(T_XL_ETH_EVENT)]
    xlEthReceive.restype = XLstatus

# vxlapi.h: 6938
if _libs["vxlapi64"].has("xlEthSetBypass", "cdecl"):
    xlEthSetBypass = _libs["vxlapi64"].get("xlEthSetBypass", "cdecl")
    xlEthSetBypass.argtypes = [XLportHandle, XLaccess, c_ushort, c_uint]
    xlEthSetBypass.restype = XLstatus

# vxlapi.h: 6945
if _libs["vxlapi64"].has("xlEthTwinkleStatusLed", "cdecl"):
    xlEthTwinkleStatusLed = _libs["vxlapi64"].get("xlEthTwinkleStatusLed", "cdecl")
    xlEthTwinkleStatusLed.argtypes = [XLportHandle, XLaccess, c_ushort]
    xlEthTwinkleStatusLed.restype = XLstatus

# vxlapi.h: 6953
if _libs["vxlapi64"].has("xlEthTransmit", "cdecl"):
    xlEthTransmit = _libs["vxlapi64"].get("xlEthTransmit", "cdecl")
    xlEthTransmit.argtypes = [XLportHandle, XLaccess, c_ushort, POINTER(T_XL_ETH_DATAFRAME_TX)]
    xlEthTransmit.restype = XLstatus

# vxlapi.h: 6973
for _lib in _libs.values():
    if not _lib.has("xlNetEthOpenNetwork", "cdecl"):
        continue
    xlNetEthOpenNetwork = _lib.get("xlNetEthOpenNetwork", "cdecl")
    xlNetEthOpenNetwork.argtypes = [String, POINTER(XLnetworkHandle), String, c_uint, c_uint]
    xlNetEthOpenNetwork.restype = XLstatus
    break

# vxlapi.h: 6983
for _lib in _libs.values():
    if not _lib.has("xlNetCloseNetwork", "cdecl"):
        continue
    xlNetCloseNetwork = _lib.get("xlNetCloseNetwork", "cdecl")
    xlNetCloseNetwork.argtypes = [XLnetworkHandle]
    xlNetCloseNetwork.restype = XLstatus
    break

# vxlapi.h: 6994
for _lib in _libs.values():
    if not _lib.has("xlNetOpenVirtualPort", "cdecl"):
        continue
    xlNetOpenVirtualPort = _lib.get("xlNetOpenVirtualPort", "cdecl")
    xlNetOpenVirtualPort.argtypes = [XLnetworkHandle, String, POINTER(XLethPortHandle), XLrxHandle]
    xlNetOpenVirtualPort.restype = XLstatus
    break

# vxlapi.h: 7007
for _lib in _libs.values():
    if not _lib.has("xlNetAddVirtualPort", "cdecl"):
        continue
    xlNetAddVirtualPort = _lib.get("xlNetAddVirtualPort", "cdecl")
    xlNetAddVirtualPort.argtypes = [XLnetworkHandle, String, String, POINTER(XLethPortHandle), XLrxHandle]
    xlNetAddVirtualPort.restype = XLstatus
    break

# vxlapi.h: 7021
for _lib in _libs.values():
    if not _lib.has("xlNetConnectMeasurementPoint", "cdecl"):
        continue
    xlNetConnectMeasurementPoint = _lib.get("xlNetConnectMeasurementPoint", "cdecl")
    xlNetConnectMeasurementPoint.argtypes = [XLnetworkHandle, String, POINTER(XLethPortHandle), XLrxHandle]
    xlNetConnectMeasurementPoint.restype = XLstatus
    break

# vxlapi.h: 7032
for _lib in _libs.values():
    if not _lib.has("xlNetActivateNetwork", "cdecl"):
        continue
    xlNetActivateNetwork = _lib.get("xlNetActivateNetwork", "cdecl")
    xlNetActivateNetwork.argtypes = [XLnetworkHandle]
    xlNetActivateNetwork.restype = XLstatus
    break

# vxlapi.h: 7040
for _lib in _libs.values():
    if not _lib.has("xlNetDeactivateNetwork", "cdecl"):
        continue
    xlNetDeactivateNetwork = _lib.get("xlNetDeactivateNetwork", "cdecl")
    xlNetDeactivateNetwork.argtypes = [XLnetworkHandle]
    xlNetDeactivateNetwork.restype = XLstatus
    break

# vxlapi.h: 7051
for _lib in _libs.values():
    if not _lib.has("xlNetEthSend", "cdecl"):
        continue
    xlNetEthSend = _lib.get("xlNetEthSend", "cdecl")
    xlNetEthSend.argtypes = [XLnetworkHandle, XLethPortHandle, c_ushort, POINTER(T_XL_NET_ETH_DATAFRAME_TX)]
    xlNetEthSend.restype = XLstatus
    break

# vxlapi.h: 7064
for _lib in _libs.values():
    if not _lib.has("xlNetEthReceive", "cdecl"):
        continue
    xlNetEthReceive = _lib.get("xlNetEthReceive", "cdecl")
    xlNetEthReceive.argtypes = [XLnetworkHandle, POINTER(T_XL_NET_ETH_EVENT), POINTER(c_uint), POINTER(XLrxHandle)]
    xlNetEthReceive.restype = XLstatus
    break

# vxlapi.h: 7075
for _lib in _libs.values():
    if not _lib.has("xlNetEthRequestChannelStatus", "cdecl"):
        continue
    xlNetEthRequestChannelStatus = _lib.get("xlNetEthRequestChannelStatus", "cdecl")
    xlNetEthRequestChannelStatus.argtypes = [XLnetworkHandle]
    xlNetEthRequestChannelStatus.restype = XLstatus
    break

# vxlapi.h: 7089
for _lib in _libs.values():
    if not _lib.has("xlNetSetNotification", "cdecl"):
        continue
    xlNetSetNotification = _lib.get("xlNetSetNotification", "cdecl")
    xlNetSetNotification.argtypes = [XLnetworkHandle, POINTER(XLhandle), c_int]
    xlNetSetNotification.restype = XLstatus
    break

# vxlapi.h: 7112
for _lib in _libs.values():
    if not _lib.has("xlNetRequestMACAddress", "cdecl"):
        continue
    xlNetRequestMACAddress = _lib.get("xlNetRequestMACAddress", "cdecl")
    xlNetRequestMACAddress.argtypes = [XLnetworkHandle, POINTER(T_XL_ETH_MAC_ADDRESS)]
    xlNetRequestMACAddress.restype = XLstatus
    break

# vxlapi.h: 7128
for _lib in _libs.values():
    if not _lib.has("xlNetReleaseMACAddress", "cdecl"):
        continue
    xlNetReleaseMACAddress = _lib.get("xlNetReleaseMACAddress", "cdecl")
    xlNetReleaseMACAddress.argtypes = [XLnetworkHandle, POINTER(T_XL_ETH_MAC_ADDRESS)]
    xlNetReleaseMACAddress.restype = XLstatus
    break

# vxlapi.h: 7137
for _lib in _libs.values():
    if not _lib.has("xlNetFlushReceiveQueue", "cdecl"):
        continue
    xlNetFlushReceiveQueue = _lib.get("xlNetFlushReceiveQueue", "cdecl")
    xlNetFlushReceiveQueue.argtypes = [XLnetworkHandle]
    xlNetFlushReceiveQueue.restype = XLstatus
    break

# vxlapi.h: 7164
if _libs["vxlapi64"].has("xlA429Receive", "cdecl"):
    xlA429Receive = _libs["vxlapi64"].get("xlA429Receive", "cdecl")
    xlA429Receive.argtypes = [XLportHandle, POINTER(XLa429RxEvent)]
    xlA429Receive.restype = XLstatus

# vxlapi.h: 7171
if _libs["vxlapi64"].has("xlA429SetChannelParams", "cdecl"):
    xlA429SetChannelParams = _libs["vxlapi64"].get("xlA429SetChannelParams", "cdecl")
    xlA429SetChannelParams.argtypes = [XLportHandle, XLaccess, POINTER(XL_A429_PARAMS)]
    xlA429SetChannelParams.restype = XLstatus

# vxlapi.h: 7178
if _libs["vxlapi64"].has("xlA429Transmit", "cdecl"):
    xlA429Transmit = _libs["vxlapi64"].get("xlA429Transmit", "cdecl")
    xlA429Transmit.argtypes = [XLportHandle, XLaccess, c_uint, POINTER(c_uint), POINTER(XL_A429_MSG_TX)]
    xlA429Transmit.restype = XLstatus

# vxlapi.h: 7191
if _libs["vxlapi64"].has("xlGetKeymanBoxes", "cdecl"):
    xlGetKeymanBoxes = _libs["vxlapi64"].get("xlGetKeymanBoxes", "cdecl")
    xlGetKeymanBoxes.argtypes = [POINTER(c_uint)]
    xlGetKeymanBoxes.restype = XLstatus

# vxlapi.h: 7201
if _libs["vxlapi64"].has("xlGetKeymanInfo", "cdecl"):
    xlGetKeymanInfo = _libs["vxlapi64"].get("xlGetKeymanInfo", "cdecl")
    xlGetKeymanInfo.argtypes = [c_uint, POINTER(c_uint), POINTER(c_uint), POINTER(XLuint64)]
    xlGetKeymanInfo.restype = XLstatus

# vxlapi.h: 7221
for _lib in _libs.values():
    if not _lib.has("xlTsCreateClock", "cdecl"):
        continue
    xlTsCreateClock = _lib.get("xlTsCreateClock", "cdecl")
    xlTsCreateClock.argtypes = [POINTER(XLtsClockHandle), String, XLtsClkExternalType, XLtsInterfaceVersion]
    xlTsCreateClock.restype = XLstatus
    break

# vxlapi.h: 7230
for _lib in _libs.values():
    if not _lib.has("xlTsDestroyClock", "cdecl"):
        continue
    xlTsDestroyClock = _lib.get("xlTsDestroyClock", "cdecl")
    xlTsDestroyClock.argtypes = [XLtsClockHandle]
    xlTsDestroyClock.restype = XLstatus
    break

# vxlapi.h: 7246
for _lib in _libs.values():
    if not _lib.has("xlTsGetDomainTime", "cdecl"):
        continue
    xlTsGetDomainTime = _lib.get("xlTsGetDomainTime", "cdecl")
    xlTsGetDomainTime.argtypes = [XLtsClockHandle, POINTER(XLtsDomainTime), POINTER(XLuint64)]
    xlTsGetDomainTime.restype = XLstatus
    break

# vxlapi.h: 7257
for _lib in _libs.values():
    if not _lib.has("xlTsSetNotification", "cdecl"):
        continue
    xlTsSetNotification = _lib.get("xlTsSetNotification", "cdecl")
    xlTsSetNotification.argtypes = [XLportHandle, XLportHandle, POINTER(XLhandle)]
    xlTsSetNotification.restype = XLstatus
    break

# vxlapi.h: 7269
for _lib in _libs.values():
    if not _lib.has("xlNetTsSetNotification", "cdecl"):
        continue
    xlNetTsSetNotification = _lib.get("xlNetTsSetNotification", "cdecl")
    xlNetTsSetNotification.argtypes = [XLportHandle, XLnetworkHandle, POINTER(XLhandle)]
    xlNetTsSetNotification.restype = XLstatus
    break

HANDLE = POINTER(None)# vxlapi.h: 22

__int64 = c_longlong# vxlapi.h: 23

# vxlapi.h: 81
try:
    XL_BUS_TYPE_NONE = 0x00000000
except:
    pass

# vxlapi.h: 82
try:
    XL_BUS_TYPE_CAN = 0x00000001
except:
    pass

# vxlapi.h: 83
try:
    XL_BUS_TYPE_LIN = 0x00000002
except:
    pass

# vxlapi.h: 84
try:
    XL_BUS_TYPE_FLEXRAY = 0x00000004
except:
    pass

# vxlapi.h: 85
try:
    XL_BUS_TYPE_AFDX = 0x00000008
except:
    pass

# vxlapi.h: 86
try:
    XL_BUS_TYPE_MOST = 0x00000010
except:
    pass

# vxlapi.h: 87
try:
    XL_BUS_TYPE_DAIO = 0x00000040
except:
    pass

# vxlapi.h: 88
try:
    XL_BUS_TYPE_J1708 = 0x00000100
except:
    pass

# vxlapi.h: 89
try:
    XL_BUS_TYPE_KLINE = 0x00000800
except:
    pass

# vxlapi.h: 90
try:
    XL_BUS_TYPE_ETHERNET = 0x00001000
except:
    pass

# vxlapi.h: 91
try:
    XL_BUS_TYPE_A429 = 0x00002000
except:
    pass

# vxlapi.h: 92
try:
    XL_BUS_TYPE_STATUS = 0x00020000
except:
    pass

# vxlapi.h: 98
try:
    XL_TRANSCEIVER_TYPE_NONE = 0x0000
except:
    pass

# vxlapi.h: 99
try:
    XL_TRANSCEIVER_TYPE_CAN_251 = 0x0001
except:
    pass

# vxlapi.h: 100
try:
    XL_TRANSCEIVER_TYPE_CAN_252 = 0x0002
except:
    pass

# vxlapi.h: 101
try:
    XL_TRANSCEIVER_TYPE_CAN_DNOPTO = 0x0003
except:
    pass

# vxlapi.h: 102
try:
    XL_TRANSCEIVER_TYPE_CAN_SWC_PROTO = 0x0005
except:
    pass

# vxlapi.h: 103
try:
    XL_TRANSCEIVER_TYPE_CAN_SWC = 0x0006
except:
    pass

# vxlapi.h: 104
try:
    XL_TRANSCEIVER_TYPE_CAN_EVA = 0x0007
except:
    pass

# vxlapi.h: 105
try:
    XL_TRANSCEIVER_TYPE_CAN_FIBER = 0x0008
except:
    pass

# vxlapi.h: 106
try:
    XL_TRANSCEIVER_TYPE_CAN_1054_OPTO = 0x000B
except:
    pass

# vxlapi.h: 107
try:
    XL_TRANSCEIVER_TYPE_CAN_SWC_OPTO = 0x000C
except:
    pass

# vxlapi.h: 108
try:
    XL_TRANSCEIVER_TYPE_CAN_B10011S = 0x000D
except:
    pass

# vxlapi.h: 109
try:
    XL_TRANSCEIVER_TYPE_CAN_1050 = 0x000E
except:
    pass

# vxlapi.h: 110
try:
    XL_TRANSCEIVER_TYPE_CAN_1050_OPTO = 0x000F
except:
    pass

# vxlapi.h: 111
try:
    XL_TRANSCEIVER_TYPE_CAN_1041 = 0x0010
except:
    pass

# vxlapi.h: 112
try:
    XL_TRANSCEIVER_TYPE_CAN_1041_OPTO = 0x0011
except:
    pass

# vxlapi.h: 113
try:
    XL_TRANSCEIVER_TYPE_CAN_VIRTUAL = 0x0016
except:
    pass

# vxlapi.h: 114
try:
    XL_TRANSCEIVER_TYPE_LIN_6258_OPTO = 0x0017
except:
    pass

# vxlapi.h: 115
try:
    XL_TRANSCEIVER_TYPE_LIN_6259_OPTO = 0x0019
except:
    pass

# vxlapi.h: 116
try:
    XL_TRANSCEIVER_TYPE_DAIO_8444_OPTO = 0x001D
except:
    pass

# vxlapi.h: 117
try:
    XL_TRANSCEIVER_TYPE_CAN_1041A_OPTO = 0x0021
except:
    pass

# vxlapi.h: 118
try:
    XL_TRANSCEIVER_TYPE_LIN_6259_MAG = 0x0023
except:
    pass

# vxlapi.h: 120
try:
    XL_TRANSCEIVER_TYPE_LIN_7259_MAG = 0x0025
except:
    pass

# vxlapi.h: 122
try:
    XL_TRANSCEIVER_TYPE_LIN_7269_MAG = 0x0027
except:
    pass

# vxlapi.h: 124
try:
    XL_TRANSCEIVER_TYPE_CAN_1054_MAG = 0x0033
except:
    pass

# vxlapi.h: 125
try:
    XL_TRANSCEIVER_TYPE_CAN_251_MAG = 0x0035
except:
    pass

# vxlapi.h: 126
try:
    XL_TRANSCEIVER_TYPE_CAN_1050_MAG = 0x0037
except:
    pass

# vxlapi.h: 127
try:
    XL_TRANSCEIVER_TYPE_CAN_1040_MAG = 0x0039
except:
    pass

# vxlapi.h: 128
try:
    XL_TRANSCEIVER_TYPE_CAN_1041A_MAG = 0x003B
except:
    pass

# vxlapi.h: 129
try:
    XL_TRANSCEIVER_TYPE_TWIN_CAN_1041A_MAG = 0x0080
except:
    pass

# vxlapi.h: 130
try:
    XL_TRANSCEIVER_TYPE_TWIN_LIN_7269_MAG = 0x0081
except:
    pass

# vxlapi.h: 132
try:
    XL_TRANSCEIVER_TYPE_TWIN_CAN_1041AV2_MAG = 0x0082
except:
    pass

# vxlapi.h: 133
try:
    XL_TRANSCEIVER_TYPE_TWIN_CAN_1054_1041A_MAG = 0x0083
except:
    pass

# vxlapi.h: 136
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_251 = 0x0101
except:
    pass

# vxlapi.h: 137
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1054 = 0x0103
except:
    pass

# vxlapi.h: 138
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_251_OPTO = 0x0105
except:
    pass

# vxlapi.h: 139
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_SWC = 0x010B
except:
    pass

# vxlapi.h: 141
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1054_OPTO = 0x0115
except:
    pass

# vxlapi.h: 142
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_SWC_OPTO = 0x0117
except:
    pass

# vxlapi.h: 143
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_TT_OPTO = 0x0119
except:
    pass

# vxlapi.h: 144
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1050 = 0x011B
except:
    pass

# vxlapi.h: 145
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1050_OPTO = 0x011D
except:
    pass

# vxlapi.h: 146
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1041 = 0x011F
except:
    pass

# vxlapi.h: 147
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1041_OPTO = 0x0121
except:
    pass

# vxlapi.h: 148
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_6258_OPTO = 0x0129
except:
    pass

# vxlapi.h: 149
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_6259_OPTO = 0x012B
except:
    pass

# vxlapi.h: 150
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_6259_MAG = 0x012D
except:
    pass

# vxlapi.h: 152
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1041A_OPTO = 0x012F
except:
    pass

# vxlapi.h: 153
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_7259_MAG = 0x0131
except:
    pass

# vxlapi.h: 155
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_7269_MAG = 0x0133
except:
    pass

# vxlapi.h: 157
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_251_MAG = 0x0135
except:
    pass

# vxlapi.h: 158
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1050_MAG = 0x0136
except:
    pass

# vxlapi.h: 159
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1040_MAG = 0x0137
except:
    pass

# vxlapi.h: 160
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1041A_MAG = 0x0138
except:
    pass

# vxlapi.h: 161
try:
    XL_TRANSCEIVER_TYPE_PB_DAIO_8444_OPTO = 0x0139
except:
    pass

# vxlapi.h: 162
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1054_MAG = 0x013B
except:
    pass

# vxlapi.h: 164
try:
    XL_TRANSCEIVER_TYPE_CAN_1051_CAP_FIX = 0x013C
except:
    pass

# vxlapi.h: 165
try:
    XL_TRANSCEIVER_TYPE_DAIO_1021_FIX = 0x013D
except:
    pass

# vxlapi.h: 166
try:
    XL_TRANSCEIVER_TYPE_LIN_7269_CAP_FIX = 0x013E
except:
    pass

# vxlapi.h: 167
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1051_CAP = 0x013F
except:
    pass

# vxlapi.h: 168
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_SWC_7356_CAP = 0x0140
except:
    pass

# vxlapi.h: 169
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1055_CAP = 0x0141
except:
    pass

# vxlapi.h: 171
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1057_CAP = 0x0142
except:
    pass

# vxlapi.h: 172
try:
    XL_TRANSCEIVER_TYPE_A429_HOLT8596_FIX = 0x0143
except:
    pass

# vxlapi.h: 173
try:
    XL_TRANSCEIVER_TYPE_A429_HOLT8455_FIX = 0x0144
except:
    pass

# vxlapi.h: 174
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1051HG_CAP = 0x0145
except:
    pass

# vxlapi.h: 175
try:
    XL_TRANSCEIVER_TYPE_CAN_1057_FIX = 0x0146
except:
    pass

# vxlapi.h: 176
try:
    XL_TRANSCEIVER_TYPE_LIN_7269_FIX = 0x0147
except:
    pass

# vxlapi.h: 177
try:
    XL_TRANSCEIVER_TYPE_PB_CAN_1462BT = 0x0149
except:
    pass

# vxlapi.h: 178
try:
    XL_TRANSCEIVER_TYPE_PB_LIN_7259 = 0x014A
except:
    pass

# vxlapi.h: 179
try:
    XL_TRANSCEIVER_TYPE_CAN_1057B_FIX = 0x014E
except:
    pass

# vxlapi.h: 180
try:
    XL_TRANSCEIVER_TYPE_CAN_1462BT_FIX = 0x014F
except:
    pass

# vxlapi.h: 181
try:
    XL_TRANSCEIVER_TYPE_LIN_7259_FIX = 0x0159
except:
    pass

# vxlapi.h: 185
try:
    XL_TRANSCEIVER_TYPE_PB_FR_1080 = 0x0201
except:
    pass

# vxlapi.h: 186
try:
    XL_TRANSCEIVER_TYPE_PB_FR_1080_MAG = 0x0202
except:
    pass

# vxlapi.h: 187
try:
    XL_TRANSCEIVER_TYPE_PB_FR_1080A_MAG = 0x0203
except:
    pass

# vxlapi.h: 188
try:
    XL_TRANSCEIVER_TYPE_PB_FR_1082_CAP = 0x0204
except:
    pass

# vxlapi.h: 189
try:
    XL_TRANSCEIVER_TYPE_PB_FRC_1082_CAP = 0x0205
except:
    pass

# vxlapi.h: 190
try:
    XL_TRANSCEIVER_TYPE_FR_1082_CAP_FIX = 0x0206
except:
    pass

# vxlapi.h: 192
try:
    XL_TRANSCEIVER_TYPE_MOST150_ONBOARD = 0x0220
except:
    pass

# vxlapi.h: 195
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM54810_FIX = 0x0230
except:
    pass

# vxlapi.h: 196
try:
    XL_TRANSCEIVER_TYPE_ETH_AR8031_FIX = 0x0231
except:
    pass

# vxlapi.h: 197
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM89810_FIX = 0x0232
except:
    pass

# vxlapi.h: 198
try:
    XL_TRANSCEIVER_TYPE_ETH_TJA1100_FIX = 0x0233
except:
    pass

# vxlapi.h: 199
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM54810_89811_FIX = 0x0234
except:
    pass

# vxlapi.h: 201
try:
    XL_TRANSCEIVER_TYPE_ETH_DP83XG710Q1_FIX = 0x0235
except:
    pass

# vxlapi.h: 202
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM54811S_FIX = 0x0236
except:
    pass

# vxlapi.h: 203
try:
    XL_TRANSCEIVER_TYPE_ETH_RTL9000AA_FIX = 0x0237
except:
    pass

# vxlapi.h: 204
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM89811_FIX = 0x0238
except:
    pass

# vxlapi.h: 205
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM54210_FIX = 0x0239
except:
    pass

# vxlapi.h: 206
try:
    XL_TRANSCEIVER_TYPE_ETH_88Q2112_FIX = 0x023A
except:
    pass

# vxlapi.h: 207
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM84891_FIX = 0x023B
except:
    pass

# vxlapi.h: 208
try:
    XL_TRANSCEIVER_TYPE_ETH_BCM89883_FIX = 0x023C
except:
    pass

# vxlapi.h: 209
try:
    XL_TRANSCEIVER_TYPE_ETH_88Q2220M_FIX = 0x023D
except:
    pass

# vxlapi.h: 210
try:
    XL_TRANSCEIVER_TYPE_ETH_GPY215_FIX = 0x023E
except:
    pass

# vxlapi.h: 213
try:
    XL_TRANSCEIVER_TYPE_PB_DAIO_8642 = 0x0280
except:
    pass

# vxlapi.h: 214
try:
    XL_TRANSCEIVER_TYPE_DAIO_AL_ONLY = 0x028f
except:
    pass

# vxlapi.h: 215
try:
    XL_TRANSCEIVER_TYPE_DAIO_1021_FIX_WITH_AL = 0x0290
except:
    pass

# vxlapi.h: 216
try:
    XL_TRANSCEIVER_TYPE_DAIO_AL_WU = 0x0291
except:
    pass

# vxlapi.h: 217
try:
    XL_TRANSCEIVER_TYPE_DAIO_1021_FIX_WITH_5V = 0x0292
except:
    pass

# vxlapi.h: 218
try:
    XL_TRANSCEIVER_TYPE_PB_DAIO_8644 = 0x0281
except:
    pass

# vxlapi.h: 221
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_BCM89810 = 0x0300
except:
    pass

# vxlapi.h: 222
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_IEEE_RGMII_AR8031 = 0x0301
except:
    pass

# vxlapi.h: 223
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_IEEE_SGMII_AR8031 = 0x0302
except:
    pass

# vxlapi.h: 224
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_TJA1100 = 0x0303
except:
    pass

# vxlapi.h: 225
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_RTL9000AA = 0x0304
except:
    pass

# vxlapi.h: 226
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_SGMII_DP83XG710Q1 = 0x0305
except:
    pass

# vxlapi.h: 227
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_88Q2112 = 0x0306
except:
    pass

# vxlapi.h: 228
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_BCM89811 = 0x0307
except:
    pass

# vxlapi.h: 229
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BR_TJA1101 = 0x0308
except:
    pass

# vxlapi.h: 232
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_88Q2112 = 0x0400
except:
    pass

# vxlapi.h: 233
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_BCM89883 = 0x0401
except:
    pass

# vxlapi.h: 234
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_BCM89890 = 0x0402
except:
    pass

# vxlapi.h: 235
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BCM84891 = 0x0403
except:
    pass

# vxlapi.h: 236
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_1AE10MLAN8670_LAN8670 = 0x0405
except:
    pass

# vxlapi.h: 237
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_1AE10MLAN8670_BCM89883 = 0x0406
except:
    pass

# vxlapi.h: 238
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_RTL9010AA = 0x0407
except:
    pass

# vxlapi.h: 239
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_88Q2221M = 0x0408
except:
    pass

# vxlapi.h: 240
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_MVQ3244 = 0x040A
except:
    pass

# vxlapi.h: 241
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_1AE10MLAN8670_LAN8670_V2 = 0x040B
except:
    pass

# vxlapi.h: 244
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_2AE1G_M88Q2221M = 0x0440
except:
    pass

# vxlapi.h: 245
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_2AE2G5_BCM89892 = 0x0441
except:
    pass

# vxlapi.h: 246
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_2AE10M_LAN8680 = 0x0442
except:
    pass

# vxlapi.h: 249
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_AQR115C = 0x0480
except:
    pass

# vxlapi.h: 250
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_BR_BCM89883_2CH = 0x0481
except:
    pass

# vxlapi.h: 251
try:
    XL_TRANSCEIVER_TYPE_ETH_MOD_BCM54210 = 0x0482
except:
    pass

# vxlapi.h: 252
try:
    XL_TRANSCEIVER_TYPE_AE_MOD_LAN8670_V2_2CH = 0x0483
except:
    pass

# vxlapi.h: 255
try:
    XL_TRANSCEIVER_TYPE_PB_ETH_100BASET1_TJA1101 = 0x1F82
except:
    pass

# vxlapi.h: 256
try:
    XL_TRANSCEIVER_TYPE_PB_ETH_1000BASET1_88Q2112 = 0x1F83
except:
    pass

# vxlapi.h: 262
try:
    XL_TRANSCEIVER_LINEMODE_NA = 0x0000
except:
    pass

# vxlapi.h: 263
try:
    XL_TRANSCEIVER_LINEMODE_TWO_LINE = 0x0001
except:
    pass

# vxlapi.h: 264
try:
    XL_TRANSCEIVER_LINEMODE_CAN_H = 0x0002
except:
    pass

# vxlapi.h: 265
try:
    XL_TRANSCEIVER_LINEMODE_CAN_L = 0x0003
except:
    pass

# vxlapi.h: 266
try:
    XL_TRANSCEIVER_LINEMODE_SWC_SLEEP = 0x0004
except:
    pass

# vxlapi.h: 267
try:
    XL_TRANSCEIVER_LINEMODE_SWC_NORMAL = 0x0005
except:
    pass

# vxlapi.h: 268
try:
    XL_TRANSCEIVER_LINEMODE_SWC_FAST = 0x0006
except:
    pass

# vxlapi.h: 269
try:
    XL_TRANSCEIVER_LINEMODE_SWC_WAKEUP = 0x0007
except:
    pass

# vxlapi.h: 270
try:
    XL_TRANSCEIVER_LINEMODE_SLEEP = 0x0008
except:
    pass

# vxlapi.h: 271
try:
    XL_TRANSCEIVER_LINEMODE_NORMAL = 0x0009
except:
    pass

# vxlapi.h: 272
try:
    XL_TRANSCEIVER_LINEMODE_STDBY = 0x000a
except:
    pass

# vxlapi.h: 273
try:
    XL_TRANSCEIVER_LINEMODE_TT_CAN_H = 0x000b
except:
    pass

# vxlapi.h: 274
try:
    XL_TRANSCEIVER_LINEMODE_TT_CAN_L = 0x000c
except:
    pass

# vxlapi.h: 275
try:
    XL_TRANSCEIVER_LINEMODE_EVA_00 = 0x000d
except:
    pass

# vxlapi.h: 276
try:
    XL_TRANSCEIVER_LINEMODE_EVA_01 = 0x000e
except:
    pass

# vxlapi.h: 277
try:
    XL_TRANSCEIVER_LINEMODE_EVA_10 = 0x000f
except:
    pass

# vxlapi.h: 278
try:
    XL_TRANSCEIVER_LINEMODE_EVA_11 = 0x0010
except:
    pass

# vxlapi.h: 284
try:
    XL_TRANSCEIVER_STATUS_PRESENT = 0x0001
except:
    pass

# vxlapi.h: 285
try:
    XL_TRANSCEIVER_STATUS_POWER_GOOD = 0x0010
except:
    pass

# vxlapi.h: 286
try:
    XL_TRANSCEIVER_STATUS_EXT_POWER_GOOD = 0x0020
except:
    pass

# vxlapi.h: 287
try:
    XL_TRANSCEIVER_STATUS_NOT_SUPPORTED = 0x0040
except:
    pass

# vxlapi.h: 292
try:
    XL_SUCCESS = 0
except:
    pass

# vxlapi.h: 293
try:
    XL_PENDING = 1
except:
    pass

# vxlapi.h: 295
try:
    XL_ERR_QUEUE_IS_EMPTY = 10
except:
    pass

# vxlapi.h: 296
try:
    XL_ERR_QUEUE_IS_FULL = 11
except:
    pass

# vxlapi.h: 297
try:
    XL_ERR_TX_NOT_POSSIBLE = 12
except:
    pass

# vxlapi.h: 298
try:
    XL_ERR_NO_LICENSE = 14
except:
    pass

# vxlapi.h: 299
try:
    XL_ERR_WRONG_PARAMETER = 101
except:
    pass

# vxlapi.h: 300
try:
    XL_ERR_TWICE_REGISTER = 110
except:
    pass

# vxlapi.h: 301
try:
    XL_ERR_INVALID_CHAN_INDEX = 111
except:
    pass

# vxlapi.h: 302
try:
    XL_ERR_INVALID_ACCESS = 112
except:
    pass

# vxlapi.h: 303
try:
    XL_ERR_PORT_IS_OFFLINE = 113
except:
    pass

# vxlapi.h: 304
try:
    XL_ERR_CHAN_IS_ONLINE = 116
except:
    pass

# vxlapi.h: 305
try:
    XL_ERR_NOT_IMPLEMENTED = 117
except:
    pass

# vxlapi.h: 306
try:
    XL_ERR_INVALID_PORT = 118
except:
    pass

# vxlapi.h: 307
try:
    XL_ERR_HW_NOT_READY = 120
except:
    pass

# vxlapi.h: 308
try:
    XL_ERR_CMD_TIMEOUT = 121
except:
    pass

# vxlapi.h: 309
try:
    XL_ERR_CMD_HANDLING = 122
except:
    pass

# vxlapi.h: 310
try:
    XL_ERR_HW_NOT_PRESENT = 129
except:
    pass

# vxlapi.h: 311
try:
    XL_ERR_NOTIFY_ALREADY_ACTIVE = 131
except:
    pass

# vxlapi.h: 312
try:
    XL_ERR_INVALID_TAG = 132
except:
    pass

# vxlapi.h: 313
try:
    XL_ERR_INVALID_RESERVED_FLD = 133
except:
    pass

# vxlapi.h: 314
try:
    XL_ERR_INVALID_SIZE = 134
except:
    pass

# vxlapi.h: 315
try:
    XL_ERR_INSUFFICIENT_BUFFER = 135
except:
    pass

# vxlapi.h: 316
try:
    XL_ERR_ERROR_CRC = 136
except:
    pass

# vxlapi.h: 317
try:
    XL_ERR_BAD_EXE_FORMAT = 137
except:
    pass

# vxlapi.h: 318
try:
    XL_ERR_NO_SYSTEM_RESOURCES = 138
except:
    pass

# vxlapi.h: 319
try:
    XL_ERR_NOT_FOUND = 139
except:
    pass

# vxlapi.h: 320
try:
    XL_ERR_INVALID_ADDRESS = 140
except:
    pass

# vxlapi.h: 321
try:
    XL_ERR_REQ_NOT_ACCEP = 141
except:
    pass

# vxlapi.h: 322
try:
    XL_ERR_INVALID_LEVEL = 142
except:
    pass

# vxlapi.h: 323
try:
    XL_ERR_NO_DATA_DETECTED = 143
except:
    pass

# vxlapi.h: 324
try:
    XL_ERR_INTERNAL_ERROR = 144
except:
    pass

# vxlapi.h: 325
try:
    XL_ERR_UNEXP_NET_ERR = 145
except:
    pass

# vxlapi.h: 326
try:
    XL_ERR_INVALID_USER_BUFFER = 146
except:
    pass

# vxlapi.h: 327
try:
    XL_ERR_INVALID_PORT_ACCESS_TYPE = 147
except:
    pass

# vxlapi.h: 328
try:
    XL_ERR_NO_RESOURCES = 152
except:
    pass

# vxlapi.h: 329
try:
    XL_ERR_WRONG_CHIP_TYPE = 153
except:
    pass

# vxlapi.h: 330
try:
    XL_ERR_WRONG_COMMAND = 154
except:
    pass

# vxlapi.h: 331
try:
    XL_ERR_INVALID_HANDLE = 155
except:
    pass

# vxlapi.h: 332
try:
    XL_ERR_RESERVED_NOT_ZERO = 157
except:
    pass

# vxlapi.h: 333
try:
    XL_ERR_INIT_ACCESS_MISSING = 158
except:
    pass

# vxlapi.h: 334
try:
    XL_ERR_WRONG_VERSION = 160
except:
    pass

# vxlapi.h: 335
try:
    XL_ERR_ALREADY_EXISTS = 183
except:
    pass

# vxlapi.h: 336
try:
    XL_ERR_CANNOT_OPEN_DRIVER = 201
except:
    pass

# vxlapi.h: 337
try:
    XL_ERR_WRONG_BUS_TYPE = 202
except:
    pass

# vxlapi.h: 338
try:
    XL_ERR_DLL_NOT_FOUND = 203
except:
    pass

# vxlapi.h: 339
try:
    XL_ERR_INVALID_CHANNEL_MASK = 204
except:
    pass

# vxlapi.h: 340
try:
    XL_ERR_NOT_SUPPORTED = 205
except:
    pass

# vxlapi.h: 342
try:
    XL_ERR_CONNECTION_BROKEN = 210
except:
    pass

# vxlapi.h: 343
try:
    XL_ERR_CONNECTION_CLOSED = 211
except:
    pass

# vxlapi.h: 344
try:
    XL_ERR_INVALID_STREAM_NAME = 212
except:
    pass

# vxlapi.h: 345
try:
    XL_ERR_CONNECTION_FAILED = 213
except:
    pass

# vxlapi.h: 346
try:
    XL_ERR_STREAM_NOT_FOUND = 214
except:
    pass

# vxlapi.h: 347
try:
    XL_ERR_STREAM_NOT_CONNECTED = 215
except:
    pass

# vxlapi.h: 348
try:
    XL_ERR_QUEUE_OVERRUN = 216
except:
    pass

# vxlapi.h: 349
try:
    XL_ERROR = 255
except:
    pass

# vxlapi.h: 353
try:
    XL_ERR_PDU_OUT_OF_MEMORY = 0x0104
except:
    pass

# vxlapi.h: 354
try:
    XL_ERR_FR_CLUSTERCONFIG_MISSING = 0x0105
except:
    pass

# vxlapi.h: 356
try:
    XL_ERR_PDU_OFFSET_REPET_INVALID = 0x0106
except:
    pass

# vxlapi.h: 357
try:
    XL_ERR_PDU_PAYLOAD_SIZE_INVALID = 0x0107
except:
    pass

# vxlapi.h: 359
try:
    XL_ERR_FR_NBR_FRAMES_OVERFLOW = 0x0109
except:
    pass

# vxlapi.h: 360
try:
    XL_ERR_FR_SLOT_ID_INVALID = 0x010B
except:
    pass

# vxlapi.h: 361
try:
    XL_ERR_FR_SLOT_ALREADY_OCCUPIED_BY_ERAY = 0x010C
except:
    pass

# vxlapi.h: 363
try:
    XL_ERR_FR_SLOT_ALREADY_OCCUPIED_BY_COLDC = 0x010D
except:
    pass

# vxlapi.h: 365
try:
    XL_ERR_FR_SLOT_OCCUPIED_BY_OTHER_APP = 0x010E
except:
    pass

# vxlapi.h: 366
try:
    XL_ERR_FR_SLOT_IN_WRONG_SEGMENT = 0x010F
except:
    pass

# vxlapi.h: 368
try:
    XL_ERR_FR_FRAME_CYCLE_MULTIPLEX_ERROR = 0x0110
except:
    pass

# vxlapi.h: 370
try:
    XL_ERR_PDU_NO_UNMAP_OF_SYNCFRAME = 0x0116
except:
    pass

# vxlapi.h: 371
try:
    XL_ERR_SYNC_FRAME_MODE = 0x0123
except:
    pass

# vxlapi.h: 372
try:
    XL_ERR_INVALID_DLC = 0x0201
except:
    pass

# vxlapi.h: 373
try:
    XL_ERR_INVALID_CANID = 0x0202
except:
    pass

# vxlapi.h: 374
try:
    XL_ERR_INVALID_FDFLAG_MODE20 = 0x0203
except:
    pass

# vxlapi.h: 375
try:
    XL_ERR_EDL_RTR = 0x0204
except:
    pass

# vxlapi.h: 376
try:
    XL_ERR_EDL_NOT_SET = 0x0205
except:
    pass

# vxlapi.h: 377
try:
    XL_ERR_UNKNOWN_FLAG = 0x0206
except:
    pass

# vxlapi.h: 378
try:
    XL_ERR_TS_DOMAIN_NOT_SYNC = 0x0502
except:
    pass

# vxlapi.h: 379
try:
    XL_ERR_TS_INVALID_CLUSTER_MASTER = 0x0503
except:
    pass

# vxlapi.h: 380
try:
    XL_ERR_TS_CLOCK_NOT_FOUND = 0x0504
except:
    pass

# vxlapi.h: 381
try:
    XL_ERR_TS_AGGREGATE_STATUS = 0x0505
except:
    pass

# vxlapi.h: 382
try:
    XL_ERR_TS_RESET_CLOCK = 0x050C
except:
    pass

# vxlapi.h: 383
try:
    XL_ERR_TS_SET_CLOCK_OFFSET = 0x050D
except:
    pass

# vxlapi.h: 384
try:
    XL_ERR_TS_MIN_OFFSET_SET = 0x050F
except:
    pass

# vxlapi.h: 385
try:
    XL_ERR_TS_SYNC_TO_LOCAL = 0x0510
except:
    pass

# vxlapi.h: 386
try:
    XL_ERR_TS_SYNC_OFF = 0x0511
except:
    pass

# vxlapi.h: 387
try:
    XL_ERR_TS_CLOCK_NOT_SYNC = 0x0512
except:
    pass

# vxlapi.h: 390
try:
    XL_ERR_ETH_PHY_ACTIVATION_FAILED = 0x1100
except:
    pass

# vxlapi.h: 391
try:
    XL_ERR_ETH_PHY_CONFIG_ABORTED = 0x1103
except:
    pass

# vxlapi.h: 392
try:
    XL_ERR_ETH_RESET_FAILED = 0x1104
except:
    pass

# vxlapi.h: 393
try:
    XL_ERR_ETH_SET_CONFIG_DELAYED = 0x1105
except:
    pass

# vxlapi.h: 394
try:
    XL_ERR_ETH_UNSUPPORTED_FEATURE = 0x1106
except:
    pass

# vxlapi.h: 395
try:
    XL_ERR_ETH_MAC_ACTIVATION_FAILED = 0x1107
except:
    pass

# vxlapi.h: 396
try:
    XL_ERR_NET_ETH_SWITCH_IS_ONLINE = 0x110C
except:
    pass

# vxlapi.h: 397
try:
    XL_ERR_ETH_PLCA_CAPTURE_ONLY_MODE_ACTIVE = 0x110E
except:
    pass

# vxlapi.h: 431
try:
    XL_RECEIVE_MSG = 0x0001
except:
    pass

# vxlapi.h: 432
try:
    XL_CHIP_STATE = 0x0004
except:
    pass

# vxlapi.h: 433
try:
    XL_TRANSCEIVER_INFO = 0x0006
except:
    pass

# vxlapi.h: 434
try:
    XL_TRANSCEIVER = XL_TRANSCEIVER_INFO
except:
    pass

# vxlapi.h: 435
try:
    XL_TIMER_EVENT = 0x0008
except:
    pass

# vxlapi.h: 436
try:
    XL_TIMER = XL_TIMER_EVENT
except:
    pass

# vxlapi.h: 437
try:
    XL_TRANSMIT_MSG = 0x000A
except:
    pass

# vxlapi.h: 438
try:
    XL_SYNC_PULSE = 0x000B
except:
    pass

# vxlapi.h: 439
try:
    XL_APPLICATION_NOTIFICATION = 0x000F
except:
    pass

# vxlapi.h: 444
try:
    LIN_MSG = 0x0014
except:
    pass

# vxlapi.h: 445
try:
    LIN_ERRMSG = 0x0015
except:
    pass

# vxlapi.h: 446
try:
    LIN_SYNCERR = 0x0016
except:
    pass

# vxlapi.h: 447
try:
    LIN_NOANS = 0x0017
except:
    pass

# vxlapi.h: 448
try:
    LIN_WAKEUP = 0x0018
except:
    pass

# vxlapi.h: 449
try:
    LIN_SLEEP = 0x0019
except:
    pass

# vxlapi.h: 450
try:
    LIN_CRCINFO = 0x001A
except:
    pass

# vxlapi.h: 455
try:
    RECEIVE_DAIO_DATA = 0x0020
except:
    pass

# vxlapi.h: 457
try:
    KLINE_MSG = 0x0024
except:
    pass

# vxlapi.h: 464
try:
    XL_FR_START_CYCLE = 0x0080
except:
    pass

# vxlapi.h: 465
try:
    XL_FR_RX_FRAME = 0x0081
except:
    pass

# vxlapi.h: 466
try:
    XL_FR_TX_FRAME = 0x0082
except:
    pass

# vxlapi.h: 467
try:
    XL_FR_TXACK_FRAME = 0x0083
except:
    pass

# vxlapi.h: 468
try:
    XL_FR_INVALID_FRAME = 0x0084
except:
    pass

# vxlapi.h: 469
try:
    XL_FR_WAKEUP = 0x0085
except:
    pass

# vxlapi.h: 470
try:
    XL_FR_SYMBOL_WINDOW = 0x0086
except:
    pass

# vxlapi.h: 471
try:
    XL_FR_ERROR = 0x0087
except:
    pass

# vxlapi.h: 472
try:
    XL_FR_ERROR_POC_MODE = 0x01
except:
    pass

# vxlapi.h: 473
try:
    XL_FR_ERROR_SYNC_FRAMES_BELOWMIN = 0x02
except:
    pass

# vxlapi.h: 474
try:
    XL_FR_ERROR_SYNC_FRAMES_OVERLOAD = 0x03
except:
    pass

# vxlapi.h: 475
try:
    XL_FR_ERROR_CLOCK_CORR_FAILURE = 0x04
except:
    pass

# vxlapi.h: 476
try:
    XL_FR_ERROR_NIT_FAILURE = 0x05
except:
    pass

# vxlapi.h: 477
try:
    XL_FR_ERROR_CC_ERROR = 0x06
except:
    pass

# vxlapi.h: 478
try:
    XL_FR_STATUS = 0x0088
except:
    pass

# vxlapi.h: 479
try:
    XL_FR_NM_VECTOR = 0x008A
except:
    pass

# vxlapi.h: 480
try:
    XL_FR_TRANCEIVER_STATUS = 0x008B
except:
    pass

# vxlapi.h: 481
try:
    XL_FR_SPY_FRAME = 0x008E
except:
    pass

# vxlapi.h: 482
try:
    XL_FR_SPY_SYMBOL = 0x008F
except:
    pass

# vxlapi.h: 491
try:
    XL_MOST_START = 0x0101
except:
    pass

# vxlapi.h: 492
try:
    XL_MOST_STOP = 0x0102
except:
    pass

# vxlapi.h: 493
try:
    XL_MOST_EVENTSOURCES = 0x0103
except:
    pass

# vxlapi.h: 494
try:
    XL_MOST_ALLBYPASS = 0x0107
except:
    pass

# vxlapi.h: 495
try:
    XL_MOST_TIMINGMODE = 0x0108
except:
    pass

# vxlapi.h: 496
try:
    XL_MOST_FREQUENCY = 0x0109
except:
    pass

# vxlapi.h: 497
try:
    XL_MOST_REGISTER_BYTES = 0x010a
except:
    pass

# vxlapi.h: 498
try:
    XL_MOST_REGISTER_BITS = 0x010b
except:
    pass

# vxlapi.h: 499
try:
    XL_MOST_SPECIAL_REGISTER = 0x010c
except:
    pass

# vxlapi.h: 500
try:
    XL_MOST_CTRL_RX_SPY = 0x010d
except:
    pass

# vxlapi.h: 501
try:
    XL_MOST_CTRL_RX_OS8104 = 0x010e
except:
    pass

# vxlapi.h: 502
try:
    XL_MOST_CTRL_TX = 0x010f
except:
    pass

# vxlapi.h: 503
try:
    XL_MOST_ASYNC_MSG = 0x0110
except:
    pass

# vxlapi.h: 504
try:
    XL_MOST_ASYNC_TX = 0x0111
except:
    pass

# vxlapi.h: 505
try:
    XL_MOST_SYNC_ALLOCTABLE = 0x0112
except:
    pass

# vxlapi.h: 506
try:
    XL_MOST_SYNC_VOLUME_STATUS = 0x0116
except:
    pass

# vxlapi.h: 507
try:
    XL_MOST_RXLIGHT = 0x0117
except:
    pass

# vxlapi.h: 508
try:
    XL_MOST_TXLIGHT = 0x0118
except:
    pass

# vxlapi.h: 509
try:
    XL_MOST_LOCKSTATUS = 0x0119
except:
    pass

# vxlapi.h: 510
try:
    XL_MOST_ERROR = 0x011a
except:
    pass

# vxlapi.h: 511
try:
    XL_MOST_CTRL_RXBUFFER = 0x011c
except:
    pass

# vxlapi.h: 512
try:
    XL_MOST_SYNC_TX_UNDERFLOW = 0x011d
except:
    pass

# vxlapi.h: 513
try:
    XL_MOST_SYNC_RX_OVERFLOW = 0x011e
except:
    pass

# vxlapi.h: 514
try:
    XL_MOST_CTRL_SYNC_AUDIO = 0x011f
except:
    pass

# vxlapi.h: 515
try:
    XL_MOST_SYNC_MUTE_STATUS = 0x0120
except:
    pass

# vxlapi.h: 516
try:
    XL_MOST_GENLIGHTERROR = 0x0121
except:
    pass

# vxlapi.h: 517
try:
    XL_MOST_GENLOCKERROR = 0x0122
except:
    pass

# vxlapi.h: 518
try:
    XL_MOST_TXLIGHT_POWER = 0x0123
except:
    pass

# vxlapi.h: 519
try:
    XL_MOST_CTRL_BUSLOAD = 0x0126
except:
    pass

# vxlapi.h: 520
try:
    XL_MOST_ASYNC_BUSLOAD = 0x0127
except:
    pass

# vxlapi.h: 521
try:
    XL_MOST_CTRL_SYNC_AUDIO_EX = 0x012a
except:
    pass

# vxlapi.h: 522
try:
    XL_MOST_TIMINGMODE_SPDIF = 0x012b
except:
    pass

# vxlapi.h: 523
try:
    XL_MOST_STREAM_STATE = 0x012c
except:
    pass

# vxlapi.h: 524
try:
    XL_MOST_STREAM_BUFFER = 0x012d
except:
    pass

# vxlapi.h: 530
try:
    XL_START = 0x0200
except:
    pass

# vxlapi.h: 531
try:
    XL_STOP = 0x0201
except:
    pass

# vxlapi.h: 532
try:
    XL_MOST150_EVENT_SOURCE = 0x0203
except:
    pass

# vxlapi.h: 533
try:
    XL_MOST150_DEVICE_MODE = 0x0204
except:
    pass

# vxlapi.h: 534
try:
    XL_MOST150_SYNC_ALLOC_INFO = 0x0205
except:
    pass

# vxlapi.h: 535
try:
    XL_MOST150_FREQUENCY = 0x0206
except:
    pass

# vxlapi.h: 536
try:
    XL_MOST150_SPECIAL_NODE_INFO = 0x0207
except:
    pass

# vxlapi.h: 537
try:
    XL_MOST150_CTRL_RX = 0x0208
except:
    pass

# vxlapi.h: 538
try:
    XL_MOST150_CTRL_TX_ACK = 0x0209
except:
    pass

# vxlapi.h: 539
try:
    XL_MOST150_ASYNC_SPY = 0x020A
except:
    pass

# vxlapi.h: 540
try:
    XL_MOST150_ASYNC_RX = 0x020B
except:
    pass

# vxlapi.h: 541
try:
    XL_MOST150_SYNC_VOLUME_STATUS = 0x020D
except:
    pass

# vxlapi.h: 542
try:
    XL_MOST150_TX_LIGHT = 0x020E
except:
    pass

# vxlapi.h: 543
try:
    XL_MOST150_RXLIGHT_LOCKSTATUS = 0x020F
except:
    pass

# vxlapi.h: 544
try:
    XL_MOST150_ERROR = 0x0210
except:
    pass

# vxlapi.h: 545
try:
    XL_MOST150_CONFIGURE_RX_BUFFER = 0x0211
except:
    pass

# vxlapi.h: 546
try:
    XL_MOST150_CTRL_SYNC_AUDIO = 0x0212
except:
    pass

# vxlapi.h: 547
try:
    XL_MOST150_SYNC_MUTE_STATUS = 0x0213
except:
    pass

# vxlapi.h: 548
try:
    XL_MOST150_LIGHT_POWER = 0x0214
except:
    pass

# vxlapi.h: 549
try:
    XL_MOST150_GEN_LIGHT_ERROR = 0x0215
except:
    pass

# vxlapi.h: 550
try:
    XL_MOST150_GEN_LOCK_ERROR = 0x0216
except:
    pass

# vxlapi.h: 551
try:
    XL_MOST150_CTRL_BUSLOAD = 0x0217
except:
    pass

# vxlapi.h: 552
try:
    XL_MOST150_ASYNC_BUSLOAD = 0x0218
except:
    pass

# vxlapi.h: 553
try:
    XL_MOST150_ETHERNET_RX = 0x0219
except:
    pass

# vxlapi.h: 554
try:
    XL_MOST150_SYSTEMLOCK_FLAG = 0x021A
except:
    pass

# vxlapi.h: 555
try:
    XL_MOST150_SHUTDOWN_FLAG = 0x021B
except:
    pass

# vxlapi.h: 556
try:
    XL_MOST150_CTRL_SPY = 0x021C
except:
    pass

# vxlapi.h: 557
try:
    XL_MOST150_ASYNC_TX_ACK = 0x021D
except:
    pass

# vxlapi.h: 558
try:
    XL_MOST150_ETHERNET_SPY = 0x021E
except:
    pass

# vxlapi.h: 559
try:
    XL_MOST150_ETHERNET_TX_ACK = 0x021F
except:
    pass

# vxlapi.h: 560
try:
    XL_MOST150_SPDIFMODE = 0x0220
except:
    pass

# vxlapi.h: 561
try:
    XL_MOST150_ECL_LINE_CHANGED = 0x0222
except:
    pass

# vxlapi.h: 562
try:
    XL_MOST150_ECL_TERMINATION_CHANGED = 0x0223
except:
    pass

# vxlapi.h: 563
try:
    XL_MOST150_NW_STARTUP = 0x0224
except:
    pass

# vxlapi.h: 564
try:
    XL_MOST150_NW_SHUTDOWN = 0x0225
except:
    pass

# vxlapi.h: 565
try:
    XL_MOST150_STREAM_STATE = 0x0226
except:
    pass

# vxlapi.h: 566
try:
    XL_MOST150_STREAM_TX_BUFFER = 0x0227
except:
    pass

# vxlapi.h: 567
try:
    XL_MOST150_STREAM_RX_BUFFER = 0x0228
except:
    pass

# vxlapi.h: 568
try:
    XL_MOST150_STREAM_TX_LABEL = 0x0229
except:
    pass

# vxlapi.h: 569
try:
    XL_MOST150_STREAM_TX_UNDERFLOW = 0x022B
except:
    pass

# vxlapi.h: 570
try:
    XL_MOST150_GEN_BYPASS_STRESS = 0x022C
except:
    pass

# vxlapi.h: 571
try:
    XL_MOST150_ECL_SEQUENCE = 0x022D
except:
    pass

# vxlapi.h: 572
try:
    XL_MOST150_ECL_GLITCH_FILTER = 0x022E
except:
    pass

# vxlapi.h: 573
try:
    XL_MOST150_SSO_RESULT = 0x022F
except:
    pass

# vxlapi.h: 578
try:
    XL_CAN_EV_TAG_RX_OK = 0x0400
except:
    pass

# vxlapi.h: 579
try:
    XL_CAN_EV_TAG_RX_ERROR = 0x0401
except:
    pass

# vxlapi.h: 580
try:
    XL_CAN_EV_TAG_TX_ERROR = 0x0402
except:
    pass

# vxlapi.h: 581
try:
    XL_CAN_EV_TAG_TX_REQUEST = 0x0403
except:
    pass

# vxlapi.h: 582
try:
    XL_CAN_EV_TAG_TX_OK = 0x0404
except:
    pass

# vxlapi.h: 583
try:
    XL_CAN_EV_TAG_CHIP_STATE = 0x0409
except:
    pass

# vxlapi.h: 587
try:
    XL_CAN_EV_TAG_TX_MSG = 0x0440
except:
    pass

# vxlapi.h: 591
try:
    XL_ETH_EVENT_TAG_FRAMERX = 0x0500
except:
    pass

# vxlapi.h: 592
try:
    XL_ETH_EVENT_TAG_FRAMERX_ERROR = 0x0501
except:
    pass

# vxlapi.h: 593
try:
    XL_ETH_EVENT_TAG_FRAMETX_ERROR = 0x0506
except:
    pass

# vxlapi.h: 594
try:
    XL_ETH_EVENT_TAG_FRAMETX_ERROR_SWITCH = 0x0507
except:
    pass

# vxlapi.h: 595
try:
    XL_ETH_EVENT_TAG_FRAMETX_ACK = 0x0510
except:
    pass

# vxlapi.h: 596
try:
    XL_ETH_EVENT_TAG_FRAMETX_ACK_SWITCH = 0x0511
except:
    pass

# vxlapi.h: 597
try:
    XL_ETH_EVENT_TAG_FRAMETX_ACK_OTHER_APP = 0x0513
except:
    pass

# vxlapi.h: 598
try:
    XL_ETH_EVENT_TAG_FRAMETX_ERROR_OTHER_APP = 0x0514
except:
    pass

# vxlapi.h: 599
try:
    XL_ETH_EVENT_TAG_CHANNEL_STATUS = 0x0520
except:
    pass

# vxlapi.h: 600
try:
    XL_ETH_EVENT_TAG_CONFIGRESULT = 0x0530
except:
    pass

# vxlapi.h: 601
try:
    XL_ETH_EVENT_TAG_FRAMERX_SIMULATION = 0x0550
except:
    pass

# vxlapi.h: 602
try:
    XL_ETH_EVENT_TAG_FRAMERX_ERROR_SIMULATION = 0x0551
except:
    pass

# vxlapi.h: 604
try:
    XL_ETH_EVENT_TAG_FRAMETX_ACK_SIMULATION = 0x0552
except:
    pass

# vxlapi.h: 606
try:
    XL_ETH_EVENT_TAG_FRAMETX_ERROR_SIMULATION = 0x0553
except:
    pass

# vxlapi.h: 609
try:
    XL_ETH_EVENT_TAG_FRAMERX_MEASUREMENT = 0x0560
except:
    pass

# vxlapi.h: 611
try:
    XL_ETH_EVENT_TAG_FRAMERX_ERROR_MEASUREMENT = 0x0561
except:
    pass

# vxlapi.h: 613
try:
    XL_ETH_EVENT_TAG_FRAMETX_MEASUREMENT = 0x0562
except:
    pass

# vxlapi.h: 615
try:
    XL_ETH_EVENT_TAG_FRAMETX_ERROR_MEASUREMENT = 0x0563
except:
    pass

# vxlapi.h: 617
try:
    XL_ETH_EVENT_TAG_LOSTEVENT = 0x05fe
except:
    pass

# vxlapi.h: 619
try:
    XL_ETH_EVENT_TAG_ERROR = 0x05ff
except:
    pass

# vxlapi.h: 624
try:
    XL_A429_EV_TAG_TX_OK = 0x0600
except:
    pass

# vxlapi.h: 625
try:
    XL_A429_EV_TAG_TX_ERR = 0x0601
except:
    pass

# vxlapi.h: 626
try:
    XL_A429_EV_TAG_RX_OK = 0x0608
except:
    pass

# vxlapi.h: 627
try:
    XL_A429_EV_TAG_RX_ERR = 0x0609
except:
    pass

# vxlapi.h: 628
try:
    XL_A429_EV_TAG_BUS_STATISTIC = 0x060F
except:
    pass

# vxlapi.h: 643
try:
    XL_NOTIFY_REASON_CHANNEL_ACTIVATION = 1
except:
    pass

# vxlapi.h: 644
try:
    XL_NOTIFY_REASON_CHANNEL_DEACTIVATION = 2
except:
    pass

# vxlapi.h: 645
try:
    XL_NOTIFY_REASON_PORT_CLOSED = 3
except:
    pass

# vxlapi.h: 654
try:
    XL_SYNC_PULSE_EXTERNAL = 0x00
except:
    pass

# vxlapi.h: 655
try:
    XL_SYNC_PULSE_OUR = 0x01
except:
    pass

# vxlapi.h: 656
try:
    XL_SYNC_PULSE_OUR_SHARED = 0x02
except:
    pass

# vxlapi.h: 685
try:
    XL_HWTYPE_NONE = 0
except:
    pass

# vxlapi.h: 686
try:
    XL_HWTYPE_VIRTUAL = 1
except:
    pass

# vxlapi.h: 687
try:
    XL_HWTYPE_CANCARDX = 2
except:
    pass

# vxlapi.h: 688
try:
    XL_HWTYPE_CANAC2PCI = 6
except:
    pass

# vxlapi.h: 689
try:
    XL_HWTYPE_CANCARDY = 12
except:
    pass

# vxlapi.h: 690
try:
    XL_HWTYPE_CANCARDXL = 15
except:
    pass

# vxlapi.h: 691
try:
    XL_HWTYPE_CANCASEXL = 21
except:
    pass

# vxlapi.h: 692
try:
    XL_HWTYPE_CANCASEXL_LOG_OBSOLETE = 23
except:
    pass

# vxlapi.h: 693
try:
    XL_HWTYPE_CANBOARDXL = 25
except:
    pass

# vxlapi.h: 694
try:
    XL_HWTYPE_CANBOARDXL_PXI = 27
except:
    pass

# vxlapi.h: 695
try:
    XL_HWTYPE_VN2600 = 29
except:
    pass

# vxlapi.h: 696
try:
    XL_HWTYPE_VN2610 = XL_HWTYPE_VN2600
except:
    pass

# vxlapi.h: 697
try:
    XL_HWTYPE_VN3300 = 37
except:
    pass

# vxlapi.h: 698
try:
    XL_HWTYPE_VN3600 = 39
except:
    pass

# vxlapi.h: 699
try:
    XL_HWTYPE_VN7600 = 41
except:
    pass

# vxlapi.h: 700
try:
    XL_HWTYPE_CANCARDXLE = 43
except:
    pass

# vxlapi.h: 701
try:
    XL_HWTYPE_VN8900 = 45
except:
    pass

# vxlapi.h: 702
try:
    XL_HWTYPE_VN8950 = 47
except:
    pass

# vxlapi.h: 703
try:
    XL_HWTYPE_VN2640 = 53
except:
    pass

# vxlapi.h: 704
try:
    XL_HWTYPE_VN1610 = 55
except:
    pass

# vxlapi.h: 705
try:
    XL_HWTYPE_VN1614 = 56
except:
    pass

# vxlapi.h: 706
try:
    XL_HWTYPE_VN1630 = 57
except:
    pass

# vxlapi.h: 707
try:
    XL_HWTYPE_VN1615 = 58
except:
    pass

# vxlapi.h: 708
try:
    XL_HWTYPE_VN1640 = 59
except:
    pass

# vxlapi.h: 709
try:
    XL_HWTYPE_VN8970 = 61
except:
    pass

# vxlapi.h: 710
try:
    XL_HWTYPE_VN1611 = 63
except:
    pass

# vxlapi.h: 711
try:
    XL_HWTYPE_VN5240 = 64
except:
    pass

# vxlapi.h: 712
try:
    XL_HWTYPE_VN5610 = 65
except:
    pass

# vxlapi.h: 713
try:
    XL_HWTYPE_VN5620 = 66
except:
    pass

# vxlapi.h: 714
try:
    XL_HWTYPE_VN7570 = 67
except:
    pass

# vxlapi.h: 715
try:
    XL_HWTYPE_VN5650 = 68
except:
    pass

# vxlapi.h: 716
try:
    XL_HWTYPE_IPCLIENT = 69
except:
    pass

# vxlapi.h: 717
try:
    XL_HWTYPE_VN5611 = 70
except:
    pass

# vxlapi.h: 718
try:
    XL_HWTYPE_IPSERVER = 71
except:
    pass

# vxlapi.h: 719
try:
    XL_HWTYPE_VN5612 = 72
except:
    pass

# vxlapi.h: 720
try:
    XL_HWTYPE_VX1121 = 73
except:
    pass

# vxlapi.h: 721
try:
    XL_HWTYPE_VX1131 = 75
except:
    pass

# vxlapi.h: 722
try:
    XL_HWTYPE_VT6204 = 77
except:
    pass

# vxlapi.h: 723
try:
    XL_HWTYPE_VN5614 = 78
except:
    pass

# vxlapi.h: 724
try:
    XL_HWTYPE_VN1630_LOG = 79
except:
    pass

# vxlapi.h: 725
try:
    XL_HWTYPE_VN7610 = 81
except:
    pass

# vxlapi.h: 726
try:
    XL_HWTYPE_VN7572 = 83
except:
    pass

# vxlapi.h: 727
try:
    XL_HWTYPE_VN8972 = 85
except:
    pass

# vxlapi.h: 728
try:
    XL_HWTYPE_VN1641 = 86
except:
    pass

# vxlapi.h: 729
try:
    XL_HWTYPE_VN0601 = 87
except:
    pass

# vxlapi.h: 730
try:
    XL_HWTYPE_VT6104B = 88
except:
    pass

# vxlapi.h: 731
try:
    XL_HWTYPE_VN5640 = 89
except:
    pass

# vxlapi.h: 732
try:
    XL_HWTYPE_VT6204B = 90
except:
    pass

# vxlapi.h: 733
try:
    XL_HWTYPE_VX0312 = 91
except:
    pass

# vxlapi.h: 734
try:
    XL_HWTYPE_VH6501 = 94
except:
    pass

# vxlapi.h: 735
try:
    XL_HWTYPE_VN8800 = 95
except:
    pass

# vxlapi.h: 736
try:
    XL_HWTYPE_IPCL8800 = 96
except:
    pass

# vxlapi.h: 737
try:
    XL_HWTYPE_IPSRV8800 = 97
except:
    pass

# vxlapi.h: 738
try:
    XL_HWTYPE_CSMCAN = 98
except:
    pass

# vxlapi.h: 739
try:
    XL_HWTYPE_VN5610A = 101
except:
    pass

# vxlapi.h: 740
try:
    XL_HWTYPE_VN7640 = 102
except:
    pass

# vxlapi.h: 741
try:
    XL_HWTYPE_VX1135 = 104
except:
    pass

# vxlapi.h: 742
try:
    XL_HWTYPE_VN4610 = 105
except:
    pass

# vxlapi.h: 743
try:
    XL_HWTYPE_VT6306 = 107
except:
    pass

# vxlapi.h: 744
try:
    XL_HWTYPE_VT6104A = 108
except:
    pass

# vxlapi.h: 745
try:
    XL_HWTYPE_VN5430 = 109
except:
    pass

# vxlapi.h: 746
try:
    XL_HWTYPE_VTSSERVICE = 110
except:
    pass

# vxlapi.h: 747
try:
    XL_HWTYPE_VN1530 = 112
except:
    pass

# vxlapi.h: 748
try:
    XL_HWTYPE_VN1531 = 113
except:
    pass

# vxlapi.h: 749
try:
    XL_HWTYPE_VX1161A = 114
except:
    pass

# vxlapi.h: 750
try:
    XL_HWTYPE_VX1161B = 115
except:
    pass

# vxlapi.h: 751
try:
    XL_HWTYPE_VN1670 = 120
except:
    pass

# vxlapi.h: 752
try:
    XL_HWTYPE_VN5620A = 121
except:
    pass

# vxlapi.h: 753
try:
    XL_MAX_HWTYPE = 123
except:
    pass

# vxlapi.h: 756
try:
    XL_DAIO_IGNORE_CHANNEL = (-1)
except:
    pass

# vxlapi.h: 765
try:
    XL_USE_ALL_CHANNELS = 0xFFFFFFFFFFFFFFFF
except:
    pass

# vxlapi.h: 766
try:
    XL_INVALID_CHANNEL_INDEX = 0xFFFFFFFF
except:
    pass

# vxlapi.h: 767
try:
    XL_INVALID_DEVICE_INDEX = 0xFFFFFFFF
except:
    pass

# vxlapi.h: 780
try:
    XL_LIN_MASTER = 0x01
except:
    pass

# vxlapi.h: 781
try:
    XL_LIN_SLAVE = 0x02
except:
    pass

# vxlapi.h: 782
try:
    XL_LIN_VERSION_1_3 = 0x01
except:
    pass

# vxlapi.h: 783
try:
    XL_LIN_VERSION_2_0 = 0x02
except:
    pass

# vxlapi.h: 784
try:
    XL_LIN_VERSION_2_1 = 0x03
except:
    pass

# vxlapi.h: 787
try:
    XL_LIN_CALC_CHECKSUM = 0x100
except:
    pass

# vxlapi.h: 788
try:
    XL_LIN_CALC_CHECKSUM_ENHANCED = 0x200
except:
    pass

# vxlapi.h: 791
try:
    XL_LIN_FLAG_NO_SLEEP_MODE_EVENT = 0x01
except:
    pass

# vxlapi.h: 792
try:
    XL_LIN_FLAG_USE_ID_AS_WAKEUPID = 0x02
except:
    pass

# vxlapi.h: 794
try:
    XL_LIN_SET_SILENT = XL_LIN_FLAG_NO_SLEEP_MODE_EVENT
except:
    pass

# vxlapi.h: 795
try:
    XL_LIN_SET_WAKEUPID = (XL_LIN_FLAG_NO_SLEEP_MODE_EVENT | XL_LIN_FLAG_USE_ID_AS_WAKEUPID)
except:
    pass

# vxlapi.h: 800
try:
    XL_LIN_CHECKSUM_CLASSIC = 0x00
except:
    pass

# vxlapi.h: 801
try:
    XL_LIN_CHECKSUM_ENHANCED = 0x01
except:
    pass

# vxlapi.h: 802
try:
    XL_LIN_CHECKSUM_UNDEFINED = 0xff
except:
    pass

# vxlapi.h: 805
try:
    XL_LIN_STAYALIVE = 0x00
except:
    pass

# vxlapi.h: 806
try:
    XL_LIN_SET_SLEEPMODE = 0x01
except:
    pass

# vxlapi.h: 807
try:
    XL_LIN_COMESFROM_SLEEPMODE = 0x02
except:
    pass

# vxlapi.h: 810
try:
    XL_LIN_WAKUP_INTERNAL = 0x01
except:
    pass

# vxlapi.h: 813
try:
    XL_LIN_UNDEFINED_DLC = 0xff
except:
    pass

# vxlapi.h: 816
try:
    XL_LIN_SLAVE_ON = 0xff
except:
    pass

# vxlapi.h: 817
try:
    XL_LIN_SLAVE_OFF = 0x00
except:
    pass

# vxlapi.h: 835
try:
    MAX_MSG_LEN = 8
except:
    pass

# vxlapi.h: 839
try:
    XL_INTERFACE_VERSION_V2 = 2
except:
    pass

# vxlapi.h: 840
try:
    XL_INTERFACE_VERSION_V3 = 3
except:
    pass

# vxlapi.h: 841
try:
    XL_INTERFACE_VERSION_V4 = 4
except:
    pass

# vxlapi.h: 843
try:
    XL_INTERFACE_VERSION = XL_INTERFACE_VERSION_V3
except:
    pass

# vxlapi.h: 845
try:
    XL_CAN_EXT_MSG_ID = 0x80000000
except:
    pass

# vxlapi.h: 847
try:
    XL_CAN_MSG_FLAG_ERROR_FRAME = 0x01
except:
    pass

# vxlapi.h: 848
try:
    XL_CAN_MSG_FLAG_OVERRUN = 0x02
except:
    pass

# vxlapi.h: 849
try:
    XL_CAN_MSG_FLAG_NERR = 0x04
except:
    pass

# vxlapi.h: 850
try:
    XL_CAN_MSG_FLAG_WAKEUP = 0x08
except:
    pass

# vxlapi.h: 851
try:
    XL_CAN_MSG_FLAG_REMOTE_FRAME = 0x10
except:
    pass

# vxlapi.h: 852
try:
    XL_CAN_MSG_FLAG_RESERVED_1 = 0x20
except:
    pass

# vxlapi.h: 853
try:
    XL_CAN_MSG_FLAG_TX_COMPLETED = 0x40
except:
    pass

# vxlapi.h: 854
try:
    XL_CAN_MSG_FLAG_TX_REQUEST = 0x80
except:
    pass

# vxlapi.h: 855
try:
    XL_CAN_MSG_FLAG_SRR_BIT_DOM = 0x0200
except:
    pass

# vxlapi.h: 857
try:
    XL_EVENT_FLAG_OVERRUN = 0x01
except:
    pass

# vxlapi.h: 860
try:
    XL_LIN_MSGFLAG_TX = XL_CAN_MSG_FLAG_TX_COMPLETED
except:
    pass

# vxlapi.h: 861
try:
    XL_LIN_MSGFLAG_CRCERROR = 0x81
except:
    pass

# vxlapi.h: 880
try:
    XL_DAIO_DATA_GET = 0x8000
except:
    pass

# vxlapi.h: 881
try:
    XL_DAIO_DATA_VALUE_DIGITAL = 0x0001
except:
    pass

# vxlapi.h: 882
try:
    XL_DAIO_DATA_VALUE_ANALOG = 0x0002
except:
    pass

# vxlapi.h: 883
try:
    XL_DAIO_DATA_PWM = 0x0010
except:
    pass

# vxlapi.h: 886
try:
    XL_DAIO_MODE_PULSE = 0x0020
except:
    pass

# vxlapi.h: 928
try:
    XL_CHIPSTAT_BUSOFF = 0x01
except:
    pass

# vxlapi.h: 929
try:
    XL_CHIPSTAT_ERROR_PASSIVE = 0x02
except:
    pass

# vxlapi.h: 930
try:
    XL_CHIPSTAT_ERROR_WARNING = 0x04
except:
    pass

# vxlapi.h: 931
try:
    XL_CHIPSTAT_ERROR_ACTIVE = 0x08
except:
    pass

# vxlapi.h: 942
try:
    XL_TRANSCEIVER_EVENT_NONE = 0
except:
    pass

# vxlapi.h: 943
try:
    XL_TRANSCEIVER_EVENT_INSERTED = 1
except:
    pass

# vxlapi.h: 944
try:
    XL_TRANSCEIVER_EVENT_REMOVED = 2
except:
    pass

# vxlapi.h: 945
try:
    XL_TRANSCEIVER_EVENT_STATE_CHANGE = 3
except:
    pass

# vxlapi.h: 954
try:
    XL_OUTPUT_MODE_SILENT = 0
except:
    pass

# vxlapi.h: 955
try:
    XL_OUTPUT_MODE_NORMAL = 1
except:
    pass

# vxlapi.h: 956
try:
    XL_OUTPUT_MODE_TX_OFF = 2
except:
    pass

# vxlapi.h: 957
try:
    XL_OUTPUT_MODE_SJA_1000_SILENT = 3
except:
    pass

# vxlapi.h: 961
try:
    XL_TRANSCEIVER_EVENT_ERROR = 1
except:
    pass

# vxlapi.h: 962
try:
    XL_TRANSCEIVER_EVENT_CHANGED = 2
except:
    pass

# vxlapi.h: 1138
try:
    DriverNotifyMessageName = 'VectorCanDriverChangeNotifyMessage'
except:
    pass

# vxlapi.h: 1142
def XL_CHANNEL_MASK(x):
    return (1 << x)

# vxlapi.h: 1144
try:
    XL_MAX_APPNAME = 32
except:
    pass

# vxlapi.h: 1152
try:
    XL_MAX_LENGTH = 31
except:
    pass

# vxlapi.h: 1153
try:
    XL_CONFIG_MAX_CHANNELS = 64
except:
    pass

# vxlapi.h: 1154
try:
    XL_MAX_NAME_LENGTH = 48
except:
    pass

# vxlapi.h: 1159
try:
    XL_APPLCONFIG_MAX_CHANNELS = 256
except:
    pass

# vxlapi.h: 1162
try:
    XL_ACTIVATE_NONE = 0
except:
    pass

# vxlapi.h: 1163
try:
    XL_ACTIVATE_RESET_CLOCK = 8
except:
    pass

# vxlapi.h: 1166
try:
    XL_BUS_COMPATIBLE_CAN = XL_BUS_TYPE_CAN
except:
    pass

# vxlapi.h: 1167
try:
    XL_BUS_COMPATIBLE_LIN = XL_BUS_TYPE_LIN
except:
    pass

# vxlapi.h: 1168
try:
    XL_BUS_COMPATIBLE_FLEXRAY = XL_BUS_TYPE_FLEXRAY
except:
    pass

# vxlapi.h: 1169
try:
    XL_BUS_COMPATIBLE_MOST = XL_BUS_TYPE_MOST
except:
    pass

# vxlapi.h: 1170
try:
    XL_BUS_COMPATIBLE_DAIO = XL_BUS_TYPE_DAIO
except:
    pass

# vxlapi.h: 1171
try:
    XL_BUS_COMPATIBLE_J1708 = XL_BUS_TYPE_J1708
except:
    pass

# vxlapi.h: 1172
try:
    XL_BUS_COMPATIBLE_KLINE = XL_BUS_TYPE_KLINE
except:
    pass

# vxlapi.h: 1173
try:
    XL_BUS_COMPATIBLE_ETHERNET = XL_BUS_TYPE_ETHERNET
except:
    pass

# vxlapi.h: 1174
try:
    XL_BUS_COMPATIBLE_A429 = XL_BUS_TYPE_A429
except:
    pass

# vxlapi.h: 1177
try:
    XL_BUS_ACTIVE_CAP_CAN = (XL_BUS_COMPATIBLE_CAN << 16)
except:
    pass

# vxlapi.h: 1178
try:
    XL_BUS_ACTIVE_CAP_LIN = (XL_BUS_COMPATIBLE_LIN << 16)
except:
    pass

# vxlapi.h: 1179
try:
    XL_BUS_ACTIVE_CAP_FLEXRAY = (XL_BUS_COMPATIBLE_FLEXRAY << 16)
except:
    pass

# vxlapi.h: 1180
try:
    XL_BUS_ACTIVE_CAP_MOST = (XL_BUS_COMPATIBLE_MOST << 16)
except:
    pass

# vxlapi.h: 1181
try:
    XL_BUS_ACTIVE_CAP_DAIO = (XL_BUS_COMPATIBLE_DAIO << 16)
except:
    pass

# vxlapi.h: 1182
try:
    XL_BUS_ACTIVE_CAP_J1708 = (XL_BUS_COMPATIBLE_J1708 << 16)
except:
    pass

# vxlapi.h: 1183
try:
    XL_BUS_ACTIVE_CAP_KLINE = (XL_BUS_COMPATIBLE_KLINE << 16)
except:
    pass

# vxlapi.h: 1184
try:
    XL_BUS_ACTIVE_CAP_ETHERNET = (XL_BUS_COMPATIBLE_ETHERNET << 16)
except:
    pass

# vxlapi.h: 1185
try:
    XL_BUS_ACTIVE_CAP_A429 = (XL_BUS_COMPATIBLE_A429 << 16)
except:
    pass

# vxlapi.h: 1187
try:
    XL_BUS_NAME_NONE = ''
except:
    pass

# vxlapi.h: 1188
try:
    XL_BUS_NAME_CAN = 'CAN'
except:
    pass

# vxlapi.h: 1189
try:
    XL_BUS_NAME_LIN = 'LIN'
except:
    pass

# vxlapi.h: 1190
try:
    XL_BUS_NAME_FLEXRAY = 'FlexRay'
except:
    pass

# vxlapi.h: 1191
try:
    XL_BUS_NAME_STREAM = 'Stream'
except:
    pass

# vxlapi.h: 1192
try:
    XL_BUS_NAME_MOST = 'MOST'
except:
    pass

# vxlapi.h: 1193
try:
    XL_BUS_NAME_DAIO = 'DAIO'
except:
    pass

# vxlapi.h: 1194
try:
    XL_BUS_NAME_HWSYNC_KEYPAD = 'HWSYNC_KEYPAD'
except:
    pass

# vxlapi.h: 1195
try:
    XL_BUS_NAME_J1708 = 'J1708'
except:
    pass

# vxlapi.h: 1196
try:
    XL_BUS_NAME_KLINE = 'K-Line'
except:
    pass

# vxlapi.h: 1197
try:
    XL_BUS_NAME_ETHERNET = 'Ethernet'
except:
    pass

# vxlapi.h: 1198
try:
    XL_BUS_NAME_AFDX = 'AFDX'
except:
    pass

# vxlapi.h: 1199
try:
    XL_BUS_NAME_A429 = 'ARINC429'
except:
    pass

# vxlapi.h: 1205
try:
    XL_CAN_STD = 0x01
except:
    pass

# vxlapi.h: 1206
try:
    XL_CAN_EXT = 0x02
except:
    pass

# vxlapi.h: 1211
try:
    CANFD_CONFOPT_NO_ISO = 0x08
except:
    pass

# vxlapi.h: 1238
try:
    XL_BUS_PARAMS_MOST_SPEED_GRADE_25 = 0x01
except:
    pass

# vxlapi.h: 1239
try:
    XL_BUS_PARAMS_MOST_SPEED_GRADE_150 = 0x02
except:
    pass

# vxlapi.h: 1242
try:
    XL_BUS_PARAMS_CANOPMODE_CAN20 = 0x01
except:
    pass

# vxlapi.h: 1243
try:
    XL_BUS_PARAMS_CANOPMODE_CANFD = 0x02
except:
    pass

# vxlapi.h: 1244
try:
    XL_BUS_PARAMS_CANOPMODE_CANFD_NO_ISO = 0x08
except:
    pass

# vxlapi.h: 1329
try:
    XL_INVALID_PORTHANDLE = (-1)
except:
    pass

# vxlapi.h: 1332
try:
    XL_CONNECTION_INFO_FAMILY_MASK = 0xff000000
except:
    pass

# vxlapi.h: 1333
try:
    XL_CONNECTION_INFO_DETAIL_MASK = 0x00ffffff
except:
    pass

# vxlapi.h: 1336
try:
    XL_CONNECTION_INFO_FAMILY_USB = (0 << 24)
except:
    pass

# vxlapi.h: 1337
try:
    XL_CONNECTION_INFO_FAMILY_NETWORK = (1 << 24)
except:
    pass

# vxlapi.h: 1338
try:
    XL_CONNECTION_INFO_FAMILY_PCIE = (2 << 24)
except:
    pass

# vxlapi.h: 1341
try:
    XL_CONNECTION_INFO_USB_UNKNOWN = 0
except:
    pass

# vxlapi.h: 1342
try:
    XL_CONNECTION_INFO_USB_FULLSPEED = 1
except:
    pass

# vxlapi.h: 1343
try:
    XL_CONNECTION_INFO_USB_HIGHSPEED = 2
except:
    pass

# vxlapi.h: 1344
try:
    XL_CONNECTION_INFO_USB_SUPERSPEED = 3
except:
    pass

# vxlapi.h: 1346
try:
    XL_FPGA_CORE_TYPE_NONE = 0
except:
    pass

# vxlapi.h: 1347
try:
    XL_FPGA_CORE_TYPE_CAN = 1
except:
    pass

# vxlapi.h: 1348
try:
    XL_FPGA_CORE_TYPE_LIN = 2
except:
    pass

# vxlapi.h: 1349
try:
    XL_FPGA_CORE_TYPE_LIN_RX = 3
except:
    pass

# vxlapi.h: 1352
try:
    XL_SPECIAL_DEVICE_STAT_FPGA_UPDATE_DONE = 0x01
except:
    pass

# vxlapi.h: 1430
try:
    XL_DAIO_DIGITAL_ENABLED = 0x00000001
except:
    pass

# vxlapi.h: 1431
try:
    XL_DAIO_DIGITAL_INPUT = 0x00000002
except:
    pass

# vxlapi.h: 1432
try:
    XL_DAIO_DIGITAL_TRIGGER = 0x00000004
except:
    pass

# vxlapi.h: 1434
try:
    XL_DAIO_ANALOG_ENABLED = 0x00000001
except:
    pass

# vxlapi.h: 1435
try:
    XL_DAIO_ANALOG_INPUT = 0x00000002
except:
    pass

# vxlapi.h: 1436
try:
    XL_DAIO_ANALOG_TRIGGER = 0x00000004
except:
    pass

# vxlapi.h: 1437
try:
    XL_DAIO_ANALOG_RANGE_32V = 0x00000008
except:
    pass

# vxlapi.h: 1440
try:
    XL_DAIO_TRIGGER_MODE_NONE = 0x00000000
except:
    pass

# vxlapi.h: 1441
try:
    XL_DAIO_TRIGGER_MODE_DIGITAL = 0x00000001
except:
    pass

# vxlapi.h: 1442
try:
    XL_DAIO_TRIGGER_MODE_ANALOG_ASCENDING = 0x00000002
except:
    pass

# vxlapi.h: 1443
try:
    XL_DAIO_TRIGGER_MODE_ANALOG_DESCENDING = 0x00000004
except:
    pass

# vxlapi.h: 1444
try:
    XL_DAIO_TRIGGER_MODE_ANALOG = (XL_DAIO_TRIGGER_MODE_ANALOG_ASCENDING | XL_DAIO_TRIGGER_MODE_ANALOG_DESCENDING)
except:
    pass

# vxlapi.h: 1447
try:
    XL_DAIO_TRIGGER_LEVEL_NONE = 0
except:
    pass

# vxlapi.h: 1450
try:
    XL_DAIO_POLLING_NONE = 0
except:
    pass

# vxlapi.h: 1468
try:
    XL_SET_TIMESYNC_NO_CHANGE = 0
except:
    pass

# vxlapi.h: 1469
try:
    XL_SET_TIMESYNC_ON = 1
except:
    pass

# vxlapi.h: 1470
try:
    XL_SET_TIMESYNC_OFF = 2
except:
    pass

XLuserHandle = c_ushort# vxlapi.h: 1480

# vxlapi.h: 1483
try:
    MOST_ALLOC_TABLE_SIZE = 64
except:
    pass

# vxlapi.h: 1489
try:
    XL_IPv4 = 4
except:
    pass

# vxlapi.h: 1490
try:
    XL_IPv6 = 6
except:
    pass

# vxlapi.h: 1493
try:
    XL_MAX_REMOTE_DEVICE_INFO = 16
except:
    pass

# vxlapi.h: 1494
try:
    XL_ALL_REMOTE_DEVICES = 0xFFFFFFFF
except:
    pass

# vxlapi.h: 1495
try:
    XL_MAX_REMOTE_ALIAS_SIZE = 64
except:
    pass

# vxlapi.h: 1497
try:
    XL_REMOTE_OFFLINE = 1
except:
    pass

# vxlapi.h: 1498
try:
    XL_REMOTE_ONLINE = 2
except:
    pass

# vxlapi.h: 1499
try:
    XL_REMOTE_BUSY = 3
except:
    pass

# vxlapi.h: 1500
try:
    XL_REMOTE_CONNECION_REFUSED = 4
except:
    pass

# vxlapi.h: 1502
try:
    XL_REMOTE_ADD_PERMANENT = 0x0
except:
    pass

# vxlapi.h: 1503
try:
    XL_REMOTE_ADD_TEMPORARY = 0x1
except:
    pass

# vxlapi.h: 1505
try:
    XL_REMOTE_REGISTER_NONE = 0x0
except:
    pass

# vxlapi.h: 1506
try:
    XL_REMOTE_REGISTER_CONNECT = 0x1
except:
    pass

# vxlapi.h: 1507
try:
    XL_REMOTE_REGISTER_TEMP_CONNECT = 0x2
except:
    pass

# vxlapi.h: 1509
try:
    XL_REMOTE_DISCONNECT_NONE = 0x0
except:
    pass

# vxlapi.h: 1510
try:
    XL_REMOTE_DISCONNECT_REMOVE_ENTRY = 0x1
except:
    pass

# vxlapi.h: 1512
try:
    XL_REMOTE_DEVICE_AVAILABLE = 0x00000001
except:
    pass

# vxlapi.h: 1513
try:
    XL_REMOTE_DEVICE_CONFIGURED = 0x00000002
except:
    pass

# vxlapi.h: 1514
try:
    XL_REMOTE_DEVICE_CONNECTED = 0x00000004
except:
    pass

# vxlapi.h: 1515
try:
    XL_REMOTE_DEVICE_ENABLED = 0x00000008
except:
    pass

# vxlapi.h: 1516
try:
    XL_REMOTE_DEVICE_BUSY = 0x00000010
except:
    pass

# vxlapi.h: 1517
try:
    XL_REMOTE_DEVICE_TEMP_CONFIGURED = 0x00000020
except:
    pass

# vxlapi.h: 1519
try:
    XL_REMOTE_DEVICE_STATUS_MASK = 0x0000003F
except:
    pass

# vxlapi.h: 1521
try:
    XL_REMOTE_NO_NET_SEARCH = 0
except:
    pass

# vxlapi.h: 1522
try:
    XL_REMOTE_NET_SEARCH = 1
except:
    pass

# vxlapi.h: 1524
try:
    XL_REMOTE_DEVICE_TYPE_UNKNOWN = 0
except:
    pass

# vxlapi.h: 1525
try:
    XL_REMOTE_DEVICE_TYPE_VN8900 = 1
except:
    pass

# vxlapi.h: 1526
try:
    XL_REMOTE_DEVICE_TYPE_STANDARD_PC = 2
except:
    pass

# vxlapi.h: 1527
try:
    XL_REMOTE_DEVICE_TYPE_VX = 3
except:
    pass

# vxlapi.h: 1528
try:
    XL_REMOTE_DEVICE_TYPE_VN8800 = 4
except:
    pass

# vxlapi.h: 1529
try:
    XL_REMOTE_DEVICE_TYPE_VN = 5
except:
    pass

# vxlapi.h: 1530
try:
    XL_REMOTE_DEVICE_TYPE_VT = 6
except:
    pass

# vxlapi.h: 1589
try:
    XL_CHANNEL_FLAG_TIME_SYNC_RUNNING = 0x00000001
except:
    pass

# vxlapi.h: 1590
try:
    XL_CHANNEL_FLAG_NO_HWSYNC_SUPPORT = 0x00000400
except:
    pass

# vxlapi.h: 1592
try:
    XL_CHANNEL_FLAG_SPDIF_CAPABLE = 0x00004000
except:
    pass

# vxlapi.h: 1593
try:
    XL_CHANNEL_FLAG_CANFD_BOSCH_SUPPORT = 0x20000000
except:
    pass

# vxlapi.h: 1594
try:
    XL_CHANNEL_FLAG_CMACTLICENSE_SUPPORT = 0x40000000
except:
    pass

# vxlapi.h: 1595
try:
    XL_CHANNEL_FLAG_CANFD_ISO_SUPPORT = 0x80000000
except:
    pass

# vxlapi.h: 1597
def XL_CHANNEL_FLAG_EX_MASK(n):
    return (1 << n)

# vxlapi.h: 1599
try:
    XL_CHANNEL_FLAG_EX1_TIME_SYNC_RUNNING = (XL_CHANNEL_FLAG_EX_MASK (0))
except:
    pass

# vxlapi.h: 1600
try:
    XL_CHANNEL_FLAG_EX1_HWSYNC_SUPPORT = (XL_CHANNEL_FLAG_EX_MASK (4))
except:
    pass

# vxlapi.h: 1601
try:
    XL_CHANNEL_FLAG_EX1_CANFD_ISO_SUPPORT = (XL_CHANNEL_FLAG_EX_MASK (10))
except:
    pass

# vxlapi.h: 1603
try:
    XL_CHANNEL_FLAG_EX1_SPDIF_CAPABLE = (XL_CHANNEL_FLAG_EX_MASK (20))
except:
    pass

# vxlapi.h: 1604
try:
    XL_CHANNEL_FLAG_EX1_CANFD_BOSCH_SUPPORT = (XL_CHANNEL_FLAG_EX_MASK (35))
except:
    pass

# vxlapi.h: 1606
try:
    XL_CHANNEL_FLAG_EX1_NET_ETH_SUPPORT = (XL_CHANNEL_FLAG_EX_MASK (36))
except:
    pass

# vxlapi.h: 1607
try:
    XL_CHANNEL_FLAG_EX1_TIME_SYNC_SERVICE_PROTOCOL_RUNNING = (XL_CHANNEL_FLAG_EX_MASK (51))
except:
    pass

# vxlapi.h: 1610
try:
    XL_MOST_SOURCE_ASYNC_SPY = 0x8000
except:
    pass

# vxlapi.h: 1611
try:
    XL_MOST_SOURCE_ASYNC_RX = 0x1000
except:
    pass

# vxlapi.h: 1612
try:
    XL_MOST_SOURCE_ASYNC_TX = 0x0800
except:
    pass

# vxlapi.h: 1613
try:
    XL_MOST_SOURCE_CTRL_OS8104A = 0x0400
except:
    pass

# vxlapi.h: 1614
try:
    XL_MOST_SOURCE_CTRL_SPY = 0x0100
except:
    pass

# vxlapi.h: 1615
try:
    XL_MOST_SOURCE_ALLOC_TABLE = 0x0080
except:
    pass

# vxlapi.h: 1616
try:
    XL_MOST_SOURCE_SYNC_RC_OVER = 0x0040
except:
    pass

# vxlapi.h: 1617
try:
    XL_MOST_SOURCE_SYNC_TX_UNDER = 0x0020
except:
    pass

# vxlapi.h: 1618
try:
    XL_MOST_SOURCE_SYNCLINE = 0x0010
except:
    pass

# vxlapi.h: 1619
try:
    XL_MOST_SOURCE_ASYNC_RX_FIFO_OVER = 0x0008
except:
    pass

# vxlapi.h: 1622
try:
    XL_MOST_OS8104_TX_LOCK_ERROR = 0x00000001
except:
    pass

# vxlapi.h: 1623
try:
    XL_MOST_OS8104_SPDIF_LOCK_ERROR = 0x00000002
except:
    pass

# vxlapi.h: 1624
try:
    XL_MOST_OS8104_ASYNC_BUFFER_FULL = 0x00000003
except:
    pass

# vxlapi.h: 1625
try:
    XL_MOST_OS8104_ASYNC_CRC_ERROR = 0x00000004
except:
    pass

# vxlapi.h: 1626
try:
    XL_MOST_ASYNC_TX_UNDERRUN = 0x00000005
except:
    pass

# vxlapi.h: 1627
try:
    XL_MOST_CTRL_TX_UNDERRUN = 0x00000006
except:
    pass

# vxlapi.h: 1628
try:
    XL_MOST_MCU_TS_CMD_QUEUE_UNDERRUN = 0x00000007
except:
    pass

# vxlapi.h: 1629
try:
    XL_MOST_MCU_TS_CMD_QUEUE_OVERRUN = 0x00000008
except:
    pass

# vxlapi.h: 1630
try:
    XL_MOST_CMD_TX_UNDERRUN = 0x00000009
except:
    pass

# vxlapi.h: 1631
try:
    XL_MOST_SYNCPULSE_ERROR = 0x0000000A
except:
    pass

# vxlapi.h: 1632
try:
    XL_MOST_OS8104_CODING_ERROR = 0x0000000B
except:
    pass

# vxlapi.h: 1633
try:
    XL_MOST_ERROR_UNKNOWN_COMMAND = 0x0000000C
except:
    pass

# vxlapi.h: 1634
try:
    XL_MOST_ASYNC_RX_OVERFLOW_ERROR = 0x0000000D
except:
    pass

# vxlapi.h: 1635
try:
    XL_MOST_FPGA_TS_FIFO_OVERFLOW = 0x0000000E
except:
    pass

# vxlapi.h: 1636
try:
    XL_MOST_SPY_OVERFLOW_ERROR = 0x0000000F
except:
    pass

# vxlapi.h: 1637
try:
    XL_MOST_CTRL_TYPE_QUEUE_OVERFLOW = 0x00000010
except:
    pass

# vxlapi.h: 1638
try:
    XL_MOST_ASYNC_TYPE_QUEUE_OVERFLOW = 0x00000011
except:
    pass

# vxlapi.h: 1639
try:
    XL_MOST_CTRL_UNKNOWN_TYPE = 0x00000012
except:
    pass

# vxlapi.h: 1640
try:
    XL_MOST_CTRL_QUEUE_UNDERRUN = 0x00000013
except:
    pass

# vxlapi.h: 1641
try:
    XL_MOST_ASYNC_UNKNOWN_TYPE = 0x00000014
except:
    pass

# vxlapi.h: 1642
try:
    XL_MOST_ASYNC_QUEUE_UNDERRUN = 0x00000015
except:
    pass

# vxlapi.h: 1645
try:
    XL_MOST_DEMANDED_START = 0x00000001
except:
    pass

# vxlapi.h: 1647
try:
    XL_MOST_RX_DATA_SIZE = 1028
except:
    pass

# vxlapi.h: 1648
try:
    XL_MOST_TS_DATA_SIZE = 12
except:
    pass

# vxlapi.h: 1649
try:
    XL_MOST_RX_ELEMENT_HEADER_SIZE = 32
except:
    pass

# vxlapi.h: 1650
try:
    XL_MOST_CTRL_RX_SPY_SIZE = 36
except:
    pass

# vxlapi.h: 1651
try:
    XL_MOST_CTRL_RX_OS8104_SIZE = 28
except:
    pass

# vxlapi.h: 1652
try:
    XL_MOST_SPECIAL_REGISTER_CHANGE_SIZE = 20
except:
    pass

# vxlapi.h: 1653
try:
    XL_MOST_ERROR_EV_SIZE_4 = 4
except:
    pass

# vxlapi.h: 1654
try:
    XL_MOST_ERROR_EV_SIZE = 16
except:
    pass

# vxlapi.h: 1657
try:
    XL_MOST_DEVICE_CASE_LINE_IN = 0
except:
    pass

# vxlapi.h: 1658
try:
    XL_MOST_DEVICE_CASE_LINE_OUT = 1
except:
    pass

# vxlapi.h: 1659
try:
    XL_MOST_DEVICE_SPDIF_IN = 7
except:
    pass

# vxlapi.h: 1660
try:
    XL_MOST_DEVICE_SPDIF_OUT = 8
except:
    pass

# vxlapi.h: 1661
try:
    XL_MOST_DEVICE_SPDIF_IN_OUT_SYNC = 11
except:
    pass

# vxlapi.h: 1664
try:
    XL_MOST_SPDIF_LOCK_OFF = 0
except:
    pass

# vxlapi.h: 1665
try:
    XL_MOST_SPDIF_LOCK_ON = 1
except:
    pass

# vxlapi.h: 1668
try:
    XL_MOST_NO_MUTE = 0
except:
    pass

# vxlapi.h: 1669
try:
    XL_MOST_MUTE = 1
except:
    pass

# vxlapi.h: 1672
try:
    XL_MOST_VN2600 = 0x01
except:
    pass

# vxlapi.h: 1673
try:
    XL_MOST_OS8104A = 0x02
except:
    pass

# vxlapi.h: 1674
try:
    XL_MOST_OS8104B = 0x04
except:
    pass

# vxlapi.h: 1675
try:
    XL_MOST_SPY = 0x08
except:
    pass

# vxlapi.h: 1678
try:
    XL_MOST_MODE_DEACTIVATE = 0
except:
    pass

# vxlapi.h: 1679
try:
    XL_MOST_MODE_ACTIVATE = 1
except:
    pass

# vxlapi.h: 1680
try:
    XL_MOST_MODE_FORCE_DEACTIVATE = 2
except:
    pass

# vxlapi.h: 1682
try:
    XL_MOST_RX_BUFFER_CLEAR_ONCE = 2
except:
    pass

# vxlapi.h: 1685
try:
    XL_MOST_TIMING_SLAVE = 0
except:
    pass

# vxlapi.h: 1686
try:
    XL_MOST_TIMING_MASTER = 1
except:
    pass

# vxlapi.h: 1687
try:
    XL_MOST_TIMING_SLAVE_SPDIF_MASTER = 2
except:
    pass

# vxlapi.h: 1688
try:
    XL_MOST_TIMING_SLAVE_SPDIF_SLAVE = 3
except:
    pass

# vxlapi.h: 1689
try:
    XL_MOST_TIMING_MASTER_SPDIF_MASTER = 4
except:
    pass

# vxlapi.h: 1690
try:
    XL_MOST_TIMING_MASTER_SPDIF_SLAVE = 5
except:
    pass

# vxlapi.h: 1691
try:
    XL_MOST_TIMING_MASTER_FROM_SPDIF_SLAVE = 6
except:
    pass

# vxlapi.h: 1695
try:
    XL_MOST_FREQUENCY_44100 = 0
except:
    pass

# vxlapi.h: 1696
try:
    XL_MOST_FREQUENCY_48000 = 1
except:
    pass

# vxlapi.h: 1697
try:
    XL_MOST_FREQUENCY_ERROR = 2
except:
    pass

# vxlapi.h: 1700
try:
    XL_MOST_LIGHT_OFF = 0
except:
    pass

# vxlapi.h: 1701
try:
    XL_MOST_LIGHT_FORCE_ON = 1
except:
    pass

# vxlapi.h: 1702
try:
    XL_MOST_LIGHT_MODULATED = 2
except:
    pass

# vxlapi.h: 1705
try:
    XL_MOST_LIGHT_FULL = 100
except:
    pass

# vxlapi.h: 1706
try:
    XL_MOST_LIGHT_3DB = 50
except:
    pass

# vxlapi.h: 1709
try:
    XL_MOST_UNLOCK = 5
except:
    pass

# vxlapi.h: 1710
try:
    XL_MOST_LOCK = 6
except:
    pass

# vxlapi.h: 1711
try:
    XL_MOST_STATE_UNKNOWN = 9
except:
    pass

# vxlapi.h: 1714
try:
    XL_MOST_TX_WHILE_UNLOCKED = 0x80000000
except:
    pass

# vxlapi.h: 1715
try:
    XL_MOST_TX_TIMEOUT = 0x40000000
except:
    pass

# vxlapi.h: 1716
try:
    XL_MOST_DIRECTION_RX = 0
except:
    pass

# vxlapi.h: 1717
try:
    XL_MOST_DIRECTION_TX = 1
except:
    pass

# vxlapi.h: 1719
try:
    XL_MOST_NO_QUEUE_OVERFLOW = 0x0000
except:
    pass

# vxlapi.h: 1720
try:
    XL_MOST_QUEUE_OVERFLOW = 0x8000
except:
    pass

# vxlapi.h: 1721
try:
    XL_MOST_COMMAND_FAILED = 0x4000
except:
    pass

# vxlapi.h: 1722
try:
    XL_MOST_INTERNAL_OVERFLOW = 0x2000
except:
    pass

# vxlapi.h: 1723
try:
    XL_MOST_MEASUREMENT_NOT_ACTIVE = 0x1000
except:
    pass

# vxlapi.h: 1724
try:
    XL_MOST_QUEUE_OVERFLOW_ASYNC = 0x0800
except:
    pass

# vxlapi.h: 1725
try:
    XL_MOST_QUEUE_OVERFLOW_CTRL = 0x0400
except:
    pass

# vxlapi.h: 1726
try:
    XL_MOST_NOT_SUPPORTED = 0x0200
except:
    pass

# vxlapi.h: 1727
try:
    XL_MOST_QUEUE_OVERFLOW_DRV = 0x0100
except:
    pass

# vxlapi.h: 1729
try:
    XL_MOST_NA_CHANGED = 0x0001
except:
    pass

# vxlapi.h: 1730
try:
    XL_MOST_GA_CHANGED = 0x0002
except:
    pass

# vxlapi.h: 1731
try:
    XL_MOST_APA_CHANGED = 0x0004
except:
    pass

# vxlapi.h: 1732
try:
    XL_MOST_NPR_CHANGED = 0x0008
except:
    pass

# vxlapi.h: 1733
try:
    XL_MOST_MPR_CHANGED = 0x0010
except:
    pass

# vxlapi.h: 1734
try:
    XL_MOST_NDR_CHANGED = 0x0020
except:
    pass

# vxlapi.h: 1735
try:
    XL_MOST_MDR_CHANGED = 0x0040
except:
    pass

# vxlapi.h: 1736
try:
    XL_MOST_SBC_CHANGED = 0x0080
except:
    pass

# vxlapi.h: 1737
try:
    XL_MOST_XTIM_CHANGED = 0x0100
except:
    pass

# vxlapi.h: 1738
try:
    XL_MOST_XRTY_CHANGED = 0x0200
except:
    pass

# vxlapi.h: 1741
try:
    XL_MOST_bGA = 0x89
except:
    pass

# vxlapi.h: 1742
try:
    XL_MOST_bNAH = 0x8A
except:
    pass

# vxlapi.h: 1743
try:
    XL_MOST_bNAL = 0x8B
except:
    pass

# vxlapi.h: 1744
try:
    XL_MOST_bSDC2 = 0x8C
except:
    pass

# vxlapi.h: 1745
try:
    XL_MOST_bSDC3 = 0x8D
except:
    pass

# vxlapi.h: 1746
try:
    XL_MOST_bCM2 = 0x8E
except:
    pass

# vxlapi.h: 1747
try:
    XL_MOST_bNDR = 0x8F
except:
    pass

# vxlapi.h: 1748
try:
    XL_MOST_bMPR = 0x90
except:
    pass

# vxlapi.h: 1749
try:
    XL_MOST_bMDR = 0x91
except:
    pass

# vxlapi.h: 1750
try:
    XL_MOST_bCM4 = 0x93
except:
    pass

# vxlapi.h: 1751
try:
    XL_MOST_bSBC = 0x96
except:
    pass

# vxlapi.h: 1752
try:
    XL_MOST_bXSR2 = 0x97
except:
    pass

# vxlapi.h: 1754
try:
    XL_MOST_bRTYP = 0xA0
except:
    pass

# vxlapi.h: 1755
try:
    XL_MOST_bRSAH = 0xA1
except:
    pass

# vxlapi.h: 1756
try:
    XL_MOST_bRSAL = 0xA2
except:
    pass

# vxlapi.h: 1757
try:
    XL_MOST_bRCD0 = 0xA3
except:
    pass

# vxlapi.h: 1759
try:
    XL_MOST_bXTIM = 0xBE
except:
    pass

# vxlapi.h: 1760
try:
    XL_MOST_bXRTY = 0xBF
except:
    pass

# vxlapi.h: 1762
try:
    XL_MOST_bXPRI = 0xC0
except:
    pass

# vxlapi.h: 1763
try:
    XL_MOST_bXTYP = 0xC1
except:
    pass

# vxlapi.h: 1764
try:
    XL_MOST_bXTAH = 0xC2
except:
    pass

# vxlapi.h: 1765
try:
    XL_MOST_bXTAL = 0xC3
except:
    pass

# vxlapi.h: 1766
try:
    XL_MOST_bXCD0 = 0xC4
except:
    pass

# vxlapi.h: 1768
try:
    XL_MOST_bXTS = 0xD5
except:
    pass

# vxlapi.h: 1770
try:
    XL_MOST_bPCTC = 0xE2
except:
    pass

# vxlapi.h: 1771
try:
    XL_MOST_bPCTS = 0xE3
except:
    pass

# vxlapi.h: 1774
try:
    XL_MOST_SPY_RX_STATUS_NO_LIGHT = 0x01
except:
    pass

# vxlapi.h: 1775
try:
    XL_MOST_SPY_RX_STATUS_NO_LOCK = 0x02
except:
    pass

# vxlapi.h: 1776
try:
    XL_MOST_SPY_RX_STATUS_BIPHASE_ERROR = 0x04
except:
    pass

# vxlapi.h: 1777
try:
    XL_MOST_SPY_RX_STATUS_MESSAGE_LENGTH_ERROR = 0x08
except:
    pass

# vxlapi.h: 1778
try:
    XL_MOST_SPY_RX_STATUS_PARITY_ERROR = 0x10
except:
    pass

# vxlapi.h: 1779
try:
    XL_MOST_SPY_RX_STATUS_FRAME_LENGTH_ERROR = 0x20
except:
    pass

# vxlapi.h: 1780
try:
    XL_MOST_SPY_RX_STATUS_PREAMBLE_TYPE_ERROR = 0x40
except:
    pass

# vxlapi.h: 1781
try:
    XL_MOST_SPY_RX_STATUS_CRC_ERROR = 0x80
except:
    pass

# vxlapi.h: 1784
try:
    XL_MOST_ASYNC_NO_ERROR = 0x00
except:
    pass

# vxlapi.h: 1785
try:
    XL_MOST_ASYNC_SBC_ERROR = 0x0C
except:
    pass

# vxlapi.h: 1786
try:
    XL_MOST_ASYNC_NEXT_STARTS_TO_EARLY = 0x0D
except:
    pass

# vxlapi.h: 1787
try:
    XL_MOST_ASYNC_TO_LONG = 0x0E
except:
    pass

# vxlapi.h: 1789
try:
    XL_MOST_ASYNC_UNLOCK = 0x0F
except:
    pass

# vxlapi.h: 1792
try:
    SYNC_PULSE_EXTERNAL = 0x00
except:
    pass

# vxlapi.h: 1793
try:
    SYNC_PULSE_OUR = 0x01
except:
    pass

# vxlapi.h: 1796
try:
    XL_MOST_CTRL_TYPE_NORMAL = 0x00
except:
    pass

# vxlapi.h: 1797
try:
    XL_MOST_CTRL_TYPE_REMOTE_READ = 0x01
except:
    pass

# vxlapi.h: 1798
try:
    XL_MOST_CTRL_TYPE_REMOTE_WRITE = 0x02
except:
    pass

# vxlapi.h: 1799
try:
    XL_MOST_CTRL_TYPE_RESOURCE_ALLOCATE = 0x03
except:
    pass

# vxlapi.h: 1800
try:
    XL_MOST_CTRL_TYPE_RESOURCE_DEALLOCATE = 0x04
except:
    pass

# vxlapi.h: 1801
try:
    XL_MOST_CTRL_TYPE_GET_SOURCE = 0x05
except:
    pass

# vxlapi.h: 1804
try:
    XL_MOST_BUSLOAD_COUNTER_TYPE_NONE = 0x00
except:
    pass

# vxlapi.h: 1805
try:
    XL_MOST_BUSLOAD_COUNTER_TYPE_1_BYTE = 0x01
except:
    pass

# vxlapi.h: 1806
try:
    XL_MOST_BUSLOAD_COUNTER_TYPE_2_BYTE = 0x02
except:
    pass

# vxlapi.h: 1807
try:
    XL_MOST_BUSLOAD_COUNTER_TYPE_3_BYTE = 0x03
except:
    pass

# vxlapi.h: 1808
try:
    XL_MOST_BUSLOAD_COUNTER_TYPE_4_BYTE = 0x04
except:
    pass

# vxlapi.h: 1811
try:
    XL_MOST_STATESEL_LIGHTLOCK = 0x0001
except:
    pass

# vxlapi.h: 1812
try:
    XL_MOST_STATESEL_REGISTERBUNCH1 = 0x0002
except:
    pass

# vxlapi.h: 1813
try:
    XL_MOST_STATESEL_BYPASSTIMING = 0x0004
except:
    pass

# vxlapi.h: 1814
try:
    XL_MOST_STATESEL_REGISTERBUNCH2 = 0x0008
except:
    pass

# vxlapi.h: 1815
try:
    XL_MOST_STATESEL_REGISTERBUNCH3 = 0x0010
except:
    pass

# vxlapi.h: 1816
try:
    XL_MOST_STATESEL_VOLUMEMUTE = 0x0020
except:
    pass

# vxlapi.h: 1817
try:
    XL_MOST_STATESEL_EVENTSOURCE = 0x0040
except:
    pass

# vxlapi.h: 1818
try:
    XL_MOST_STATESEL_RXBUFFERMODE = 0x0080
except:
    pass

# vxlapi.h: 1819
try:
    XL_MOST_STATESEL_ALLOCTABLE = 0x0100
except:
    pass

# vxlapi.h: 1820
try:
    XL_MOST_STATESEL_SUPERVISOR_LOCKSTATUS = 0x0200
except:
    pass

# vxlapi.h: 1821
try:
    XL_MOST_STATESEL_SUPERVISOR_MESSAGE = 0x0400
except:
    pass

# vxlapi.h: 1824
try:
    XL_MOST_STREAM_RX_DATA = 0
except:
    pass

# vxlapi.h: 1825
try:
    XL_MOST_STREAM_TX_DATA = 1
except:
    pass

# vxlapi.h: 1827
try:
    XL_MOST_STREAM_ADD_FRAME_HEADER = 1
except:
    pass

# vxlapi.h: 1830
try:
    XL_MOST_STREAM_STATE_CLOSED = 0x01
except:
    pass

# vxlapi.h: 1831
try:
    XL_MOST_STREAM_STATE_OPENED = 0x02
except:
    pass

# vxlapi.h: 1832
try:
    XL_MOST_STREAM_STATE_STARTED = 0x03
except:
    pass

# vxlapi.h: 1833
try:
    XL_MOST_STREAM_STATE_STOPPED = 0x04
except:
    pass

# vxlapi.h: 1834
try:
    XL_MOST_STREAM_STATE_START_PENDING = 0x05
except:
    pass

# vxlapi.h: 1835
try:
    XL_MOST_STREAM_STATE_STOP_PENDING = 0x06
except:
    pass

# vxlapi.h: 1836
try:
    XL_MOST_STREAM_STATE_UNKNOWN = 0xFF
except:
    pass

# vxlapi.h: 1839
try:
    XL_MOST_STREAM_ACTIVATE = 0
except:
    pass

# vxlapi.h: 1840
try:
    XL_MOST_STREAM_DEACTIVATE = 1
except:
    pass

# vxlapi.h: 1842
try:
    XL_MOST_STREAM_INVALID_HANDLE = 0
except:
    pass

# vxlapi.h: 1845
try:
    XL_MOST_STREAM_LATENCY_VERY_LOW = 0
except:
    pass

# vxlapi.h: 1846
try:
    XL_MOST_STREAM_LATENCY_LOW = 1
except:
    pass

# vxlapi.h: 1847
try:
    XL_MOST_STREAM_LATENCY_MEDIUM = 2
except:
    pass

# vxlapi.h: 1848
try:
    XL_MOST_STREAM_LATENCY_HIGH = 3
except:
    pass

# vxlapi.h: 1849
try:
    XL_MOST_STREAM_LATENCY_VERY_HIGH = 4
except:
    pass

# vxlapi.h: 1852
try:
    XL_MOST_STREAM_ERR_NO_ERROR = 0x00
except:
    pass

# vxlapi.h: 1853
try:
    XL_MOST_STREAM_ERR_INVALID_HANDLE = 0x01
except:
    pass

# vxlapi.h: 1854
try:
    XL_MOST_STREAM_ERR_NO_MORE_BUFFERS_AVAILABLE = 0x02
except:
    pass

# vxlapi.h: 1855
try:
    XL_MOST_STREAM_ERR_ANY_BUFFER_LOCKED = 0x03
except:
    pass

# vxlapi.h: 1856
try:
    XL_MOST_STREAM_ERR_WRITE_RE_FAILED = 0x04
except:
    pass

# vxlapi.h: 1857
try:
    XL_MOST_STREAM_ERR_STREAM_ALREADY_STARTED = 0x05
except:
    pass

# vxlapi.h: 1858
try:
    XL_MOST_STREAM_ERR_TX_BUFFER_UNDERRUN = 0x06
except:
    pass

# vxlapi.h: 1859
try:
    XL_MOST_STREAM_ERR_RX_BUFFER_OVERFLOW = 0x07
except:
    pass

# vxlapi.h: 1860
try:
    XL_MOST_STREAM_ERR_INSUFFICIENT_RESOURCES = 0x08
except:
    pass

# vxlapi.h: 1864
try:
    RX_FIFO_MOST_QUEUE_SIZE_MAX = 1048576
except:
    pass

# vxlapi.h: 1865
try:
    RX_FIFO_MOST_QUEUE_SIZE_MIN = 8192
except:
    pass

# vxlapi.h: 2070
try:
    XL_MOST_EVENT_HEADER_SIZE = 32
except:
    pass

# vxlapi.h: 2071
try:
    XL_MOST_EVENT_MAX_DATA_SIZE = 1024
except:
    pass

# vxlapi.h: 2072
try:
    XL_MOST_EVENT_MAX_SIZE = (XL_MOST_EVENT_HEADER_SIZE + XL_MOST_EVENT_MAX_DATA_SIZE)
except:
    pass

# vxlapi.h: 2214
try:
    XL_FR_MAX_DATA_LENGTH = 254
except:
    pass

# vxlapi.h: 2302
try:
    XL_FR_CHANNEL_CFG_STATUS_INIT_APP_PRESENT = 0x01
except:
    pass

# vxlapi.h: 2303
try:
    XL_FR_CHANNEL_CFG_STATUS_CHANNEL_ACTIVATED = 0x02
except:
    pass

# vxlapi.h: 2304
try:
    XL_FR_CHANNEL_CFG_STATUS_VALID_CLUSTER_CFG = 0x04
except:
    pass

# vxlapi.h: 2305
try:
    XL_FR_CHANNEL_CFG_STATUS_VALID_CFG_MODE = 0x08
except:
    pass

# vxlapi.h: 2308
try:
    XL_FR_CHANNEL_CFG_MODE_SYNCHRONOUS = 1
except:
    pass

# vxlapi.h: 2309
try:
    XL_FR_CHANNEL_CFG_MODE_COMBINED = 2
except:
    pass

# vxlapi.h: 2310
try:
    XL_FR_CHANNEL_CFG_MODE_ASYNCHRONOUS = 3
except:
    pass

# vxlapi.h: 2313
try:
    XL_FR_MODE_NORMAL = 0x00
except:
    pass

# vxlapi.h: 2314
try:
    XL_FR_MODE_COLD_NORMAL = 0x04
except:
    pass

# vxlapi.h: 2315
try:
    XL_FR_MODE_BUS_HALT = 0x06
except:
    pass

# vxlapi.h: 2318
try:
    XL_FR_MODE_NONE = 0x00
except:
    pass

# vxlapi.h: 2319
try:
    XL_FR_MODE_WAKEUP = 0x01
except:
    pass

# vxlapi.h: 2320
try:
    XL_FR_MODE_COLDSTART_LEADING = 0x02
except:
    pass

# vxlapi.h: 2321
try:
    XL_FR_MODE_COLDSTART_FOLLOWING = 0x03
except:
    pass

# vxlapi.h: 2322
try:
    XL_FR_MODE_WAKEUP_AND_COLDSTART_LEADING = 0x04
except:
    pass

# vxlapi.h: 2323
try:
    XL_FR_MODE_WAKEUP_AND_COLDSTART_FOLLOWING = 0x05
except:
    pass

# vxlapi.h: 2335
try:
    XL_FR_SYMBOL_MTS = 0x01
except:
    pass

# vxlapi.h: 2336
try:
    XL_FR_SYMBOL_CAS = 0x02
except:
    pass

# vxlapi.h: 2340
try:
    XL_FR_TRANSCEIVER_MODE_SLEEP = 0x01
except:
    pass

# vxlapi.h: 2341
try:
    XL_FR_TRANSCEIVER_MODE_NORMAL = 0x02
except:
    pass

# vxlapi.h: 2342
try:
    XL_FR_TRANSCEIVER_MODE_RECEIVE_ONLY = 0x03
except:
    pass

# vxlapi.h: 2343
try:
    XL_FR_TRANSCEIVER_MODE_STANDBY = 0x04
except:
    pass

# vxlapi.h: 2346
try:
    XL_FR_SYNC_PULSE_EXTERNAL = XL_SYNC_PULSE_EXTERNAL
except:
    pass

# vxlapi.h: 2347
try:
    XL_FR_SYNC_PULSE_OUR = XL_SYNC_PULSE_OUR
except:
    pass

# vxlapi.h: 2348
try:
    XL_FR_SYNC_PULSE_OUR_SHARED = XL_SYNC_PULSE_OUR_SHARED
except:
    pass

# vxlapi.h: 2351
try:
    XL_FR_SPY_MODE_ASYNCHRONOUS = 0x01
except:
    pass

# vxlapi.h: 2359
try:
    XL_FR_FILTER_PASS = 0x00000000
except:
    pass

# vxlapi.h: 2360
try:
    XL_FR_FILTER_BLOCK = 0x00000001
except:
    pass

# vxlapi.h: 2363
try:
    XL_FR_FILTER_TYPE_DATA = 0x00000001
except:
    pass

# vxlapi.h: 2364
try:
    XL_FR_FILTER_TYPE_NF = 0x00000002
except:
    pass

# vxlapi.h: 2365
try:
    XL_FR_FILTER_TYPE_FILLUP_NF = 0x00000004
except:
    pass

# vxlapi.h: 2368
try:
    XL_FR_FILTER_CHANNEL_A = 0x00000001
except:
    pass

# vxlapi.h: 2369
try:
    XL_FR_FILTER_CHANNEL_B = 0x00000002
except:
    pass

# vxlapi.h: 2383
try:
    XL_FR_CHANNEL_A = 0x01
except:
    pass

# vxlapi.h: 2384
try:
    XL_FR_CHANNEL_B = 0x02
except:
    pass

# vxlapi.h: 2385
try:
    XL_FR_CHANNEL_AB = (XL_FR_CHANNEL_A | XL_FR_CHANNEL_B)
except:
    pass

# vxlapi.h: 2386
try:
    XL_FR_CC_COLD_A = 0x04
except:
    pass

# vxlapi.h: 2387
try:
    XL_FR_CC_COLD_B = 0x08
except:
    pass

# vxlapi.h: 2388
try:
    XL_FR_CC_COLD_AB = (XL_FR_CC_COLD_A | XL_FR_CC_COLD_B)
except:
    pass

# vxlapi.h: 2389
try:
    XL_FR_SPY_CHANNEL_A = 0x10
except:
    pass

# vxlapi.h: 2390
try:
    XL_FR_SPY_CHANNEL_B = 0x20
except:
    pass

# vxlapi.h: 2392
try:
    XL_FR_QUEUE_OVERFLOW = 0x0100
except:
    pass

# vxlapi.h: 2399
try:
    XL_FR_FRAMEFLAG_STARTUP = 0x0001
except:
    pass

# vxlapi.h: 2400
try:
    XL_FR_FRAMEFLAG_SYNC = 0x0002
except:
    pass

# vxlapi.h: 2401
try:
    XL_FR_FRAMEFLAG_NULLFRAME = 0x0004
except:
    pass

# vxlapi.h: 2402
try:
    XL_FR_FRAMEFLAG_PAYLOAD_PREAMBLE = 0x0008
except:
    pass

# vxlapi.h: 2403
try:
    XL_FR_FRAMEFLAG_FR_RESERVED = 0x0010
except:
    pass

# vxlapi.h: 2405
try:
    XL_FR_FRAMEFLAG_REQ_TXACK = 0x0020
except:
    pass

# vxlapi.h: 2406
try:
    XL_FR_FRAMEFLAG_TXACK_SS = XL_FR_FRAMEFLAG_REQ_TXACK
except:
    pass

# vxlapi.h: 2407
try:
    XL_FR_FRAMEFLAG_RX_UNEXPECTED = XL_FR_FRAMEFLAG_REQ_TXACK
except:
    pass

# vxlapi.h: 2409
try:
    XL_FR_FRAMEFLAG_NEW_DATA_TX = 0x0040
except:
    pass

# vxlapi.h: 2410
try:
    XL_FR_FRAMEFLAG_DATA_UPDATE_LOST = 0x0080
except:
    pass

# vxlapi.h: 2412
try:
    XL_FR_FRAMEFLAG_SYNTAX_ERROR = 0x0200
except:
    pass

# vxlapi.h: 2413
try:
    XL_FR_FRAMEFLAG_CONTENT_ERROR = 0x0400
except:
    pass

# vxlapi.h: 2414
try:
    XL_FR_FRAMEFLAG_SLOT_BOUNDARY_VIOLATION = 0x0800
except:
    pass

# vxlapi.h: 2415
try:
    XL_FR_FRAMEFLAG_TX_CONFLICT = 0x1000
except:
    pass

# vxlapi.h: 2416
try:
    XL_FR_FRAMEFLAG_EMPTY_SLOT = 0x2000
except:
    pass

# vxlapi.h: 2417
try:
    XL_FR_FRAMEFLAG_FRAME_TRANSMITTED = 0x8000
except:
    pass

# vxlapi.h: 2421
try:
    XL_FR_SPY_FRAMEFLAG_FRAMING_ERROR = 0x01
except:
    pass

# vxlapi.h: 2422
try:
    XL_FR_SPY_FRAMEFLAG_HEADER_CRC_ERROR = 0x02
except:
    pass

# vxlapi.h: 2423
try:
    XL_FR_SPY_FRAMEFLAG_FRAME_CRC_ERROR = 0x04
except:
    pass

# vxlapi.h: 2424
try:
    XL_FR_SPY_FRAMEFLAG_BUS_ERROR = 0x08
except:
    pass

# vxlapi.h: 2427
try:
    XL_FR_SPY_FRAMEFLAG_FRAME_CRC_NEW_LAYOUT = 0x80000000
except:
    pass

# vxlapi.h: 2430
try:
    XL_FR_SPY_FRAMEFLAG_STATIC_FRAME = 0x01
except:
    pass

# vxlapi.h: 2433
try:
    XL_FR_TX_MODE_CYCLIC = 0x01
except:
    pass

# vxlapi.h: 2434
try:
    XL_FR_TX_MODE_SINGLE_SHOT = 0x02
except:
    pass

# vxlapi.h: 2435
try:
    XL_FR_TX_MODE_NONE = 0xff
except:
    pass

# vxlapi.h: 2438
try:
    XL_FR_PAYLOAD_INCREMENT_8BIT = 8
except:
    pass

# vxlapi.h: 2439
try:
    XL_FR_PAYLOAD_INCREMENT_16BIT = 16
except:
    pass

# vxlapi.h: 2440
try:
    XL_FR_PAYLOAD_INCREMENT_32BIT = 32
except:
    pass

# vxlapi.h: 2441
try:
    XL_FR_PAYLOAD_INCREMENT_NONE = 0
except:
    pass

# vxlapi.h: 2444
try:
    XL_FR_STATUS_DEFAULT_CONFIG = 0x00
except:
    pass

# vxlapi.h: 2445
try:
    XL_FR_STATUS_READY = 0x01
except:
    pass

# vxlapi.h: 2446
try:
    XL_FR_STATUS_NORMAL_ACTIVE = 0x02
except:
    pass

# vxlapi.h: 2447
try:
    XL_FR_STATUS_NORMAL_PASSIVE = 0x03
except:
    pass

# vxlapi.h: 2448
try:
    XL_FR_STATUS_HALT = 0x04
except:
    pass

# vxlapi.h: 2449
try:
    XL_FR_STATUS_MONITOR_MODE = 0x05
except:
    pass

# vxlapi.h: 2450
try:
    XL_FR_STATUS_CONFIG = 0x0f
except:
    pass

# vxlapi.h: 2452
try:
    XL_FR_STATUS_WAKEUP_STANDBY = 0x10
except:
    pass

# vxlapi.h: 2453
try:
    XL_FR_STATUS_WAKEUP_LISTEN = 0x11
except:
    pass

# vxlapi.h: 2454
try:
    XL_FR_STATUS_WAKEUP_SEND = 0x12
except:
    pass

# vxlapi.h: 2455
try:
    XL_FR_STATUS_WAKEUP_DETECT = 0x13
except:
    pass

# vxlapi.h: 2457
try:
    XL_FR_STATUS_STARTUP_PREPARE = 0x20
except:
    pass

# vxlapi.h: 2458
try:
    XL_FR_STATUS_COLDSTART_LISTEN = 0x21
except:
    pass

# vxlapi.h: 2459
try:
    XL_FR_STATUS_COLDSTART_COLLISION_RESOLUTION = 0x22
except:
    pass

# vxlapi.h: 2460
try:
    XL_FR_STATUS_COLDSTART_CONSISTENCY_CHECK = 0x23
except:
    pass

# vxlapi.h: 2461
try:
    XL_FR_STATUS_COLDSTART_GAP = 0x24
except:
    pass

# vxlapi.h: 2462
try:
    XL_FR_STATUS_COLDSTART_JOIN = 0x25
except:
    pass

# vxlapi.h: 2463
try:
    XL_FR_STATUS_INTEGRATION_COLDSTART_CHECK = 0x26
except:
    pass

# vxlapi.h: 2464
try:
    XL_FR_STATUS_INTEGRATION_LISTEN = 0x27
except:
    pass

# vxlapi.h: 2465
try:
    XL_FR_STATUS_INTEGRATION_CONSISTENCY_CHECK = 0x28
except:
    pass

# vxlapi.h: 2466
try:
    XL_FR_STATUS_INITIALIZE_SCHEDULE = 0x29
except:
    pass

# vxlapi.h: 2467
try:
    XL_FR_STATUS_ABORT_STARTUP = 0x2a
except:
    pass

# vxlapi.h: 2468
try:
    XL_FR_STATUS_STARTUP_SUCCESS = 0x2b
except:
    pass

# vxlapi.h: 2471
try:
    XL_FR_ERROR_POC_ACTIVE = 0x00
except:
    pass

# vxlapi.h: 2472
try:
    XL_FR_ERROR_POC_PASSIVE = 0x01
except:
    pass

# vxlapi.h: 2473
try:
    XL_FR_ERROR_POC_COMM_HALT = 0x02
except:
    pass

# vxlapi.h: 2476
try:
    XL_FR_ERROR_NIT_SENA = 0x100
except:
    pass

# vxlapi.h: 2477
try:
    XL_FR_ERROR_NIT_SBNA = 0x200
except:
    pass

# vxlapi.h: 2478
try:
    XL_FR_ERROR_NIT_SENB = 0x400
except:
    pass

# vxlapi.h: 2479
try:
    XL_FR_ERROR_NIT_SBNB = 0x800
except:
    pass

# vxlapi.h: 2482
try:
    XL_FR_ERROR_MISSING_OFFSET_CORRECTION = 0x00000001
except:
    pass

# vxlapi.h: 2483
try:
    XL_FR_ERROR_MAX_OFFSET_CORRECTION_REACHED = 0x00000002
except:
    pass

# vxlapi.h: 2484
try:
    XL_FR_ERROR_MISSING_RATE_CORRECTION = 0x00000004
except:
    pass

# vxlapi.h: 2485
try:
    XL_FR_ERROR_MAX_RATE_CORRECTION_REACHED = 0x00000008
except:
    pass

# vxlapi.h: 2488
try:
    XL_FR_ERROR_CC_PERR = 0x00000040
except:
    pass

# vxlapi.h: 2489
try:
    XL_FR_ERROR_CC_IIBA = 0x00000200
except:
    pass

# vxlapi.h: 2490
try:
    XL_FR_ERROR_CC_IOBA = 0x00000400
except:
    pass

# vxlapi.h: 2491
try:
    XL_FR_ERROR_CC_MHF = 0x00000800
except:
    pass

# vxlapi.h: 2492
try:
    XL_FR_ERROR_CC_EDA = 0x00010000
except:
    pass

# vxlapi.h: 2493
try:
    XL_FR_ERROR_CC_LTVA = 0x00020000
except:
    pass

# vxlapi.h: 2494
try:
    XL_FR_ERROR_CC_TABA = 0x00040000
except:
    pass

# vxlapi.h: 2495
try:
    XL_FR_ERROR_CC_EDB = 0x01000000
except:
    pass

# vxlapi.h: 2496
try:
    XL_FR_ERROR_CC_LTVB = 0x02000000
except:
    pass

# vxlapi.h: 2497
try:
    XL_FR_ERROR_CC_TABB = 0x04000000
except:
    pass

# vxlapi.h: 2500
try:
    XL_FR_WAKEUP_UNDEFINED = 0x00
except:
    pass

# vxlapi.h: 2501
try:
    XL_FR_WAKEUP_RECEIVED_HEADER = 0x01
except:
    pass

# vxlapi.h: 2502
try:
    XL_FR_WAKEUP_RECEIVED_WUP = 0x02
except:
    pass

# vxlapi.h: 2503
try:
    XL_FR_WAKEUP_COLLISION_HEADER = 0x03
except:
    pass

# vxlapi.h: 2504
try:
    XL_FR_WAKEUP_COLLISION_WUP = 0x04
except:
    pass

# vxlapi.h: 2505
try:
    XL_FR_WAKEUP_COLLISION_UNKNOWN = 0x05
except:
    pass

# vxlapi.h: 2506
try:
    XL_FR_WAKEUP_TRANSMITTED = 0x06
except:
    pass

# vxlapi.h: 2507
try:
    XL_FR_WAKEUP_EXTERNAL_WAKEUP = 0x07
except:
    pass

# vxlapi.h: 2508
try:
    XL_FR_WAKEUP_WUP_RECEIVED_WITHOUT_WUS_TX = 0x10
except:
    pass

# vxlapi.h: 2509
try:
    XL_FR_WAKEUP_RESERVED = 0xFF
except:
    pass

# vxlapi.h: 2512
try:
    XL_FR_SYMBOL_STATUS_SESA = 0x01
except:
    pass

# vxlapi.h: 2513
try:
    XL_FR_SYMBOL_STATUS_SBSA = 0x02
except:
    pass

# vxlapi.h: 2514
try:
    XL_FR_SYMBOL_STATUS_TCSA = 0x04
except:
    pass

# vxlapi.h: 2515
try:
    XL_FR_SYMBOL_STATUS_SESB = 0x08
except:
    pass

# vxlapi.h: 2516
try:
    XL_FR_SYMBOL_STATUS_SBSB = 0x10
except:
    pass

# vxlapi.h: 2517
try:
    XL_FR_SYMBOL_STATUS_TCSB = 0x20
except:
    pass

# vxlapi.h: 2518
try:
    XL_FR_SYMBOL_STATUS_MTSA = 0x40
except:
    pass

# vxlapi.h: 2519
try:
    XL_FR_SYMBOL_STATUS_MTSB = 0x80
except:
    pass

# vxlapi.h: 2524
try:
    XL_FR_RX_EVENT_HEADER_SIZE = 32
except:
    pass

# vxlapi.h: 2525
try:
    XL_FR_MAX_EVENT_SIZE = 512
except:
    pass

# vxlapi.h: 2706
try:
    XL_DAIO_PORT_TYPE_MASK_DIGITAL = 0x01
except:
    pass

# vxlapi.h: 2707
try:
    XL_DAIO_PORT_TYPE_MASK_ANALOG = 0x02
except:
    pass

# vxlapi.h: 2710
try:
    XL_DAIO_TRIGGER_TYPE_CYCLIC = 0x01
except:
    pass

# vxlapi.h: 2711
try:
    XL_DAIO_TRIGGER_TYPE_PORT = 0x02
except:
    pass

# vxlapi.h: 2731
try:
    XL_DAIO_TRIGGER_TYPE_RISING = 0x01
except:
    pass

# vxlapi.h: 2732
try:
    XL_DAIO_TRIGGER_TYPE_FALLING = 0x02
except:
    pass

# vxlapi.h: 2733
try:
    XL_DAIO_TRIGGER_TYPE_BOTH = 0x03
except:
    pass

# vxlapi.h: 2745
try:
    XL_DAIO_PORT_DIGITAL_IN = 0x00
except:
    pass

# vxlapi.h: 2746
try:
    XL_DAIO_PORT_DIGITAL_PUSHPULL = 0x01
except:
    pass

# vxlapi.h: 2747
try:
    XL_DAIO_PORT_DIGITAL_OPENDRAIN = 0x02
except:
    pass

# vxlapi.h: 2748
try:
    XL_DAIO_PORT_DIGITAL_SWITCH = 0x05
except:
    pass

# vxlapi.h: 2749
try:
    XL_DAIO_PORT_DIGITAL_IN_OUT = 0x06
except:
    pass

# vxlapi.h: 2752
try:
    XL_DAIO_PORT_ANALOG_IN = 0x00
except:
    pass

# vxlapi.h: 2753
try:
    XL_DAIO_PORT_ANALOG_OUT = 0x01
except:
    pass

# vxlapi.h: 2754
try:
    XL_DAIO_PORT_ANALOG_DIFF = 0x02
except:
    pass

# vxlapi.h: 2755
try:
    XL_DAIO_PORT_ANALOG_OFF = 0x03
except:
    pass

# vxlapi.h: 2759
try:
    XL_DAIO_DO_LEVEL_0V = 0
except:
    pass

# vxlapi.h: 2760
try:
    XL_DAIO_DO_LEVEL_5V = 5
except:
    pass

# vxlapi.h: 2761
try:
    XL_DAIO_DO_LEVEL_12V = 12
except:
    pass

# vxlapi.h: 2772
try:
    XL_DAIO_PORT_MASK_DIGITAL_D0 = 0x01
except:
    pass

# vxlapi.h: 2773
try:
    XL_DAIO_PORT_MASK_DIGITAL_D1 = 0x02
except:
    pass

# vxlapi.h: 2774
try:
    XL_DAIO_PORT_MASK_DIGITAL_D2 = 0x04
except:
    pass

# vxlapi.h: 2775
try:
    XL_DAIO_PORT_MASK_DIGITAL_D3 = 0x08
except:
    pass

# vxlapi.h: 2776
try:
    XL_DAIO_PORT_MASK_DIGITAL_D4 = 0x10
except:
    pass

# vxlapi.h: 2777
try:
    XL_DAIO_PORT_MASK_DIGITAL_D5 = 0x20
except:
    pass

# vxlapi.h: 2778
try:
    XL_DAIO_PORT_MASK_DIGITAL_D6 = 0x40
except:
    pass

# vxlapi.h: 2779
try:
    XL_DAIO_PORT_MASK_DIGITAL_D7 = 0x80
except:
    pass

# vxlapi.h: 2790
try:
    XL_DAIO_PORT_MASK_ANALOG_A0 = 0x01
except:
    pass

# vxlapi.h: 2791
try:
    XL_DAIO_PORT_MASK_ANALOG_A1 = 0x02
except:
    pass

# vxlapi.h: 2792
try:
    XL_DAIO_PORT_MASK_ANALOG_A2 = 0x04
except:
    pass

# vxlapi.h: 2793
try:
    XL_DAIO_PORT_MASK_ANALOG_A3 = 0x08
except:
    pass

# vxlapi.h: 2797
try:
    XL_DAIO_EVT_ID_DIGITAL = XL_DAIO_PORT_TYPE_MASK_DIGITAL
except:
    pass

# vxlapi.h: 2798
try:
    XL_DAIO_EVT_ID_ANALOG = XL_DAIO_PORT_TYPE_MASK_ANALOG
except:
    pass

# vxlapi.h: 2807
try:
    XL_KLINE_EVT_RX_DATA = 1
except:
    pass

# vxlapi.h: 2808
try:
    XL_KLINE_EVT_TX_DATA = 2
except:
    pass

# vxlapi.h: 2810
try:
    XL_KLINE_EVT_TESTER_5BD = 3
except:
    pass

# vxlapi.h: 2811
try:
    XL_KLINE_EVT_ECU_5BD = 5
except:
    pass

# vxlapi.h: 2813
try:
    XL_KLINE_EVT_TESTER_FI_WU_PATTERN = 7
except:
    pass

# vxlapi.h: 2814
try:
    XL_KLINE_EVT_ECU_FI_WU_PATTERN = 8
except:
    pass

# vxlapi.h: 2815
try:
    XL_KLINE_EVT_ERROR = 9
except:
    pass

# vxlapi.h: 2817
try:
    XL_KLINE_EVT_CONFIRMATION = 10
except:
    pass

# vxlapi.h: 2898
try:
    XL_KLINE_UART_PARITY_NONE = 0
except:
    pass

# vxlapi.h: 2899
try:
    XL_KLINE_UART_PARITY_EVEN = 1
except:
    pass

# vxlapi.h: 2900
try:
    XL_KLINE_UART_PARITY_ODD = 2
except:
    pass

# vxlapi.h: 2901
try:
    XL_KLINE_UART_PARITY_MARK = 3
except:
    pass

# vxlapi.h: 2902
try:
    XL_KLINE_UART_PARITY_SPACE = 4
except:
    pass

# vxlapi.h: 2907
try:
    XL_KLINE_TRXMODE_NORMAL = 0
except:
    pass

# vxlapi.h: 2908
try:
    XL_KLINE_TRXMODE_HIGHSPEED = 1
except:
    pass

# vxlapi.h: 2913
try:
    XL_KLINE_TESTERRESISTOR_OFF = 0
except:
    pass

# vxlapi.h: 2914
try:
    XL_KLINE_TESTERRESISTOR_ON = 1
except:
    pass

# vxlapi.h: 2919
try:
    XL_KLINE_UNCONFIGURE_ECU = 0
except:
    pass

# vxlapi.h: 2920
try:
    XL_KLINE_CONFIGURE_ECU = 1
except:
    pass

# vxlapi.h: 2925
try:
    XL_KLINE_EVT_TAG_5BD_ADDR = 1
except:
    pass

# vxlapi.h: 2926
try:
    XL_KLINE_EVT_TAG_5BD_BAUDRATE = 2
except:
    pass

# vxlapi.h: 2927
try:
    XL_KLINE_EVT_TAG_5BD_KB1 = 3
except:
    pass

# vxlapi.h: 2928
try:
    XL_KLINE_EVT_TAG_5BD_KB2 = 4
except:
    pass

# vxlapi.h: 2929
try:
    XL_KLINE_EVT_TAG_5BD_KB2NOT = 5
except:
    pass

# vxlapi.h: 2930
try:
    XL_KLINE_EVT_TAG_5BD_ADDRNOT = 6
except:
    pass

# vxlapi.h: 2933
try:
    XL_KLINE_BYTE_FRAMING_ERROR_MASK = 0x1
except:
    pass

# vxlapi.h: 2934
try:
    XL_KLINE_BYTE_PARITY_ERROR_MASK = 0x2
except:
    pass

# vxlapi.h: 2937
try:
    XL_KLINE_EVT_TAG_SET_COMM_PARAM_TESTER = 1
except:
    pass

# vxlapi.h: 2938
try:
    XL_KLINE_EVT_TAG_COMM_PARAM_ECU = 2
except:
    pass

# vxlapi.h: 2939
try:
    XL_KLINE_EVT_TAG_SWITCH_HIGHSPEED = 3
except:
    pass

# vxlapi.h: 2942
try:
    XL_KLINE_FLAG_TAKE_KB2NOT = 0x80000000
except:
    pass

# vxlapi.h: 2945
try:
    XL_KLINE_FLAG_TAKE_ADDRNOT = 0x80000000
except:
    pass

# vxlapi.h: 2949
try:
    XL_KLINE_ERROR_TYPE_RXTX_ERROR = 1
except:
    pass

# vxlapi.h: 2950
try:
    XL_KLINE_ERROR_TYPE_5BD_TESTER = 2
except:
    pass

# vxlapi.h: 2951
try:
    XL_KLINE_ERROR_TYPE_5BD_ECU = 3
except:
    pass

# vxlapi.h: 2952
try:
    XL_KLINE_ERROR_TYPE_IBS = 4
except:
    pass

# vxlapi.h: 2953
try:
    XL_KLINE_ERROR_TYPE_FI = 5
except:
    pass

# vxlapi.h: 2956
try:
    XL_KLINE_ERR_RXTX_UA = 0x04
except:
    pass

# vxlapi.h: 2957
try:
    XL_KLINE_ERR_RXTX_MA = 0x02
except:
    pass

# vxlapi.h: 2958
try:
    XL_KLINE_ERR_RXTX_ISB = 0x01
except:
    pass

# vxlapi.h: 2961
try:
    XL_KLINE_ERR_TESTER_W1MIN = 1
except:
    pass

# vxlapi.h: 2962
try:
    XL_KLINE_ERR_TESTER_W1MAX = 2
except:
    pass

# vxlapi.h: 2963
try:
    XL_KLINE_ERR_TESTER_W2MIN = 3
except:
    pass

# vxlapi.h: 2964
try:
    XL_KLINE_ERR_TESTER_W2MAX = 4
except:
    pass

# vxlapi.h: 2965
try:
    XL_KLINE_ERR_TESTER_W3MIN = 5
except:
    pass

# vxlapi.h: 2966
try:
    XL_KLINE_ERR_TESTER_W3MAX = 6
except:
    pass

# vxlapi.h: 2967
try:
    XL_KLINE_ERR_TESTER_W4MIN = 7
except:
    pass

# vxlapi.h: 2968
try:
    XL_KLINE_ERR_TESTER_W4MAX = 8
except:
    pass

# vxlapi.h: 2971
try:
    XL_KLINE_ERR_ECU_W4MIN = 1
except:
    pass

# vxlapi.h: 2972
try:
    XL_KLINE_ERR_ECU_W4MAX = 2
except:
    pass

# vxlapi.h: 2975
try:
    XL_KLINE_ERR_IBS_P1 = 1
except:
    pass

# vxlapi.h: 2976
try:
    XL_KLINE_ERR_IBS_P4 = 2
except:
    pass

# vxlapi.h: 2988
try:
    XL_ETH_EVENT_SIZE_HEADER = 32
except:
    pass

# vxlapi.h: 2989
try:
    XL_ETH_EVENT_SIZE_MAX = 2048
except:
    pass

# vxlapi.h: 2991
try:
    XL_ETH_RX_FIFO_QUEUE_SIZE_MAX = ((64 * 1024) * 1024)
except:
    pass

# vxlapi.h: 2992
try:
    XL_ETH_RX_FIFO_QUEUE_SIZE_MIN = (64 * 1024)
except:
    pass

# vxlapi.h: 2994
try:
    XL_ETH_PAYLOAD_SIZE_MAX = 1500
except:
    pass

# vxlapi.h: 2995
try:
    XL_ETH_PAYLOAD_SIZE_MIN = 46
except:
    pass

# vxlapi.h: 2996
try:
    XL_ETH_RAW_FRAME_SIZE_MAX = 1600
except:
    pass

# vxlapi.h: 2998
try:
    XL_ETH_RAW_FRAME_SIZE_MIN = 24
except:
    pass

# vxlapi.h: 3001
try:
    XL_ETH_MACADDR_OCTETS = 6
except:
    pass

# vxlapi.h: 3002
try:
    XL_ETH_ETHERTYPE_OCTETS = 2
except:
    pass

# vxlapi.h: 3003
try:
    XL_ETH_VLANTAG_OCTETS = 4
except:
    pass

# vxlapi.h: 3009
try:
    XL_ETH_CHANNEL_CAP_IEEE100T1 = 0x0001
except:
    pass

# vxlapi.h: 3010
try:
    XL_ETH_CHANNEL_CAP_IEEE100TX = 0x0002
except:
    pass

# vxlapi.h: 3012
try:
    XL_ETH_CHANNEL_CAP_IEEE1000T = 0x0004
except:
    pass

# vxlapi.h: 3013
try:
    XL_ETH_CHANNEL_CAP_IEEE1000T1 = 0x0008
except:
    pass

# vxlapi.h: 3016
try:
    XL_NET_ETH_SWITCH_CAP_REALSWITCH = 0x00000000
except:
    pass

# vxlapi.h: 3017
try:
    XL_NET_ETH_SWITCH_CAP_DIRECTCONN = 0x00000001
except:
    pass

# vxlapi.h: 3018
try:
    XL_NET_ETH_SWITCH_CAP_TAP_LINK = 0x00000002
except:
    pass

# vxlapi.h: 3019
try:
    XL_NET_ETH_SWITCH_CAP_MULTIDROP = 0x00000004
except:
    pass

# vxlapi.h: 3024
try:
    XL_ETH_CONNECTOR_RJ45 = 0x0001
except:
    pass

# vxlapi.h: 3025
try:
    XL_ETH_CONNECTOR_DSUB = 0x0002
except:
    pass

# vxlapi.h: 3026
try:
    XL_ETH_PHY_IEEE = 0x0004
except:
    pass

# vxlapi.h: 3027
try:
    XL_ETH_PHY_BROADR = 0x0008
except:
    pass

# vxlapi.h: 3028
try:
    XL_ETH_FRAME_BYPASSED = 0x0010
except:
    pass

# vxlapi.h: 3029
try:
    XL_ETH_QUEUE_OVERFLOW = 0x0100
except:
    pass

# vxlapi.h: 3030
try:
    XL_ETH_BYPASS_QUEUE_OVERFLOW = 0x8000
except:
    pass

# vxlapi.h: 3037
try:
    XL_ETH_MODE_SPEED_AUTO_100 = 2
except:
    pass

# vxlapi.h: 3038
try:
    XL_ETH_MODE_SPEED_AUTO_1000 = 4
except:
    pass

# vxlapi.h: 3039
try:
    XL_ETH_MODE_SPEED_AUTO_100_1000 = 5
except:
    pass

# vxlapi.h: 3040
try:
    XL_ETH_MODE_SPEED_FIXED_10 = 7
except:
    pass

# vxlapi.h: 3041
try:
    XL_ETH_MODE_SPEED_FIXED_100 = 8
except:
    pass

# vxlapi.h: 3042
try:
    XL_ETH_MODE_SPEED_FIXED_1000 = 9
except:
    pass

# vxlapi.h: 3045
try:
    XL_ETH_MODE_DUPLEX_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3046
try:
    XL_ETH_MODE_DUPLEX_AUTO = 1
except:
    pass

# vxlapi.h: 3048
try:
    XL_ETH_MODE_DUPLEX_HALF = 2
except:
    pass

# vxlapi.h: 3049
try:
    XL_ETH_MODE_DUPLEX_FULL = 3
except:
    pass

# vxlapi.h: 3052
try:
    XL_ETH_MODE_CONNECTOR_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3053
try:
    XL_ETH_MODE_CONNECTOR_RJ45 = 1
except:
    pass

# vxlapi.h: 3054
try:
    XL_ETH_MODE_CONNECTOR_DSUB = 2
except:
    pass

# vxlapi.h: 3057
try:
    XL_ETH_MODE_PHY_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3058
try:
    XL_ETH_MODE_PHY_IEEE_802_3 = 1
except:
    pass

# vxlapi.h: 3059
try:
    XL_ETH_MODE_PHY_BROADR_REACH = 2
except:
    pass

# vxlapi.h: 3062
try:
    XL_ETH_MODE_CLOCK_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3063
try:
    XL_ETH_MODE_CLOCK_AUTO = 1
except:
    pass

# vxlapi.h: 3065
try:
    XL_ETH_MODE_CLOCK_MASTER = 2
except:
    pass

# vxlapi.h: 3066
try:
    XL_ETH_MODE_CLOCK_SLAVE = 3
except:
    pass

# vxlapi.h: 3069
try:
    XL_ETH_MODE_MDI_AUTO = 1
except:
    pass

# vxlapi.h: 3070
try:
    XL_ETH_MODE_MDI_STRAIGHT = 2
except:
    pass

# vxlapi.h: 3071
try:
    XL_ETH_MODE_MDI_CROSSOVER = 3
except:
    pass

# vxlapi.h: 3074
try:
    XL_ETH_MODE_BR_PAIR_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3075
try:
    XL_ETH_MODE_BR_PAIR_1PAIR = 1
except:
    pass

# vxlapi.h: 3084
try:
    XL_ETH_STATUS_LINK_UNKNOWN = 0
except:
    pass

# vxlapi.h: 3085
try:
    XL_ETH_STATUS_LINK_DOWN = 1
except:
    pass

# vxlapi.h: 3086
try:
    XL_ETH_STATUS_LINK_UP = 2
except:
    pass

# vxlapi.h: 3087
try:
    XL_ETH_STATUS_LINK_ERROR = 4
except:
    pass

# vxlapi.h: 3090
try:
    XL_ETH_STATUS_SPEED_UNKNOWN = 0
except:
    pass

# vxlapi.h: 3091
try:
    XL_ETH_STATUS_SPEED_10 = 1
except:
    pass

# vxlapi.h: 3092
try:
    XL_ETH_STATUS_SPEED_100 = 2
except:
    pass

# vxlapi.h: 3093
try:
    XL_ETH_STATUS_SPEED_1000 = 3
except:
    pass

# vxlapi.h: 3094
try:
    XL_ETH_STATUS_SPEED_2500 = 4
except:
    pass

# vxlapi.h: 3095
try:
    XL_ETH_STATUS_SPEED_5000 = 5
except:
    pass

# vxlapi.h: 3096
try:
    XL_ETH_STATUS_SPEED_10000 = 6
except:
    pass

# vxlapi.h: 3099
try:
    XL_ETH_STATUS_DUPLEX_UNKNOWN = 0
except:
    pass

# vxlapi.h: 3100
try:
    XL_ETH_STATUS_DUPLEX_HALF = 1
except:
    pass

# vxlapi.h: 3101
try:
    XL_ETH_STATUS_DUPLEX_FULL = 2
except:
    pass

# vxlapi.h: 3104
try:
    XL_ETH_STATUS_MDI_UNKNOWN = 0
except:
    pass

# vxlapi.h: 3105
try:
    XL_ETH_STATUS_MDI_STRAIGHT = 1
except:
    pass

# vxlapi.h: 3106
try:
    XL_ETH_STATUS_MDI_CROSSOVER = 2
except:
    pass

# vxlapi.h: 3109
try:
    XL_ETH_STATUS_CONNECTOR_DEFAULT = 0
except:
    pass

# vxlapi.h: 3110
try:
    XL_ETH_STATUS_CONNECTOR_RJ45 = 1
except:
    pass

# vxlapi.h: 3111
try:
    XL_ETH_STATUS_CONNECTOR_DSUB = 2
except:
    pass

# vxlapi.h: 3114
try:
    XL_ETH_STATUS_PHY_UNKNOWN = 0
except:
    pass

# vxlapi.h: 3115
try:
    XL_ETH_STATUS_PHY_IEEE_802_3 = 1
except:
    pass

# vxlapi.h: 3116
try:
    XL_ETH_STATUS_PHY_BROADR_REACH = 2
except:
    pass

# vxlapi.h: 3117
try:
    XL_ETH_STATUS_PHY_100BASE_T1 = 2
except:
    pass

# vxlapi.h: 3118
try:
    XL_ETH_STATUS_PHY_1000BASE_T1 = 4
except:
    pass

# vxlapi.h: 3119
try:
    XL_ETH_STATUS_PHY_2500BASE_T1 = 5
except:
    pass

# vxlapi.h: 3120
try:
    XL_ETH_STATUS_PHY_5000BASE_T1 = 6
except:
    pass

# vxlapi.h: 3121
try:
    XL_ETH_STATUS_PHY_10000BASE_T1 = 7
except:
    pass

# vxlapi.h: 3122
try:
    XL_ETH_STATUS_PHY_10BASE_T1S = 8
except:
    pass

# vxlapi.h: 3125
try:
    XL_ETH_STATUS_CLOCK_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3126
try:
    XL_ETH_STATUS_CLOCK_MASTER = 1
except:
    pass

# vxlapi.h: 3127
try:
    XL_ETH_STATUS_CLOCK_SLAVE = 2
except:
    pass

# vxlapi.h: 3130
try:
    XL_ETH_STATUS_BR_PAIR_DONT_CARE = 0
except:
    pass

# vxlapi.h: 3131
try:
    XL_ETH_STATUS_BR_PAIR_1PAIR = 1
except:
    pass

# vxlapi.h: 3137
try:
    XL_ETH_RX_ERROR_INVALID_LENGTH = 0x00000001
except:
    pass

# vxlapi.h: 3139
try:
    XL_ETH_RX_ERROR_INVALID_CRC = 0x00000002
except:
    pass

# vxlapi.h: 3141
try:
    XL_ETH_RX_ERROR_PHY_ERROR = 0x00000004
except:
    pass

# vxlapi.h: 3147
try:
    XL_ETH_DATAFRAME_FLAGS_USE_SOURCE_MAC = 0x00000001
except:
    pass

# vxlapi.h: 3150
try:
    XL_ETH_BYPASS_INACTIVE = 0
except:
    pass

# vxlapi.h: 3151
try:
    XL_ETH_BYPASS_PHY = 1
except:
    pass

# vxlapi.h: 3152
try:
    XL_ETH_BYPASS_MACCORE = 2
except:
    pass

# vxlapi.h: 3157
try:
    XL_ETH_TX_ERROR_BYPASS_ENABLED = 1
except:
    pass

# vxlapi.h: 3158
try:
    XL_ETH_TX_ERROR_NO_LINK = 2
except:
    pass

# vxlapi.h: 3159
try:
    XL_ETH_TX_ERROR_PHY_NOT_CONFIGURED = 3
except:
    pass

# vxlapi.h: 3160
try:
    XL_ETH_TX_ERROR_INVALID_LENGTH = 7
except:
    pass

# vxlapi.h: 3163
try:
    XL_ETH_NETWORK_TX_ERROR_NO_LINK = 0x00000001
except:
    pass

# vxlapi.h: 3164
try:
    XL_ETH_NETWORK_TX_ERROR_PHY_NOT_CONFIGURED = 0x00000002
except:
    pass

# vxlapi.h: 3165
try:
    XL_ETH_NETWORK_TX_ERROR_PHY_BRIDGE_ENABLED = 0x00000004
except:
    pass

# vxlapi.h: 3166
try:
    XL_ETH_NETWORK_TX_ERROR_CONVERTER_RESET = 0x00000008
except:
    pass

# vxlapi.h: 3167
try:
    XL_ETH_NETWORK_TX_ERROR_INVALID_LENGTH = 0x00000010
except:
    pass

# vxlapi.h: 3169
try:
    XL_ETH_NETWORK_TX_ERROR_INVALID_CRC = 0x00000020
except:
    pass

# vxlapi.h: 3171
try:
    XL_ETH_NETWORK_TX_ERROR_MACADDR_ERROR = 0x00000040
except:
    pass

# vxlapi.h: 3175
try:
    XL_ETH_NETWORK_RX_ERROR_INVALID_LENGTH = 0x00000001
except:
    pass

# vxlapi.h: 3177
try:
    XL_ETH_NETWORK_RX_ERROR_INVALID_CRC = 0x00000002
except:
    pass

# vxlapi.h: 3179
try:
    XL_ETH_NETWORK_RX_ERROR_PHY_ERROR = 0x00000004
except:
    pass

# vxlapi.h: 3180
try:
    XL_ETH_NETWORK_RX_ERROR_MACADDR_ERROR = 0x00000008
except:
    pass

# vxlapi.h: 3187
try:
    XL_NET_MAX_NAME_LENGTH = 32
except:
    pass

# vxlapi.h: 3189
try:
    XL_ACCESS_TYPE_UNRELIABLE = 0x00000000
except:
    pass

# vxlapi.h: 3190
try:
    XL_ACCESS_TYPE_RELIABLE = 0x00000001
except:
    pass

# vxlapi.h: 3194
try:
    XL_INVALID_NETWORKID = (-1)
except:
    pass

# vxlapi.h: 3196
try:
    XL_INVALID_SWITCHID = (-1)
except:
    pass

# vxlapi.h: 3198
try:
    XL_INVALID_NETWORKHANDLE = (-1)
except:
    pass

# vxlapi.h: 3200
try:
    XL_INVALID_ETHPORTHANDLE = (-1)
except:
    pass

# vxlapi.h: 3202
try:
    XL_INVALID_RXHANDLE = (-1)
except:
    pass

# vxlapi.h: 3206
try:
    XL_NET_CFG_STAT_OK = 0x00
except:
    pass

# vxlapi.h: 3207
try:
    XL_NET_CFG_DUPLICATE_SEGMENT_NAME = 0x01
except:
    pass

# vxlapi.h: 3208
try:
    XL_NET_CFG_DUPLICATE_VP_NAME = 0x02
except:
    pass

# vxlapi.h: 3209
try:
    XL_NET_CFG_DUPLICATE_MP_NAME = 0x03
except:
    pass

# vxlapi.h: 3212
try:
    XL_TS_DEFAULT_TIMEDOMAIN_NAME = 'xlDefaultTimeDomain'
except:
    pass

# vxlapi.h: 3214
try:
    XL_TS_LEAP_SECONDS_FLAGS_VALID = 0x01
except:
    pass

# vxlapi.h: 3216
try:
    XL_TS_DOMAIN_STAT_APP_IN_SYNC = 0x01
except:
    pass

# vxlapi.h: 3217
try:
    XL_TS_DOMAIN_STAT_DOMAIN_IN_SYNC = 0x04
except:
    pass

# vxlapi.h: 3543
try:
    XL_MOST150_RX_EVENT_HEADER_SIZE = 32
except:
    pass

# vxlapi.h: 3544
try:
    XL_MOST150_MAX_EVENT_DATA_SIZE = 2048
except:
    pass

# vxlapi.h: 3545
try:
    MOST150_SYNC_ALLOC_INFO_SIZE = 372
except:
    pass

# vxlapi.h: 3547
try:
    XL_MOST150_CTRL_PAYLOAD_MAX_SIZE = 45
except:
    pass

# vxlapi.h: 3548
try:
    XL_MOST150_ASYNC_PAYLOAD_MAX_SIZE = 1524
except:
    pass

# vxlapi.h: 3549
try:
    XL_MOST150_ETHERNET_PAYLOAD_MAX_SIZE = 1506
except:
    pass

# vxlapi.h: 3550
try:
    XL_MOST150_ASYNC_SEND_PAYLOAD_MAX_SIZE = 1600
except:
    pass

# vxlapi.h: 3551
try:
    XL_MOST150_ETHERNET_SEND_PAYLOAD_MAX_SIZE = 1600
except:
    pass

# vxlapi.h: 3556
try:
    XL_MOST150_VN2640 = 0x0001
except:
    pass

# vxlapi.h: 3557
try:
    XL_MOST150_INIC = 0x0002
except:
    pass

# vxlapi.h: 3558
try:
    XL_MOST150_SPY = 0x0004
except:
    pass

# vxlapi.h: 3559
try:
    XL_MOST150_QUEUE_OVERFLOW = 0x0100
except:
    pass

# vxlapi.h: 3562
try:
    XL_MOST150_SOURCE_SPECIAL_NODE = 0x00000001
except:
    pass

# vxlapi.h: 3563
try:
    XL_MOST150_SOURCE_SYNC_ALLOC_INFO = 0x00000004
except:
    pass

# vxlapi.h: 3564
try:
    XL_MOST150_SOURCE_CTRL_SPY = 0x00000008
except:
    pass

# vxlapi.h: 3565
try:
    XL_MOST150_SOURCE_ASYNC_SPY = 0x00000010
except:
    pass

# vxlapi.h: 3566
try:
    XL_MOST150_SOURCE_ETH_SPY = 0x00000020
except:
    pass

# vxlapi.h: 3567
try:
    XL_MOST150_SOURCE_SHUTDOWN_FLAG = 0x00000040
except:
    pass

# vxlapi.h: 3568
try:
    XL_MOST150_SOURCE_SYSTEMLOCK_FLAG = 0x00000080
except:
    pass

# vxlapi.h: 3569
try:
    XL_MOST150_SOURCE_LIGHTLOCK_SPY = 0x00000200
except:
    pass

# vxlapi.h: 3570
try:
    XL_MOST150_SOURCE_LIGHTLOCK_INIC = 0x00000400
except:
    pass

# vxlapi.h: 3571
try:
    XL_MOST150_SOURCE_ECL_CHANGE = 0x00000800
except:
    pass

# vxlapi.h: 3572
try:
    XL_MOST150_SOURCE_LIGHT_STRESS = 0x00001000
except:
    pass

# vxlapi.h: 3573
try:
    XL_MOST150_SOURCE_LOCK_STRESS = 0x00002000
except:
    pass

# vxlapi.h: 3574
try:
    XL_MOST150_SOURCE_BUSLOAD_CTRL = 0x00004000
except:
    pass

# vxlapi.h: 3575
try:
    XL_MOST150_SOURCE_BUSLOAD_ASYNC = 0x00008000
except:
    pass

# vxlapi.h: 3576
try:
    XL_MOST150_SOURCE_CTRL_MLB = 0x00010000
except:
    pass

# vxlapi.h: 3577
try:
    XL_MOST150_SOURCE_ASYNC_MLB = 0x00020000
except:
    pass

# vxlapi.h: 3578
try:
    XL_MOST150_SOURCE_ETH_MLB = 0x00040000
except:
    pass

# vxlapi.h: 3579
try:
    XL_MOST150_SOURCE_TXACK_MLB = 0x00080000
except:
    pass

# vxlapi.h: 3580
try:
    XL_MOST150_SOURCE_STREAM_UNDERFLOW = 0x00100000
except:
    pass

# vxlapi.h: 3581
try:
    XL_MOST150_SOURCE_STREAM_OVERFLOW = 0x00200000
except:
    pass

# vxlapi.h: 3582
try:
    XL_MOST150_SOURCE_STREAM_RX_DATA = 0x00400000
except:
    pass

# vxlapi.h: 3583
try:
    XL_MOST150_SOURCE_ECL_SEQUENCE = 0x00800000
except:
    pass

# vxlapi.h: 3586
try:
    XL_MOST150_DEVICEMODE_SLAVE = 0x00
except:
    pass

# vxlapi.h: 3587
try:
    XL_MOST150_DEVICEMODE_MASTER = 0x01
except:
    pass

# vxlapi.h: 3588
try:
    XL_MOST150_DEVICEMODE_STATIC_MASTER = 0x03
except:
    pass

# vxlapi.h: 3589
try:
    XL_MOST150_DEVICEMODE_RETIMED_BYPASS_SLAVE = 0x04
except:
    pass

# vxlapi.h: 3590
try:
    XL_MOST150_DEVICEMODE_RETIMED_BYPASS_MASTER = 0x05
except:
    pass

# vxlapi.h: 3593
try:
    XL_MOST150_FREQUENCY_44100 = 0x00000000
except:
    pass

# vxlapi.h: 3594
try:
    XL_MOST150_FREQUENCY_48000 = 0x00000001
except:
    pass

# vxlapi.h: 3595
try:
    XL_MOST150_FREQUENCY_ERROR = 0x00000002
except:
    pass

# vxlapi.h: 3598
try:
    XL_MOST150_NA_CHANGED = 0x00000001
except:
    pass

# vxlapi.h: 3599
try:
    XL_MOST150_GA_CHANGED = 0x00000002
except:
    pass

# vxlapi.h: 3600
try:
    XL_MOST150_NPR_CHANGED = 0x00000004
except:
    pass

# vxlapi.h: 3601
try:
    XL_MOST150_MPR_CHANGED = 0x00000008
except:
    pass

# vxlapi.h: 3602
try:
    XL_MOST150_SBC_CHANGED = 0x00000010
except:
    pass

# vxlapi.h: 3603
try:
    XL_MOST150_CTRL_RETRY_PARAMS_CHANGED = 0x00000060
except:
    pass

# vxlapi.h: 3604
try:
    XL_MOST150_ASYNC_RETRY_PARAMS_CHANGED = 0x00000180
except:
    pass

# vxlapi.h: 3605
try:
    XL_MOST150_MAC_ADDR_CHANGED = 0x00000200
except:
    pass

# vxlapi.h: 3606
try:
    XL_MOST150_NPR_SPY_CHANGED = 0x00000400
except:
    pass

# vxlapi.h: 3607
try:
    XL_MOST150_MPR_SPY_CHANGED = 0x00000800
except:
    pass

# vxlapi.h: 3608
try:
    XL_MOST150_SBC_SPY_CHANGED = 0x00001000
except:
    pass

# vxlapi.h: 3609
try:
    XL_MOST150_INIC_NISTATE_CHANGED = 0x00002000
except:
    pass

# vxlapi.h: 3610
try:
    XL_MOST150_SPECIAL_NODE_MASK_CHANGED = 0x00003FFF
except:
    pass

# vxlapi.h: 3613
try:
    XL_MOST150_CTRL_RETRY_TIME_MIN = 3
except:
    pass

# vxlapi.h: 3614
try:
    XL_MOST150_CTRL_RETRY_TIME_MAX = 31
except:
    pass

# vxlapi.h: 3615
try:
    XL_MOST150_CTRL_SEND_ATTEMPT_MIN = 1
except:
    pass

# vxlapi.h: 3616
try:
    XL_MOST150_CTRL_SEND_ATTEMPT_MAX = 16
except:
    pass

# vxlapi.h: 3617
try:
    XL_MOST150_ASYNC_RETRY_TIME_MIN = 0
except:
    pass

# vxlapi.h: 3618
try:
    XL_MOST150_ASYNC_RETRY_TIME_MAX = 255
except:
    pass

# vxlapi.h: 3619
try:
    XL_MOST150_ASYNC_SEND_ATTEMPT_MIN = 1
except:
    pass

# vxlapi.h: 3620
try:
    XL_MOST150_ASYNC_SEND_ATTEMPT_MAX = 16
except:
    pass

# vxlapi.h: 3623
try:
    XL_MOST150_INIC_NISTATE_NET_OFF = 0x00000000
except:
    pass

# vxlapi.h: 3624
try:
    XL_MOST150_INIC_NISTATE_NET_INIT = 0x00000001
except:
    pass

# vxlapi.h: 3625
try:
    XL_MOST150_INIC_NISTATE_NET_RBD = 0x00000002
except:
    pass

# vxlapi.h: 3626
try:
    XL_MOST150_INIC_NISTATE_NET_ON = 0x00000003
except:
    pass

# vxlapi.h: 3627
try:
    XL_MOST150_INIC_NISTATE_NET_RBD_RESULT = 0x00000004
except:
    pass

# vxlapi.h: 3630
try:
    XL_MOST150_TX_OK = 0x00000001
except:
    pass

# vxlapi.h: 3631
try:
    XL_MOST150_TX_FAILED_FORMAT_ERROR = 0x00000002
except:
    pass

# vxlapi.h: 3632
try:
    XL_MOST150_TX_FAILED_NETWORK_OFF = 0x00000004
except:
    pass

# vxlapi.h: 3633
try:
    XL_MOST150_TX_FAILED_TIMEOUT = 0x00000005
except:
    pass

# vxlapi.h: 3634
try:
    XL_MOST150_TX_FAILED_WRONG_TARGET = 0x00000008
except:
    pass

# vxlapi.h: 3635
try:
    XL_MOST150_TX_OK_ONE_SUCCESS = 0x00000009
except:
    pass

# vxlapi.h: 3636
try:
    XL_MOST150_TX_FAILED_BAD_CRC = 0x0000000C
except:
    pass

# vxlapi.h: 3637
try:
    XL_MOST150_TX_FAILED_RECEIVER_BUFFER_FULL = 0x0000000E
except:
    pass

# vxlapi.h: 3642
try:
    XL_MOST150_VALID_DATALENANNOUNCED = 0x00000001
except:
    pass

# vxlapi.h: 3643
try:
    XL_MOST150_VALID_SOURCEADDRESS = 0x00000002
except:
    pass

# vxlapi.h: 3644
try:
    XL_MOST150_VALID_TARGETADDRESS = 0x00000004
except:
    pass

# vxlapi.h: 3645
try:
    XL_MOST150_VALID_PACK = 0x00000008
except:
    pass

# vxlapi.h: 3646
try:
    XL_MOST150_VALID_CACK = 0x00000010
except:
    pass

# vxlapi.h: 3647
try:
    XL_MOST150_VALID_PINDEX = 0x00000020
except:
    pass

# vxlapi.h: 3648
try:
    XL_MOST150_VALID_PRIORITY = 0x00000040
except:
    pass

# vxlapi.h: 3649
try:
    XL_MOST150_VALID_CRC = 0x00000080
except:
    pass

# vxlapi.h: 3650
try:
    XL_MOST150_VALID_CRCCALCULATED = 0x00000100
except:
    pass

# vxlapi.h: 3651
try:
    XL_MOST150_VALID_MESSAGE = 0x80000000
except:
    pass

# vxlapi.h: 3656
try:
    XL_MOST150_PACK_OK = 0x00000004
except:
    pass

# vxlapi.h: 3657
try:
    XL_MOST150_PACK_BUFFER_FULL = 0x00000001
except:
    pass

# vxlapi.h: 3658
try:
    XL_MOST150_PACK_NO_RESPONSE = 0x00000000
except:
    pass

# vxlapi.h: 3663
try:
    XL_MOST150_CACK_OK = 0x00000004
except:
    pass

# vxlapi.h: 3664
try:
    XL_MOST150_CACK_CRC_ERROR = 0x00000001
except:
    pass

# vxlapi.h: 3665
try:
    XL_MOST150_CACK_NO_RESPONSE = 0x00000000
except:
    pass

# vxlapi.h: 3668
try:
    XL_MOST150_ASYNC_INVALID_RX_LENGTH = 0x00008000
except:
    pass

# vxlapi.h: 3672
try:
    XL_MOST150_ETHERNET_INVALID_RX_LENGTH = 0x80000000
except:
    pass

# vxlapi.h: 3676
try:
    XL_MOST150_LIGHT_OFF = 0x00000000
except:
    pass

# vxlapi.h: 3677
try:
    XL_MOST150_LIGHT_FORCE_ON = 0x00000001
except:
    pass

# vxlapi.h: 3678
try:
    XL_MOST150_LIGHT_MODULATED = 0x00000002
except:
    pass

# vxlapi.h: 3682
try:
    XL_MOST150_LIGHT_ON_UNLOCK = 0x00000003
except:
    pass

# vxlapi.h: 3683
try:
    XL_MOST150_LIGHT_ON_LOCK = 0x00000004
except:
    pass

# vxlapi.h: 3684
try:
    XL_MOST150_LIGHT_ON_STABLE_LOCK = 0x00000005
except:
    pass

# vxlapi.h: 3685
try:
    XL_MOST150_LIGHT_ON_CRITICAL_UNLOCK = 0x00000006
except:
    pass

# vxlapi.h: 3688
try:
    XL_MOST150_ERROR_ASYNC_TX_ACK_HANDLE = 0x00000001
except:
    pass

# vxlapi.h: 3689
try:
    XL_MOST150_ERROR_ETH_TX_ACK_HANDLE = 0x00000002
except:
    pass

# vxlapi.h: 3692
try:
    XL_MOST150_RX_BUFFER_TYPE_CTRL = 0x00000001
except:
    pass

# vxlapi.h: 3693
try:
    XL_MOST150_RX_BUFFER_TYPE_ASYNC = 0x00000002
except:
    pass

# vxlapi.h: 3696
try:
    XL_MOST150_RX_BUFFER_NORMAL_MODE = 0x00000000
except:
    pass

# vxlapi.h: 3697
try:
    XL_MOST150_RX_BUFFER_BLOCK_MODE = 0x00000001
except:
    pass

# vxlapi.h: 3700
try:
    XL_MOST150_DEVICE_LINE_IN = 0x00000000
except:
    pass

# vxlapi.h: 3701
try:
    XL_MOST150_DEVICE_LINE_OUT = 0x00000001
except:
    pass

# vxlapi.h: 3702
try:
    XL_MOST150_DEVICE_SPDIF_IN = 0x00000002
except:
    pass

# vxlapi.h: 3703
try:
    XL_MOST150_DEVICE_SPDIF_OUT = 0x00000003
except:
    pass

# vxlapi.h: 3704
try:
    XL_MOST150_DEVICE_ALLOC_BANDWIDTH = 0x00000004
except:
    pass

# vxlapi.h: 3707
try:
    XL_MOST150_DEVICE_MODE_OFF = 0x00000000
except:
    pass

# vxlapi.h: 3708
try:
    XL_MOST150_DEVICE_MODE_ON = 0x00000001
except:
    pass

# vxlapi.h: 3709
try:
    XL_MOST150_DEVICE_MODE_OFF_BYPASS_CLOSED = 0x00000002
except:
    pass

# vxlapi.h: 3710
try:
    XL_MOST150_DEVICE_MODE_OFF_NOT_IN_NETON = 0x00000003
except:
    pass

# vxlapi.h: 3711
try:
    XL_MOST150_DEVICE_MODE_OFF_NO_MORE_RESOURCES = 0x00000004
except:
    pass

# vxlapi.h: 3712
try:
    XL_MOST150_DEVICE_MODE_OFF_NOT_ENOUGH_FREE_BW = 0x00000005
except:
    pass

# vxlapi.h: 3713
try:
    XL_MOST150_DEVICE_MODE_OFF_DUE_TO_NET_OFF = 0x00000006
except:
    pass

# vxlapi.h: 3714
try:
    XL_MOST150_DEVICE_MODE_OFF_DUE_TO_CFG_NOT_OK = 0x00000007
except:
    pass

# vxlapi.h: 3715
try:
    XL_MOST150_DEVICE_MODE_OFF_COMMUNICATION_ERROR = 0x00000008
except:
    pass

# vxlapi.h: 3716
try:
    XL_MOST150_DEVICE_MODE_OFF_STREAM_CONN_ERROR = 0x00000009
except:
    pass

# vxlapi.h: 3717
try:
    XL_MOST150_DEVICE_MODE_OFF_CL_ALREADY_USED = 0x0000000A
except:
    pass

# vxlapi.h: 3718
try:
    XL_MOST150_DEVICE_MODE_CL_NOT_ALLOCATED = 0x000000FF
except:
    pass

# vxlapi.h: 3721
try:
    XL_MOST150_ALLOC_BANDWIDTH_NUM_CL_MAX = 10
except:
    pass

# vxlapi.h: 3724
try:
    XL_MOST150_CL_DEALLOC_ALL = 0x00000FFF
except:
    pass

# vxlapi.h: 3727
try:
    XL_MOST150_VOLUME_MIN = 0x00000000
except:
    pass

# vxlapi.h: 3728
try:
    XL_MOST150_VOLUME_MAX = 0x000000FF
except:
    pass

# vxlapi.h: 3731
try:
    XL_MOST150_NO_MUTE = 0x00000000
except:
    pass

# vxlapi.h: 3732
try:
    XL_MOST150_MUTE = 0x00000001
except:
    pass

# vxlapi.h: 3735
try:
    XL_MOST150_LIGHT_FULL = 0x00000064
except:
    pass

# vxlapi.h: 3736
try:
    XL_MOST150_LIGHT_3DB = 0x00000032
except:
    pass

# vxlapi.h: 3739
try:
    XL_MOST150_SYSTEMLOCK_FLAG_NOT_SET = 0x00000000
except:
    pass

# vxlapi.h: 3740
try:
    XL_MOST150_SYSTEMLOCK_FLAG_SET = 0x00000001
except:
    pass

# vxlapi.h: 3743
try:
    XL_MOST150_SHUTDOWN_FLAG_NOT_SET = 0x00000000
except:
    pass

# vxlapi.h: 3744
try:
    XL_MOST150_SHUTDOWN_FLAG_SET = 0x00000001
except:
    pass

# vxlapi.h: 3748
try:
    XL_MOST150_ECL_LINE_LOW = 0x00000000
except:
    pass

# vxlapi.h: 3749
try:
    XL_MOST150_ECL_LINE_HIGH = 0x00000001
except:
    pass

# vxlapi.h: 3751
try:
    XL_MOST150_ECL_LINE_PULL_UP_NOT_ACTIVE = 0x00000000
except:
    pass

# vxlapi.h: 3752
try:
    XL_MOST150_ECL_LINE_PULL_UP_ACTIVE = 0x00000001
except:
    pass

# vxlapi.h: 3756
try:
    XL_MOST150_ECL_SEQ_NUM_STATES_MAX = 200
except:
    pass

# vxlapi.h: 3758
try:
    XL_MOST150_ECL_SEQ_DURATION_MIN = 1
except:
    pass

# vxlapi.h: 3759
try:
    XL_MOST150_ECL_SEQ_DURATION_MAX = 655350
except:
    pass

# vxlapi.h: 3763
try:
    XL_MOST150_ECL_GLITCH_FILTER_MIN = 50
except:
    pass

# vxlapi.h: 3764
try:
    XL_MOST150_ECL_GLITCH_FILTER_MAX = 50000
except:
    pass

# vxlapi.h: 3771
try:
    XL_MOST150_MODE_DEACTIVATED = 0
except:
    pass

# vxlapi.h: 3772
try:
    XL_MOST150_MODE_ACTIVATED = 1
except:
    pass

# vxlapi.h: 3775
try:
    XL_MOST150_BUSLOAD_TYPE_DATA_PACKET = 0
except:
    pass

# vxlapi.h: 3776
try:
    XL_MOST150_BUSLOAD_TYPE_ETHERNET_PACKET = 1
except:
    pass

# vxlapi.h: 3779
try:
    XL_MOST150_BUSLOAD_COUNTER_TYPE_NONE = 0x00
except:
    pass

# vxlapi.h: 3780
try:
    XL_MOST150_BUSLOAD_COUNTER_TYPE_1_BYTE = 0x01
except:
    pass

# vxlapi.h: 3781
try:
    XL_MOST150_BUSLOAD_COUNTER_TYPE_2_BYTE = 0x02
except:
    pass

# vxlapi.h: 3782
try:
    XL_MOST150_BUSLOAD_COUNTER_TYPE_3_BYTE = 0x03
except:
    pass

# vxlapi.h: 3783
try:
    XL_MOST150_BUSLOAD_COUNTER_TYPE_4_BYTE = 0x04
except:
    pass

# vxlapi.h: 3787
try:
    XL_MOST150_SPDIF_MODE_SLAVE = 0x00000000
except:
    pass

# vxlapi.h: 3788
try:
    XL_MOST150_SPDIF_MODE_MASTER = 0x00000001
except:
    pass

# vxlapi.h: 3791
try:
    XL_MOST150_SPDIF_ERR_NO_ERROR = 0x00000000
except:
    pass

# vxlapi.h: 3792
try:
    XL_MOST150_SPDIF_ERR_HW_COMMUNICATION = 0x00000001
except:
    pass

# vxlapi.h: 3795
try:
    XL_MOST150_STARTUP_NO_ERROR = 0x00000000
except:
    pass

# vxlapi.h: 3797
try:
    XL_MOST150_STARTUP_NO_ERRORINFO = 0xFFFFFFFF
except:
    pass

# vxlapi.h: 3800
try:
    XL_MOST150_SHUTDOWN_NO_ERROR = 0x00000000
except:
    pass

# vxlapi.h: 3802
try:
    XL_MOST150_SHUTDOWN_NO_ERRORINFO = 0xFFFFFFFF
except:
    pass

# vxlapi.h: 3805
try:
    XL_MOST150_STREAM_RX_DATA = 0
except:
    pass

# vxlapi.h: 3806
try:
    XL_MOST150_STREAM_TX_DATA = 1
except:
    pass

# vxlapi.h: 3808
try:
    XL_MOST150_STREAM_INVALID_HANDLE = 0
except:
    pass

# vxlapi.h: 3811
try:
    XL_MOST150_STREAM_STATE_CLOSED = 0x01
except:
    pass

# vxlapi.h: 3812
try:
    XL_MOST150_STREAM_STATE_OPENED = 0x02
except:
    pass

# vxlapi.h: 3813
try:
    XL_MOST150_STREAM_STATE_STARTED = 0x03
except:
    pass

# vxlapi.h: 3814
try:
    XL_MOST150_STREAM_STATE_STOPPED = 0x04
except:
    pass

# vxlapi.h: 3815
try:
    XL_MOST150_STREAM_STATE_START_PENDING = 0x05
except:
    pass

# vxlapi.h: 3816
try:
    XL_MOST150_STREAM_STATE_STOP_PENDING = 0x06
except:
    pass

# vxlapi.h: 3817
try:
    XL_MOST150_STREAM_STATE_OPEN_PENDING = 0x07
except:
    pass

# vxlapi.h: 3818
try:
    XL_MOST150_STREAM_STATE_CLOSE_PENDING = 0x08
except:
    pass

# vxlapi.h: 3821
try:
    XL_MOST150_STREAM_TX_BYTES_PER_FRAME_MIN = 1
except:
    pass

# vxlapi.h: 3822
try:
    XL_MOST150_STREAM_TX_BYTES_PER_FRAME_MAX = 152
except:
    pass

# vxlapi.h: 3825
try:
    XL_MOST150_STREAM_RX_NUM_CL_MAX = 8
except:
    pass

# vxlapi.h: 3828
try:
    XL_MOST150_STREAM_CL_MIN = 0x000C
except:
    pass

# vxlapi.h: 3829
try:
    XL_MOST150_STREAM_CL_MAX = 0x017F
except:
    pass

# vxlapi.h: 3833
try:
    XL_MOST150_STREAM_STATE_ERROR_NO_ERROR = 0
except:
    pass

# vxlapi.h: 3834
try:
    XL_MOST150_STREAM_STATE_ERROR_NOT_ENOUGH_BW = 1
except:
    pass

# vxlapi.h: 3835
try:
    XL_MOST150_STREAM_STATE_ERROR_NET_OFF = 2
except:
    pass

# vxlapi.h: 3836
try:
    XL_MOST150_STREAM_STATE_ERROR_CONFIG_NOT_OK = 3
except:
    pass

# vxlapi.h: 3837
try:
    XL_MOST150_STREAM_STATE_ERROR_CL_DISAPPEARED = 4
except:
    pass

# vxlapi.h: 3838
try:
    XL_MOST150_STREAM_STATE_ERROR_INIC_SC_ERROR = 5
except:
    pass

# vxlapi.h: 3839
try:
    XL_MOST150_STREAM_STATE_ERROR_DEVICEMODE_BYPASS = 6
except:
    pass

# vxlapi.h: 3840
try:
    XL_MOST150_STREAM_STATE_ERROR_NISTATE_NOT_NETON = 7
except:
    pass

# vxlapi.h: 3841
try:
    XL_MOST150_STREAM_STATE_ERROR_INIC_BUSY = 8
except:
    pass

# vxlapi.h: 3842
try:
    XL_MOST150_STREAM_STATE_ERROR_CL_MISSING = 9
except:
    pass

# vxlapi.h: 3843
try:
    XL_MOST150_STREAM_STATE_ERROR_NUM_BYTES_MISMATCH = 10
except:
    pass

# vxlapi.h: 3844
try:
    XL_MOST150_STREAM_STATE_ERROR_INIC_COMMUNICATION = 11
except:
    pass

# vxlapi.h: 3847
try:
    XL_MOST150_STREAM_BUFFER_ERROR_NO_ERROR = 0
except:
    pass

# vxlapi.h: 3848
try:
    XL_MOST150_STREAM_BUFFER_ERROR_NOT_ENOUGH_DATA = 1
except:
    pass

# vxlapi.h: 3849
try:
    XL_MOST150_STREAM_BUFFER_TX_FIFO_CLEARED = 2
except:
    pass

# vxlapi.h: 3853
try:
    XL_MOST150_STREAM_BUFFER_ERROR_STOP_BY_APP = 1
except:
    pass

# vxlapi.h: 3854
try:
    XL_MOST150_STREAM_BUFFER_ERROR_MOST_SIGNAL_OFF = 2
except:
    pass

# vxlapi.h: 3855
try:
    XL_MOST150_STREAM_BUFFER_ERROR_UNLOCK = 3
except:
    pass

# vxlapi.h: 3856
try:
    XL_MOST150_STREAM_BUFFER_ERROR_CL_MISSING = 4
except:
    pass

# vxlapi.h: 3857
try:
    XL_MOST150_STREAM_BUFFER_ERROR_ALL_CL_MISSING = 5
except:
    pass

# vxlapi.h: 3858
try:
    XL_MOST150_STREAM_BUFFER_ERROR_OVERFLOW = 128
except:
    pass

# vxlapi.h: 3861
try:
    XL_MOST150_STREAM_LATENCY_VERY_LOW = 0
except:
    pass

# vxlapi.h: 3862
try:
    XL_MOST150_STREAM_LATENCY_LOW = 1
except:
    pass

# vxlapi.h: 3863
try:
    XL_MOST150_STREAM_LATENCY_MEDIUM = 2
except:
    pass

# vxlapi.h: 3864
try:
    XL_MOST150_STREAM_LATENCY_HIGH = 3
except:
    pass

# vxlapi.h: 3865
try:
    XL_MOST150_STREAM_LATENCY_VERY_HIGH = 4
except:
    pass

# vxlapi.h: 3869
try:
    XL_MOST150_BYPASS_STRESS_TIME_MIN = 10
except:
    pass

# vxlapi.h: 3870
try:
    XL_MOST150_BYPASS_STRESS_TIME_MAX = 65535
except:
    pass

# vxlapi.h: 3873
try:
    XL_MOST150_BYPASS_STRESS_STOPPED = 0
except:
    pass

# vxlapi.h: 3874
try:
    XL_MOST150_BYPASS_STRESS_STARTED = 1
except:
    pass

# vxlapi.h: 3875
try:
    XL_MOST150_BYPASS_STRESS_STOPPED_LIGHT_OFF = 2
except:
    pass

# vxlapi.h: 3876
try:
    XL_MOST150_BYPASS_STRESS_STOPPED_DEVICE_MODE = 3
except:
    pass

# vxlapi.h: 3881
try:
    XL_MOST150_SSO_RESULT_NO_RESULT = 0x00000000
except:
    pass

# vxlapi.h: 3882
try:
    XL_MOST150_SSO_RESULT_NO_FAULT_SAVED = 0x00000001
except:
    pass

# vxlapi.h: 3883
try:
    XL_MOST150_SSO_RESULT_SUDDEN_SIGNAL_OFF = 0x00000002
except:
    pass

# vxlapi.h: 3884
try:
    XL_MOST150_SSO_RESULT_CRITICAL_UNLOCK = 0x00000003
except:
    pass

# vxlapi.h: 4380
try:
    XL_CAN_MAX_DATA_LEN = 64
except:
    pass

# vxlapi.h: 4381
try:
    XL_CANFD_RX_EVENT_HEADER_SIZE = 32
except:
    pass

# vxlapi.h: 4382
try:
    XL_CANFD_MAX_EVENT_SIZE = 128
except:
    pass

# vxlapi.h: 4385
try:
    XL_CAN_TXMSG_FLAG_EDL = 0x0001
except:
    pass

# vxlapi.h: 4386
try:
    XL_CAN_TXMSG_FLAG_BRS = 0x0002
except:
    pass

# vxlapi.h: 4387
try:
    XL_CAN_TXMSG_FLAG_RTR = 0x0010
except:
    pass

# vxlapi.h: 4388
try:
    XL_CAN_TXMSG_FLAG_HIGHPRIO = 0x0080
except:
    pass

# vxlapi.h: 4389
try:
    XL_CAN_TXMSG_FLAG_WAKEUP = 0x0200
except:
    pass

# vxlapi.h: 4397
try:
    XL_CAN_RXMSG_FLAG_EDL = 0x0001
except:
    pass

# vxlapi.h: 4398
try:
    XL_CAN_RXMSG_FLAG_BRS = 0x0002
except:
    pass

# vxlapi.h: 4399
try:
    XL_CAN_RXMSG_FLAG_ESI = 0x0004
except:
    pass

# vxlapi.h: 4400
try:
    XL_CAN_RXMSG_FLAG_RTR = 0x0010
except:
    pass

# vxlapi.h: 4401
try:
    XL_CAN_RXMSG_FLAG_EF = 0x0200
except:
    pass

# vxlapi.h: 4402
try:
    XL_CAN_RXMSG_FLAG_ARB_LOST = 0x0400
except:
    pass

# vxlapi.h: 4404
try:
    XL_CAN_RXMSG_FLAG_WAKEUP = 0x2000
except:
    pass

# vxlapi.h: 4405
try:
    XL_CAN_RXMSG_FLAG_TE = 0x4000
except:
    pass

# vxlapi.h: 4470
try:
    XL_CAN_ERRC_BIT_ERROR = 1
except:
    pass

# vxlapi.h: 4471
try:
    XL_CAN_ERRC_FORM_ERROR = 2
except:
    pass

# vxlapi.h: 4472
try:
    XL_CAN_ERRC_STUFF_ERROR = 3
except:
    pass

# vxlapi.h: 4473
try:
    XL_CAN_ERRC_OTHER_ERROR = 4
except:
    pass

# vxlapi.h: 4474
try:
    XL_CAN_ERRC_CRC_ERROR = 5
except:
    pass

# vxlapi.h: 4475
try:
    XL_CAN_ERRC_ACK_ERROR = 6
except:
    pass

# vxlapi.h: 4476
try:
    XL_CAN_ERRC_NACK_ERROR = 7
except:
    pass

# vxlapi.h: 4477
try:
    XL_CAN_ERRC_OVLD_ERROR = 8
except:
    pass

# vxlapi.h: 4478
try:
    XL_CAN_ERRC_EXCPT_ERROR = 9
except:
    pass

# vxlapi.h: 4487
try:
    XL_CAN_QUEUE_OVERFLOW = 0x100
except:
    pass

# vxlapi.h: 4490
try:
    RX_FIFO_CANFD_QUEUE_SIZE_MAX = 524288
except:
    pass

# vxlapi.h: 4491
try:
    RX_FIFO_CANFD_QUEUE_SIZE_MIN = 8192
except:
    pass

# vxlapi.h: 4533
try:
    XL_A429_MSG_CHANNEL_DIR_TX = 0x01
except:
    pass

# vxlapi.h: 4534
try:
    XL_A429_MSG_CHANNEL_DIR_RX = 0x02
except:
    pass

# vxlapi.h: 4537
try:
    XL_A429_MSG_BITRATE_SLOW_MIN = 10500
except:
    pass

# vxlapi.h: 4538
try:
    XL_A429_MSG_BITRATE_SLOW_MAX = 16000
except:
    pass

# vxlapi.h: 4539
try:
    XL_A429_MSG_BITRATE_FAST_MIN = 90000
except:
    pass

# vxlapi.h: 4540
try:
    XL_A429_MSG_BITRATE_FAST_MAX = 110000
except:
    pass

# vxlapi.h: 4543
try:
    XL_A429_MSG_GAP_4BIT = 32
except:
    pass

# vxlapi.h: 4546
try:
    XL_A429_MSG_BITRATE_RX_MIN = 10000
except:
    pass

# vxlapi.h: 4547
try:
    XL_A429_MSG_BITRATE_RX_MAX = 120000
except:
    pass

# vxlapi.h: 4550
try:
    XL_A429_MSG_AUTO_BAUDRATE_DISABLED = 0
except:
    pass

# vxlapi.h: 4551
try:
    XL_A429_MSG_AUTO_BAUDRATE_ENABLED = 1
except:
    pass

# vxlapi.h: 4554
try:
    XL_A429_MSG_FLAG_ON_REQUEST = 0x00000001
except:
    pass

# vxlapi.h: 4555
try:
    XL_A429_MSG_FLAG_CYCLIC = 0x00000002
except:
    pass

# vxlapi.h: 4556
try:
    XL_A429_MSG_FLAG_DELETE_CYCLIC = 0x00000004
except:
    pass

# vxlapi.h: 4559
try:
    XL_A429_MSG_CYCLE_MAX = 0x3FFFFFFF
except:
    pass

# vxlapi.h: 4562
try:
    XL_A429_MSG_GAP_DEFAULT = 0
except:
    pass

# vxlapi.h: 4563
try:
    XL_A429_MSG_GAP_MAX = 0x000FFFFF
except:
    pass

# vxlapi.h: 4567
try:
    XL_A429_MSG_PARITY_DEFAULT = 0
except:
    pass

# vxlapi.h: 4568
try:
    XL_A429_MSG_PARITY_DISABLED = 1
except:
    pass

# vxlapi.h: 4569
try:
    XL_A429_MSG_PARITY_ODD = 2
except:
    pass

# vxlapi.h: 4570
try:
    XL_A429_MSG_PARITY_EVEN = 3
except:
    pass

# vxlapi.h: 4573
try:
    XL_A429_EV_TX_MSG_CTRL_ON_REQUEST = 0
except:
    pass

# vxlapi.h: 4574
try:
    XL_A429_EV_TX_MSG_CTRL_CYCLIC = 1
except:
    pass

# vxlapi.h: 4577
try:
    XL_A429_EV_TX_ERROR_ACCESS_DENIED = 0
except:
    pass

# vxlapi.h: 4578
try:
    XL_A429_EV_TX_ERROR_TRANSMISSION_ERROR = 1
except:
    pass

# vxlapi.h: 4581
try:
    XL_A429_EV_RX_ERROR_GAP_VIOLATION = 0
except:
    pass

# vxlapi.h: 4582
try:
    XL_A429_EV_RX_ERROR_PARITY = 1
except:
    pass

# vxlapi.h: 4583
try:
    XL_A429_EV_RX_ERROR_BITRATE_LOW = 2
except:
    pass

# vxlapi.h: 4584
try:
    XL_A429_EV_RX_ERROR_BITRATE_HIGH = 3
except:
    pass

# vxlapi.h: 4585
try:
    XL_A429_EV_RX_ERROR_FRAME_FORMAT = 4
except:
    pass

# vxlapi.h: 4586
try:
    XL_A429_EV_RX_ERROR_CODING_RZ = 5
except:
    pass

# vxlapi.h: 4587
try:
    XL_A429_EV_RX_ERROR_DUTY_FACTOR = 6
except:
    pass

# vxlapi.h: 4588
try:
    XL_A429_EV_RX_ERROR_AVG_BIT_LENGTH = 7
except:
    pass

# vxlapi.h: 4591
try:
    XL_A429_QUEUE_OVERFLOW = 0x100
except:
    pass

# vxlapi.h: 4594
try:
    XL_A429_RX_FIFO_QUEUE_SIZE_MAX = 524288
except:
    pass

# vxlapi.h: 4595
try:
    XL_A429_RX_FIFO_QUEUE_SIZE_MIN = 8192
except:
    pass

# vxlapi.h: 4732
try:
    XL_INVALID_CONFIG_HANDLE = 0
except:
    pass

# vxlapi.h: 7274
def CANFD_GET_NUM_DATABYTES(dlc, edl, rtr):
    return rtr and 0 or (dlc < 9) and dlc or (not edl) and 8 or (dlc == 9) and 12 or (dlc == 10) and 16 or (dlc == 11) and 20 or (dlc == 12) and 24 or (dlc == 13) and 32 or (dlc == 14) and 48 or 64

s_xl_application_notification = struct_s_xl_application_notification# vxlapi.h: 650

s_xl_sync_pulse_ev = struct_s_xl_sync_pulse_ev# vxlapi.h: 664

s_xl_sync_pulse = struct_s_xl_sync_pulse# vxlapi.h: 670

s_xl_can_msg = struct_s_xl_can_msg# vxlapi.h: 866

s_xl_daio_data = struct_s_xl_daio_data# vxlapi.h: 888

s_xl_io_digital_data = struct_s_xl_io_digital_data# vxlapi.h: 905

s_xl_io_analog_data = struct_s_xl_io_analog_data# vxlapi.h: 912

s_xl_daio_piggy_data = struct_s_xl_daio_piggy_data# vxlapi.h: 915

s_xl_chip_state = struct_s_xl_chip_state# vxlapi.h: 934

s_xl_transceiver = struct_s_xl_transceiver# vxlapi.h: 947

s_xl_lin_msg = struct_s_xl_lin_msg# vxlapi.h: 968

s_xl_lin_sleep = struct_s_xl_lin_sleep# vxlapi.h: 976

s_xl_lin_no_ans = struct_s_xl_lin_no_ans# vxlapi.h: 980

s_xl_lin_wake_up = struct_s_xl_lin_wake_up# vxlapi.h: 984

s_xl_lin_crc_info = struct_s_xl_lin_crc_info# vxlapi.h: 991

s_xl_lin_msg_api = union_s_xl_lin_msg_api# vxlapi.h: 998

s_xl_kline_rx_data = struct_s_xl_kline_rx_data# vxlapi.h: 1012

s_xl_kline_tx_data = struct_s_xl_kline_tx_data# vxlapi.h: 1018

s_xl_kline_tester_5bd = struct_s_xl_kline_tester_5bd# vxlapi.h: 1024

s_xl_kline_ecu_5bd = struct_s_xl_kline_ecu_5bd# vxlapi.h: 1030

s_xl_kline_tester_fastinit_wu_pattern = struct_s_xl_kline_tester_fastinit_wu_pattern# vxlapi.h: 1035

s_xl_kline_ecu_fastinit_wu_pattern = struct_s_xl_kline_ecu_fastinit_wu_pattern# vxlapi.h: 1040

s_xl_kline_confirmation = struct_s_xl_kline_confirmation# vxlapi.h: 1046

s_xl_kline_error_rxtx = struct_s_xl_kline_error_rxtx# vxlapi.h: 1050

s_xl_kline_error_5bd_tester = struct_s_xl_kline_error_5bd_tester# vxlapi.h: 1054

s_xl_kline_error_5bd_ecu = struct_s_xl_kline_error_5bd_ecu# vxlapi.h: 1058

s_xl_kline_error_ibs = struct_s_xl_kline_error_ibs# vxlapi.h: 1063

s_xl_kline_error = struct_s_xl_kline_error# vxlapi.h: 1078

s_xl_kline_data = struct_s_xl_kline_data# vxlapi.h: 1101

s_xl_tag_data = union_s_xl_tag_data# vxlapi.h: 1106

s_xl_event = struct_s_xl_event# vxlapi.h: 1123

s_xl_license_info = struct_s_xl_license_info# vxlapi.h: 1361

s_xl_channel_config = struct_s_xl_channel_config# vxlapi.h: 1410

s_xl_driver_config = struct_s_xl_driver_config# vxlapi.h: 1420

_XLacc_filt = struct__XLacc_filt# vxlapi.h: 1453

_XLacceptance = struct__XLacceptance# vxlapi.h: 1461

s_xl_ip_address = struct_s_xl_ip_address# vxlapi.h: 1552

s_xl_remote_location_config = struct_s_xl_remote_location_config# vxlapi.h: 1563

s_xl_remote_device = struct_s_xl_remote_device# vxlapi.h: 1571

s_xl_remote_device_info = struct_s_xl_remote_device_info# vxlapi.h: 1579

s_xl_most_ctrl_spy = struct_s_xl_most_ctrl_spy# vxlapi.h: 1883

s_xl_most_ctrl_msg = struct_s_xl_most_ctrl_msg# vxlapi.h: 1893

s_xl_most_async_msg = struct_s_xl_most_async_msg# vxlapi.h: 1903

s_xl_most_async_tx = struct_s_xl_most_async_tx# vxlapi.h: 1911

s_xl_most_special_register = struct_s_xl_most_special_register# vxlapi.h: 1928

s_xl_most_event_source = struct_s_xl_most_event_source# vxlapi.h: 1933

s_xl_most_all_bypass = struct_s_xl_most_all_bypass# vxlapi.h: 1937

s_xl_most_timing_mode = struct_s_xl_most_timing_mode# vxlapi.h: 1941

s_xl_most_timing_mode_spdif = struct_s_xl_most_timing_mode_spdif# vxlapi.h: 1945

s_xl_most_frequency = struct_s_xl_most_frequency# vxlapi.h: 1949

s_xl_most_register_bytes = struct_s_xl_most_register_bytes# vxlapi.h: 1955

s_xl_most_register_bits = struct_s_xl_most_register_bits# vxlapi.h: 1961

s_xl_most_sync_alloc = struct_s_xl_most_sync_alloc# vxlapi.h: 1965

s_xl_most_ctrl_sync_audio = struct_s_xl_most_ctrl_sync_audio# vxlapi.h: 1971

s_xl_most_ctrl_sync_audio_ex = struct_s_xl_most_ctrl_sync_audio_ex# vxlapi.h: 1977

s_xl_most_sync_volume_status = struct_s_xl_most_sync_volume_status# vxlapi.h: 1982

s_xl_most_sync_mutes_status = struct_s_xl_most_sync_mutes_status# vxlapi.h: 1987

s_xl_most_rx_light = struct_s_xl_most_rx_light# vxlapi.h: 1991

s_xl_most_tx_light = struct_s_xl_most_tx_light# vxlapi.h: 1995

s_xl_most_light_power = struct_s_xl_most_light_power# vxlapi.h: 1999

s_xl_most_lock_status = struct_s_xl_most_lock_status# vxlapi.h: 2003

s_xl_most_supervisor_lock_status = struct_s_xl_most_supervisor_lock_status# vxlapi.h: 2007

s_xl_most_gen_light_error = struct_s_xl_most_gen_light_error# vxlapi.h: 2013

s_xl_most_gen_lock_error = struct_s_xl_most_gen_lock_error# vxlapi.h: 2019

s_xl_most_rx_buffer = struct_s_xl_most_rx_buffer# vxlapi.h: 2023

s_xl_most_error = struct_s_xl_most_error# vxlapi.h: 2028

s_xl_most_ctrl_busload = struct_s_xl_most_ctrl_busload# vxlapi.h: 2034

s_xl_most_async_busload = struct_s_xl_most_async_busload# vxlapi.h: 2038

s_xl_most_stream_state = struct_s_xl_most_stream_state# vxlapi.h: 2045

s_xl_most_stream_buffer = struct_s_xl_most_stream_buffer# vxlapi.h: 2057

s_xl_most_sync_tx_underflow = struct_s_xl_most_sync_tx_underflow# vxlapi.h: 2063

s_xl_most_sync_rx_overflow = struct_s_xl_most_sync_rx_overflow# vxlapi.h: 2068

s_xl_most_tag_data = union_s_xl_most_tag_data# vxlapi.h: 2075

s_xl_most_event = struct_s_xl_most_event# vxlapi.h: 2112

s_xl_most_ctrl_busload_configuration = struct_s_xl_most_ctrl_busload_configuration# vxlapi.h: 2136

s_xl_most_async_busload_configuration = struct_s_xl_most_async_busload_configuration# vxlapi.h: 2143

s_xl_most_device_state = struct_s_xl_most_device_state# vxlapi.h: 2180

s_xl_most_stream_open = struct_s_xl_most_stream_open# vxlapi.h: 2190

s_xl_most_stream_info = struct_s_xl_most_stream_info# vxlapi.h: 2203

s_xl_fr_cluster_configuration = struct_s_xl_fr_cluster_configuration# vxlapi.h: 2290

s_xl_fr_channel_config = struct_s_xl_fr_channel_config# vxlapi.h: 2299

s_xl_fr_set_modes = struct_s_xl_fr_set_modes# vxlapi.h: 2332

s_xl_fr_acceptance_filter = struct_s_xl_fr_acceptance_filter# vxlapi.h: 2376

s_xl_fr_start_cycle = struct_s_xl_fr_start_cycle# vxlapi.h: 2537

s_xl_fr_rx_frame = struct_s_xl_fr_rx_frame# vxlapi.h: 2546

s_xl_fr_tx_frame = struct_s_xl_fr_tx_frame# vxlapi.h: 2560

s_xl_fr_wakeup = struct_s_xl_fr_wakeup# vxlapi.h: 2566

s_xl_fr_symbol_window = struct_s_xl_fr_symbol_window# vxlapi.h: 2573

s_xl_fr_status = struct_s_xl_fr_status# vxlapi.h: 2578

s_xl_fr_nm_vector = struct_s_xl_fr_nm_vector# vxlapi.h: 2584

s_xl_fr_error_poc_mode = struct_s_xl_fr_error_poc_mode# vxlapi.h: 2591

s_xl_fr_error_sync_frames = struct_s_xl_fr_error_sync_frames# vxlapi.h: 2599

s_xl_fr_error_clock_corr_failure = struct_s_xl_fr_error_clock_corr_failure# vxlapi.h: 2609

s_xl_fr_error_nit_failure = struct_s_xl_fr_error_nit_failure# vxlapi.h: 2614

s_xl_fr_error_cc_error = struct_s_xl_fr_error_cc_error# vxlapi.h: 2619

s_xl_fr_error_info = union_s_xl_fr_error_info# vxlapi.h: 2621

s_xl_fr_error = struct_s_xl_fr_error# vxlapi.h: 2635

s_xl_fr_spy_frame = struct_s_xl_fr_spy_frame# vxlapi.h: 2650

s_xl_fr_spy_symbol = struct_s_xl_fr_spy_symbol# vxlapi.h: 2655

s_xl_fr_tag_data = union_s_xl_fr_tag_data# vxlapi.h: 2662

s_xl_fr_event = struct_s_xl_fr_event# vxlapi.h: 2682

triggerTypeParams = union_triggerTypeParams# vxlapi.h: 2719

s_xl_daio_trigger_mode = struct_s_xl_daio_trigger_mode# vxlapi.h: 2729

xl_daio_set_port = struct_xl_daio_set_port# vxlapi.h: 2742

xl_daio_digital_params = struct_xl_daio_digital_params# vxlapi.h: 2769

xl_daio_analog_params = struct_xl_daio_analog_params# vxlapi.h: 2786

s_xl_kline_uart_params = struct_s_xl_kline_uart_params# vxlapi.h: 2825

s_xl_kline_init_tester = struct_s_xl_kline_init_tester# vxlapi.h: 2833

s_xl_kline_init_5BdTester = struct_s_xl_kline_init_5BdTester# vxlapi.h: 2851

s_xl_kline_init_5BdEcu = struct_s_xl_kline_init_5BdEcu# vxlapi.h: 2870

s_xl_kline_set_com_tester = struct_s_xl_kline_set_com_tester# vxlapi.h: 2878

s_xl_kline_set_com_ecu = struct_s_xl_kline_set_com_ecu# vxlapi.h: 2890

s_xl_timesync_leap_seconds = struct_s_xl_timesync_leap_seconds# vxlapi.h: 3249

s_xl_timesync_clock_uuid_ = struct_s_xl_timesync_clock_uuid_# vxlapi.h: 3270

s_xl_ts_domain_time = struct_s_xl_ts_domain_time# vxlapi.h: 3278

s_xl_eth_frame = struct_s_xl_eth_frame# vxlapi.h: 3297

s_xl_eth_framedata = union_s_xl_eth_framedata# vxlapi.h: 3302

s_xl_eth_dataframe_rx = struct_s_xl_eth_dataframe_rx# vxlapi.h: 3314

s_xl_eth_dataframe_rxerror = struct_s_xl_eth_dataframe_rxerror# vxlapi.h: 3327

s_xl_eth_dataframe_tx = struct_s_xl_eth_dataframe_tx# vxlapi.h: 3338

s_xl_eth_dataframe_tx_event = struct_s_xl_eth_dataframe_tx_event# vxlapi.h: 3352

s_xl_eth_dataframe_txerror = struct_s_xl_eth_dataframe_txerror# vxlapi.h: 3361

s_xl_eth_config_result = struct_s_xl_eth_config_result# vxlapi.h: 3372

s_xl_eth_channel_status = struct_s_xl_eth_channel_status# vxlapi.h: 3383

s_xl_eth_lostevent = struct_s_xl_eth_lostevent# vxlapi.h: 3408

s_xl_eth_tag_data = union_s_xl_eth_tag_data# vxlapi.h: 3422

s_xl_eth_event = struct_s_xl_eth_event# vxlapi.h: 3442

s_xl_net_eth_dataframe_rx = struct_s_xl_net_eth_dataframe_rx# vxlapi.h: 3459

s_xl_net_eth_dataframe_rx_error = struct_s_xl_net_eth_dataframe_rx_error# vxlapi.h: 3472

s_xl_eth_net_tag_data = union_s_xl_eth_net_tag_data# vxlapi.h: 3504

s_xl_net_eth_event = struct_s_xl_net_eth_event# vxlapi.h: 3516

s_xl_most150_event_source = struct_s_xl_most150_event_source# vxlapi.h: 3898

s_xl_most150_device_mode = struct_s_xl_most150_device_mode# vxlapi.h: 3902

s_xl_most150_frequency = struct_s_xl_most150_frequency# vxlapi.h: 3906

s_xl_most150_special_node_info = struct_s_xl_most150_special_node_info# vxlapi.h: 3926

s_xl_most150_ctrl_rx = struct_s_xl_most150_ctrl_rx# vxlapi.h: 3938

s_xl_most150_ctrl_spy = struct_s_xl_most150_ctrl_spy# vxlapi.h: 3959

s_xl_most150_async_rx_msg = struct_s_xl_most150_async_rx_msg# vxlapi.h: 3966

s_xl_most150_async_spy_msg = struct_s_xl_most150_async_spy_msg# vxlapi.h: 3984

s_xl_most150_ethernet_rx = struct_s_xl_most150_ethernet_rx# vxlapi.h: 3991

s_xl_most150_ethernet_spy = struct_s_xl_most150_ethernet_spy# vxlapi.h: 4009

s_xl_most150_cl_info = struct_s_xl_most150_cl_info# vxlapi.h: 4014

s_xl_most150_sync_alloc_info = struct_s_xl_most150_sync_alloc_info# vxlapi.h: 4018

s_xl_most150_sync_volume_status = struct_s_xl_most150_sync_volume_status# vxlapi.h: 4024

s_xl_most150_tx_light = struct_s_xl_most150_tx_light# vxlapi.h: 4028

s_xl_most150_rx_light_lock_status = struct_s_xl_most150_rx_light_lock_status# vxlapi.h: 4032

s_xl_most150_error = struct_s_xl_most150_error# vxlapi.h: 4037

s_xl_most150_configure_rx_buffer = struct_s_xl_most150_configure_rx_buffer# vxlapi.h: 4042

s_xl_most150_ctrl_sync_audio = struct_s_xl_most150_ctrl_sync_audio# vxlapi.h: 4049

s_xl_most150_sync_mute_status = struct_s_xl_most150_sync_mute_status# vxlapi.h: 4054

s_xl_most150_tx_light_power = struct_s_xl_most150_tx_light_power# vxlapi.h: 4058

s_xl_most150_gen_light_error = struct_s_xl_most150_gen_light_error# vxlapi.h: 4062

s_xl_most150_gen_lock_error = struct_s_xl_most150_gen_lock_error# vxlapi.h: 4066

s_xl_most150_ctrl_busload = struct_s_xl_most150_ctrl_busload# vxlapi.h: 4070

s_xl_most150_async_busload = struct_s_xl_most150_async_busload# vxlapi.h: 4074

s_xl_most150_systemlock_flag = struct_s_xl_most150_systemlock_flag# vxlapi.h: 4078

s_xl_most150_shutdown_flag = struct_s_xl_most150_shutdown_flag# vxlapi.h: 4082

s_xl_most150_spdif_mode = struct_s_xl_most150_spdif_mode# vxlapi.h: 4087

s_xl_most150_ecl = struct_s_xl_most150_ecl# vxlapi.h: 4091

s_xl_most150_ecl_termination = struct_s_xl_most150_ecl_termination# vxlapi.h: 4095

s_xl_most150_nw_startup = struct_s_xl_most150_nw_startup# vxlapi.h: 4100

s_xl_most150_nw_shutdown = struct_s_xl_most150_nw_shutdown# vxlapi.h: 4105

s_xl_most150_stream_state = struct_s_xl_most150_stream_state# vxlapi.h: 4111

s_xl_most150_stream_tx_buffer = struct_s_xl_most150_stream_tx_buffer# vxlapi.h: 4117

s_xl_most150_stream_rx_buffer = struct_s_xl_most150_stream_rx_buffer# vxlapi.h: 4124

s_xl_most150_stream_tx_underflow = struct_s_xl_most150_stream_tx_underflow# vxlapi.h: 4129

s_xl_most150_stream_tx_label = struct_s_xl_most150_stream_tx_label# vxlapi.h: 4136

s_xl_most150_gen_bypass_stress = struct_s_xl_most150_gen_bypass_stress# vxlapi.h: 4140

s_xl_most150_ecl_sequence = struct_s_xl_most150_ecl_sequence# vxlapi.h: 4144

s_xl_most150_ecl_glitch_filter = struct_s_xl_most150_ecl_glitch_filter# vxlapi.h: 4148

s_xl_most150_sso_result = struct_s_xl_most150_sso_result# vxlapi.h: 4152

s_xl_most150_ctrl_tx_ack = struct_s_xl_most150_ctrl_tx_ack# vxlapi.h: 4177

s_xl_most150_async_tx_ack = struct_s_xl_most150_async_tx_ack# vxlapi.h: 4187

s_xl_most150_ethernet_tx = struct_s_xl_most150_ethernet_tx# vxlapi.h: 4197

s_xl_most150_hw_sync = struct_s_xl_most150_hw_sync# vxlapi.h: 4201

s_xl_event_most150 = struct_s_xl_event_most150# vxlapi.h: 4261

s_xl_set_most150_special_node_info = struct_s_xl_set_most150_special_node_info# vxlapi.h: 4278

s_xl_most150_ctrl_tx_msg = struct_s_xl_most150_ctrl_tx_msg# vxlapi.h: 4300

s_xl_most150_async_tx_msg = struct_s_xl_most150_async_tx_msg# vxlapi.h: 4309

s_xl_most150_ethernet_tx_msg = struct_s_xl_most150_ethernet_tx_msg# vxlapi.h: 4319

s_xl_most150_sync_audio_parameter = struct_s_xl_most150_sync_audio_parameter# vxlapi.h: 4327

s_xl_most150_ctrl_busload_config = struct_s_xl_most150_ctrl_busload_config# vxlapi.h: 4335

s_xl_most150_async_busload_config = struct_s_xl_most150_async_busload_config# vxlapi.h: 4349

s_xl_most150_stream_open = struct_s_xl_most150_stream_open# vxlapi.h: 4358

s_xl_most150_stream_get_info = struct_s_xl_most150_stream_get_info# vxlapi.h: 4369

u_tagData = union_u_tagData# vxlapi.h: 4506

s_xl_a429_params = struct_s_xl_a429_params# vxlapi.h: 4629

s_xl_a429_msg_tx = struct_s_xl_a429_msg_tx# vxlapi.h: 4645

s_xl_a429_ev_tx_ok = struct_s_xl_a429_ev_tx_ok# vxlapi.h: 4659

s_xl_a429_ev_tx_err = struct_s_xl_a429_ev_tx_err# vxlapi.h: 4670

s_xl_a429_ev_rx_ok = struct_s_xl_a429_ev_rx_ok# vxlapi.h: 4679

s_xl_a429_ev_rx_err = struct_s_xl_a429_ev_rx_err# vxlapi.h: 4691

s_xl_a429_ev_bus_statistic = struct_s_xl_a429_ev_bus_statistic# vxlapi.h: 4697

XLIDriverConfig = struct_XLIDriverConfig# vxlapi.h: 4726

_XLdriverConfig = struct__XLdriverConfig# vxlapi.h: 4729

s_xl_channel_drv_config_v1 = struct_s_xl_channel_drv_config_v1# vxlapi.h: 4735

s_channel_drv_config_list_v1 = struct_s_channel_drv_config_list_v1# vxlapi.h: 4762

s_xl_device_drv_config_v1 = struct_s_xl_device_drv_config_v1# vxlapi.h: 4769

s_device_drv_config_list_v1 = struct_s_device_drv_config_list_v1# vxlapi.h: 4791

s_xl_virtual_port_drv_config_v1 = struct_s_xl_virtual_port_drv_config_v1# vxlapi.h: 4800

s_virtual_port_drv_config_list_v1 = struct_s_virtual_port_drv_config_list_v1# vxlapi.h: 4806

s_xl_measurement_point_drv_config_v1 = struct_s_xl_measurement_point_drv_config_v1# vxlapi.h: 4818

s_xl_measurement_point_drv_config_list_v1 = struct_s_xl_measurement_point_drv_config_list_v1# vxlapi.h: 4824

s_xl_switch_drv_config_v1 = struct_s_xl_switch_drv_config_v1# vxlapi.h: 4839

s_switch_drv_config_list_v1 = struct_s_switch_drv_config_list_v1# vxlapi.h: 4845

s_xl_network_drv_config_v1 = struct_s_xl_network_drv_config_v1# vxlapi.h: 4860

s_xl_network_drv_config_list_v1 = struct_s_xl_network_drv_config_list_v1# vxlapi.h: 4866

s_xl_dll_drv_config_v1 = struct_s_xl_dll_drv_config_v1# vxlapi.h: 4875

s_xlapi_driver_config_v1 = struct_s_xlapi_driver_config_v1# vxlapi.h: 4895

# No inserted files

# No prefix-stripping

