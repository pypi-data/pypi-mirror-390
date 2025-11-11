import configparser
import http.client
import sys
import os
import json
import socket
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from typing import List, Dict, Union, Optional, Callable
from io import StringIO
from functools import wraps
import subprocess
from typing import Optional

def check_server_available(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.config.is_server_available():
            return json.dumps({
                "status": "error",
                "message": "Server unavailable"
            }, ensure_ascii=False)
        return func(self, *args, **kwargs)
    return wrapper

def validate_hex_address(address: Union[int, str]) -> Optional[str]:
    if isinstance(address, int):
        return hex(address)

    addr_str = str(address).strip()
    if not addr_str:
        return None

    if addr_str.startswith(('0x', '0X')):
        try:
            int(addr_str, 16)
            return addr_str
        except ValueError:
            return None
    try:
        int(addr_str, 10)
        return addr_str
    except ValueError:
        return None

class Config:
    def __init__(self, address: str = "127.0.0.1", port: int = 8000):
        self.address = address
        self.port = port
        self.ida_server_addr = f"http://{address}:{port}"
        self.ida_path = None
        self.ida_http = "http://moles.lyshark.com/"
        self.ida_engine = "IDAMoles.dll"
        self.timeout = 5

    def is_server_available(self, timeout: Optional[int] = None) -> bool:
        timeout = timeout or self.timeout
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((self.address, self.port))
                return result == 0
        except socket.error as e:
            print(f"WARNING: Server check failed: {str(e)}")
            return False

    def set_ida_path(self, ida_path: str) -> str:
        if not sys.platform.startswith("win32"):
            error_msg = "Only supports setting IDA path on Windows system"
            print(f"ERROR: {error_msg}")
            return ""

        ida_path = ida_path.strip("'\" ").strip()
        if not ida_path:
            print("ERROR: Empty path provided")
            return ""

        try:
            expanded_path = os.path.expandvars(ida_path)
            abs_path = os.path.abspath(expanded_path)
            normalized_path = os.path.normpath(abs_path)
        except Exception as e:
            print(f"ERROR: Invalid path format: {ida_path} (reason: {str(e)})")
            return ""

        if os.path.basename(normalized_path).lower() == "plugins":
            normalized_path = os.path.dirname(normalized_path)
            print(f"WARNING: Path contains 'plugins', automatically adjusted to: {normalized_path}")

        if not os.path.exists(normalized_path):
            error_msg = f"The path does not exist: {normalized_path} (original input: {ida_path})"
            print(f"ERROR: {error_msg}")
            return ""

        if not os.path.isdir(normalized_path):
            error_msg = f"Not a valid directory: {normalized_path} (original input: {ida_path})"
            print(f"ERROR: {error_msg}")
            return ""

        if not os.access(normalized_path, os.R_OK):
            error_msg = f"No read permission for path: {normalized_path}"
            print(f"ERROR: {error_msg}")
            return ""

        ida_exe_path = os.path.join(normalized_path, "ida.exe")
        if not os.path.exists(ida_exe_path):
            error_msg = f"IDA executable 'ida.exe' not found in root directory: {normalized_path}"
            print(f"ERROR: {error_msg}")
            return ""

        if not os.path.isfile(ida_exe_path):
            error_msg = f"'{ida_exe_path}' is not a valid file (expected ida.exe)"
            print(f"ERROR: {error_msg}")
            return ""

        self.ida_path = os.path.join(normalized_path, "plugins")
        print(f"The IDA path has been set to: {self.ida_path} (original input: {ida_path})")
        return self.ida_path

    def install_moles(self) -> str:
        if self.ida_path is None:
            print("WARNING: Please first execute set_ida_path to set the IDA directory")
            return ""

        try:
            target_path = os.path.join(self.ida_path, self.ida_engine)
            save_dir = os.path.dirname(target_path)

            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
                print(f"Created directory: {save_dir}")

            with urllib.request.urlopen(self.ida_http + self.ida_engine, timeout=self.timeout) as response:
                file_size = int(response.headers.get('Content-Length', 0))
                downloaded_size = 0
                chunk_size = 8192

                with open(target_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if file_size > 0:
                            progress = (downloaded_size / file_size) * 100
                            print(f"\rDownload progress: {progress:.2f}%", end='')

            print(f"\n[*] Install Moles Success")
            return

        except HTTPError as e:
            print(f"ERROR: HTTP Error: Server returns status code {e.code}")
        except URLError as e:
            print(f"ERROR: URL error: unable to connect to server - {e.reason}")
        except TimeoutError:
            print("ERROR: Connection to server or data read timeout")
        except IOError as e:
            print(f"ERROR: File write error: unable to write to {target_path} - {e}")
        except PermissionError:
            print(f"ERROR: Permission denied: Unable to write to {target_path}. Please run as administrator.")
        except Exception as e:
            print(f"ERROR: Unknown error occurred: {e}")
        return ""

    def get_version(self) -> Optional[str]:
        try:
            req = urllib.request.Request(url=f"{self.ida_http}version.ini")
            with urllib.request.urlopen(req, timeout=15) as response:
                try:
                    ini_content = response.read().decode("utf-8")
                except UnicodeDecodeError:
                    ini_content = response.read().decode("gbk")

                config = configparser.ConfigParser()
                config.read_file(StringIO(ini_content))

                if not config.has_section("setting") or not config.has_option("setting", "version"):
                    return None

                return config.get("setting", "version").strip()

        except (HTTPError, URLError, configparser.Error, TimeoutError, Exception) as e:
            print(f"WARNING: Failed to get version: {str(e)}")
            return None

    def open_ida_with_program(self, program_path: str, auto_mode: bool = False, force_new: bool = False) -> bool:
        """
        启动IDA并加载指定程序

        Args:
            program_path: 要加载的目标程序路径（如.exe、.dll等）
            auto_mode: 是否以自动模式启动（-A参数，不弹出交互对话框）
            force_new: 是否强制创建新数据库（-c参数，覆盖旧数据库）

        Returns:
            启动成功返回True，失败返回False
        """
        # 1. 检查IDA路径是否已设置且有效
        if not self.ida_path:
            print("ERROR: Please call set_ida_path to set the IDA path first")
            return False

        # 提取IDA根目录（self.ida_path是plugins目录，上层为根目录）
        ida_root = os.path.dirname(self.ida_path)
        ida_exe_path = os.path.join(ida_root, "ida.exe")
        if not os.path.exists(ida_exe_path) or not os.path.isfile(ida_exe_path):
            print(f"ERROR: ida.exe not found, path:{ida_exe_path}")
            return False

        # 2. 检查目标程序路径是否有效
        program_path = os.path.abspath(program_path)
        if not os.path.exists(program_path) or not os.path.isfile(program_path):
            print(f"ERROR: The target program does not exist or is not a file. Path:{program_path}")
            return False

        # 3. 构造IDA命令行参数
        cmd = [ida_exe_path]
        if auto_mode:
            cmd.append("-A")  # 自动模式（无交互）
        if force_new:
            cmd.append("-c")  # 强制创建新数据库
        cmd.append(program_path)  # 目标程序路径

        # 4. 启动IDA进程
        try:
            # 启动进程（不等待IDA关闭，若需等待可改用subprocess.call）
            subprocess.Popen(cmd, shell=False)
            print(f"SUCCESS: IDA has been started and the program has been loaded:{program_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to start IDA:{str(e)}")
            return False

class BaseHttpClient:
    """HTTP客户端基类，提供基础的HTTP请求功能"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        parsed_url = urlparse(self.config.ida_server_addr)
        self.address = parsed_url.hostname
        self.port = parsed_url.port
        self.scheme = parsed_url.scheme
        self.path = parsed_url.path or '/'
        self.verify_ssl = True  # 默认验证SSL证书

    def custom_post(self,
                    json_data: Optional[Dict] = None,
                    headers: Optional[Dict] = None,
                    timeout: Optional[int] = None) -> str:
        """
        发送POST请求

        Args:
            json_data: 要发送的JSON数据
            headers: 请求头
            timeout: 超时时间(秒)

        Returns:
            服务器响应的JSON字符串，出错时返回包含错误信息的JSON
        """
        if not headers:
            headers = {}
        if json_data and 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        body = json.dumps(json_data).encode('utf-8') if json_data else None
        timeout = timeout or self.config.timeout

        try:
            if self.scheme == 'https':
                import ssl
                context = ssl._create_unverified_context() if not self.verify_ssl else None
                conn = http.client.HTTPSConnection(self.address, self.port, timeout=timeout, context=context)
            else:
                conn = http.client.HTTPConnection(self.address, self.port, timeout=timeout)

            conn.request("POST", self.path, body=body, headers=headers)
            response = conn.getresponse()
            response_text = response.read().decode('utf-8')
            conn.close()
            return response_text

        except socket.timeout:
            return json.dumps({
                "status": "error",
                "message": "Request timed out"
            }, ensure_ascii=False)
        except ConnectionRefusedError:
            return json.dumps({
                "status": "error",
                "message": "Connection refused by server"
            }, ensure_ascii=False)
        except json.JSONDecodeError:
            return json.dumps({
                "status": "error",
                "message": "Failed to serialize request data"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Request failed: {str(e)}"
            }, ensure_ascii=False)


class Debugger(BaseHttpClient):
    """调试器相关接口"""

    @check_server_available
    def get_basic_info(self) -> str:
        """获取基本信息"""
        request_data = {
            "class": "Debugger",
            "interface": "GetBasicInfo",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_image_info(self) -> str:
        """获取镜像信息"""
        request_data = {
            "class": "Debugger",
            "interface": "GetImageInfo",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_register(self, reg: str) -> str:
        """
        获取寄存器值

        Args:
            reg: 寄存器名称(如"eax"、"rsp")

        Returns:
            包含寄存器值的JSON响应
        """
        if not reg.strip():
            return json.dumps({
                "status": "error",
                "message": "Register name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Debugger",
            "interface": "GetRegVal",
            "params": [reg.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def set_register(self, reg: str, value: Union[int, str]) -> str:
        """设置寄存器值"""
        if not reg.strip():
            return json.dumps({
                "status": "error",
                "message": "Register name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Debugger",
            "interface": "SetRegVal",
            "params": [reg.strip(), str(value)]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def step_into(self) -> str:
        """单步步入"""
        request_data = {
            "class": "Debugger",
            "interface": "StepInto",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def step_over(self) -> str:
        """单步步过"""
        request_data = {
            "class": "Debugger",
            "interface": "StepOver",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def step_until_ret(self) -> str:
        """步直到返回"""
        request_data = {
            "class": "Debugger",
            "interface": "StepUntilRet",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_sp_val(self) -> str:
        """获取栈指针值"""
        rsp_data = {
            "class": "Debugger",
            "interface": "GetRegVal",
            "params": ["rsp"]
        }
        rsp_response = self.custom_post(json_data=rsp_data)

        try:
            if json.loads(rsp_response).get("status") == "success":
                return rsp_response
        except json.JSONDecodeError:
            pass

        esp_data = {
            "class": "Debugger",
            "interface": "GetRegVal",
            "params": ["esp"]
        }
        return self.custom_post(json_data=esp_data)

    @check_server_available
    def get_process_state(self) -> str:
        """获取进程状态"""
        request_data = {
            "class": "Debugger",
            "interface": "GetProcessState",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def set_breakpoint(self, address: Union[int, str]) -> str:
        """
        设置断点

        Args:
            address: 断点地址(支持十进制整数或十六进制字符串)
        """
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Debugger",
            "interface": "SetBreakPoint",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)


class Function(BaseHttpClient):
    """函数相关接口"""

    @check_server_available
    def get_functions(self) -> str:
        """获取所有函数"""
        request_data = {
            "class": "Function",
            "interface": "GetFunction",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_info(self, func_start_addr: Union[int, str]) -> str:
        """获取函数信息"""
        addr_str = validate_hex_address(func_start_addr)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Function",
            "interface": "GetFunctionInfo",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_import_functions(self) -> str:
        """获取导入函数"""
        request_data = {
            "class": "Function",
            "interface": "GetImportFunctions",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_count(self) -> str:
        """获取函数数量"""
        request_data = {
            "class": "Function",
            "interface": "GetFunctionCount",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_by_addr(self, func_start_addr: Union[int, str]) -> str:
        """通过地址获取函数"""
        addr_str = validate_hex_address(func_start_addr)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Function",
            "interface": "GetFunctionByAddr",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_by_name(self, func_name: str) -> str:
        """通过名称获取函数"""
        if not func_name.strip():
            return json.dumps({
                "status": "error",
                "message": "Function name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Function",
            "interface": "GetFunctionByName",
            "params": [func_name.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def find_function_by_name(self, keyword: str) -> str:
        """通过关键字搜索函数"""
        if not keyword.strip():
            return json.dumps({
                "status": "error",
                "message": "The search keyword cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Function",
            "interface": "FindFunctionByName",
            "params": [keyword.strip()]
        }
        return self.custom_post(json_data=request_data)


class Segment(BaseHttpClient):
    """段相关接口"""

    @check_server_available
    def get_segments(self) -> str:
        """获取所有段"""
        request_data = {
            "class": "Segment",
            "interface": "GetSegment",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_segment_count(self) -> str:
        """获取段数量"""
        request_data = {
            "class": "Segment",
            "interface": "GetSegmentCount",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_segment_from_addr(self, address: Union[int, str]) -> str:
        """通过地址获取段信息"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Segment",
            "interface": "GetSegmentFromAddr",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)


class Reverse(BaseHttpClient):
    """逆向分析相关接口"""

    @check_server_available
    def disassembly_function(self, address: Union[int, str]) -> str:
        """反汇编函数"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty address"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DisassembleFunction",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def disassembly_count(self, address: Union[int, str], line_count: Union[int, str]) -> str:
        """按行数反汇编"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty address"
            }, ensure_ascii=False)

        try:
            # 支持十进制和十六进制输入
            line_count_int = int(str(line_count).strip(), 0)
            if line_count_int <= 0 or line_count_int > 1024:
                return json.dumps({
                    "status": "error",
                    "message": "The line count must be between 1 and 1024"
                }, ensure_ascii=False)
        except ValueError:
            return json.dumps({
                "status": "error",
                "message": "Invalid line count (must be integer)"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DisassemblyCount",
            "params": [addr_str, str(line_count_int)]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def disassembly_range(self, start_address: Union[int, str], end_address: Union[int, str]) -> str:
        """按地址范围反汇编"""
        start_addr = validate_hex_address(start_address)
        end_addr = validate_hex_address(end_address)

        if not start_addr:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty start address"
            }, ensure_ascii=False)

        if not end_addr:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty end address"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DisassemblyRange",
            "params": [start_addr, end_addr]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_checked(self, address: Union[int, str]) -> str:
        """反编译检查"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty address"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DeompileChecked",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_micro_code(self, address: Union[int, str]) -> str:
        """反编译微代码"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid or empty address"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "GetMicroCode",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_from_addr(self, address: Union[int, str]) -> str:
        """从地址反编译函数"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DecompileFunctionFromAddr",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_from_name(self, func_name: str) -> str:
        """从名称反编译函数"""
        if not func_name.strip():
            return json.dumps({
                "status": "error",
                "message": "Function name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DecompileFunctionFromName",
            "params": [func_name.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_line_to_address(self, address: str, line: str) -> str:
        """反编译行到地址"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        if not line.strip():
            return json.dumps({
                "status": "error",
                "message": "Line number cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DecompileLineToAddress",
            "params": [addr_str, line.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def decompile_address_to_line(self, address: str) -> str:
        """反编译地址到行"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Reverse",
            "interface": "DecompileAddressToLine",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)


class Memory(BaseHttpClient):
    """内存相关接口"""

    @check_server_available
    def get_entry_points(self) -> str:
        """获取入口点"""
        request_data = {
            "class": "Memory",
            "interface": "GetEntryPoints",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_defined_struct(self) -> str:
        """获取已定义结构"""
        request_data = {
            "class": "Memory",
            "interface": "GetDefinedStruct",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_byte(self, address: str) -> str:
        """获取内存字节"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetMemoryByte",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_word(self, address: str) -> str:
        """获取内存字(2字节)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetMemoryWord",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_dword(self, address: str) -> str:
        """获取内存双字(4字节)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetMemoryDword",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_qword(self, address: str) -> str:
        """获取内存四字(8字节)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetMemoryQword",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_bytes(self, address: str, byte_len: str) -> str:
        """获取指定长度内存"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        try:
            length = int(byte_len.strip())
            if length <= 0:
                return json.dumps({
                    "status": "error",
                    "message": "Length must be positive"
                }, ensure_ascii=False)
        except ValueError:
            return json.dumps({
                "status": "error",
                "message": "Invalid length format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetMemoryBytes",
            "params": [addr_str, str(length)]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_string_info(self) -> str:
        """获取字符串信息"""
        request_data = {
            "class": "Memory",
            "interface": "GetStringInfo",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_memory_search(self, start_address: str, end_address: str, param: str) -> str:
        """内存搜索"""
        start_addr = validate_hex_address(start_address)
        end_addr = validate_hex_address(end_address)

        if not start_addr:
            return json.dumps({
                "status": "error",
                "message": "Invalid start address format"
            }, ensure_ascii=False)

        if not end_addr:
            return json.dumps({
                "status": "error",
                "message": "Invalid end address format"
            }, ensure_ascii=False)

        if not param.strip():
            return json.dumps({
                "status": "error",
                "message": "Search parameter cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "MemorySearch",
            "params": [start_addr, end_addr, param.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_local_types(self) -> str:
        """获取本地类型"""
        request_data = {
            "class": "Memory",
            "interface": "GetLocalTypes",
            "params": []
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_type_by_name(self, type_name: str) -> str:
        """通过名称获取类型"""
        if not type_name.strip():
            return json.dumps({
                "status": "error",
                "message": "Type name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "GetTypeByName",
            "params": [type_name.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def xref_code_first_to(self, address: str) -> str:
        """获取代码交叉引用(到该地址)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "XrefCodeFirstTo",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def xref_code_first_from(self, address: str) -> str:
        """获取代码交叉引用(从该地址)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "XrefCodeFirstFrom",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def xref_data_first_to(self, address: str) -> str:
        """获取数据交叉引用(到该地址)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "XrefDataFirstTo",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def xref_data_first_from(self, address: str) -> str:
        """获取数据交叉引用(从该地址)"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Memory",
            "interface": "XrefDataFirstFrom",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)


class Other(BaseHttpClient):
    """其他功能接口"""

    @check_server_available
    def set_function_commnet(self, address: str, comment: str) -> str:
        """设置函数注释"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        if not comment.strip():
            return json.dumps({
                "status": "error",
                "message": "Comment cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "SetFunctionComment",
            "params": [addr_str, comment.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_name(self, address: str) -> str:
        """获取函数名称"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "GetFunctionName",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def set_function_name(self, address: str, text: str) -> str:
        """设置函数名称"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        if not text.strip():
            return json.dumps({
                "status": "error",
                "message": "Function name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "SetFunctionName",
            "params": [addr_str, text.strip()]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def switch_pseudocode_to(self, address: str) -> str:
        """切换到伪代码视图"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "SwitchPseudoCodeTo",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def get_function_var_name(self, address: str) -> str:
        """获取函数变量名称"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "GetFunctionVarName",
            "params": [addr_str]
        }
        return self.custom_post(json_data=request_data)

    @check_server_available
    def set_function_var_name(self, address: str, uid: str, names: str) -> str:
        """设置函数变量名称"""
        addr_str = validate_hex_address(address)
        if not addr_str:
            return json.dumps({
                "status": "error",
                "message": "Invalid address format"
            }, ensure_ascii=False)

        if not uid.strip():
            return json.dumps({
                "status": "error",
                "message": "UID cannot be empty"
            }, ensure_ascii=False)

        if not names.strip():
            return json.dumps({
                "status": "error",
                "message": "Variable name cannot be empty"
            }, ensure_ascii=False)

        request_data = {
            "class": "Other",
            "interface": "SetFunctionVarName",
            "params": [addr_str, uid.strip(), names.strip()]
        }
        return self.custom_post(json_data=request_data)