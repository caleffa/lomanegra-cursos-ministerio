const fs = require('fs-extra');
const concat = require('concat');
(async function build() {
  const files = [
    './dist/runtime.js',
    './dist/polyfills.js',
    './dist/scripts.js', 
    './dist/main.js'
  ];
  let actualFiles = []
  files.forEach(f => {
    try {
      if (fs.existsSync(f)) {
        actualFiles.push(f);
      }
    } catch(err) { }    
  });

  await fs.ensureDir('elements');
  await concat(actualFiles, 'elements/arbol-curso.js');
})();