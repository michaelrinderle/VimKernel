"      __ _/| _/. _  ._/__ /
"   _\/_// /_///_// / /_|/
"             _/
"   sof digital 2021
"   written by michael rinderle <michael@sofdigital.net>

"   mit license
"   Permission is hereby granted, free of charge, to any person obtaining a copy
"   of this software and associated documentation files (the "Software"), to deal
"   in the Software without restriction, including without limitation the rights
"   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
"   copies of the Software, and to permit persons to whom the Software is
"   furnished to do so, subject to the following conditions:
"   The above copyright notice and this permission notice shall be included in all
"   copies or substantial portions of the Software.
"   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
"   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
"   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
"   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
"   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
"   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
"   SOFTWARE.

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

augroup vim-kernel-autocommands
    autocmd!
    autocmd VimEnter,WinEnter,BufEnter,FileChangedShellPost,BufWritePost  * call kernel#RunCheckPatchScript()
    autocmd CursorMoved,CursorMovedI * call kernel#LoadPatchCheck() 
augroup END

function! kernel#LoadPyModules()
python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import kernel
kernel.set_vim_settings()
EOF
endfunction

function! kernel#RunCheckPatchScript()
python3 << EOF
kernel.run_check_patch_script()
EOF
endfunction

function! kernel#LoadPatchCheck()
python3 << EOF
kernel.load_patch_violation_hint()
EOF
endfunction