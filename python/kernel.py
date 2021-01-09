#      __ _/| _/. _  ._/__ /
#   _\/_// /_///_// / /_|/
#             _/
#   sof digital 2021
#   written by michael rinderle <michael@sofdigital.net>

#   mit license
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import os
import subprocess
import sys
import vim

class PatchViolation():
    def __init__(self):
        self.type = ''
        self.warning = ''
        self.line = ''
        self.snippet = ''

patch_violations = list()
DEBUG = True

def set_vim_settings():
    # set column and kernel error gutter sign
    vim.command(":highlight SignColumn guibg=darkgrey")
    vim.command(":sign define kernel text=k")
    # set tab spaces for kernel styling
    # kernel.org/doc/html/v4.10/process/coding-style.html
    vim.command(":set expandtab!")
    vim.command(":set softtabstop=8")
    vim.command(":set tabstop=8")
    vim.command(":set shiftwidth=8")
    vim.command(":retab")

def linux_kernel_git_repo_check():
    try:
        # determine if in linux git repository
        # only requirement is git, which user should have already
        linux_tree = "origin\thttps://github.com/torvalds/linux.git (fetch)\n"
        proc = subprocess.Popen(["git remote -v"], stdout=subprocess.PIPE, shell=True)
        result = proc.stdout.readlines()
        if linux_tree == result[0].decode():
            return True
        return False
    except Exception as e:
        display_explicit_exception(e)

def get_check_patch_script():
    # get repo base and append checkpatch.pl script location
    root = os.getcwd().rsplit('linux', 1)[0]
    return os.path.join(root, "linux/scripts/checkpatch.pl")

def run_check_patch_script():
    try:
        # abort if user isnt working in linux kernel git repo
        if not linux_kernel_git_repo_check():
            # aborting running checkpatch.pl
            return
        # getting current file name of buffer 
        buffer_filename = vim.eval("""expand("%p")""")
        if(buffer_filename != ''):
            # run checkpatch.pl in subprocess against current patch file 
            cmd = "perl {} -f {}".format(get_check_patch_script(), str(buffer_filename))
            proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
            # parse subprocess stdout result
            parse_script_violations(proc.stdout.readlines())
            proc.wait()
    except Exception as e:
        print(e)

def parse_script_violations(output):
    try:
        # declare global patch violations
        global patch_violations
        patch_violations = list()
        # declare locals 
        temp_violation = PatchViolation()
        header_parsed = False
        line_parsed = False
        # clear old kernel violation signs in gutter
        clear_gutter()
        # iterate over our subprocess output 
        # parse into a list of patch violations
        for line in output:
            line = line.decode('utf-8')
            if line.startswith("total:"):
                break
            if not header_parsed:
                temp_violation.type = str(line.split(":")[0])
                temp_violation.warning = str(line.split(":")[1])
                header_parsed = True
            elif not line_parsed:
                temp_violation.line = line.split(":")[0].replace('#', '')
                line_parsed = True
                place_sign(temp_violation.line)
            else:
                if line != '\n':
                    temp_violation.snippet += line
                else:
                    patch_violations.append(temp_violation)
                    temp_violation = PatchViolation()
                    header_parsed = False
                    line_parsed = False
    except Exception as e:
        display_explicit_exception(e)

def load_patch_violation_hint():       
    try:
        # declare global patch violations
        global patch_violations
        # determine our cursor location
        row, col = vim.current.window.cursor
        print("") # clearing status line
        # look for a violation on line 
        for violation in patch_violations:
            if row == int(violation.line):
                # display violation hint
                display_status_bar_hint(violation)
                break
    except Exception as e:
        display_explicit_exception(e)
    
def place_sign(line):
    # place kernel violation sign in the gutter 
    buffer_filename = vim.eval("""expand("%p")""")
    vim.command(":sign place 1 line={0} name=kernel file={1}".format(line, buffer_filename))

def clear_gutter():
    # clear all kernel violation signs in the current buffer's gutter
    buffer_filename = vim.eval("""expand("%p")""")
    vim.command(":sign unplace * file={0}".format(buffer_filename))

def display_status_bar_hint(patch_violation):
    # create our violation hint and print to status bar
    content = "{0}:{1}".format(patch_violation.type, patch_violation.warning
        .replace('\n', '').encode('unicode-escape').decode())
    print(content)
    
def display_explicit_exception(e):
    global debug
    if DEBUG == False:
        print(e)
    else:
        # extra explicit exception for debugging
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)