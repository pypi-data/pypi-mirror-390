import os
import time
import socket
import paramiko
import subprocess
from datetime import datetime
from func_timeout import func_set_timeout
from func_timeout.exceptions import FunctionTimedOut
from paramiko import SSHException
import time
import functools
import logging
import traceback
import inspect
from pathlib import Path
from typing import Callable, Any
from typing import List, Dict, Any, Optional

log=logging.getLogger(__name__)


class ExecResult():
    def __init__(self, exit_status_code, stdout="", stderr=""):
        self.__exit_status_code = exit_status_code
        self.__stdout = stdout
        self.__stderr = stderr

    @property
    def exit_status_code(self):
        return self.__exit_status_code

    @property
    def stdout(self):
        return self.__stdout

    @property
    def stderr(self):
        return self.__stderr

def enter_and_leave_function(func: Callable) -> Callable:
    """
    函数调用日志装饰器：
    1. 记录函数入参、调用位置
    2. 正常执行时记录返回值
    3. 异常时记录完整堆栈（含函数内具体报错行数）
    """

    @functools.wraps(func)  # 保留原函数元信息（如 __name__、__doc__）
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取函数定义的文件路径和行号（基础位置信息）
        func_def_file = inspect.getsourcefile(func) or "unknown_file"
        func_def_file = func_def_file.split("/")[-1]
        func_def_line = inspect.getsourcelines(func)[1] if func_def_file != "unknown_file" else "unknown_line"
        try:
            result = func(*args, **kwargs)
            if isinstance(result, ExecResult):
                if result.exit_status_code != 0:
                    log.warning(
                        f"[{func_def_file}: {func_def_line}]"
                        f" failed to run function {func.__name__}(), stderr is: {result.stderr} "
                    )
            return result

        except Exception as e:
            error_traceback = traceback.format_exc()

            log.error(
                f"[{func_def_file}: {func_def_line}]"
                f"failed to run function {func.__name__}() :Failed. "
                f"| error_type：{type(e).__name__} "
                f"| error_message：{str(e)} "
                f"| full_stack_trace：\n{error_traceback}",
                exc_info=False  # 已手动捕获堆栈，避免 logging 重复打印
            )
            raise  # 重新抛出异常，不中断原异常链路

    return wrapper

