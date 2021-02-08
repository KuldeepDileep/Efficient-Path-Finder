import urllib.request               # Extensible library for opening urls
import json                         # is a lightweight data interchange format inspired
                                    # by JavaScript object literal syntax (although it is not a
                                    # strict subset of JavaScript [1])
                                    
import csv                          # for reading from comma separated files, we can even set
                                    # the delimeter accroding to our desire
                                    
from gmplot import gmplot           #A matplotlib-like interface to generate the HTML and
                                    #javascript to render all the data you’d like on top of Google Maps.

filename='Order.csv'                #It is the file containing names,address and capacity of the desired location where delivery is to be made. 
source_name="FAST"                  #The user has to define a source from where the delivery is to made to every other point.In this case FAST is our source.
source_address="22-G، Pakistan Employees Co-Operative Housing Society Block 6 PECHS, Karachi, Karachi City, Sindh" #This is exact source address obtained from google map
source_capacity=100                 #The user has to define a fixed specific capacity the vehicle can carry

##------------------------------Helper Functions(For Graphs)-----------------------------------##
def addNodes(G,nodes):
    for i in nodes:
        if i not in G.keys():
            G[i]=[]
    return G
def addEdges(G,edges,directed=False):
    for i in range(len(edges)):
        if directed==False:
            if len(edges[i])==3:
                G[edges[i][0]].append((edges[i][1],edges[i][2]))
                G[edges[i][1]].append((edges[i][0],edges[i][2]))
            else:
                G[edges[i][0]].append((edges[i][1],1))
                G[edges[i][1]].append((edges[i][0],1))
        else:
            if len(edges[i])==3:
                G[edges[i][0]].append((edges[i][1],edges[i][2]))
            else:
                G[edges[i][0]].append((edges[i][1],1))         
    return G
def listOfNodes(G):
    lst=[]
    for i in G.keys():
        lst.append(i)
    return lst
def listOfEdges(G):
    lst=[]
    for i in G.keys():
        for x,y in G[i]:
            s=()
            s=(i,x,y)
            lst.append(s)
    return lst
def getNeighbor(G,node):
    neighbours=[]
    for x in G[node]:
        neighbours.append(x[0])
    return neighbours
def Weight(G,U,V):
    edges=listOfEdges(G)
    for i,j,k in edges:
        if i==U and j==V:
            return k
##----------------------------------------------------------------------------------------##

def Djikstra(graph,SV): # The shortest path algorithm is defined here so that it could be used as
                        #a helper function later in our major efficient pathfinder algorithm 
    UV=listOfNodes(graph)
    V=[]
    SD=[]
    U=SV
    for i in UV:
        SD.append((None,i,float('inf')))
    for x in range(len(SD)):
        if U in SD[x]:
            SD[x]=(U,SD[x][1],0)
            break    
    while UV!=[]:
        lst=[]
        for i,j,k in SD:
            if j not in V:
                lst.append(k)
        minimum=min(lst)
        for i,j,k in SD:
            if minimum==k and j not in V:
                U=j
                break
        for i in range(len(getNeighbor(graph,U))):
            node=getNeighbor(graph,U)[i]
            if node not in V:
                for i in range(len(SD)):
                    if SD[i][1]==node:
                        change=i
                        prev=SD[i][2]                
                        break
        
                if prev>(minimum)+Weight(graph,U,node):
                    SD[change]=(U,SD[change][1],minimum+Weight(graph,U,node))
        V.append(UV.pop(UV.index(U)))
    for i in range(len(SD)-1):
        if SD[i][2]==0:
            SD.pop(i)
    return SD

def getShortestPath(graph,SV,to):   #This shortest path algorithm is used as a helper function
                                    #to provide us with the shortest path betweem two specific nodes.
                                    #This also uses Djikstra's Algorithm to compute the shortest path.
    UV=listOfNodes(graph)
    V=[]
    SD=[]
    U=SV
    for i in UV:
        SD.append((None,i,float('inf')))
    for x in range(len(SD)):
        if U in SD[x]:
            SD[x]=(U,SD[x][1],0)
            break    
    while UV!=[]:
        lst=[]
        for i,j,k in SD:
            if j not in V:
                lst.append(k)
        minimum=min(lst)
        for i,j,k in SD:
            if minimum==k and j not in V:
                U=j
                break
        for i in range(len(getNeighbor(graph,U))):
            node=getNeighbor(graph,U)[i]
            if node not in V:
                for i in range(len(SD)):
                    if SD[i][1]==node:
                        change=i
                        prev=SD[i][2]                
                        break
                if prev>minimum+Weight(graph,U,node):
                    SD[change]=(U,SD[change][1],minimum+Weight(graph,U,node))
        V.append(UV.pop(UV.index(U)))
    SD_final=[]
    start=""
    end=to
    while start!=SV:
        for x in SD:
            if x[1]==end:
                SD_final.append(x)
                end=x[0]
                start=x[1]
    for i in range(len(SD_final)):
        if SD_final[i][2]==0:
            SD_final.pop(i)

    return SD_final[::-1]

