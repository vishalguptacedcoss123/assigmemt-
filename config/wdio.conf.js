const path = require('path');
require('dotenv').config();

exports.config = {
    // ====================
    // Runner Configuration
    // ====================
    runner: 'local',
    autoCompileOpts: {
        autoCompile: true,
        tsNodeOpts: {
            project: './tsconfig.json',
            transpileOnly: true
        }
    },

    // ==================
    // Specify Test Files
    // ==================
    specs: [
        './src/tests/**/*.js',
        './src/tests/**/*.ts'
    ],
    exclude: [
        './src/tests/**/*.spec.js',
        './src/tests/**/*.spec.ts'
    ],

    // ============
    // Capabilities
    // ============
    maxInstances: process.env.MAX_WORKERS || 1,
    capabilities: [{
        browserName: process.env.BROWSER_NAME || 'chrome',
        'goog:chromeOptions': {
            args: [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--headless=' + (process.env.HEADLESS_MODE === 'true'),
                '--window-size=' + (process.env.WINDOW_WIDTH || '1920') + ',' + (process.env.WINDOW_HEIGHT || '1080')
            ]
        },
        'moz:firefoxOptions': {
            args: [
                '--headless',
                '--width=' + (process.env.WINDOW_WIDTH || '1920'),
                '--height=' + (process.env.WINDOW_HEIGHT || '1080')
            ]
        }
    }],

    // ===================
    // Test Configurations
    // ===================
    logLevel: process.env.LOG_LEVEL || 'info',
    bail: 0,
    baseUrl: process.env[process.env.CURRENT_ENV?.toUpperCase() + '_URL'] || 'https://app.rudderstack.com',
    waitforTimeout: parseInt(process.env.BROWSER_TIMEOUT) || 10000,
    connectionRetryTimeout: 120000,
    connectionRetryCount: 3,
    services: [
        'chromedriver',
        'geckodriver'
    ],
    framework: 'mocha',
    reporters: [
        'spec',
        ['allure', {
            outputDir: 'allure-results',
            disableWebdriverStepsReporting: true,
            disableWebdriverScreenshotsReporting: false,
        }]
    ],

    // =====
    // Hooks
    // =====
    beforeSession: function (config, capabilities, specs) {
        require('ts-node').register({ files: true });
    },
    
    before: function (capabilities, specs) {
        browser.setWindowSize(
            parseInt(process.env.WINDOW_WIDTH) || 1920,
            parseInt(process.env.WINDOW_HEIGHT) || 1080
        );
    },

    afterTest: function (test, context, { error, result, duration, passed, retries }) {
        if (!passed) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = `./screenshots/failure-${timestamp}.png`;
            browser.saveScreenshot(screenshotPath);
            console.log(`Screenshot saved: ${screenshotPath}`);
        }
    },

    after: function (result, capabilities, specs) {
        // Clean up after all tests
    },

    // =====
    // Mocha
    // =====
    mochaOpts: {
        ui: 'bdd',
        timeout: 60000,
        retries: parseInt(process.env.MAX_RETRIES) || 3
    },

    // =====
    // Retry
    // =====
    retry: parseInt(process.env.MAX_RETRIES) || 3,
    retryDelay: parseInt(process.env.RETRY_DELAY) || 2000,

    // =====
    // Output
    // =====
    outputDir: './logs',
    logOutputs: true,
    excludeDriverLogs: ['*'],
    logLevels: {
        webdriver: 'warn',
        'wdio-chromedriver-service': 'warn',
        'wdio-geckodriver-service': 'warn'
    }
}; 