import parsegument as pg

parser = pg.Parsegumenter(name="Parsegument", help="Base Command Group")
group = pg.CommandGroup(name="group", help="another group")
parser.add_child(group)

@group.on_call
def group_call():
    print("group_call")

@group.command(name="foo", help="prints the argument")
@pg.argument("bar", help="string to print out")
def foo(bar: str):
    print(bar)

@group.command(name="foo2", help="prints the argument again")
@pg.argument(name="bar", help="string to print out again")
def foo2(bar: str):
    print(bar)

print(parser.execute("Parsegument group"))
print(len(group))
print(group.length)