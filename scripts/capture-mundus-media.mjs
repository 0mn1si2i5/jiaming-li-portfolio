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
const storyViewport = { width: 1920, height: 1080 };
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
const retainedCaptures = [
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
];
const storyCaptures = [
  {
    mode: 'other-side',
    role: 'story-other-side',
    url: `${liveUrl}?mode=antipodes&v=1`,
    png: '/tmp/mundus-other-side-detail.png',
    target: 'other-side-detail.webp',
  },
  {
    mode: 'development',
    role: 'story-development',
    url: `${liveUrl}?mode=development&indicator=hdi&year=2023&v=1`,
    png: '/tmp/mundus-development.png',
    target: 'development.webp',
  },
  {
    mode: 'sunline',
    role: 'story-sunline',
    url: `${liveUrl}?mode=sunline&v=1`,
    png: '/tmp/mundus-sunline.png',
    target: 'sunline.webp',
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

async function waitForHealthyPage(page, url, mode) {
  const response = await page.goto(url, { waitUntil: 'networkidle' });
  assert(response?.ok(), `${mode} returned ${response?.status()}`);
  await page.waitForFunction(() =>
    [...document.images].every(
      (image) =>
        image.complete &&
        image.naturalWidth > 0 &&
        image.naturalHeight > 0,
    ),
  );
  await page.locator('section[data-mode]').waitFor({ state: 'visible' });
  await page.waitForFunction((expectedMode) => {
    const intro = document.querySelector('section[data-mode]');
    const globe = document.querySelector(
      '[role="region"][aria-label="交互式三维地球"]',
    );
    return (
      intro?.getAttribute('data-mode') ===
        (expectedMode === 'other-side' ? 'antipodes' : expectedMode) &&
      globe?.getAttribute('data-vector-state') === 'ready' &&
      (expectedMode !== 'other-side' ||
        globe.getAttribute('data-antipode-relation-state') === 'ready')
    );
  }, mode);
  await page.waitForTimeout(500);
}

async function visiblePanelOverflows(page) {
  return page
    .locator('[role="complementary"], [role="complementary"] *')
    .evaluateAll((elements) =>
      elements
        .filter((element) => {
          if (
            !(element instanceof HTMLElement) ||
            element.offsetParent === null
          ) {
            return false;
          }
          const hasHorizontalOverflow =
            element.scrollWidth > element.clientWidth + 1;
          const hasVerticalOverflow =
            element.scrollHeight > element.clientHeight + 1;
          const overflowY = getComputedStyle(element).overflowY;
          const intentionalVerticalScroll =
            hasVerticalOverflow &&
            (overflowY === 'auto' || overflowY === 'scroll');
          return (
            hasHorizontalOverflow ||
            (hasVerticalOverflow && !intentionalVerticalScroll)
          );
        })
        .map((element) => ({
          tag: element.tagName,
          text: element.innerText.slice(0, 120),
          overflowY: getComputedStyle(element).overflowY,
          clientWidth: element.clientWidth,
          scrollWidth: element.scrollWidth,
          clientHeight: element.clientHeight,
          scrollHeight: element.scrollHeight,
        })),
    );
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
}

async function publishArtifacts(artifacts) {
  for (const artifact of artifacts) {
    artifact.hadOriginal = await pathExists(artifact.target);
    if (artifact.hadOriginal) {
      await fs.copyFile(artifact.target, artifact.backup);
    }
  }

  try {
    for (const artifact of artifacts) {
      await fs.rename(artifact.staged, artifact.target);
    }
  } catch (publicationError) {
    const rollbackErrors = [];
    for (const artifact of [...artifacts].reverse()) {
      try {
        if (artifact.hadOriginal) {
          await fs.rename(artifact.backup, artifact.target);
        } else {
          await fs.rm(artifact.target, { force: true });
        }
      } catch (rollbackError) {
        rollbackErrors.push(rollbackError);
      }
    }

    if (rollbackErrors.length > 0) {
      const rollbackFailure = new AggregateError(
        [publicationError, ...rollbackErrors],
        'Mundus media publication failed and rollback was incomplete',
        { cause: publicationError },
      );
      rollbackFailure.rollbackIncomplete = true;
      throw rollbackFailure;
    }
    throw publicationError;
  }
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
  page.on('response', (response) => {
    const responseUrl = response.url();
    if (
      response.request().resourceType() === 'document' ||
      (!responseUrl.startsWith('http://') &&
        !responseUrl.startsWith('https://'))
    ) {
      return;
    }
    if (!response.ok()) {
      requestFailures.push({
        url: responseUrl,
        status: response.status(),
      });
    }
  });

  await waitForHealthyPage(page, liveUrl, 'other-side');

  const globe = page.getByRole('region', {
    name: '交互式三维地球',
  });
  const result = page.getByRole('complementary', {
    name: '位置结果',
  });
  await globe.waitFor();
  await result.waitFor();

  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    ),
    false,
    'public page has horizontal overflow',
  );

  const panelOverflows = await visiblePanelOverflows(page);
  assert.deepEqual(panelOverflows, [], 'result-panel content is clipped');

  const canvas = globe.locator('canvas');
  const canvasBox = await canvas.boundingBox();
  assert(canvasBox, 'capture regions are unavailable');

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
    path: retainedCaptures[0].png,
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
    path: retainedCaptures[1].png,
    fullPage: false,
    animations: 'disabled',
  });

  const storyOverflows = {};
  await page.setViewportSize(storyViewport);
  for (const capture of storyCaptures) {
    await waitForHealthyPage(page, capture.url, capture.mode);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      ),
      false,
      `${capture.mode} page has horizontal overflow`,
    );
    const overflows = await visiblePanelOverflows(page);
    storyOverflows[capture.mode] = overflows;
    assert.deepEqual(overflows, [], `${capture.mode} content is clipped`);
    await page.screenshot({
      path: capture.png,
      fullPage: false,
      animations: 'disabled',
    });
  }

  assert.deepEqual(consoleErrors, []);
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(requestFailures, []);

  const images = [];
  const stagingRoot = await fs.mkdtemp(
    path.join(portfolioRoot, '.mundus-media-'),
  );
  let preserveStagingRoot = false;
  try {
    for (const capture of retainedCaptures) {
      const data = await fs.readFile(path.join(mediaRoot, capture.target));
      images.push({
        role: capture.role,
        path: capture.target,
        ...webpDimensions(data),
        sha256: crypto.createHash('sha256').update(data).digest('hex'),
      });
    }
    for (const capture of storyCaptures) {
      const stagedTarget = path.join(stagingRoot, capture.target);
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
        stagedTarget,
      ]);
      const data = await fs.readFile(stagedTarget);
      images.push({
        role: capture.role,
        path: capture.target,
        ...webpDimensions(data),
        sha256: crypto.createHash('sha256').update(data).digest('hex'),
      });
    }

    assert(images[1].width >= 1920, 'hero capture is too narrow');
    assert.deepEqual(
      images
        .filter((image) => image.role.startsWith('story-'))
        .map(({ width, height }) => ({ width, height })),
      storyCaptures.map(() => storyViewport),
    );
    assert.equal(new Set(images.map((image) => image.sha256)).size, 5);

    const storyPanelOverflowCount = Object.values(storyOverflows).reduce(
      (count, overflows) => count + overflows.length,
      0,
    );
    const manifest = {
      schemaVersion: 1,
      sourceUrl: liveUrl,
      sourceRevision: revision,
      captureLocale: 'zh-CN',
      capturedViewport: viewport,
      storyViewport,
      previewVisibleUiCount,
      panelOverflowCount: panelOverflows.length,
      storyPanelOverflowCount,
      consoleErrorCount: consoleErrors.length,
      pageErrorCount: pageErrors.length,
      failedRequestCount: requestFailures.length,
      images,
    };
    const stagedManifestPath = path.join(stagingRoot, 'mundus-media.json');
    await fs.writeFile(
      stagedManifestPath,
      `${JSON.stringify(manifest, null, 2)}\n`,
    );

    const backupRoot = path.join(stagingRoot, 'backup');
    await fs.mkdir(backupRoot);
    const publicationArtifacts = [
      ...storyCaptures.map((capture) => ({
        staged: path.join(stagingRoot, capture.target),
        target: path.join(mediaRoot, capture.target),
        backup: path.join(backupRoot, capture.target),
      })),
      {
        staged: stagedManifestPath,
        target: evidencePath,
        backup: path.join(backupRoot, 'mundus-media.json'),
      },
    ];
    try {
      await publishArtifacts(publicationArtifacts);
    } catch (error) {
      preserveStagingRoot = error.rollbackIncomplete === true;
      throw error;
    }
  } finally {
    if (!preserveStagingRoot) {
      await fs.rm(stagingRoot, { recursive: true, force: true });
    }
  }
} finally {
  await browser.close();
}
