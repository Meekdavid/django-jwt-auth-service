#!/usr/bin/env python3
"""
Railway startup script with comprehensive error logging and debugging
"""
import os
import subprocess
import sys
import traceback
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('railway_startup')

def log_environment():
    """Log all environment variables and system info"""
    logger.info("=" * 80)
    logger.info("RAILWAY STARTUP DEBUGGING SESSION")
    logger.info("=" * 80)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Command line args: {sys.argv}")
    
    # Log all environment variables
    logger.info("ENVIRONMENT VARIABLES:")
    for key, value in sorted(os.environ.items()):
        if 'PORT' in key.upper() or 'DJANGO' in key.upper() or 'DATABASE' in key.upper():
            logger.info(f"  {key} = {repr(value)}")
        elif key in ['PATH', 'HOME', 'USER', 'SHELL']:
            logger.info(f"  {key} = {value[:100]}...")
    
    # Specifically check PORT variable
    port_raw = os.environ.get('PORT')
    logger.info(f"PORT ANALYSIS:")
    logger.info(f"  os.environ.get('PORT') = {repr(port_raw)}")
    logger.info(f"  Type: {type(port_raw)}")
    if port_raw:
        logger.info(f"  Length: {len(port_raw)}")
        logger.info(f"  Repr: {repr(port_raw)}")
        logger.info(f"  Is digit: {port_raw.isdigit()}")
        logger.info(f"  Stripped: {repr(port_raw.strip())}")

def validate_port(port_str):
    """Validate and clean port value"""
    logger.info(f"VALIDATING PORT: {repr(port_str)}")
    
    if port_str is None:
        logger.warning("PORT is None, using default 8000")
        return "8000"
    
    # Clean the port string
    cleaned = str(port_str).strip()
    logger.info(f"Cleaned port: {repr(cleaned)}")
    
    # Check if it's still a variable reference
    if cleaned.startswith('$'):
        logger.error(f"PORT still contains variable reference: {repr(cleaned)}")
        logger.error("This means environment variable expansion failed!")
        return "8000"
    
    # Validate it's a number
    if not cleaned.isdigit():
        logger.error(f"PORT is not a valid number: {repr(cleaned)}")
        return "8000"
    
    port_num = int(cleaned)
    if port_num < 1 or port_num > 65535:
        logger.error(f"PORT out of valid range (1-65535): {port_num}")
        return "8000"
    
    logger.info(f"Valid port: {port_num}")
    return cleaned

def test_gunicorn_command(cmd):
    """Test the gunicorn command before executing"""
    logger.info("TESTING GUNICORN COMMAND:")
    logger.info(f"  Full command: {cmd}")
    
    # Extract the bind parameter
    bind_param = None
    for i, arg in enumerate(cmd):
        if arg == '--bind' and i + 1 < len(cmd):
            bind_param = cmd[i + 1]
            break
    
    logger.info(f"  Bind parameter: {repr(bind_param)}")
    
    if bind_param and ':' in bind_param:
        host, port = bind_param.split(':', 1)
        logger.info(f"  Host: {repr(host)}")
        logger.info(f"  Port: {repr(port)}")
        
        # Check if port looks like a variable
        if port.startswith('$'):
            logger.error(f"FOUND THE PROBLEM! Port is still a variable: {repr(port)}")
            logger.error("This will cause gunicorn to fail with 'not a valid port number'")
            return False
    
    return True

def main():
    try:
        # Log everything about the environment
        log_environment()
        
        # Get and validate port
        port_raw = os.environ.get('PORT', '8000')
        port = validate_port(port_raw)
        
        logger.info(f"FINAL PORT VALUE: {repr(port)}")
        
        # Set Django settings
        django_settings = 'auth_service.settings.railway'
        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings
        logger.info(f"Django settings: {django_settings}")
        
        # Collect static files
        logger.info("COLLECTING STATIC FILES...")
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'collectstatic', '--noinput'], 
                capture_output=True, 
                text=True,
                timeout=120
            )
            logger.info(f"Static files stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"Static files stderr: {result.stderr}")
            if result.returncode != 0:
                logger.warning(f"Static files failed with code: {result.returncode}")
        except Exception as e:
            logger.error(f"Static files collection error: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Build gunicorn command
        cmd = [
            'gunicorn',
            'auth_service.wsgi:application',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '60',
            '--log-level', 'debug',
            '--access-logfile', '-',
            '--error-logfile', '-',
            '--capture-output'
        ]
        
        # Test the command
        if not test_gunicorn_command(cmd):
            logger.error("Command validation failed! Aborting.")
            sys.exit(1)
        
        logger.info("STARTING GUNICORN:")
        logger.info(f"  Command: {' '.join(cmd)}")
        
        # Check if we're on Windows (for local testing)
        if os.name == 'nt':
            logger.warning("WINDOWS DETECTED - Gunicorn won't work on Windows!")
            logger.warning("This is expected for local testing. On Railway (Linux), it will work.")
            logger.info("SUCCESS: Script validation complete. PORT handling is correct!")
            return
        
        # Try to start gunicorn (on Linux/Railway)
        logger.info("Executing gunicorn...")
        os.execvp('gunicorn', cmd)
        
    except Exception as e:
        logger.error("FATAL ERROR IN STARTUP SCRIPT:")
        logger.error(f"Exception: {e}")
        logger.error(f"Type: {type(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        # Try to provide helpful debug info
        logger.error("DEBUG INFORMATION:")
        logger.error(f"  Python path: {sys.path[:3]}")
        logger.error(f"  Current dir contents: {os.listdir('.')[:10]}")
        
        sys.exit(1)

if __name__ == '__main__':
    main()
