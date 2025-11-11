// Test script to show exact tokenization of test.mk lines

// Simulate the stream interface
class MockStream {
  constructor(text) {
    this.text = text;
    this.pos = 0;
  }

  peek() {
    if (this.pos >= this.text.length) return null;
    return this.text[this.pos];
  }

  next() {
    if (this.pos >= this.text.length) return null;
    return this.text[this.pos++];
  }

  eol() {
    return this.pos >= this.text.length;
  }

  match(pattern, consume = true) {
    const remaining = this.text.slice(this.pos);
    const match = remaining.match(pattern);
    if (match && match.index === 0) {
      if (consume) {
        this.pos += match[0].length;
      }
      return match[0];
    }
    return null;
  }

  sol() {
    return this.pos === 0;
  }
}

// Tokenize a line and show all tokens
function tokenizeLine(line) {
  const stream = new MockStream(line);
  const tokens = [];
  let state = { parenDepth: 0, inRecipe: false, inComment: false };

  while (!stream.eol()) {
    const startPos = stream.pos;
    const ch = stream.peek();
    let tokenType = null;

    // Comments
    if (ch === '#') {
      stream.skipToEnd();
      tokenType = 'comment';
    }
    // Handle $( constructs
    else if (ch === '$' && stream.match(/\$\(/, false)) {
      stream.next(); // consume $
      stream.next(); // consume (
      state.parenDepth++;
      tokenType = 'processingInstruction';
    }
    // Track ALL opening parentheses when inside $(...)
    else if (ch === '(' && state.parenDepth > 0) {
      state.parenDepth++;
      stream.next();
      tokenType = 'paren';
    }
    // Closing ) when inside $(...)
    else if (ch === ')' && state.parenDepth > 0) {
      state.parenDepth--;
      stream.next();
      tokenType = state.parenDepth === 0 ? 'processingInstruction' : 'paren';
    }
    // String parsing - double quotes
    else if (ch === '"') {
      if (state.parenDepth === 0) {
        stream.next(); // consume opening "
        while (!stream.eol()) {
          const next = stream.next();
          if (next === '"') {
            break;
          }
          if (next === '\\') {
            stream.next();
          }
        }
        tokenType = 'string';
      } else {
        stream.next();
        tokenType = 'atom';
      }
    }
    // String parsing - single quotes
    else if (ch === "'") {
      if (state.parenDepth === 0) {
        stream.next(); // consume opening '
        while (!stream.eol()) {
          const next = stream.next();
          if (next === "'") {
            break;
          }
          if (next === '\\') {
            stream.next();
          }
        }
        tokenType = 'string';
      } else {
        stream.next();
        tokenType = 'atom';
      }
    }
    // Variable assignments
    else if (stream.sol() || stream.match(/^\s*/)) {
      const match = stream.match(/^[A-Z_][A-Z0-9_]*\s*[:?+]?=/, false);
      if (match) {
        const varName = stream.match(/^[A-Z_][A-Z0-9_]*/);
        if (varName) {
          stream.match(/\s*[:?+]?=/);
          tokenType = 'variableName';
        }
      }
    }

    // Default - consume one character
    if (stream.pos === startPos) {
      stream.next();
      tokenType = tokenType || null;
    }

    const text = line.slice(startPos, stream.pos);
    tokens.push({
      text,
      type: tokenType,
      start: startPos,
      end: stream.pos,
      depth: state.parenDepth
    });
  }

  return tokens;
}

// Display tokens with color-coded output
function displayTokens(lineNum, line, tokens) {
  console.log('\n' + '='.repeat(80));
  console.log(`Line ${lineNum}: ${line}`);
  console.log('='.repeat(80));

  // Show visual representation
  let visual = '';
  let lastPos = 0;

  tokens.forEach(token => {
    // Pad to position
    while (lastPos < token.start) {
      visual += ' ';
      lastPos++;
    }

    // Add token marker
    const marker = token.type ? token.type.charAt(0).toUpperCase() : '-';
    visual += marker.repeat(token.text.length);
    lastPos = token.end;
  });

  console.log('Visual:');
  console.log(line);
  console.log(visual);
  console.log('\nTokens:');

  tokens.forEach(token => {
    if (token.type) {
      const typeStr = token.type.padEnd(22);
      const posStr = `[${token.start.toString().padStart(3)}-${token.end.toString().padStart(3)}]`;
      const depthStr = token.depth > 0 ? ` depth=${token.depth}` : '';
      console.log(`  ${posStr} ${typeStr}${depthStr} "${token.text}"`);
    }
  });
}

// Test lines from test.mk
const testLines = [
  { num: 3, line: 'VERSION := $(shell command -v node >/dev/null 2>&1 && node -p "require(\'./package.json\').version" || echo "0.0.0")' },
  { num: 14, line: 'TEST := "simple string"' },
  { num: 20, line: "TEST2 := 'simple single'" },
  { num: 21, line: 'TEST3 := "string with \'single\' inside"' },
  { num: 22, line: "TEST4 := 'string with \"double\" inside'" }
];

console.log('\n' + '#'.repeat(80));
console.log('# TOKENIZATION RESULTS FOR test.mk');
console.log('#'.repeat(80));
console.log('\nLegend:');
console.log('  P = processingInstruction ($(, ))');
console.log('  S = string');
console.log('  A = atom (quotes inside $(...))');
console.log('  V = variableName');
console.log('  C = comment');
console.log('  - = null/default');

testLines.forEach(({ num, line }) => {
  const tokens = tokenizeLine(line);
  displayTokens(num, line, tokens);
});
