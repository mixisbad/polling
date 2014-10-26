import time, threading
import json, sys
import urllib.request
import fileinput
import datetime

#define global var here
#filename = ""
traffic_data = {}

"""
                {  (switch_id, output_port)  : { match : }, ():{}, ():{}}
traffic_data = {("00:00:00:00:00:00:00:00",1) : { 
                                                  {
                                                    "dataLayerDestination":"7e:38:97:71:2c:2e",
                                                    "dataLayerSource":"ee:3e:76:7f:17:4e",
                                                    "dataLayerType":"0x0000",
                                                    "dataLayerVirtualLan":-1,
                                                    "dataLayerVirtualLanPriorityCodePoint":0,
                                                    "inputPort":4,
                                                    "networkDestination":"0.0.0.0",
                                                    "networkDestinationMaskLen":0,
                                                    "networkProtocol":0,
                                                    "networkSource":"0.0.0.0",
                                                    "networkSourceMaskLen":0,
                                                    "networkTypeOfService":0,
                                                    "transportDestination":0,
                                                    "transportSource":0,
                                                    "wildcards":3678448
                                                    } : {"byteCount":121213, "durationSecond":5}}
"""

def parsejson(stringdata):
    global traffic_data
    #global filename
    #global f_ptr 

    #f_ptr = open(filename,'a',encoding='utf-8')
    new_traffic_data = {}
    switch_dicts = json.loads(stringdata)
    for switch_id in switch_dicts:
        if switch_dicts[switch_id]:
            for flow in switch_dicts[switch_id]:
                match = flow["match"]
                print("switch_id : ",switch_id,"dst : ",match["networkDestination"]," src : ",match["networkSource"], " transportDestination(port number) : ", match["transportDestination"])
                #f_ptr.write(switch_id + "\t" + match["dataLayerDestination"] + "\t" + match["dataLayerSource"] + "\t" + str(match["inputPort"]) + "\t")
                actions = flow["actions"]

                #f_ptr.write("switch\t dst\t src\t inport\t outport\t bandwidth\t duration\n");
                for action in actions:
                    if action["type"] == "OUTPUT" or action["type"] == "OPAQUE_ENQUEUE":
                        #may need to handle case of flood though.....
                        print("outputPort : ", action["port"])
                        #f_ptr.write(str(action["port"]) + "\t")
                        #print("durationSeconds : ", flow["durationSeconds"]," byteCount : ", flow["byteCount"])
                        total_duration = 0
                        total_byte = 0
                        accumulate_byte = 0
                        accumulate_time = 0
                        found = False
                        if (switch_id,action["port"],match["networkDestination"],match["networkSource"],match["transportDestination"]) in traffic_data:
                            #print("found switch_id : ", switch_id, "action[port] : ", action["port"])
                            temp_traffic = traffic_data[(switch_id,action["port"],match["networkDestination"],match["networkSource"],match["transportDestination"])]
                            if str(match) in temp_traffic:
                                #print("str(match) is in")
                                found = True
                                temp_flow = temp_traffic[str(match)]
                                old_duration = temp_flow["duration"]
                                old_bytecount = temp_flow["byteCount"]                               
                                total_byte = flow["byteCount"]-old_bytecount
                                accumulate_byte = flow["byteCount"]
                                accumulate_time = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)
                                total_duration = accumulate_time-old_duration
                            
                            #else:
                            #    print("str(match) isn't in")
                        if not found:
                            total_duration = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)
                            total_byte = flow["byteCount"]
                            accumulate_byte = flow["byteCount"]
                            accumulate_time = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)

                        buildkey = (switch_id,action["port"],match["networkDestination"],match["networkSource"],match["transportDestination"])
  
                        #add information into globall traffic data for next iteration 
                        if buildkey not in new_traffic_data:
                            new_traffic_data[buildkey] = {}
                        new_traffic_data[buildkey][str(match)] = {}
                        new_traffic_data[buildkey][str(match)]["duration"] = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)
                        new_traffic_data[buildkey][str(match)]["byteCount"] = flow["byteCount"]
                        
                        print("duration : ", total_duration," byteCount : ", total_byte) 
                        print("accumulate_byte : ", accumulate_byte)
                        print("accumulate_time : ", accumulate_time)
                        bw = ((total_byte*8)/(total_duration))/1000000
                        print("bandwidth : ", bw, "Mbps")

                        #f_ptr.write(str(bw) + "\t" + str(total_duration) + "\n");
                        #f_ptr.closed
                    else :
                        print("action : ", action["type"])

    traffic_data = new_traffic_data
                        

def poll():
    #global filename

    #page = urllib.request.urlopen('http://localhost:8080/wm/core/controller/switches/json')
    #line = page.read().decode("utf-8")
    #print(line)

    #page = urllib.request.urlopen('http://localhost:8080/wm/core/controller/switches/json')
    #line = page.read().decode("utf-8")
    #line = "[{\"a\":\"hi\"},{\"a\":\"ho\"}]"

    #collections = json.loads(line)

    #for switch in collections:
    #    print( switch["dpid"] )
    
    #print( len(collections))


    #print( "00:00:00:00:00:00:00:15".replace(':',''))
    #print( int('0x00:00:00:00:00:00:00:15',16))

    page = urllib.request.urlopen('http://localhost:8080/wm/core/switch/all/flow/json')
    line = page.read().decode("utf-8")

    parsejson(line)
    print()
    print("-----------------------------------------------------------------")
    print()
    threading.Timer(1,poll).start()
    #poll()


'''
now = datetime.datetime.now()
m = now.month
str_m = str(m)
if m < 10:
    str_m = '0' + str_m
d = now.day
str_d = str(d)
if d < 10:
    str_d = '0' + str_d
h = now.hour
str_h = str(h)
if h < 10:
    str_h = '0' + str_h
mm = now.minute
str_mm = str(mm)
if mm < 10:
    str_mm = '0' + str_mm
s = now.second
str_s = str(s)
if s < 10:
    str_s = '0' + str_s
filename = 'log' + str(now.year) + str_m + str_d + str_h + str_mm + str_s + '.txt'
print(filename)

f_ptr = open(filename,"w",encoding='utf-8')
f_ptr.write("switch\t dst\t src\t inport\t outport\t bandwidth\t duration\n");
'''
poll()

