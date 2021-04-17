import krpc
import numpy as np
import pygame


RENDER_NETWORK = True

def tanh(x):
    return np.tanh(x)

class Agent:
    def __init__(self, network_size, network_weights):
        self.network_size = network_size
        count = 0
        matrices = []
        for i,_ in enumerate(network_size):
            if i >= len(network_size) -1:
                continue
            matrices.append(np.array(network_weights[count:count+network_size[i+1]*network_size[i]]).reshape((network_size[i+1],network_size[i])))
            count+=network_size[i+1]*network_size[i]
        self.matrices = matrices
        self.activate = np.vectorize(tanh)
        
    def calculate_output(self, input):
        matrix = np.matrix(input).transpose()
        for mat in self.matrices:
            matrix = self.activate(mat @ matrix)
        # flatten matrix to 1D list
        return  matrix.tolist()
    def calculate_node_values(self, input):
        matrix = np.matrix(input).transpose()
        node_data = []
        node_data.append(matrix.tolist())
        for mat in self.matrices:
            matrix = self.activate(mat @ matrix)
            # flatten matrix to 1D list
            node_data.append(matrix.tolist())
      
        return node_data
        
    def to_array(self):
        return [np.asarray(i).tolist() for i in self.matrices]
    def to_matrix(self, arr):
        self.matrices = [np.matrix(i) for i in arr]


def load_network():
    file = open("nn.txt", "r")
    network_size = [int(i) for i in file.readline().replace("\n", "").split(",")]
    
    network_weights = [float(i) for i in file.readline().replace("\n", "").split(",")]
        
    agent = Agent(network_size, network_weights)
   
    file.close()
    
    return (agent,network_weights)

def reset_trial(connection):
    connection.space_center.load("ai_500m")

def get_inputs(connection):
    
    inputs = [0.0]*8
    
    # get current rocket
    vessel = connection.space_center.active_vessel
    
    flight_info = vessel.flight()
    ref_frame = connection.space_center.ReferenceFrame.create_hybrid(
    position=vessel.orbit.body.reference_frame,
    rotation=vessel.surface_reference_frame)
    
    inputs[0], inputs[1], inputs[2], inputs[3] = (1.0,1.0,1.0,1.0) #flight_info.rotation
    
    inputs[4] = (flight_info.surface_altitude-20)/500.0 
    
    speed = vessel.flight(ref_frame).speed
    horizontal_speed = vessel.flight(ref_frame).horizontal_speed
    y_vel, x_vel, z_vel = vessel.flight(ref_frame).velocity
    vertical_speed = vessel.flight(ref_frame).vertical_speed * y_vel / np.abs(y_vel)
    #print(speed,horizontal_speed,vertical_speed)
    
    inputs[5] = horizontal_speed/100;
    inputs[6] = vertical_speed/100;
    inputs[7] = speed/100;

    #print(inputs)
    return inputs
def get_color(weight):
    weight = max(-1,min(1,weight))
    color = (max(0,int(weight*255)),0,max(0,int(-weight*255)))
    return color

def render_network(agent, screen, inputs, weight_render, render_weights, network_weights):
    network_size = agent.network_size
    NODE_DIST = 50
    NODE_SIZE = 10
    X_OFFSET = 100
    Y_OFFSET = 50
    
    # render weights
    if(render_weights):
        count = 0
        for i, layer in enumerate(network_size):
            if i==len(network_size)-1:
                break
            for row in range(network_size[i+1]):
                for col in range(network_size[i]):
                    index = row*network_size[i+1] + col + count
                    weight = network_weights[index]
                    v1_dist = (500-Y_OFFSET)//layer
                    node1_x = X_OFFSET+(i*125)
                    node1_y = Y_OFFSET+(col*v1_dist)
                    v2_dist = (500-Y_OFFSET)//network_size[i+1]
                    node2_x = X_OFFSET+((i+1)*125)
                    node2_y = Y_OFFSET+(row*v2_dist)
                    color = get_color(weight)
                    pygame.draw.line(weight_render, color=color,start_pos=(node1_x,node1_y), end_pos=(node2_x,node2_y))
            count += network_size[i+1]*network_size[i]
    # draw weights to screen
    screen.blit(weight_render, (0,0))
    
    network_data = agent.calculate_node_values(inputs)
    
    # draw nodes
    for i, layer in enumerate(network_size):
        v_dist = (500-Y_OFFSET)//layer
        node_data = network_data[i]
        for node in range(layer):
            val = node_data[node][0]
            color = get_color(val)
            pygame.draw.circle(screen,radius=NODE_SIZE, center=(X_OFFSET+(i*125),Y_OFFSET+(node*v_dist)), color=color)
    

def main():
    
    agent,network_weights = load_network()
    print("Agent loaded.")
    
    print("Connecting to server...")
    # connect to server
    connection = krpc.connect(
        name='yolo',
        address='localhost',
        rpc_port=50000, stream_port=50001) #Default ports are 50000, 50001
    print("Successfully connected to server.")

    print("Loading quick save...")
    reset_trial(connection)
    print("Loaded quick save")
    
    pygame.init()
    
    screen = pygame.display.set_mode((600,500))
    weight_render = pygame.Surface((600,500))
    weight_render.fill((100,100,100))
    render_weights = True
    
    running = True
    cycle_count = 0
    while running:
        cycle_count+=1;
        # get inputs to NN
        inputs = get_inputs(connection)
        
        # Calculate output of NN
        outputs = agent.calculate_output(inputs)
        
        # Use the output to control the agent
        control = connection.space_center.active_vessel.control
        control.throttle = (outputs[0][0]+1)/2
        #print(outputs[0][0],(outputs[0][0]+1)/2)

        if str(connection.space_center.active_vessel.situation) == "VesselSituation.landed":
            # reset throttle if the lander has touched the ground
            control.throttle = 0.0
            print("Landed")
            running = False
        # Every Kth cycle, display network
        if RENDER_NETWORK and cycle_count%10==0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((255,255,255))
            render_network(agent,screen, inputs, weight_render,render_weights,network_weights)
            render_weights = False
            pygame.display.update()
    connection.close()
if __name__ == "__main__":
    main()