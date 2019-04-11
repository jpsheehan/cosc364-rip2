import configparser

def read_config_file(file):
    config = configparser.ConfigParser()
    config.read_file(file)
    router = {}
    routerId = (config.get('DEFAULT', 'router-id'))
    inputPorts = (config.get('DEFAULT', 'input-ports'))
    outputPorts = (config.get('DEFAULT', 'output-ports'))
    

    router["routerId"] = check_router_id(routerId)
    
    router["inputPorts"] = check_input_ports(inputPorts)
    
    router["outputPorts"] = check_output_ports(router)
    
    print(router)
    
def check_router_id(routerId):
    try:
        routerId = int(routerId)
    except:
        raise TypeError("RouterID must be an integer")
    if (routerId > 64000 or routerId < 1):
        raise ValueError("RouterID must be between 1 and 64000")
    return routerId
    
    
def check_input_ports(inputPorts):
    try:
        inputPorts = [int(port.strip()) for port in inputPorts.split(',')]
    except:
        raise TypeError("Input ports should be comma seperated ints")
    for port in inputPorts:
        if (port > 64000 or port < 1024):
            raise ValueError("Port should be between 1024 and 64000")
    if len(inputPorts) != len(set(inputPorts)):
        raise ValueError("Ports should be unique")
    return inputPorts
        

def check_output_ports(outputPorts):
    pass
                        


def open_config_file(filePath):
    file = open(filePath, 'r')
    if file.mode == 'r':
        read_config_file(file)
    else:
        print("Error opening file")
    return