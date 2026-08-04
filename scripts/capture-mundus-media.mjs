import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const revision = '378fe528ca1c8f83f0280f83383b5e785e851285';
const liveUrl = 'https://0mn1si2i5.github.io/Mundus/';
const viewport = { width: 2160, height: 1350 };
const mundusRoot = process.env.MUNDUS_ROOT;

assert(mundusRoot, 'MUNDUS_ROOT is required');

const portfolioRoot = path.resolve(import.meta.dirname, '..');
const portfolioRequire = createRequire(import.meta.url);
const ffmpeg = portfolioRequire('ffmpeg-static');
const mundusRequire = createRequire(
  pathToFileURL(path.join(mundusRoot, 'package.json')),
);
const { chromium } = mundusRequire('@playwright/test');

assert(ffmpeg, 'ffmpeg-static executable is unavailable');

const mediaRoot = path.join(portfolioRoot, 'public/media/mundus');
const evidencePath = path.join(
  portfolioRoot,
  'docs/verification/evidence/mundus-media.json',
);
const captures = [
  {
    role: 'homepage-globe',
    png: '/tmp/mundus-globe-preview.png',
    target: 'globe-preview.webp',
  },
  {
    role: 'project-full-interface',
    png: '/tmp/mundus-other-side-full.png',
    target: 'other-side-full.webp',
  },
  {
    role: 'story-other-side-detail',
    png: '/tmp/mundus-other-side-detail.png',
    target: 'other-side-detail.webp',
  },
];

function webpDimensions(data) {
  const extended = data.indexOf(Buffer.from('VP8X'));
  if (extended >= 0) {
    return {
      width: 1 + data.readUIntLE(extended + 12, 3),
      height: 1 + data.readUIntLE(extended + 15, 3),
    };
  }

  const lossy = data.indexOf(Buffer.from([0x9d, 0x01, 0x2a]));
  if (lossy >= 0) {
    return {
      width: data.readUInt16LE(lossy + 3) & 0x3fff,
      height: data.readUInt16LE(lossy + 5) & 0x3fff,
    };
  }

  const lossless = data.indexOf(Buffer.from('VP8L'));
  assert(lossless >= 0 && data[lossless + 8] === 0x2f, 'unsupported WebP');
  const packed = data.readUInt32LE(lossless + 9);
  return {
    width: (packed & 0x3fff) + 1,
    height: ((packed >> 14) & 0x3fff) + 1,
  };
}

execFileSync('git', ['-C', mundusRoot, 'fetch', 'origin', 'main'], {
  stdio: 'inherit',
});
const originMain = execFileSync(
  'git',
  ['-C', mundusRoot, 'rev-parse', 'origin/main'],
  { encoding: 'utf8' },
).trim();
assert.equal(
  originMain,
  revision,
  `Mundus origin/main drifted to ${originMain}`,
);

const deploymentEndpoint =
  'repos/0mn1si2i5/Mundus/deployments?environment=github-pages&per_page=1';
const deployment = JSON.parse(
  execFileSync('gh', ['api', deploymentEndpoint, '--jq', '.[0]'], {
    encoding: 'utf8',
  }),
);
assert(deployment?.id, 'latest github-pages deployment is unavailable');
assert.equal(
  deployment.sha,
  revision,
  `Mundus Pages deployment drifted to ${deployment.sha}`,
);
const deploymentState = execFileSync(
  'gh',
  [
    'api',
    `repos/0mn1si2i5/Mundus/deployments/${deployment.id}/statuses?per_page=1`,
    '--jq',
    '.[0].state',
  ],
  { encoding: 'utf8' },
).trim();
assert.equal(
  deploymentState,
  'success',
  `Mundus Pages deployment is ${deploymentState}`,
);

await fs.mkdir(mediaRoot, { recursive: true });

const consoleErrors = [];
const pageErrors = [];
const requestFailures = [];
const browser = await chromium.launch({ headless: true });

