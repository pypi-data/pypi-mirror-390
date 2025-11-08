import yaml
import sys

from yaml.scanner import ScannerError
from yaml.parser import ParserError

from pydantic import BaseModel, ValidationError

from yaml_syntax.exceptions import (
    YamlFormatFileError,
    EmptyFileError,
    SyntaxValidationError,
    NotSerializable
)


from .exception_handler import (
    default_syntax_error_message
)


class YamlSyntax:
    """
    handle syntax of yaml file

    Raises:
        YamlFormatFileError: format file error if the load file or input text is not in YAML format.
        SyntaxValidationError: When the syntax of a loaded YAML file does not match the syntax schema.
        EmptyFileError: When the input file is empty.
        NotSerializable: When a loaded YAML file is not dict-like. We need to make a dict to make serialized data. 
    """

    serialized_data:BaseModel|None = None
    yaml_syntax_error_handler = staticmethod(default_syntax_error_message)
    raise_syntax_validation_error = False

    def __init__(self, syntax_schema:BaseModel, yaml_text:str|bytes, yaml_syntax_error_handler=None,
                 raise_syntax_validation_error:bool=False):
        """
        load yaml file and check syntax of yaml file

        Args:
            syntax_schema (BaseModel): syntax schema
            yaml_text (str | bytes): text of yaml file
            yaml_syntax_error_handler (_type_, optional): function to handle message of syntax error. Defaults to None.
            raise_syntax_validation_error (bool, optional): Raise a SyntaValidationError if the YAML file has a syntax error.
            Otherwise, it will print an error message and exit with code 1. Defaults to False.


        Raises:
            YamlFormatFileError: if file is not yaml like.
        """

        try:
            loaded_yaml = yaml.safe_load(yaml_text)
        except ScannerError:
            raise YamlFormatFileError("are you sure this is an yaml file? this is not yaml file.")
        except ParserError:
            raise YamlFormatFileError("are you sure this is an yaml file? this is not yaml file.")


        self.__check_loaded_yaml(loaded_yaml=loaded_yaml)

        if yaml_syntax_error_handler:
            self.yaml_syntax_error_handler = staticmethod(yaml_syntax_error_handler) 

        self.raise_syntax_validation_error = raise_syntax_validation_error
        
        self.__serialize_yaml_file(syntax_schema, loaded_yaml)


    def __serialize_yaml_file(self, syntax_schema:BaseModel, loaded_yaml:dict):
        """
        serialize loaded yaml text

        Args:
            syntax_schema (BaseModel): syntax schema
            loaded_yaml (dict): loaded yaml file

        Raises:
            SyntaxValidationError: When the syntax of a loaded YAML file does not match the syntax schema
            ex: any exceptions
        """

        try:
            self.serialized_data = syntax_schema(**loaded_yaml)

        except ValidationError as validation_error:
            if not self.raise_syntax_validation_error:
                print(self.yaml_syntax_error_handler(validation_error))
                sys.exit(1)
            else:
                raise SyntaxValidationError(self.yaml_syntax_error_handler(validation_error))



    def __check_loaded_yaml(self, loaded_yaml):
        """
        check loaded yaml is true or not

        Args:
            loaded_yaml (Any): loaded yaml file. it cannot be None or str

        Raises:
            EmptyFileError: when file is empty
            NotSerializable: if loaded_yaml file is str or anything exclude dict
        """

        if loaded_yaml is None:
            raise EmptyFileError("file is empty!")

        if isinstance(loaded_yaml, str):
            raise NotSerializable("yaml file content is not serializable")



    @classmethod
    def from_file(cls, syntax_schema:BaseModel, yaml_file:str, yaml_syntax_error_handler=None,
                        raise_syntax_validation_error:bool=False):
        """
        check syntax of file from file.

        Args:
            syntax_schema (BaseModel): syntax schema
            yaml_file (str): file name or file path
            yaml_syntax_error_handler (_type_, optional): function to handle message of syntax error. Defaults to None.
            raise_syntax_validation_error (bool, optional): Raise a SyntaValidationError if the YAML file has a syntax error.
            Otherwise, it will print an error message and exit with code 1. Defaults to False.

        Returns:
            YamlSyntax
        """
        with open(yaml_file) as file:
            return cls(syntax_schema, file.read(), yaml_syntax_error_handler, raise_syntax_validation_error)



    @property
    def to_json(self) -> dict|None:
        if self.serialized_data:
            return self.serialized_data.model_dump()
        return None

