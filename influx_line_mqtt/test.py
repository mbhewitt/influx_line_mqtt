

from datetime import datetime
import time


class labm: 
    def tt(self,obj):
        import datetime
        if isinstance(obj, datetime.datetime):
            print(obj.timestamp())
        else:
            print("Not a datetime object")

tag ={"measurement_type":"temp","room":"bed"}
print(list(tag.keys()))
tp = [1,2,3,4,5,6,7,8,9,10]
print(tp[1:])