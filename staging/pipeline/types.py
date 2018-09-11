from typing import NamedTuple
from recordclass import recordclass


class User_Tweet(NamedTuple):
    uid: int
    tid: int

Tweet = recordclass('Tweet',
                    ['id', 'uid', 'text', 'lang',
                     'truncated','in_reply_to_status_id',
                     'in_reply_to_user_id', 'retweeted'],
                    verbose=False)

class Example(NamedTuple):
    point: Tweet
    label: float
