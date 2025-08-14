const { defineConfig, devices } = require('@playwright/test');
require('dotenv').config();

module.exports = defineConfig({
  testDir: './src/tests',
  fullyParallel: process.env.PARALLEL_MODE === 'true',
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : parseInt(process.env.MAX_RETRIES) || 0,
  workers: process.env.CI ? 1 : parseInt(process.env.MAX_WORKERS) || 1,
  reporter: [
    ['html'],
    ['allure-playwright', {
      detail: true,
      outputFolder: 'allure-results',
      suiteTitle: false,
    }],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  use: {
    baseURL: process.env[process.env.CURRENT_ENV?.toUpperCase() + '_URL'] || 'https://app.rudderstack.com',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: process.env.VIDEO_RECORDING === 'true' ? 'retain-on-failure' : 'off',
    headless: process.env.HEADLESS_MODE === 'true',
    viewport: {
      width: parseInt(process.env.WINDOW_WIDTH) || 1920,
      height: parseInt(process.env.WINDOW_HEIGHT) || 1080
    },
    actionTimeout: parseInt(process.env.BROWSER_TIMEOUT) || 10000,
    navigationTimeout: parseInt(process.env.PAGE_LOAD_TIMEOUT) || 30000,
    ignoreHTTPSErrors: true,
    extraHTTPHeaders: {
      'Accept': 'application/json, text/plain, */*',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
  },

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
          ]
        }
      },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  outputDir: 'test-results/',
  globalSetup: require.resolve('./global-setup.js'),
  globalTeardown: require.resolve('./global-teardown.js'),
  
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
}); 