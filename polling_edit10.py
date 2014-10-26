import time, threading
import json, sys
import urllib.request
import fileinput

#define global var here
linkbandwidth = 10.0
switchnumport = 6
switchnum = 0
filename = ""
traffic_file_name = "/home/mininet/floodlight-qos-beta-master/traffic.txt"
traffic_data = {}
name_index = {}
bandwidthout = [[]]

def parsejson(stringdata):
    global traffic_data
    global traffic_file_name
    global filename
    global name_index
    global f_ptr 
    global bandwidthout
    global switchnum

    f_ptr = open(traffic_file_name,'w',encoding='utf-8')
    new_traffic_data = {}
    switch_dicts = json.loads(stringdata)
    for switch_id in switch_dicts:
        if switch_id in switch_dicts.keys():
            switch_index = name_index[switch_id]
            if switch_dicts[switch_id]:
                for flow in switch_dicts[switch_id]:
                    match = flow["match"]

                    actions = flow["actions"]

                    for action in actions:
                        if action["type"] == "OUTPUT":
                            total_duration = 0
                            total_byte = 0
                            found = False
                            if (switch_id,action["port"]) in traffic_data:
                                temp_traffic = traffic_data[(switch_id,action["port"])]
                                if str(match) in temp_traffic:
                                    found = True
                                    temp_flow = temp_traffic[str(match)]
                                    old_duration = temp_flow["duration"]
                                    old_bytecount = temp_flow["byteCount"]
                                    total_duration = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)-old_duration
                                    total_byte = flow["byteCount"]-old_bytecount

                            if not found:
                                total_duration = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)
                                total_byte = flow["byteCount"]

                            buildkey = (switch_id,action["port"])
                        
                        #add information into globall traffic data for next iteration 
                            if buildkey not in new_traffic_data:
                                new_traffic_data[buildkey] = {}
                            new_traffic_data[buildkey][str(match)] = {}
                            new_traffic_data[buildkey][str(match)]["duration"] = (flow["durationSeconds"]+flow["durationNanoseconds"]/1000000000)
                            new_traffic_data[buildkey][str(match)]["byteCount"] = flow["byteCount"]
                        
                            bw = ((total_byte*8)/(total_duration))/1000000
                            bandwidthout[switch_index][action["port"]-1] = bandwidthout[switch_index][action["port"]-1] - bw
                           
    f_ptr.write(str(switchnum) + "\t" + str(switchnumport) + "\n")

    for key in name_index:
        f_ptr.write(key + "\n" + str(name_index[key])+"\n")

    for sw in range(switchnum):
        for port in range (switchnumport):
            print ("%.2f" % bandwidthout[sw][port], " ", end="")
            f_ptr.write(str(bandwidthout[sw][port]) + " ")
        print ()
        f_ptr.write("\n")
    print("-----------------------------------------------------")
    f_ptr.closed
    traffic_data = new_traffic_data
                        

def poll():
    global filename
    global name_index
    global bandwidthout
    global linkbandwidth
    global switchnum

    try:
    #get all switch dopi
        page = urllib.request.urlopen('http://localhost:8080/wm/core/controller/switches/json')
        line = page.read().decode("utf-8")

        collections = json.loads(line)

        num = 0

        for switch in collections:
            name_index[switch["dpid"]] = num
            num = num+1

        switchnum = num

    #need to store in dictionary for index to use with global 2D array
    
        bandwidthout = [[linkbandwidth for x in range(switchnumport)] for x in range(num)]

        page = urllib.request.urlopen('http://localhost:8080/wm/core/switch/all/flow/json')
        line = page.read().decode("utf-8")

        parsejson(line)
    except:
        f_ptr = open(traffic_file_name,'w',encoding='utf-8')
        f_ptr.write("0 \t 0\n")
        f_ptr.closed
    threading.Timer(0,poll).start()
    #poll()

poll()
