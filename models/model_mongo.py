from sanic_motor import BaseModel

class UserMon(BaseModel):
    __coll__ = 'users_agent'
    __unique_fields__ = ['username']
    # __unique_fields__ = ['name, age']   # name and age for unique


class Gift_list(BaseModel):
    __coll__ = 'gift_list'
    __unique_fields__ = ['rid']