// Check if extension loads properly
const fs = require('fs');
const path = require('path');

const extDir = '/Users/astewart/Library/Python/3.9/share/jupyter/labextensions/jupyterlab-biolm';
const staticDir = path.join(extDir, 'static');
const remoteEntry = path.join(staticDir, 'remoteEntry.f26ab13d8771cdd72a18.js');

console.log('Checking extension files...');
console.log('Extension dir exists:', fs.existsSync(extDir));
console.log('Static dir exists:', fs.existsSync(staticDir));
console.log('RemoteEntry exists:', fs.existsSync(remoteEntry));

if (fs.existsSync(remoteEntry)) {
  const content = fs.readFileSync(remoteEntry, 'utf8');
  const hasPlugin = content.includes('jupyterlab-biolm:plugin');
  const hasActivate = content.includes('activate');
  console.log('RemoteEntry contains plugin ID:', hasPlugin);
  console.log('RemoteEntry contains activate:', hasActivate);
  
  // Check for common issues
  if (!hasPlugin) {
    console.log('⚠️  WARNING: Plugin ID not found in remoteEntry');
  }
}