class SSHClient(object):
    def __init__(self, ip="127.0.0.1", port=22, username="root", password="", connect_timeout=10,get_tty=False):
        self.__ip = ip
        self.__port = port
        self.__username = username
        self.__password = password
        self.__connect_timeout = connect_timeout
        self.__ssh = None
        self.__sftp = None
        self.__get_tty = get_tty

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def is_sshable(self):
        ssh = None
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.__ip,
                port=self.__port,
                username=self.__username,
                password=self.__password,
                look_for_keys=False,
                allow_agent=False,
                timeout=self.__connect_timeout
            )
            return True
        except SSHException as e:
            log.warning(f"{self.__ip}:{self.__port} | cannot create ssh session, err msg is {str(e)}.")
            return False
        except Exception as e:
            log.warning(f"{self.__ip}:{self.__port} | server is not sshable.")
            return False
        finally:
            try:
                ssh.close()
            except Exception as e:
                pass

    @enter_and_leave_function
    def wait_for_sshable(self, timeout=60):
        count=0
        while True:
            count += 1
            if self.is_sshable:
                return True
            if count > int(timeout/self.__connect_timeout):
                return False
            time.sleep(self.__connect_timeout)

    @enter_and_leave_function
    def __connect(self):
        try:
            self.__ssh = paramiko.SSHClient()
            self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh.connect(
                self.__ip,
                port=self.__port,
                username=self.__username,
                password=self.__password,
                look_for_keys=False,
                allow_agent=False,
                timeout=self.__connect_timeout
            )
            return True
        except socket.timeout as e:
            log.warning(f"{self.__ip}:{self.__port} | failed to ssh connect. err msg is {str(e)}")
            return False
        except SSHException as e:
            log.warning(f"{self.__ip}:{self.__port} | failed to ssh connect. err msg is {str(e)}")
            return False
        except Exception as e:
            log.warning(f"{self.__ip}:{self.__port} | failed to ssh connect. err msg is {str(e)}")
            return False

    def reconnect(self):
        self.close()
        return self.__connect()

    def close(self):
        try:
            self.__sftp.close()
        except:
            pass
        try:
            self.__ssh.close()
        except:
            pass

    @enter_and_leave_function
    def _exec(self, cmd, promt_response,timeout=60):
        try:
            transport = self.__ssh.get_transport()
            if not transport or not transport.is_active():
                log.warning(f"{self.__ip}:{self.__port} | ssh connection is not active.")
                return ExecResult(1, "", "SSH连接已关闭或不可用")

            if promt_response:
                channel = transport.open_session()
                # 设置终端尺寸
                channel.get_pty(width=80, height=100)
                channel.settimeout(3600)
                channel.exec_command(cmd)
                output = ""
                begin=datetime.now()
                stderr = ""
                while True:
                    end = datetime.now()
                    if (end-begin).total_seconds()>timeout:
                        output=""
                        stderr=f"timeout to run cmd.{cmd}"
                    if channel.recv_ready():
                        output_chunk  = channel.recv(1024).decode('utf-8', 'ignore')
                        output += output_chunk
                        print(output_chunk, end='')

                        # 检查输出是否包含预期的提示信息
                        for elem in promt_response:
                            prompt = elem["prompt"]
                            response = elem["response"]
                            if prompt in output:
                                # 发送相应的回答
                                channel.send(response)
                    if channel.recv_stderr_ready():
                        stderr_chunk =channel.recv_stderr(2024).decode('utf-8', 'ignore')
                        stderr += stderr_chunk
                        print(stderr_chunk, end='')
                    if channel.closed and not (channel.recv_ready() or channel.recv_stderr_ready()):
                        break
                return_code = channel.recv_exit_status()
                return ExecResult(return_code, output, stderr)
            else:
                if self.__get_tty:
                    channel = transport.open_session()
                    # 设置终端尺寸
                    channel.get_pty(width=80, height=100)
                    channel.settimeout(3600)
                    stdin, stdout, stderr = self.__ssh.exec_command(
                        cmd,
                        get_pty=True,
                        timeout=timeout
                    )
                else:
                    stdin, stdout, stderr = self.__ssh.exec_command(
                        cmd,
                        get_pty=False,
                        timeout=timeout
                    )
                exit_status = stdout.channel.recv_exit_status()
                std_output = stdout.read().decode()
                std_err = stderr.read().decode()
                return ExecResult(exit_status, std_output, std_err)
        except Exception as e:
            return ExecResult(1, "", str(e))

    @func_set_timeout(3600)
    @enter_and_leave_function
    def exec(self, cmd, promt_response=[], timeout=60):
        try:
            if not self.__ssh:
                if not self.reconnect():
                    raise RuntimeError("ssh transport is not active and failed to reconnect.")
            return self._exec(cmd,promt_response,timeout)
        except Exception as e:
            log.warning(f"when run cmd: {cmd}, meets exception, err msg is {str(e)}")
            return ExecResult(1, "", str(e))

    @enter_and_leave_function
    def _scp_to_remote(self, local_path, remote_path):
        """递归拷贝本地文件/文件夹到远端，确保父目录存在"""
        local_path = Path(local_path).resolve()
        remote_path = Path(remote_path)

        # 处理本地文件：确保远端父目录存在后再上传
        if local_path.is_file():
            # 关键修复：创建文件的父目录（避免 "No such file" 错误）
            remote_parent = remote_path.parent
            mkdir_cmd = f"mkdir -p {remote_parent}"
            rs = self.exec(mkdir_cmd)
            if rs.exit_status_code != 0:
                log.error(f" {self.__ip}:{self.__port} | 无法创建文件父目录 {remote_parent}，命令: {mkdir_cmd}")
                return False

            # 上传文件
            try:
                self.__sftp.put(str(local_path), str(remote_path))
            except Exception as e:
                log.error(f" {self.__ip}:{self.__port} | 文件上传失败: {local_path} -> {remote_path}, 错误: {str(e)}")
                return False

            # 验证文件是否存在
            rs = self.exec(f"ls {remote_path}")
            if rs.exit_status_code != 0:
                log.warning(f" {self.__ip}:{self.__port} | 文件拷贝失败: 远端未找到 {remote_path}")
                return False
            return True

        # 处理本地文件夹：递归创建目录并拷贝内容
        if local_path.is_dir():
            # 创建远端根目录
            mkdir_cmd = f"mkdir -p {remote_path}"
            rs = self.exec(mkdir_cmd)
            if rs.exit_status_code != 0:
                log.error(f" {self.__ip}:{self.__port} | 无法创建远端根目录 {remote_path}，命令: {mkdir_cmd}")
                return False

            # 遍历本地文件夹
            for root, dirs, files in os.walk(local_path):
                # 计算相对路径，保持目录结构
                relative_root = Path(root).relative_to(local_path)
                remote_current_dir = remote_path / relative_root

                # 拷贝文件（关键：每个文件都确保其父目录存在）
                for file in files:
                    local_file = Path(root) / file
                    remote_file = remote_current_dir / file

                    # 强制创建当前文件的父目录（即使是子目录中的文件）
                    remote_file_parent = remote_file.parent
                    rs=self.exec(f"ls {remote_file_parent}")
                    if rs.exit_status_code != 0:
                        rs=self.exec(f"mkdir -p {remote_file_parent}")
                        if rs.exit_status_code != 0:
                            log.error(f" {self.__ip}:{self.__port} | 创建目录失败: {remote_file_parent}")
                            return False
                    # 上传文件
                    try:
                        self.__sftp.put(str(local_file), str(remote_file))
                    except Exception as e:
                        log.error(
                            f" {self.__ip}:{self.__port} | 拷贝失败: {local_file} -> {remote_file}, 错误: {str(e)}")
                        return False

            return True

        # 本地路径无效
        log.error(f" {self.__ip}:{self.__port} | 本地路径无效: {local_path}（不是文件或文件夹）")
        return False

    @enter_and_leave_function
    def scp_to_remote(self, local_path, remote_path, timeout=120):
        try:
            if not self.__ssh:
                if not self.reconnect():
                    raise RuntimeError("SSH连接未激活且重连失败")
            if not self.__sftp:
                self.__sftp = self.__ssh.open_sftp()

            local_path = Path(local_path)
            remote_path = Path(remote_path)

            # 处理远端路径冲突（文件覆盖为目录）
            if local_path.is_dir():
                # 检查远端是否存在同名文件
                if self.exec(f"test -f {remote_path}").exit_status_code == 0:
                    log.warning(f" {self.__ip}:{self.__port} | 远端存在同名文件，删除后创建目录: {remote_path}")
                    if self.exec(f"rm -f {remote_path}").exit_status_code != 0:
                        log.error(f" {self.__ip}:{self.__port} | 无法删除远端冲突文件: {remote_path}")
                        return False

            return self._scp_to_remote(local_path, remote_path)
        except Exception as e:
            log.warning(f" {self.__ip}:{self.__port} | SCP操作异常: 本地 {local_path} -> 远端 {remote_path}",
                        exc_info=True)
            return False

    @enter_and_leave_function
    def _scp_file_to_local(self, remote_path, local_path):
        if os.path.isfile(local_path):
            subprocess.run(['rm', '-rf', local_path], capture_output=True, text=True)
        for i in range(3):
            try:
                self.__sftp.get(remote_path, local_path)
                return True
            except OSError as e:
                log.warning(
                    f" {self.__ip}:{self.__port} | failed to copy file from remote {remote_path} to local host{local_path}:Error. err msg is {str(e)}")
                self.reconnect()
                self.__sftp = self.__ssh.open_sftp()
            except Exception as e:
                log.warning(
                    f" {self.__ip}:{self.__port} | failed to copy file from remote {remote_path} to local host{local_path}:Error.")
        else:
            log.error(
                f" {self.__ip}:{self.__port} | failed to copy file from remote {remote_path} to local host{local_path}:Error.")
            return False


    @enter_and_leave_function
    def ssh_is_active(self):
        try:
            if self.__ssh:
                return self.__ssh.get_transport().is_active()
            else:
                return False
        except Exception:
            return False

    @enter_and_leave_function
    def sftp_is_active(self):
        if not self.__ssh.get_transport() or not self.__ssh.get_transport().is_active():
            return False
        try:
            self.__sftp.getcwd()
            return True
        except (paramiko.SSHException, IOError, OSError,Exception) as e:
            log.warning(f"SFTP不可用: {e}")
            return False

    @enter_and_leave_function
    def scp_file_to_local(self, remote_path, local_path,timeout=120):
        try:
            if not self.ssh_is_active():
                if not self.reconnect():
                    raise RuntimeError("ssh transport is not active and failed to reconnect.")
            if not self.sftp_is_active():
                self.__sftp = self.__ssh.open_sftp()
            return self._scp_file_to_local(remote_path, local_path)
        except Exception:
            log.warning(f"when scp from remote {remote_path} to local {local_path}, meets exception.", exc_info=True)
            return False

    def __del__(self):
        self.close()
