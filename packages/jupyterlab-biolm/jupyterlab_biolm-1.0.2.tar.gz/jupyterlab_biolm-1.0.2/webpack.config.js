const path = require('path');

// Use JupyterLab's extension config
const extensionConfig = require('@jupyterlab/builder/lib/extensionConfig').default;

module.exports = [
  extensionConfig({
    packagePath: __dirname,
    outputDir: path.resolve(__dirname, 'jupyterlab_biolm/labextension'),
    devMode: true
  })
];
