def load_classes(class_defs_path: str) -> DynamicClassTable:
    """
    Loads a class table which contains all the data layouts 
    for all the classes, bitflags, and enums within the loaded file.

    This expects a cdb file, which is a specialised file format containing the required information.

    To create a cdb file, use the function `convert_xml_to_cdb`.
    """
    ...
def convert_xml_to_cdb(input_path: str, output_path: str):
    """
    Converts the data within the xml file 'input_path' and converts it to a cdb file and outputs it to 'output_path'.
    """
    ...
def merge_cdb_defs(client_def_path: str, server_def_path: str, output_path: str):
    """
    Merges the cdb data from `client_def_path` and `server_def_path` while prioritising `client_def_path`'s data.
    The merged data is saved at `output_path`
    """
    ...
def light_hash_string(value: str) -> int:
    """
    Hashes the `value` string and returns the hash representation.

    This uses a light hashing algorithm commonly used by KI for field types, and in pirate also class names & field names.
    """
    ...
def wiz_hash_string(value: str) -> int:
    """
    Hashes the `value` string and returns the hash representation.

    This uses a in house hashing algorithm used by KI exclusively in Wizard101 for class names & field names.
    """
    ...
def hash_field_type(name: str, type: str) -> int:
    """
    Hashes `name` and `type` names together to represent Wizard101's has values for fields within classes.
    """
    ...

class DynamicClass:
    """
    Dynamic class created with the kiclass module.

    This is used to read and modify the data from KI's code.
    """
    def class_name(self) -> str:
        """
        Returns the name of the dynamic class.
        """
        ...
    def base_name(self) -> str:
        """
        Returns the name of the dynamic class's base.
        """
        ...
    def into_base(self) -> DynamicClass:
        """
        Converts the dynamic class into it's base class. (removing all fields not within base)
        """
        ...
    def field_flags(self, field_name: str) -> str:
        """
        Returns the flags for the field within the dynamic class with the name.

        Parameters
        ----------
        field_name : str
            The name of the field within the class
        """
        ...
    def field_flags_by_index(self, field_index: int) -> str:
        """
        Returns the flags for the field within the dynamic class via it's position.

        Parameters
        ----------
        field_index : int
            The position of the field within the class
        """
        ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> dict.__iter__: ...
    def is_known(self) -> bool:
        """
        Returns True as this is a known class.
        """
        return True
    def has_unknown_fields(self) -> bool:
        """
        Returns True if the dynamic class has any unknown fields within it.
        """
        ...
    def unknown_fields(self) -> dict:
        """
        Returns the unknown fields within the dynamic class.
        """
        ...
    def to_json(self) -> str:
        """
        Returns the json representation of the dynamic class as a str.
        """
        ...
    def to_xml(self) -> str:
        """
        Returns the json representation of the dynamic class as a str.
        """
        ...

class UnknownClass:
    def data(self) -> bytes:
        """
        Returns the byte representation of the unknown class.
        """
        ...
    def id(self) -> int:
        """
        Returns the id of the class which is not recognised.
        """
        ...
    def is_known(self) -> bool:
        """
        Returns False as this is a unknown class.
        """
        return False
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    
class KIBinaryFileReader:
    def __new__(class_table: DynamicClassTable) -> KIBinaryFileReader:
        """
        Creates a reusable binary file reader for KI's binary XMLs.
        """
        ...
    def read_file(self, path: str) -> DynamicClass|UnknownClass|None:
        """
        Returns the dynamic class representation from the path.

        If the class is not known but it is valid data then `UnknownClass` is returned.

        If the file is not a valid binary XML then None is returned.
        """
        ...

class DynamicClassTable:
    def __new__(class_defs_path: str) -> DynamicClassTable:
        """
        Loads a class table which contains all the data layouts 
        for all the classes, bitflags, and enums within the loaded file.

        This expects a cdb file, which is a specialised file format containing the required information.

        To create a cdb file, use the function `convert_xml_to_cdb`.
        """
        ...
    def create_class(self, class_name: str) -> DynamicClass|None:
        """
        Creates a dynamic class with the name `class_name`.

        If the class name is not found then None is returned.
        """
        ...
    def create_class_by_id(self, class_hash: int) -> DynamicClass|None:
        """
        Creates a dynamic class with the hash id `class_hash`.

        If the class hash match is not found then None is returned.
        """
        ...

class FieldFlags:
    def __new__(value: str|FieldFlags|int|None) -> FieldFlags: ...
    def save() -> FieldFlags: ...
    def copy() -> FieldFlags: ...
    def public() -> FieldFlags: ...
    def transmitplayer() -> FieldFlags: ...
    def transmitcsr() -> FieldFlags: ...
    def persist() -> FieldFlags: ...
    def deprecated() -> FieldFlags: ...
    def noscript() -> FieldFlags: ...
    def deltasave() -> FieldFlags: ...
    def binary() -> FieldFlags: ...
    def default() -> FieldFlags: ...
    def transmit() -> FieldFlags: ...
    def noedit() -> FieldFlags: ...
    def filename() -> FieldFlags: ...
    def color() -> FieldFlags: ...
    def range() -> FieldFlags: ...
    def bits() -> FieldFlags: ...
    def enum() -> FieldFlags: ...
    def localized() -> FieldFlags: ...
    def stringkey() -> FieldFlags: ...
    def objectid() -> FieldFlags: ...
    def referenceid() -> FieldFlags: ...
    def radians() -> FieldFlags: ...
    def name() -> FieldFlags: ...
    def nameref() -> FieldFlags: ...
    def override() -> FieldFlags: ...
    def weak() -> FieldFlags: ...
    def editormask() -> FieldFlags: ...
    def __eq__(self, other: int|FieldFlags) -> bool: ...
    def __and__(self, other: int|FieldFlags) -> FieldFlags: ...
    def __or__(self, other: int|FieldFlags) -> FieldFlags: ...
    def __xor__(self, other: int|FieldFlags) -> FieldFlags: ...
    def __invert__(self) -> FieldFlags: ...
    def __int__(self) -> int: ...

class Vector3D:
    x: float
    y: float
    z: float
    def __new__(x: int, y: int, z: int) -> Vector3D: ...

class Matrix3x3:
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    x3: float
    y3: float
    z3: float
    def __new__(data: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]) -> Matrix3x3: ...

class UUniqueID:
    def __new__(bytes) -> UUniqueID: ...

class Color:
    r: int
    g: int
    b: int
    a: int
    def __new__(r: int, g: int, b: int, a: int) -> Color: ...

class PointFloat:
    x: float
    y: float
    def __new__(x: float, y: float) -> PointFloat: ...

class PointInt:
    x: int
    y: int
    def __new__(x: int, y: int) -> PointInt: ...

class PointUInt:
    x: int
    y: int
    def __new__(x: int, y: int) -> PointUInt: ...

class SizeFloat:
    x: float
    y: float
    def __new__(x: float, y: float) -> SizeFloat: ...

class SizeInt:
    x: int
    y: int
    def __new__(x: int, y: int) -> SizeInt: ...

class SizeUInt:
    x: int
    y: int
    def __new__(x: int, y: int) -> SizeUInt: ...