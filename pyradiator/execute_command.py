import subprocess


def _execute_command(function, *args, **kwargs):
    try:
        process = function(*args, **kwargs)
    except OSError:
        pass
    else:
        output = process.communicate()[0].decode()
        if output:
            return output.splitlines()
    return []


def execute_simple_command(command):
    def _popen_call(command):
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process

    return _execute_command(_popen_call, command)


def execute_compound_command(command_1, command_2):
    def _popen_calls(command_1, command_2):
        process_1 = subprocess.Popen(command_1,
                                     stdout=subprocess.PIPE)
        process_2 = subprocess.Popen(command_2,
                                     stdin=process_1.stdout,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        process_1.stdout.close()
        return process_2

    return _execute_command(_popen_calls, command_1, command_2)
