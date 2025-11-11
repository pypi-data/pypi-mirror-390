// Test script to verify string parsing logic

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

// Test the string parsing logic (matching makefile-mode.ts exactly)
function testStringParsing(testString) {
  console.log('\n' + '='.repeat(60));
  console.log(`Testing: "${testString}"`);
  console.log('='.repeat(60));

  const stream = new MockStream(testString);
  const tokens = [];
  let state = { parenDepth: 0, lastLineStart: -1 };

  while (!stream.eol()) {
    const startPos = stream.pos;
    const ch = stream.peek();
    let tokenType = null;

    // Comments
    if (ch === '#') {
      console.log(`  Pos ${startPos}: Comment, skipping rest of line`);
      while (!stream.eol()) stream.next();
      tokenType = 'comment';
    }
    // Handle $( - MUST come before string handling
    else if (ch === '$' && stream.match(/\$\(/, false)) {
      stream.next(); // consume $
      stream.next(); // consume (
      state.parenDepth++;
      console.log(`  Pos ${startPos}: Matched $(, incrementing depth to ${state.parenDepth}`);

      // Check for known Make functions
      if (stream.match(/shell\b|wildcard\b|patsubst\b|filter\b|subst\b|foreach\b/, false)) {
        const funcName = stream.match(/\w+/);
        console.log(`    -> Recognized Make function: ${funcName}`);
        tokenType = 'keyword';
      } else {
        tokenType = 'processingInstruction';
      }
    }
    // Track nested ( inside $(...)
    else if (ch === '(' && state.parenDepth > 0) {
      state.parenDepth++;
      stream.next();
      console.log(`  Pos ${startPos}: Found ( inside $(...), incrementing depth to ${state.parenDepth}`);
      tokenType = null;
    }
    // Track ) inside $(...)
    else if (ch === ')' && state.parenDepth > 0) {
      state.parenDepth--;
      stream.next();
      console.log(`  Pos ${startPos}: Matched ), decrementing depth to ${state.parenDepth}`);
      tokenType = state.parenDepth === 0 ? 'processingInstruction' : null;
    }
    // String parsing - double quotes
    else if (ch === '"') {
      console.log(`  Pos ${startPos}: Found " at depth=${state.parenDepth}`);
      if (state.parenDepth === 0) {
        stream.next(); // consume opening "
        let content = '';
        while (!stream.eol()) {
          const next = stream.next();
          if (next === '"') {
            console.log(`    -> Parsed as STRING: "${content}"`);
            break;
          }
          if (next === '\\') {
            content += next;
            if (!stream.eol()) {
              content += stream.next();
            }
          } else {
            content += next;
          }
        }
        tokenType = 'string';
      } else {
        stream.next();
        console.log(`    -> Parsed as ATOM (inside $())`);
        tokenType = 'atom';
      }
    }
    // String parsing - single quotes
    else if (ch === "'") {
      console.log(`  Pos ${startPos}: Found ' at depth=${state.parenDepth}`);
      if (state.parenDepth === 0) {
        stream.next(); // consume opening '
        let content = '';
        while (!stream.eol()) {
          const next = stream.next();
          if (next === "'") {
            console.log(`    -> Parsed as STRING: '${content}'`);
            break;
          }
          if (next === '\\') {
            content += next;
            if (!stream.eol()) {
              content += stream.next();
            }
          } else {
            content += next;
          }
        }
        tokenType = 'string';
      } else {
        stream.next();
        console.log(`    -> Parsed as ATOM (inside $())`);
        tokenType = 'atom';
      }
    }
    // Variable references - but ONLY if we're not starting a $(...)
    else if (ch === '$' && !stream.match(/\$\(/, false)) {
      // Shell-style variables ${VAR}
      if (stream.match(/\$\{[A-Za-z0-9_]+\}/)) {
        console.log(`  Pos ${startPos}: Matched shell variable`);
        tokenType = 'variableName.special';
      }
      // Automatic variables $@, $<, etc.
      else if (stream.match(/\$[@<^+?*%|]/)) {
        console.log(`  Pos ${startPos}: Matched automatic variable`);
        tokenType = 'variableName.special';
      }
      // Fallback for other $ uses
      else {
        stream.next();
        tokenType = 'variableName';
      }
    }
    // Default - consume one character
    else {
      stream.next();
      tokenType = 'default';
    }

    const text = testString.slice(startPos, stream.pos);
    tokens.push({ text, type: tokenType, start: startPos, end: stream.pos });

    if (tokenType !== 'default') {
      console.log(`  -> Token: [${startPos}-${stream.pos}] "${text}" -> ${tokenType}`);
    }
  }

  console.log('\nFinal token breakdown:');
  tokens.forEach(t => {
    if (t.type !== 'default' && t.type !== null) {
      console.log(`  [${t.start.toString().padStart(2)}-${t.end.toString().padStart(2)}] ${t.type.padEnd(20)} "${t.text}"`);
    }
  });

  return tokens;
}

// Run tests
console.log('\n' + '#'.repeat(60));
console.log('# STRING PARSING TESTS');
console.log('#'.repeat(60));

console.log('\n### Simple strings (from basic.mk) ###');
testStringParsing('"simple string"');
testStringParsing("'simple single'");
testStringParsing('"string with \'single\' inside"');
testStringParsing('\'string with "double" inside\'');

console.log('\n### Complex $(shell ...) constructs ###');
testStringParsing('$(shell echo "hello")');
testStringParsing('$(shell command -v node >/dev/null 2>&1 && node -p "require(\'./package.json\').version" || echo "0.0.0")');

console.log('\n### Full lines from basic.mk ###');
testStringParsing('TEST := "simple string"');
testStringParsing("TEST2 := 'simple single'");
testStringParsing('TEST3 := "string with \'single\' inside"');
testStringParsing('TEST4 := \'string with "double" inside\'');
