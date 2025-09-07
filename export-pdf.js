const path = require('path');
const { execSync } = require('child_process');

// 获取全局 node_modules 路径
const globalNodeModules = execSync('npm root -g').toString().trim();
const puppeteerPath = path.join(globalNodeModules, 'puppeteer');

const puppeteer = require(puppeteerPath);

// 命令行参数解析
const args = process.argv.slice(2).reduce((acc, arg) => {
    const [key, value] = arg.split('=');
    acc[key] = value;
    return acc;
}, {});

// 默认参数
const inputPath = args.input || 'demo_custom.html';
const outputPath = args.output || 'output.pdf';
const pageSize = args.size || 'A3';
const title = args.title || '\U0001f4d8 文档标题';
// 创建页面并禁用所有超时
async function createPage(browser) {
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(0);
    page.setDefaultTimeout(0);
    return page;
}

(async () => {
    const browser = await puppeteer.launch({
        executablePath: 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        protocolTimeout: 0 // 或者设置为更大的值，比如 300000（5分钟）
    });

    const page = await createPage(browser);
    const fileUrl = `file://${path.resolve(inputPath)}`;

    await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 0 });

    await page.pdf({
        path: outputPath,
        format: pageSize,
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: `<div style="font-size:10px; text-align:left; width:100%;padding-left:20px;"><span>${title}</span></div>`,
        footerTemplate: `<div style="font-size:10px; text-align:right; width:100%; padding-right:20px;"><span>第 <span class="pageNumber"></span> 页</span></div>`,
        margin: {
            top: '60px',
            bottom: '60px',
            left: '40px',
            right: '40px',
        },
    });

    await browser.close();
})();

