from aws_lambda_powertools.utilities.parser import BaseModel as _BaseModel


class BaseModel(_BaseModel):

    class Config:
        @staticmethod
        def alias_generator(snake_case_string):
            """to camelCase"""
            words = snake_case_string.split('_')
            return words[0] + ''.join(word.title() for word in words[1:])

    def dict(self, *args, **kwargs):
        if "by_alias" in kwargs:
            del kwargs["by_alias"]
        return super().dict(*args, by_alias=True, **kwargs)

    def json(self, *args, **kwargs):
        if "by_alias" in kwargs:
            del kwargs["by_alias"]
        return super().json(*args, by_alias=True, **kwargs)
