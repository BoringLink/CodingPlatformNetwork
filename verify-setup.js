#!/usr/bin/env node

/**
 * Frontend Setup Verification Script
 * Verifies that all required dependencies and configurations are in place
 */

import fs from 'fs';
import path from 'path';

const checks = [];

// Check if required files exist
const requiredFiles = [
  'package.json',
  'next.config.ts',
  'tsconfig.json',
  'tailwind.config.ts',
  'postcss.config.mjs',
  'components.json',
  'app/layout.tsx',
  'app/globals.css',
  'lib/utils.ts',
  'lib/api-client.ts',
  'components/ui/button.tsx',
  'components/providers/query-provider.tsx',
  'store/graph-store.ts',
  'store/ui-store.ts',
  'types/api.ts',
  'hooks/use-graph-data.ts',
];

console.log('🔍 Verifying frontend setup...\n');

// Check files
console.log('📁 Checking required files:');
requiredFiles.forEach(file => {
  const exists = fs.existsSync(path.join(import.meta.dirname, file));
  checks.push({ name: file, passed: exists });
  console.log(`  ${exists ? '✅' : '❌'} ${file}`);
});

// Check package.json dependencies
console.log('\n📦 Checking dependencies:');
const packageJson = JSON.parse(fs.readFileSync(path.join(import.meta.dirname, 'package.json'), 'utf8'));
const requiredDeps = [
  'next',
  'react',
  'react-dom',
  'typescript',
  'tailwindcss',
  '@tanstack/react-query',
  'zustand',
  'cytoscape',
  'react-cytoscapejs',
  'clsx',
  'tailwind-merge',
  'class-variance-authority',
];

requiredDeps.forEach(dep => {
  const exists = packageJson.dependencies?.[dep] || packageJson.devDependencies?.[dep];
  checks.push({ name: `dependency: ${dep}`, passed: !!exists });
  console.log(`  ${exists ? '✅' : '❌'} ${dep} ${exists ? `(${exists})` : ''}`);
});

// Summary
const passed = checks.filter(c => c.passed).length;
const total = checks.length;
const allPassed = passed === total;

console.log(`\n${'='.repeat(50)}`);
console.log(`📊 Summary: ${passed}/${total} checks passed`);
console.log(`${'='.repeat(50)}`);

if (allPassed) {
  console.log('\n✅ Frontend setup is complete and verified!');
  console.log('\n🚀 Next steps:');
  console.log('  1. Copy .env.local.example to .env.local');
  console.log('  2. Run: npm run dev');
  console.log('  3. Open: http://localhost:3000');
  process.exit(0);
} else {
  console.log('\n❌ Some checks failed. Please review the setup.');
  process.exit(1);
}
