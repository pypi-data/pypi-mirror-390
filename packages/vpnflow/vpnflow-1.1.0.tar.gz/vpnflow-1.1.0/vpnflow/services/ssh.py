# -*- coding: utf-8 -*-
import time
from contextlib import contextmanager
from logging import getLogger

from paramiko import AutoAddPolicy, SSHClient

logger = getLogger(__name__)


@contextmanager
def ssh_session(host, username, password):
    """⭐"""
    logger.info(f"Start ssh session {host}@{username}")
    with SSHClient() as ssh:
        t0 = time.perf_counter()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(host, username=username, password=password)
            yield ssh
        except Exception as exc:
            logger.error(f"Exception in ssh session: {exc}")
        finally:
            logger.info(f"Ssh session duration: {time.perf_counter() - t0 :.2f} s")


def upload_files(ssh_session, *files_paths):
    """⭐"""
    with ssh_session.open_sftp() as sftp:
        for local_path, remote_path in files_paths:
            try:
                sftp.put(local_path, remote_path)
            except FileNotFoundError as exc:
                logger.error(exc)
                return False
            else:
                logger.debug(f"File uploaded {local_path} -> {remote_path}")
    return True


def exec_commands(ssh_session, *commands, timeout=600):
    """⭐"""
    for command in commands:
        logger.debug(f"Execute command: {command}")
        stdin, stdout, stderr = ssh_session.exec_command(command, timeout=timeout)
        logger.debug("Stdout:\n{stdout}".format(stdout='\n'.join(l.strip() for l in stdout)))


def add_marzban_node_service(host, username, password, files_paths, commands):
    """⭐"""
    with ssh_session(host, username, password) as session:
        is_files_uploaded = upload_files(session, *files_paths)
        if not is_files_uploaded:
            logger.error(f"Files not uploaded: {files_paths}")
            return
        exec_commands(session, *commands)