try {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
    colorScheme: 'light',
    reducedMotion: 'reduce',
    locale: 'zh-CN',
  });
  await context.addInitScript(() => {
    window.localStorage.setItem('mundus:discovery-hint:v1', 'dismissed');
  });

  const page = await context.newPage();
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('requestfailed', (request) => {
    requestFailures.push({
      url: request.url(),
      reason: request.failure()?.errorText ?? 'unknown',
    });
  });

  const response = await page.goto(liveUrl, { waitUntil: 'networkidle' });
  assert(response?.ok(), `Mundus returned ${response?.status()}`);
  await page.waitForFunction(() =>
    [...document.images].every((image) => image.complete),
  );

  const globe = page.getByRole('region', {
    name: '交互式三维地球',
  });
  const result = page.getByRole('complementary', {
    name: '位置结果',
  });
  await globe.waitFor();
  await result.waitFor();
  await page.waitForFunction(() => {
    const element = document.querySelector(
      '[role="region"][aria-label="交互式三维地球"]',
    );
    return (
      element?.getAttribute('data-vector-state') === 'ready' &&
      element?.getAttribute('data-antipode-relation-state') === 'ready'
    );
  });
  await page.waitForTimeout(500);

  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    ),
    false,
    'public page has horizontal overflow',
  );

  const panelOverflows = await result.locator('*').evaluateAll((elements) =>
    elements
      .filter((element) => {
        if (!(element instanceof HTMLElement) || element.offsetParent === null) {
          return false;
        }
        return (
          element.scrollWidth > element.clientWidth + 1 ||
          element.scrollHeight > element.clientHeight + 1
        );
      })
      .map((element) => ({
        tag: element.tagName,
        text: element.innerText.slice(0, 120),
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
        clientHeight: element.clientHeight,
        scrollHeight: element.scrollHeight,
      })),
  );
  assert.deepEqual(panelOverflows, [], 'result-panel content is clipped');

  const canvas = globe.locator('canvas');
  const canvasBox = await canvas.boundingBox();
  const globeBox = await globe.boundingBox();
  const resultBox = await result.boundingBox();
  assert(canvasBox && globeBox && resultBox, 'capture regions are unavailable');

  const previewSize = Math.min(
    canvasBox.height * 0.9,
    canvasBox.width * 0.58,
  );
  const previewVisibleUiCount = await canvas.evaluate((canvasElement) => {
    const ancestors = new Set();
    let current = canvasElement;
    while (current) {
      ancestors.add(current);
      current = current.parentElement;
    }

    const style = document.createElement('style');
    style.id = 'mundus-canvas-only-capture';
    style.textContent =
      '[data-mundus-capture-hidden] { visibility: hidden !important; }';
    document.head.append(style);

    for (const element of document.body.querySelectorAll('*')) {
      if (!ancestors.has(element)) {
        element.setAttribute('data-mundus-capture-hidden', '');
      }
    }

    return [...document.body.querySelectorAll('*')].filter((element) => {
      if (
        ancestors.has(element) ||
        !(element instanceof HTMLElement) ||
        element.offsetParent === null
      ) {
        return false;
      }
      const computed = getComputedStyle(element);
      return (
        computed.visibility !== 'hidden' &&
        (element.innerText.trim().length > 0 ||
          element.matches(
            'button, a, input, select, textarea, [role], [aria-label]',
          ))
      );
    }).length;
  });
  assert.equal(
    previewVisibleUiCount,
    0,
    'homepage preview contains visible interface elements',
  );
  await page.screenshot({
    path: captures[0].png,
    animations: 'disabled',
    clip: {
      x: Math.round(canvasBox.x + (canvasBox.width - previewSize) / 2),
      y: Math.round(canvasBox.y + (canvasBox.height - previewSize) / 2),
      width: Math.round(previewSize),
      height: Math.round(previewSize),
    },
  });
  await page.evaluate(() => {
    document.getElementById('mundus-canvas-only-capture')?.remove();
    for (const element of document.querySelectorAll(
      '[data-mundus-capture-hidden]',
    )) {
      element.removeAttribute('data-mundus-capture-hidden');
    }
  });
  await result.waitFor({ state: 'visible' });
  await page.screenshot({
    path: captures[1].png,
    fullPage: false,
    animations: 'disabled',
  });

  const dragStart = await canvas.evaluate((element) => {
    const bounds = element.getBoundingClientRect();
    const offsets = [
      [0, 0],
      [0.05, 0],
      [-0.05, 0],
      [0, -0.05],
      [0, 0.05],
    ];
    for (const [xOffset, yOffset] of offsets) {
      const x = bounds.left + bounds.width * (0.5 + xOffset);
      const y = bounds.top + bounds.height * (0.5 + yOffset);
      if (document.elementFromPoint(x, y) === element) return { x, y };
    }
    return null;
  });
  assert(dragStart, 'globe canvas center is covered by page UI');
  await page.mouse.move(dragStart.x, dragStart.y);
  await page.mouse.down();
  await page.mouse.move(dragStart.x + globeBox.width * 0.05, dragStart.y, {
    steps: 8,
  });
  await page.waitForFunction(() => {
    const element = document.querySelector(
      '[role="region"][aria-label="交互式三维地球"]',
    );
    return element?.getAttribute('data-antipode-drag-state') === 'active';
  });
  await page.waitForTimeout(250);

  const detailLeft = Math.max(0, globeBox.x + globeBox.width * 0.28);
  const detailTop = Math.max(0, resultBox.y - 100);
  const detailRight = Math.min(
    viewport.width,
    Math.max(globeBox.x + globeBox.width, resultBox.x + resultBox.width),
  );
  const detailBottom = Math.min(
    viewport.height - 120,
    Math.max(
      resultBox.y + resultBox.height + 100,
      dragStart.y + globeBox.height * 0.32,
    ),
  );
  await page.screenshot({
    path: captures[2].png,
    animations: 'disabled',
    clip: {
      x: Math.floor(detailLeft),
      y: Math.floor(detailTop),
      width: Math.floor(detailRight - detailLeft),
      height: Math.floor(detailBottom - detailTop),
    },
  });
  await page.mouse.up();

  const images = [];
  for (const capture of captures) {
    const target = path.join(mediaRoot, capture.target);
    execFileSync(ffmpeg, [
      '-loglevel',
      'error',
      '-y',
      '-i',
      capture.png,
      '-c:v',
      'libwebp',
      '-q:v',
      '86',
      target,
    ]);
    const data = await fs.readFile(target);
    images.push({
      role: capture.role,
      path: capture.target,
      ...webpDimensions(data),
      sha256: crypto.createHash('sha256').update(data).digest('hex'),
    });
  }

  assert(images[1].width >= 1920, 'hero capture is too narrow');
  assert.equal(new Set(images.map((image) => image.sha256)).size, 3);
  assert.deepEqual(consoleErrors, []);
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(requestFailures, []);

  const manifest = {
    schemaVersion: 1,
    sourceUrl: liveUrl,
    sourceRevision: revision,
    captureLocale: 'zh-CN',
    capturedViewport: viewport,
    previewVisibleUiCount,
    panelOverflowCount: panelOverflows.length,
    consoleErrorCount: consoleErrors.length,
    pageErrorCount: pageErrors.length,
    failedRequestCount: requestFailures.length,
    images,
  };
  await fs.writeFile(evidencePath, `${JSON.stringify(manifest, null, 2)}\n`);
} finally {
  await browser.close();
}
