"""
Main entry point for Rudderstack SDET Assignment Framework
Provides command-line interface for running tests and managing the framework.
"""

import sys
import argparse
import subprocess
from pathlib import Path
from loguru import logger

from utils.config_manager import config_manager
from utils.test_data import test_scenario_manager


def main():
    """Main entry point for the framework"""
    parser = argparse.ArgumentParser(
        description="Rudderstack SDET Assignment Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py run-tests                    # Run all tests
  python src/main.py run-tests --smoke            # Run smoke tests only
  python src/main.py run-tests --integration      # Run integration tests only
  python src/main.py run-tests --env qa           # Run tests against QA environment
  python src/main.py validate-config              # Validate configuration
  python src/main.py list-scenarios               # List available test scenarios
  python src/main.py setup                        # Setup the framework
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run tests command
    run_parser = subparsers.add_parser('run-tests', help='Run test scenarios')
    run_parser.add_argument('--smoke', action='store_true', help='Run smoke tests only')
    run_parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    run_parser.add_argument('--regression', action='store_true', help='Run regression tests only')
    run_parser.add_argument('--env', choices=['dev', 'qa', 'prod'], default='dev', help='Environment to test against')
    run_parser.add_argument('--headless', action='store_true', help='Run tests in headless mode')
    run_parser.add_argument('--browser', choices=['chrome', 'firefox', 'safari'], default='chrome', help='Browser to use')
    run_parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    run_parser.add_argument('--scenario', help='Run specific test scenario')
    
    # Validate config command
    subparsers.add_parser('validate-config', help='Validate framework configuration')
    
    # List scenarios command
    subparsers.add_parser('list-scenarios', help='List available test scenarios')
    
    # Setup command
    subparsers.add_parser('setup', help='Setup the framework')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'run-tests':
        run_tests(args)
    elif args.command == 'validate-config':
        validate_config()
    elif args.command == 'list-scenarios':
        list_scenarios()
    elif args.command == 'setup':
        setup_framework()


def run_tests(args):
    """Run test scenarios"""
    logger.info("Starting test execution...")
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest', 'src/tests/', '-v']
    
    # Add markers based on test type
    if args.smoke:
        cmd.extend(['-m', 'smoke'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.regression:
        cmd.extend(['-m', 'regression'])
    
    # Add environment
    cmd.extend(['--env', args.env])
    
    # Add browser
    cmd.extend(['--browser', args.browser])
    
    # Add headless mode
    if args.headless:
        cmd.append('--headless')
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    # Add specific scenario
    if args.scenario:
        cmd.extend(['-k', args.scenario])
    
    # Add HTML report
    cmd.extend(['--html=reports/pytest-report.html', '--self-contained-html'])
    
    # Add Allure report
    cmd.extend(['--alluredir=allure-results'])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        logger.info("Test execution completed successfully")
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Test execution failed with return code: {e.returncode}")
        return e.returncode


def validate_config():
    """Validate framework configuration"""
    logger.info("Validating framework configuration...")
    
    try:
        # Check environment settings
        settings = config_manager.settings
        logger.info(f"Environment: {settings.current_env}")
        logger.info(f"Base URL: {config_manager.get_environment_url()}")
        
        # Check credentials
        credentials = config_manager.get_credentials()
        if credentials['email'] and credentials['email'] != 'your-business-email@domain.com':
            logger.info("✓ Rudderstack email configured")
        else:
            logger.warning("⚠ Rudderstack email not configured")
        
        if credentials['password'] and credentials['password'] != 'your-password':
            logger.info("✓ Rudderstack password configured")
        else:
            logger.warning("⚠ Rudderstack password not configured")
        
        # Check webhook URL
        webhook_url = config_manager.get_webhook_url()
        if webhook_url and webhook_url != 'https://your-requestcatcher-url.requestcatcher.com':
            logger.info("✓ Webhook URL configured")
        else:
            logger.warning("⚠ Webhook URL not configured")
        
        # Check browser configuration
        browser_config = config_manager.browser_config
        logger.info(f"Browser: {browser_config.name}")
        logger.info(f"Headless mode: {browser_config.headless}")
        logger.info(f"Timeout: {browser_config.timeout}ms")
        
        # Check API configuration
        api_config = config_manager.api_config
        logger.info(f"API timeout: {api_config.timeout}s")
        logger.info(f"Retry attempts: {api_config.retry_attempts}")
        
        logger.info("✓ Configuration validation completed")
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        return 1
    
    return 0


def list_scenarios():
    """List available test scenarios"""
    logger.info("Available test scenarios:")
    
    scenarios = test_scenario_manager.get_all_scenarios()
    
    for scenario_id, scenario in scenarios.items():
        print(f"\n{scenario_id}:")
        print(f"  Name: {scenario['name']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Steps: {', '.join(scenario['steps'])}")
        print(f"  Expected Results: {', '.join(scenario['expected_results'].keys())}")


def setup_framework():
    """Setup the framework"""
    logger.info("Setting up Rudderstack SDET Assignment Framework...")
    
    try:
        # Create necessary directories
        directories = ['logs', 'screenshots', 'videos', 'reports', 'allure-results', 'test-results']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Check if .env file exists
        if not Path('.env').exists():
            if Path('env.example').exists():
                import shutil
                shutil.copy('env.example', '.env')
                logger.info("Created .env file from template")
                logger.warning("Please edit .env file with your credentials")
            else:
                logger.warning("env.example not found, please create .env file manually")
        
        # Install dependencies
        logger.info("Installing Python dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        logger.info("Installing Node.js dependencies...")
        subprocess.run(['npm', 'install'], check=True)
        
        logger.info("Installing Playwright browsers...")
        subprocess.run(['npx', 'playwright', 'install', '--with-deps'], check=True)
        
        logger.info("✓ Framework setup completed successfully")
        
    except Exception as e:
        logger.error(f"Framework setup failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 