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
    
    return agent

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

def main():
    
    agent = load_network()
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
    screen = pygame.display.set_mode((500,500))
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
        if cycle_count%10==0:
            
        
        
    connection.close()
if __name__ == "__main__":
    main()