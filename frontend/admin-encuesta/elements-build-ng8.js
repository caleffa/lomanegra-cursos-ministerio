const fs = require('fs-extra');
const concat = require('concat');
(async function build() {
  const files = [
    './dist/runtime-es2015.js',
    './dist/polyfills-es2015.js',
    './dist/scripts-es2015.js',
    './dist/main-es2015.js'
  ];
  const files_es5 = [
    './dist/runtime-es5.js',
    './dist/polyfills-es5.js',
    './dist/scripts-es5.js',
    './dist/main-es5.js'
  ];
  let actualFiles = [];
  files.forEach(f => {
    try {
      if (fs.existsSync(f)) {
        actualFiles.push(f);
      }
    } catch(err) { }    
  });

  await fs.ensureDir('elements');
  await concat(actualFiles, 'elements/admin-encuesta.js');

  actualFiles = [];
  files_es5.forEach(f => {
    try {
      if (fs.existsSync(f)) {
        actualFiles.push(f);
      }
    } catch(err) { }
  });
  await concat(actualFiles, 'elements/admin-encuesta-es5.js');
})();