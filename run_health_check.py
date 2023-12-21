import sys
import multiprocessing

def exitProgram():
        exit()

def getInputFile():
    num_args = len(sys.argv)
    if num_args != 2:
        print("Invalid Format!\nPlease provide filename in the format - python run_health_check.py <path to the file>\n")
        exitProgram()

    filename = sys.argv[1]
    
    try:
        file_descriptor = open(filename, "r")
        return file_descriptor
    except FileNotFoundError:
        print("File Does not exist!\nPlease provide path to a valid file")
        exitProgram()

# def testEndpoint():
#      """
#      Function to test a endpoint
#      Args:
#      @
#      """

def main():
    file_descriptor = getInputFile()
    # p1 = multiprocessing.Process(target=testEndpoint, args=(, )) 

if __name__ == "__main__":
    main()