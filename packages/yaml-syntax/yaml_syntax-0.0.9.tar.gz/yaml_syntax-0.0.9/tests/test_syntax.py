import pytest

from yaml_syntax.syntax import YamlSyntax
from yaml_syntax.exceptions import (
    NotSerializable,
    EmptyFileError,
    YamlFormatFileError,
    SyntaxValidationError,
)

from pydantic import BaseModel


def test_check_yaml_syntax_from_file():

    class SimpleSyntax(BaseModel):
        version:int
    
    yaml_text ="version: 13"


    y = YamlSyntax(SimpleSyntax, yaml_text)

    excpect_serialized_data = SimpleSyntax(version=13)

    assert y.serialized_data == excpect_serialized_data


def test_not_serializable_yaml():
     
    with pytest.raises(NotSerializable) as e:

        class SimpleSyntax(BaseModel):
            version:int
    
        yaml_text ="vtest_check_yaml_syntax_from_fileersion"


        YamlSyntax(SimpleSyntax, yaml_text)

    assert "not serializable" in str(e.value)


def test_empty_yaml_file():

    with pytest.raises(EmptyFileError) as e:

        class SimpleSyntax(BaseModel):
            version:int
    
        yaml_text =""


        YamlSyntax(SimpleSyntax, yaml_text)

    assert "empty" in str(e.value)



def test_invalid_yaml_format():

    with pytest.raises(YamlFormatFileError) as e:

        class SimpleSyntax(BaseModel):
            version:int
    

        YamlSyntax.from_file(SimpleSyntax, "./tests/test.txt")

    assert "not yaml file" in str(e.value)


def test_raised_syntax_validdation_error():

    class SimpleSyntax(BaseModel):
        case_name:str
    
    with pytest.raises(SyntaxValidationError) as e:


        YamlSyntax.from_file(SimpleSyntax, "./tests/test.yaml", raise_syntax_validation_error=True)

    assert "error" in str(e.value)

    with pytest.raises(SyntaxValidationError) as e:


        YamlSyntax(SimpleSyntax, "name: sss", raise_syntax_validation_error=True)

    assert "error" in str(e.value)



def test_customized_syntax_validation_error_handler():

    def customized_func(validation_error):
        return "customized error!"
    
    class SimpleSyntax(BaseModel):
        case_name:str
    

    with pytest.raises(SyntaxValidationError) as e:


        YamlSyntax.from_file(SimpleSyntax, "./tests/test.yaml",
                             raise_syntax_validation_error=True,
                             yaml_syntax_error_handler=customized_func)

    assert "customized error!" in str(e.value)

    with pytest.raises(SyntaxValidationError) as e:


        YamlSyntax(SimpleSyntax, "name: sss", raise_syntax_validation_error=True,
                   yaml_syntax_error_handler=customized_func)

    assert "customized error!" in str(e.value)


