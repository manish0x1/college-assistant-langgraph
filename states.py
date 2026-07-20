# so  now we are creating a graph
# and now first thing you create is a state


import os



# typed  DICT  -  most comman approach
from typing import TypedDict
class State(TypedDict):
    topic: str
    summary :str
    score:int




#2) Pydantic Approcah
# it is good at datavalidation and type checking at run time
from pydantic import BaseModel, field_validator


class State(BaseModel):
    topic: str
    score:int
    summary :str = ""

    @field_validator
    def score_positive(cls,v):
        if v < 0:
            raise ValueError("Score Must be Positive")
        





#python dataclasses

#standard  python dataclass  but it is used very  rarely 

from dataclasses import dataclass, field
@dataclass 
class State:
    topic: str =""
    summary : str =""
    message : list = field(default_factroy = list)









from langgraph.graph import MessagesState

class State(MessagesState):
    # messages field is already included
    user_name: str
    language: str




    

    
