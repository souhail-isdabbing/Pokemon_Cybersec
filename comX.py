from attack import command_exec
import pickle
def check_command_exec(simple_command:str,result,index):
    web_output=command_exec(simple_command).split('\n')[8:]
    response='\n'.join(web_output)
    result[index]=response
