const fs = require('fs');
const html = fs.readFileSync('/Users/izzadev/.gemini/antigravity/scratch/hse-management-system/backend/static/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
let errors = [];

if (scriptMatch) {
    const script = scriptMatch[1];
    const lines = script.split('\n');

    // 1. Syntax check
    try {
        new Function(script);
        console.log('✅ JavaScript syntax: VALID');
    } catch (e) {
        console.log('❌ JavaScript syntax ERROR:', e.message);
        errors.push('Syntax: ' + e.message);
    }

    // 2. Brace balance check
    let openBraces = (script.match(/{/g) || []).length;
    let closeBraces = (script.match(/}/g) || []).length;
    let openParens = (script.match(/\(/g) || []).length;
    let closeParens = (script.match(/\)/g) || []).length;
    let openBrackets = (script.match(/\[/g) || []).length;
    let closeBrackets = (script.match(/\]/g) || []).length;

    if (openBraces === closeBraces) console.log('✅ Braces balanced:', openBraces);
    else { console.log('❌ Braces NOT balanced'); errors.push('Braces'); }

    if (openParens === closeParens) console.log('✅ Parens balanced:', openParens);
    else { console.log('❌ Parens NOT balanced'); errors.push('Parens'); }

    if (openBrackets === closeBrackets) console.log('✅ Brackets balanced:', openBrackets);
    else { console.log('❌ Brackets NOT balanced'); errors.push('Brackets'); }

    // 3. Check for duplicates
    const funcMatches = script.match(/function\s+(\w+)\s*\(/g) || [];
    const funcNames = funcMatches.map(m => m.match(/function\s+(\w+)/)[1]);
    const duplicates = funcNames.filter((name, i) => funcNames.indexOf(name) !== i);
    if (duplicates.length === 0) console.log('✅ No duplicate functions');
    else { console.log('❌ Duplicate functions:', duplicates); errors.push('Duplicates: ' + duplicates.join(', ')); }

    // 4. Check for actual corruption patterns
    // These are ACTUAL corruptions, not false positives from document.getElementById
    const corruptionPatterns = [
        { pattern: / nst /, name: 'corrupted const (nst)' },
        { pattern: / unction /, name: 'corrupted function (unction)' },
        { pattern: /\(\s*;/, name: 'empty first argument (;' },
        { pattern: /[^u]ment\.getE/, name: 'corrupted document (partial cut)' },
        { pattern: /documen[^t]/, name: 'corrupted document spelling' },
        { pattern: /\.valu[^e]/, name: 'corrupted .value' },
        { pattern: /\.valu;/, name: 'incomplete .value' },
    ];

    let corruptionFound = false;
    lines.forEach((line, i) => {
        corruptionPatterns.forEach(({ pattern, name }) => {
            if (pattern.test(line)) {
                console.log('❌ Corruption found:', name, 'at line', (i + 1), ':', line.trim().substring(0, 60));
                corruptionFound = true;
                errors.push(name + ' at line ' + (i + 1));
            }
        });
    });
    if (!corruptionFound) console.log('✅ No corruption patterns found');

    // 5. Check window exports
    const exportedFunctions = (script.match(/window\.(\w+)\s*=/g) || []).map(m => m.match(/window\.(\w+)/)[1]);
    console.log('📊 Window exports:', exportedFunctions.length, 'functions');

    // 6. Check total lines
    console.log('📊 JavaScript lines:', lines.length);
}

// 7. Check HTML structure
const htmlLines = html.split('\n').length;
console.log('📊 Total HTML lines:', htmlLines);

if (errors.length === 0) {
    console.log('\n🎉 ALL CHECKS PASSED - File is VALID');
    process.exit(0);
} else {
    console.log('\n❌ ERRORS FOUND:', errors.length);
    errors.forEach(e => console.log('  - ' + e));
    process.exit(1);
}
