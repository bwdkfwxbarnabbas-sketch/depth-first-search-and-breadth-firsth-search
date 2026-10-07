from . import fronteir,node
def run():
    goalstate=[4,4]
    initstate=[0,0]
    Maze=node.Maze(5,5)
    coords=[[0,0],[0,1],[0,2],[0,3],[0,4],[1,2],[2,0],[2,1],[2,2],[2,3],[2,4],[3,2],[3,3],[3,4],[4,2],[4,4]]
    Maze.createurcustommaze(coords)
    initail_state_fronteir=fronteir.QeueFronteir()
    initail_state_fronteir.storage.append(Maze[0][0])
    no_trys=0
    while True:
        if not initail_state_fronteir.storage:
            print("no solution")
            break
        else:
            node_to_consider=initail_state_fronteir.removenode()
            if node_to_consider.state==goalstate:
                print(f"here is the solution:{node_to_consider}")
                break
            else:
                _,resultingnodes=node_to_consider.chexk_thewayford(Maze)
                #filtering
                for i in resultingnodes:
                    for j in initail_state_fronteir.storage:
                        if j.name==i.name:
                            resultingnodes.remove(i)
                    for jj in initail_state_fronteir.exploredset:
                        if jj.name==i.name:
                            resultingnodes.remove(i)
                #filtering
                initail_state_fronteir.addnode(resultingnodes)
        no_trys+=1
    return no_trys,initail_state_fronteir.exploredset,Maze,initstate,goalstate                    
