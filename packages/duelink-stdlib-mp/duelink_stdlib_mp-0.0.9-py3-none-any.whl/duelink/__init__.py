from duelink.duelinklib import DUELinkController

def build_bytearray(data, offset=0, count=-1):
    if count == -1:
        count = len(data)-offset
    arr = "["
    i=offset;
    while count > 0:
        if (i>offset):
            arr=arr+","
        arr=arr+str(data[i])
        i=i+1
        count=count-1
    arr=arr+"]"
    return arr

def build_floatarray(data, offset=0, count=-1):
    if count == -1:
        count = len(data)-offset
    arr = "{"
    i=offset;
    while count > 0:
        if (i>offset):
            arr=arr+","
        arr=arr+str(data[i])
        i=i+1
        count=count-1
    arr=arr+"}"
    return arr