'''
Created on 2013. 5. 30.

@author: kongseokhwan
'''

import colander

class Friend(colander.TupleSchema):
    rank = colander.SchemaNode(colander.Int(),
                               validator=colander.Range(0, 9999))
    name = colander.SchemaNode(colander.String())

class Phone(colander.MappingSchema):
    location = colander.SchemaNode(colander.String(),
                                  validator=colander.OneOf(['home', 'work']))
    number = colander.SchemaNode(colander.String())

class Friends(colander.SequenceSchema):
    friend = Friend()

class Phones(colander.SequenceSchema):
    phone = Phone()

class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Int(),
                             validator=colander.Range(0, 200))
    friends = Friends()
    phones = Phones()
    
    
cstruct = {
         'name':'keith',
         'age':'20',
         'friends':[('1', 'jim'),('2', 'bob'), ('3', 'joe'), ('4', 'fred')],
         'phones':[{'location':'home', 'number':'555-1212'},
                   {'location':'work', 'number':'555-8989'},],
         }

schema = Person()
deserialized = schema.deserialize(cstruct)

print deserialized.name

    