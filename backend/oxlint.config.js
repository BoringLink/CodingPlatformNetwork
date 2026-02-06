module.exports = {
  extends: ['eslint:recommended'],
  rules: {
    'no-unused-vars': 'error',
    'no-console': 'warn',
    'prefer-const': 'error'
  },
  ignorePatterns: [
    'node_modules',
    'dist',
    'build',
    '.env'
  ]
};
