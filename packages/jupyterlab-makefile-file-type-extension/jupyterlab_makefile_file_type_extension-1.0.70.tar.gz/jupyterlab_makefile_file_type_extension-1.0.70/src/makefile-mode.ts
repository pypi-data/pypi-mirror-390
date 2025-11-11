import { StreamParser } from '@codemirror/language';

const variableRegex = /\$[\({][A-Za-z0-9_]+[\)}]/;
const shellVariableRegex = /\$\{[A-Za-z0-9_]+\}/;

export const makefile: StreamParser<{
  inRecipe: boolean;
  inComment: boolean;
  parenDepth: number;
  lastLineStart: number;
}> = {
  name: 'makefile',

  startState: () => ({
    inRecipe: false,
    inComment: false,
    parenDepth: 0,
    lastLineStart: -1
  }),

  token: (stream, state) => {
    const ch = stream.peek();

    // Reset paren depth only when moving to NEW line
    const currentLineStart = (stream as any).lineStart || 0;
    if (currentLineStart !== state.lastLineStart) {
      state.parenDepth = 0;
      state.lastLineStart = currentLineStart;
    }

    // Line continuation backslash at end of line (must be last char)
    if (ch === '\\') {
      const pos = stream.pos;
      stream.next();
      // Check if this is truly at end of line (no trailing whitespace)
      if (stream.eol()) {
        return 'keyword.control escape';
      }
      // Not at EOL, backtrack
      stream.pos = pos;
    }

    // Comments
    if (ch === '#') {
      stream.skipToEnd();
      return 'comment';
    }

    // Handle $( - MUST come before string handling
    if (ch === '$' && stream.match(/\$\(/, false)) {
      stream.next();
      stream.next();
      state.parenDepth++;

      // Check for known Make functions
      if (stream.match(/shell\b|wildcard\b|patsubst\b|filter\b|subst\b|foreach\b/, false)) {
        stream.match(/\w+/);
        return 'keyword';
      }

      return 'processingInstruction';
    }

    // Track nested ( inside $(...)
    if (ch === '(' && state.parenDepth > 0) {
      state.parenDepth++;
      stream.next();
      return null;
    }

    // Track ) inside $(...)
    if (ch === ')' && state.parenDepth > 0) {
      state.parenDepth--;
      stream.next();
      return state.parenDepth === 0 ? 'processingInstruction' : null;
    }

    // Strings - double quote
    if (ch === '"') {
      const pos = stream.pos;
      const line = (stream as any).string;
      console.log(`[STRING] pos=${pos} depth=${state.parenDepth} char="${ch}" line="${line}"`);
      if (state.parenDepth === 0) {
        stream.next();
        while (!stream.eol()) {
          const n = stream.next();
          if (n === '"') break;
          if (n === '\\') stream.next();
        }
        console.log(`[STRING] Parsed as string, consumed to pos=${stream.pos}`);
        return 'string';
      } else {
        stream.next();
        console.log(`[STRING] Parsed as atom (inside $())`);
        return 'atom';
      }
    }

    // Strings - single quote
    if (ch === "'") {
      if (state.parenDepth === 0) {
        stream.next();
        while (!stream.eol()) {
          const n = stream.next();
          if (n === "'") break;
          if (n === '\\') stream.next();
        }
        return 'string';
      } else {
        stream.next();
        return 'atom';
      }
    }

    // Recipe lines (commands starting with tab)
    if (stream.sol() && ch === '\t') {
      state.inRecipe = true;
      stream.next();
      return 'meta';
    }

    // Reset recipe state at start of non-tab line
    if (stream.sol() && ch !== '\t') {
      state.inRecipe = false;
    }

    // Inside recipe - treat as shell commands
    if (state.inRecipe) {
      // Variables in recipes
      if (ch === '$') {
        if (stream.match(variableRegex)) {
          return 'variableName';
        }
        stream.next();
        return 'variableName';
      }
      // Shell operators and keywords
      if (stream.match(/^(if|then|else|fi|for|in|do|done|case|esac|while|until)\b/)) {
        return 'keyword';
      }
      if (stream.match(/^(echo|cd|mkdir|rm|cp|mv|grep|sed|awk|make)\b/)) {
        return 'keyword';
      }
      stream.next();
      return null;
    }

    // Variable assignments (e.g., VERSION := ...)
    if (stream.sol() || stream.match(/^\s*/)) {
      const match = stream.match(/^[A-Z_][A-Z0-9_]*\s*[:?+]?=/, false);
      if (match) {
        const varName = stream.match(/^[A-Z_][A-Z0-9_]*/);
        if (varName) {
          stream.match(/\s*[:?+]?=/);
          return 'variableName.definition strong';
        }
      }
    }

    // Target definitions (e.g., build:)
    if (stream.sol() || (stream.match(/^\s*/) && stream.sol())) {
      const targetMatch = stream.match(/^[a-zA-Z0-9_-]+(?=\s*:)/);
      if (targetMatch) {
        return 'keyword.control strong';
      }
    }

    // Special targets (.PHONY, .DEFAULT_GOAL, etc.)
    if (stream.match(/^\.[A-Z_]+/)) {
      return 'keyword.control';
    }

    // Variable references - but ONLY if we're not starting a $(...)
    if (ch === '$' && !stream.match(/\$\(/, false)) {
      // Shell-style variables ${VAR}
      if (stream.match(shellVariableRegex)) {
        return 'variableName.special';
      }
      // Automatic variables $@, $<, etc.
      if (stream.match(/\$[@<^+?*%|]/)) {
        return 'variableName.special';
      }
      // Fallback for other $ uses
      stream.next();
      return 'variableName';
    }

    // Operators
    if (stream.match(/[:=]/) || stream.match(/[?+:]=/)) {
      return 'operator';
    }

    stream.next();
    return null;
  }
};
