from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):

    class Config:
        @staticmethod
        def alias_generator(snake_case_string):
            """to camelCase"""
            words = snake_case_string.split('_')
            return words[0] + ''.join(word.title() for word in words[1:])
