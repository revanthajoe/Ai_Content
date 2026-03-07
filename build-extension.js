#!/usr/bin/env node
/**
 * Build script for Content DNA OS browser extension.
 * Produces zip files for Chrome/Edge (Manifest V3) and Firefox (Manifest V2).
 *
 * Usage:
 *   node build-extension.js           # builds both
 *   node build-extension.js chrome    # Chrome/Edge only
 *   node build-extension.js firefox   # Firefox only
 *
 * Prerequisites:
 *   - Place PNG icons in extension/icons/ (icon-16.png, icon-32.png, icon-48.png, icon-128.png)
 *     OR run this script and it will generate them from the SVG if 'sharp' is installed.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const EXT_DIR = path.join(__dirname, 'extension');
const DIST_DIR = path.join(__dirname, 'dist-extension');

const SHARED_FILES = [
  'popup.html',
  'popup.css',
  'popup.js',
  'sidepanel.html',
  'content-script.js',
  'content-style.css',
  'background.js',
  'icons/icon.svg',
  'icons/icon-16.png',
  'icons/icon-32.png',
  'icons/icon-48.png',
  'icons/icon-128.png',
];

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function copyFile(src, dest) {
  const destDir = path.dirname(dest);
  ensureDir(destDir);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, dest);
  }
}

function generatePngIcons() {
  const svgPath = path.join(EXT_DIR, 'icons', 'icon.svg');
  if (!fs.existsSync(svgPath)) {
    console.warn('⚠ No icon.svg found. Please add PNG icons manually.');
    return;
  }

  // Try using sharp if available
  try {
    const sharp = require('sharp');
    const sizes = [16, 32, 48, 128];
    for (const size of sizes) {
      const outPath = path.join(EXT_DIR, 'icons', `icon-${size}.png`);
      if (!fs.existsSync(outPath)) {
        sharp(svgPath).resize(size, size).png().toFile(outPath);
        console.log(`  Generated icon-${size}.png`);
      }
    }
  } catch {
    console.warn('⚠ sharp not installed. Add PNG icons manually or run: npm install sharp');
  }
}

function createZip(sourceDir, outFile) {
  // Use PowerShell Compress-Archive on Windows, zip on Unix
  if (process.platform === 'win32') {
    const cmd = `powershell -Command "Compress-Archive -Path '${sourceDir}\\*' -DestinationPath '${outFile}' -Force"`;
    execSync(cmd, { stdio: 'inherit' });
  } else {
    execSync(`cd "${sourceDir}" && zip -r "${outFile}" .`, { stdio: 'inherit' });
  }
}

function buildChrome() {
  console.log('\n🔨 Building Chrome/Edge extension (Manifest V3)...');
  const buildDir = path.join(DIST_DIR, 'chrome');
  ensureDir(buildDir);

  // Copy manifest
  copyFile(path.join(EXT_DIR, 'manifest.json'), path.join(buildDir, 'manifest.json'));

  // Copy shared files
  for (const file of SHARED_FILES) {
    copyFile(path.join(EXT_DIR, file), path.join(buildDir, file));
  }

  // Create zip
  const zipPath = path.join(DIST_DIR, 'content-dna-os-chrome.zip');
  createZip(buildDir, zipPath);
  console.log(`✅ Chrome/Edge extension: ${zipPath}`);
}

function buildFirefox() {
  console.log('\n🔨 Building Firefox extension (Manifest V2)...');
  const buildDir = path.join(DIST_DIR, 'firefox');
  ensureDir(buildDir);

  // Copy Firefox manifest as manifest.json
  copyFile(path.join(EXT_DIR, 'manifest-firefox.json'), path.join(buildDir, 'manifest.json'));

  // Copy shared files
  for (const file of SHARED_FILES) {
    // Skip sidepanel (not supported in Firefox MV2)
    if (file === 'sidepanel.html') continue;
    copyFile(path.join(EXT_DIR, file), path.join(buildDir, file));
  }

  // Create zip (Firefox uses .xpi but .zip works for web-ext)
  const zipPath = path.join(DIST_DIR, 'content-dna-os-firefox.zip');
  createZip(buildDir, zipPath);
  console.log(`✅ Firefox extension: ${zipPath}`);
}

// ─── Main ───
const target = process.argv[2] || 'all';

ensureDir(DIST_DIR);
generatePngIcons();

if (target === 'all' || target === 'chrome') buildChrome();
if (target === 'all' || target === 'firefox') buildFirefox();

console.log('\n📦 Extension build complete!');
console.log('\nTo load in Chrome/Edge:');
console.log('  1. Go to chrome://extensions or edge://extensions');
console.log('  2. Enable "Developer mode"');
console.log('  3. Click "Load unpacked" → select dist-extension/chrome/');
console.log('\nTo load in Firefox:');
console.log('  1. Go to about:debugging#/runtime/this-firefox');
console.log('  2. Click "Load Temporary Add-on"');
console.log('  3. Select dist-extension/firefox/manifest.json');
console.log('\nTo publish:');
console.log('  Chrome Web Store: Upload content-dna-os-chrome.zip');
console.log('  Firefox Add-ons:  Upload content-dna-os-firefox.zip');
console.log('  Edge Add-ons:     Upload content-dna-os-chrome.zip (same as Chrome)');