G={}
def sort(lst):                      # This is the insertion sort algorithm used for sorting
    for i in range(len(lst)):
        j=i
        while (j>0 and lst[j][2]<lst[j-1][2]):
            lst[j],lst[j-1]=lst[j-1],lst[j]
            j-=1
    return lst

def LoadData(filename):             # This function reads data from the file
                                    # containing information for delivery.
                                    # The file is in csv format.
    with open(filename,'r') as csvfile:
        data=csv.reader(csvfile,delimiter=',')
        datalist=[]
        for row in data:
            tup=()
            for index in range(len(row)):
                    tup+=(row[index],)
            datalist.append(tup)
    return datalist

def Extract(lst):                   #This function extracts the required data and forms different
                                    #usable dictionaries from the datalist loaded in the previous
                                    #function LOADDATA
    nodeswithamount={}
    nodeswithaddresses={}
    returnnodes={}
    for i in lst[1:]:
        nodeswithamount[i[0]]=int(i[2])
        nodeswithaddresses[i[0]]=i[1]
        returnnodes[i[1]]=i[0]
    return nodeswithamount,nodeswithaddresses,returnnodes

def weightAPI(origin,destination):  # This function calculates the distance between locations
                                    # using google's API (application program interface)
    endpoint= "https://maps.googleapis.com/maps/api/directions/json?"
    api_key='AIzaSyCxv8yNbHnfRckDFvjQiNRi5tvMjL1NvKE'       #API key is generated through a google account
    source=origin.replace(" ","+").replace(",","").replace("،","")
    dest=destination.replace(" ","+").replace(",","").replace("،","")
    nav_request= "origin="+source+'&destination='+dest+'&key='+api_key
    request=endpoint+nav_request
    response = urllib.request.urlopen(request).read()
    directions=json.loads(response)
    distance=directions['routes'][0]['legs'][0]['distance']['text']
    return distance[:len(distance)-3]


##def LatitudeandLongitude(filename):     #To get latitude and longitude of a given address.
##                                        #It is returning sometimes but sometimes gives error.
##    latlong={}
##    lst=LoadData(filename)
##    a,nodeswithaddresses,c=Extract(lst)
##    for i in nodeswithaddresses.keys():
##        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+nodeswithaddresses[i])
##        resp_json_payload = response.json()
##        latlong[i]=(resp_json_payload['results'][0]['geometry']['location']['lat'],resp_json_payload['results'][0]['geometry']['location']['lng'])
##        print(latlong[i])
##    return latlong


def GraphMaker(filename,source_name,source_address,source_capacity):#This function uses the extracted
                                                                    #information to make the graph
                                                                    #which will be used by our main
                                                                    #algorithm.
    lst=LoadData(filename)
    nodeswithamount,nodeswithaddresses,returnnodes=Extract(lst)
    AddressList=[source_address]+list(returnnodes.keys())
    Graph={}
    returnnodes[source_address]=source_name
    addNodes(Graph,[source_name])
    checklst=[]
    for i in AddressList:
        for j in AddressList:
            addNodes(Graph,[returnnodes[i],returnnodes[j]])
            if j!=i and ((i,j) and (j,i) not in checklst):
                checklst.append((i,j))
                weight=float(weightAPI(i,j))
                addEdges(Graph,[(returnnodes[i],returnnodes[j],weight)])
    return Graph,nodeswithamount
G,nodeswithamount=GraphMaker(filename,source_name,source_address,source_capacity)
nodeswithamount[source_name]=source_capacity

