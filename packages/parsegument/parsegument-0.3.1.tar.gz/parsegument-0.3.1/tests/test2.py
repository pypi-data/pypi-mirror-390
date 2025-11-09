from typing import Optional, Any
from pprint import pprint
import parsegument as pg
from parsegument import CommandGroup

class ChildGroup(CommandGroup):
    def __init__(self):
        super().__init__("ChildGroup")

    @staticmethod
    @pg.argument("test", int)
    def method_thing(test:str) -> Optional[Any]:
        if type(test) == str:
            return test + ", This is a method thing"
        elif type(test) == int:
            return test + 2
        return None

    @staticmethod
    def method_thing2(testing:str) -> Optional[Any]:
        if type(testing) == str:
            return "this is a string"
        else:
            return "WTF IS THIS"



parser = pg.Parsegumenter(prefix="!", name="test")
group = ChildGroup()
group.initialise()
parser.add_child(group)
print(parser.execute("!test ChildGroup method_thing 10.5"))
pprint(parser.schema)