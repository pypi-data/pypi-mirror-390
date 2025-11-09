import threading
import subprocess
import time
import sys
from cli.utils.singleton import singleton


@singleton
class Shell:
    @staticmethod
    def run(cmd, show_loading=False):
        def stream_output(pipe, callback):
            for line in iter(pipe.readline, ''):
                callback(line)
            pipe.close()

        def print_end(line):
            print(line, end='')

        def loading_animation():
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            while not process_done.is_set():
                for char in spinner:
                    sys.stdout.write(f'\r{char} Loading, please wait ...')
                    time.sleep(0.1)
                    sys.stdout.flush()
            sys.stdout.write('\r' + ' ' * 20 + '\r')
            sys.stdout.flush()

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        process_done = threading.Event()

        stdout_thread = threading.Thread(
            target=stream_output, args=(process.stdout, print_end))
        stderr_thread = threading.Thread(
            target=stream_output, args=(process.stderr, print_end))

        stdout_thread.start()
        stderr_thread.start()

        if show_loading:
            loading_thread = threading.Thread(target=loading_animation)
            loading_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        process_done.set()
        if show_loading:
            loading_thread.join()

        return_code = process.wait()
        return return_code