def pathfinder(G,source_name,source_capacity,nodeswithamount):  #This is the main function that returns
                                                                #the optimized path keeping in consideration
                                                                #the limited carrying capacity of the
                                                                #delivery vehicle.
        tobedelivered=[]                                    
        totaldist=0
        updatedsource=source_name
        capacity=source_capacity
        path=[]
        while len(tobedelivered)!=len(nodeswithamount): #stops when the delivery is complete.
                SD=Djikstra(G,updatedsource)            #shortest path
                SD=sort(SD)                             #closest delivery
                for i,j,k in SD:
                        if j not in tobedelivered and capacity!=0 and j!=source_name:
                                least=j
                                break
                        elif capacity==0:
                            least=source_name           #Returns to the start to refill
                            break
                        
                #4 different conditions that can occur so 4 conditions.
                #In each condition the delivery amount is updated and the cpacity is also monitored.
                #If the vehicle is out of capacity it returns to the source node to refill.
                #We are also storing the path that the vehicle follows in a list.
                        
                if least==source_name:
                        print(least)
                        print(source_name)
                        capacity= source_capacity       #REFILL
                        dist=getShortestPath(G,updatedsource,least) #shortest path to get between two points.
                        for i,j,k in dist:
                            path.append((i,j,Weight(G,i,j)))
                        totaldist+=dist[-1][2]
                        nodeswithamount[least]=0
                        updatedsource=least
                        
                elif least==updatedsource:
                        print(least)
                        print(updatedsource)
                        dist=getShortestPath(G,least,source_name)
                        for i,j,k in dist:
                            path.append((i,j,Weight(G,i,j)))
                        for i,j,k in dist:
                            if j==source_name:
                                capacity=source_capacity        #REFILL
                                break
                        totaldist+=dist[-1][2]
                        break
                        
                elif least!=source_name and capacity>=nodeswithamount[least]: 
                        dist=getShortestPath(G,updatedsource,least)
                        for i,j,k in dist:
                            path.append((i,j,Weight(G,i,j)))
                        for i,j,k in dist:
                            if j==source_name:
                                capacity=source_capacity    #REFILL
                                break
                        totaldist+=dist[-1][2]
                        capacity=capacity-nodeswithamount[least]
                        nodeswithamount[least]=0
                        if least!=source_name:
                            tobedelivered.append(least)
                        updatedsource=least
                        
                else:
                     dist=getShortestPath(G,updatedsource,least)
                     for i,j,k in dist:
                            path.append((i,j,Weight(G,i,j)))
                     for i,j,k in dist:
                            if j==source_name:
                                capacity=source_capacity    #REFILL
                                break 
                     var=nodeswithamount[least]-capacity
                     nodeswithamount[least]=var
                     totaldist+=dist[-1][2]
                     capacity=0
                     dist2=getShortestPath(G,source_name,least)
                     totaldist+=dist2[-1][2]
                     updatedsource=least
                
                print("PATH------->",path)              #Prints the path of the vehicle 
                print("LOAD------->",nodeswithamount)   #Updates the remaining load at each node
                                                #We have written in while loop so that at each and every step
                                                #it is visible.
        string=''+"(START)"+source_name+'---->'
        for x in range(1,len(path)):             
            if path[x][0]==source_name:
                string+=path[x][0]+'(REFILL)'+'---->'
            else:
                string+=path[x][0]+'---->'
        string+=source_name+'(END)'             #This string gives the complete journey of the vehicle
        print("PATH".center(80,' '))
        print(string)
        #GUI CODE
        
        #We have given manual inputs of longitude and latitude because the function sometimes returns the latitude and longitude from the address but sometimes does not.
        nodeswithlatlon={'Habib University':(24.9051,67.1380),'Aga Khan University':(24.8920,67.0748),'FAST':(24.8569,67.2643),'NED University':(24.9314,67.1125),'Karachi University':(24.9400,67.1209)}
        forpolygon=[]
        for x in path:
            forpolygon.append(nodeswithlatlon[x[1]])

        forpolygon=[nodeswithlatlon[source_name]]+forpolygon

        # Place map
        gmap = gmplot.GoogleMapPlotter(24.9008,67.1681, 13)

        # Polygon
        a,b = zip(*forpolygon)
        gmap.plot(a,b, 'cornflowerblue', edge_width=10)

        # Scatter points
        c,d = zip(*forpolygon)
        gmap.scatter(c,d, '#3B0B39', size=40, marker=False)

        # Marker
        e,f = 24.9008,67.1681
        gmap.marker(e,f, 'cornflowerblue')

        # Draw
        gmap.draw("MAP.html")

        return totaldist                    #gives the total minimum distance that the vehicel has to cover.
                
                
print('Minimum Distance to deliver to all the nodes:',pathfinder(G,source_name,source_capacity,nodeswithamount))                      
