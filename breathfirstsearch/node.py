class Node1():
    def __init__(self,state,parent=None,action=None,pathcost=1):
        self.name=(state[0]+1)*(state[1]+1)
        self.state=state
        self.parent=parent
        self.action=action
        self.pathcost=pathcost
    def chexk_thewayford(self,maze):
        posiibilitys=[]
        nodes_as_a_result=[]
        if (self.state[0]-1)<0:
            pass
        elif ((maze[self.state[0]-1][self.state[1]])!=0):
            posiibilitys.append("up")
            nodes_as_a_result.append(maze[self.state[0]-1][self.state[1]])
        if (self.state[1]+1)>maze.maxcolumn:
            pass
        elif ((maze[self.state[0]][self.state[1]+1])!=0):
            posiibilitys.append("right")
            nodes_as_a_result.append(maze[self.state[0]][self.state[1]+1])
        if (self.state[0]+1)>maze.maxrow:
            pass
        elif ((maze[self.state[0]+1][self.state[1]])!=0):
            posiibilitys.append("down")
            nodes_as_a_result.append(maze[self.state[0]+1][self.state[1]])
        if (self.state[1]-1)<0:
            pass
        elif ((maze[self.state[0]][self.state[1]-1])!=0):
            posiibilitys.append("left")
            nodes_as_a_result.append(maze[self.state[0]][self.state[1]-1])
        return posiibilitys,nodes_as_a_result
        
class Maze():
    def __init__(self,x_dimension_rows,y_dimension_columns):
        self.maxrow=x_dimension_rows
        self.maxcolumn=y_dimension_columns
        self.maze=[[0 for i in range(y_dimension_columns)] for i in range(x_dimension_rows)]
    def createurcustommaze(self,coords):#point is the index
        for point in coords:
            self.maze[point[0]][point[1]]=Node1(state=point)
           