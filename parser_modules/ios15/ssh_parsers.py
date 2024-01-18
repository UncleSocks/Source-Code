import re
from ssh_module import ssh_send
from report_modules.main_report import generate_report


def compliance_check_hostname(connection, command, cis_check, level, global_report_output):
    command_output = ssh_send(connection, command)
    regex_pattern = re.match(r'hostname (?P<hostname>\S+)', command_output)
    if regex_pattern:
        hostname = regex_pattern.group('hostname')
    else:
        raise ValueError("Error P0001 - Hostname Parser did not match any value.")
        
    compliant = hostname.lower() != "router"
    current_configuration = command_output
    global_report_output.append(generate_report(cis_check, level, compliant, current_configuration))


def compliance_check_ssh(connection, command, cis_check_one, cis_check_two, cis_check_three, level, global_report_output):
    command_output = ssh_send(connection, command)
    regex_pattern = re.search(r'SSH (?P<status>Enabled|Disabled) - version (?P<version>\d+\.\d+)\nAuthentication timeout: (?P<timeout>\d+) secs; Authentication retries: (?P<retries>\d+)',
                               command_output)
    
    if regex_pattern:
        ssh_status = regex_pattern.group('status')
        ssh_version = regex_pattern.group('version')
        auth_timeout = int(regex_pattern.group('timeout'))
        auth_retries = int(regex_pattern.group('retries'))
        ssh_info = {'Status':ssh_status, 'Version':ssh_version, 'Authentication Timeout':auth_timeout, 'Authentication Retries':auth_retries}
    
    else:
        raise ValueError("Error P0002 - SSH Info Parser did not match any value.")
    
    return compliance_check_ssh_config(ssh_info, cis_check_one, cis_check_two, cis_check_three, level, global_report_output)
    

def compliance_check_ssh_config(ssh_info, cis_check_one, cis_check_two, cis_check_three, level, global_report_output):
    compliant = ssh_info["Authentication Timeout"] <= 60
    current_configuration = f"Authentication Timeout - {ssh_info['Authentication Timeout']}"
    global_report_output.append(generate_report(cis_check_one, level, compliant, current_configuration))

    compliant = ssh_info["Authentication Retries"] <= 3
    current_configuration = f"Authentication Retries - {ssh_info['Authentication Retries']}"
    global_report_output.append(generate_report(cis_check_two, level, compliant, current_configuration))

    compliant = ssh_info["Version"] == "2.0"
    current_configuration = ssh_info
    global_report_output.append(generate_report(cis_check_three, level, compliant, current_configuration))