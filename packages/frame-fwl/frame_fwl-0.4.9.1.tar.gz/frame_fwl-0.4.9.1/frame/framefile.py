import sys
import os
import subprocess
from .frame_core import *
from .frame_core import _framecore_version_


def help():
    help_text = '''
=== FrameFile Starter HELP ===
Args -

    GROUP start:
        stjson [name] - start json framefile
        stpick [name] - start pickle framefile
        GROUP_ARGS:
            -s - turn safemode
            NOTE: without safemode file can show errors
        GROUP_FORMAT:
            command [name] -[safemode]

    GROUP help:
        getcode_s / getcode [name] - get code of frame (safe/unsafe)
        compile_s / compile [name] [out_name] - compile framefile to .py file (safe/unsafe)
        is_safe_s / is_safe [name] - check safemode for framefile (safe/unsafe)
        NOTE: without safemode file can show errors
        NOTE: safe/unsafe - load mode
        GROUP_ARGS:
            -json - json format
            -pick - pickle format
        GROUP_FORMAT:
            command [args] -[format]
    
    GROUP other:
        -v - show frame version
        -h - show this

==============================
'''
    print(help_text)

def getframe(filename, format, safe):
    return Frame(safemode=safe).load(filename, format, safe)

def getcode(filename, format, safe):
    frame = getframe(filename, format, safe)
    return frame.compile()

def print_code(args: list, ln: int, safe: bool = False):
    if ln < 1:
        raise KeyError("Filename is required")
    filename = args[0]
    format_type = 'pickle' if ln > 1 and args[1] == '-pick' else 'json'
    print(getcode(filename, format_type, safe))

def compile_code(args: list, ln: int, safe: bool = False):
    if ln < 1:
        raise KeyError("Filename is required")
    filename = args[0]
    output_name = args[1] if ln > 1 else f'bin_framefile_{filename}.py'
    format_type = 'pickle' if ln > 2 and args[2] == '-pick' else 'json'
    code = getcode(filename, format_type, safe)
    with open(output_name, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"Compiled to: {output_name}")

def start(args: list, ln: int, file_type: str = 'json'):
    if ln < 1:
        raise KeyError("Filename is required")
    filename = args[0]
    safe_mode = ln > 1 and args[1] == '-s'
    output_name = f'_tmp_bin_framefile_{filename}.py'
    compile_code([filename, output_name, f'-{file_type}'], 3, safe_mode)
    try:
        subprocess.run([sys.executable, output_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running compiled file: \n{e}")
    finally:
        if os.path.exists(output_name):
            os.remove(output_name)
        

def is_safe(args: list, ln: int, safe: bool):
    if ln < 1:
        raise KeyError("Filename is required")
    filename = args[0]
    format_type = 'pickle' if ln > 1 and args[1] == '-pick' else 'json'
    frame = getframe(filename, format_type, safe)
    return frame._get_safemode()




def main():
    if len(sys.argv) < 2:
        print('Unknown Command. Type -h for help.')
        return
    command = sys.argv[1]
    args = sys.argv[2:]
    args_count = len(args)
    command_handlers = {
        'stjson': lambda: start(args, args_count, 'json') if args_count >= 1 else FileNotFoundError("Filename required"),
        'stpick': lambda: start(args, args_count, 'pick') if args_count >= 1 else FileNotFoundError("Filename required"),
        'getcode': lambda: print_code(args, args_count, False) if args_count >= 1 else FileNotFoundError("Filename required"),
        'getcode_s': lambda: print_code(args, args_count, True) if args_count >= 1 else FileNotFoundError("Filename required"),
        'compile': lambda: compile_code(args, args_count, False) if args_count >= 1 else FileNotFoundError("Filename required"),
        'compile_s': lambda: compile_code(args, args_count, True) if args_count >= 1 else FileNotFoundError("Filename required"),
        'is_safe': lambda: print('Safemode:', is_safe(args, args_count, False)) if args_count >= 1 else FileNotFoundError("Filename required"),
        'is_safe_s': lambda: print('Safemode:', is_safe(args, args_count, True)) if args_count >= 1 else FileNotFoundError("Filename required"),
        '-h': lambda: help(),
        '-v': lambda: print(f'Frames Concept v{_framecore_version_}'),
    }
    command = command.lower()
    if command in command_handlers:
        try:
            command_handlers[command]()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print('Unknown Command. Type -h for help.')

if __name__ == '__main__':
    main()