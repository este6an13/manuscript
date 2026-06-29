/* ============================================================
   MANUSCRIPT.JS — Codex Interactivity
   ============================================================
   Theme toggling, Python syntax highlighting, margin-note
   interactions, and page-load animations.
   ============================================================ */

(function () {
  'use strict';

  /* --- Helpers --- */
  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  /* ==========================================================
     1. THEME TOGGLE
     ========================================================== */
  function initThemeToggle() {
    var saved = localStorage.getItem('manuscript-theme');
    if (saved) {
      document.documentElement.setAttribute('data-theme', saved);
    } else if (!document.documentElement.getAttribute('data-theme')) {
      document.documentElement.setAttribute('data-theme', 'light');
    }

    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('manuscript-theme', next);
    });
  }

  /* ==========================================================
     2. PYTHON SYNTAX HIGHLIGHTING
     ========================================================== */
  var PY_KEYWORDS = [
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
    'break', 'class', 'continue', 'def', 'del', 'elif', 'else',
    'except', 'finally', 'for', 'from', 'global', 'if', 'import',
    'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
    'return', 'try', 'while', 'with', 'yield'
  ];

  var PY_BUILTINS = [
    'print', 'len', 'range', 'list', 'dict', 'set', 'tuple',
    'int', 'float', 'str', 'bytes', 'bool', 'complex',
    'max', 'min', 'sum', 'abs', 'round',
    'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter',
    'type', 'isinstance', 'issubclass', 'id', 'hash',
    'input', 'open', 'super', 'object',
    'any', 'all', 'iter', 'next', 'callable', 'chr', 'ord',
    'hex', 'oct', 'bin', 'repr', 'format', 'vars', 'dir',
    'getattr', 'setattr', 'hasattr', 'delattr', 'property',
    'staticmethod', 'classmethod',
    'ValueError', 'TypeError', 'KeyError', 'IndexError',
    'AttributeError', 'RuntimeError', 'StopIteration',
    'Exception', 'NotImplementedError', 'ZeroDivisionError',
    'FileNotFoundError', 'IOError', 'OSError', 'OverflowError',
    'MemoryError', 'RecursionError', 'ImportError',
    'ArithmeticError', 'LookupError', 'NameError',
    'SyntaxError', 'SystemError', 'UnicodeError'
  ];

  var keywordSet = {};
  PY_KEYWORDS.forEach(function (k) { keywordSet[k] = true; });
  var builtinSet = {};
  PY_BUILTINS.forEach(function (b) { builtinSet[b] = true; });

  function tokenizeLine(line) {
    var result = '';
    var i = 0;
    var len = line.length;

    while (i < len) {
      var ch = line[i];

      // Comments
      if (ch === '#') {
        result += '<span class="py-comment">' + escapeHtml(line.slice(i)) + '</span>';
        break;
      }

      // Strings (single and double quotes, including triple-quoted)
      if (ch === '"' || ch === "'") {
        var quote = ch;
        var strStart = i;
        var triple = (line.slice(i, i + 3) === quote + quote + quote);
        if (triple) {
          i += 3;
          while (i < len) {
            if (line[i] === '\\') { i += 2; continue; }
            if (line.slice(i, i + 3) === quote + quote + quote) { i += 3; break; }
            i++;
          }
        } else {
          i++;
          while (i < len) {
            if (line[i] === '\\') { i += 2; continue; }
            if (line[i] === quote) { i++; break; }
            i++;
          }
        }
        result += '<span class="py-string">' + escapeHtml(line.slice(strStart, i)) + '</span>';
        continue;
      }

      // Decorators
      if (ch === '@' && (i === 0 || /\s/.test(line[i - 1]))) {
        var decStart = i;
        i++;
        while (i < len && /[A-Za-z0-9_.]/.test(line[i])) i++;
        result += '<span class="py-decorator">' + escapeHtml(line.slice(decStart, i)) + '</span>';
        continue;
      }

      // Numbers
      if (/[0-9]/.test(ch) && (i === 0 || !/[A-Za-z_]/.test(line[i - 1]))) {
        var numStart = i;
        // Hex, oct, bin prefixes
        if (ch === '0' && i + 1 < len && /[xXoObB]/.test(line[i + 1])) {
          i += 2;
          while (i < len && /[0-9a-fA-F_]/.test(line[i])) i++;
        } else {
          while (i < len && /[0-9_.]/.test(line[i])) i++;
          // Exponent
          if (i < len && /[eE]/.test(line[i])) {
            i++;
            if (i < len && /[+-]/.test(line[i])) i++;
            while (i < len && /[0-9_]/.test(line[i])) i++;
          }
          // Complex literal
          if (i < len && line[i] === 'j') i++;
        }
        result += '<span class="py-number">' + escapeHtml(line.slice(numStart, i)) + '</span>';
        continue;
      }

      // Words (identifiers, keywords, builtins, self)
      if (/[A-Za-z_]/.test(ch)) {
        var wordStart = i;
        while (i < len && /[A-Za-z0-9_]/.test(line[i])) i++;
        var word = line.slice(wordStart, i);
        var escaped = escapeHtml(word);

        if (word === 'self') {
          result += '<span class="py-self">' + escaped + '</span>';
        } else if (keywordSet[word]) {
          result += '<span class="py-keyword">' + escaped + '</span>';
        } else if (builtinSet[word]) {
          result += '<span class="py-builtin">' + escaped + '</span>';
        } else {
          if (window.MANUSCRIPT_IMPORTS && window.MANUSCRIPT_IMPORTS[word]) {
            result += '<a href="' + window.MANUSCRIPT_IMPORTS[word] + '" class="py-link">' + escaped + '</a>';
          } else {
            result += escaped;
          }
        }
        continue;
      }

      // Everything else — operators, punctuation, whitespace
      result += escapeHtml(ch);
      i++;
    }

    return result;
  }

  function highlightPython() {
    var blocks = document.querySelectorAll('code.language-python');
    for (var b = 0; b < blocks.length; b++) {
      var code = blocks[b];
      var text = code.textContent;
      var lines = text.split('\n');

      // Remove trailing empty line from split
      if (lines.length > 0 && lines[lines.length - 1] === '') {
        lines.pop();
      }

      var html = '';
      for (var n = 0; n < lines.length; n++) {
        var highlighted = tokenizeLine(lines[n]);
        html += '<span class="code-line" data-line="' + (n + 1) + '">' + highlighted + '</span>\n';
      }

      // Post-process: wrap function/class names after def/class keywords
      html = html.replace(
        /(<span class="py-keyword">def<\/span> )([A-Za-z_]\w*)/g,
        '$1<span class="py-function">$2</span>'
      );
      html = html.replace(
        /(<span class="py-keyword">class<\/span> )([A-Za-z_]\w*)/g,
        '$1<span class="py-function">$2</span>'
      );

      code.innerHTML = html;
    }
  }

  /* ==========================================================
     3. MARGIN NOTE INTERACTION
     ========================================================== */
  function initMarginNotes() {
    var notes = document.querySelectorAll('.margin-note');
    for (var i = 0; i < notes.length; i++) {
      notes[i].addEventListener('click', handleNoteClick);
    }
  }

  function handleNoteClick(e) {
    var note = e.currentTarget;
    var lineRef = note.getAttribute('data-line');
    if (!lineRef) return;

    var section = note.closest('.section-content');
    if (!section) return;

    var wasActive = note.classList.contains('active');

    // Clear all highlights and active states in this section
    var allNotes = section.querySelectorAll('.margin-note');
    for (var i = 0; i < allNotes.length; i++) {
      allNotes[i].classList.remove('active');
    }
    var allHighlights = section.querySelectorAll('.code-line.line-highlight');
    for (var j = 0; j < allHighlights.length; j++) {
      allHighlights[j].classList.remove('line-highlight');
    }

    // If the note was not active, activate it and highlight lines
    if (!wasActive) {
      note.classList.add('active');
      var lineNums = lineRef.split(',');
      for (var k = 0; k < lineNums.length; k++) {
        var num = lineNums[k].trim();
        var codeLine = section.querySelector('.code-line[data-line="' + num + '"]');
        if (codeLine) {
          codeLine.classList.add('line-highlight');
        }
      }
    }
  }

  /* ==========================================================
     4. PAGE LOAD
     ========================================================== */
  document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();
    highlightPython();
    initMarginNotes();

    // Trigger codex fade-in animation
    var codex = document.querySelector('.codex');
    if (codex) {
      // Small delay for the browser to register the initial state
      requestAnimationFrame(function () {
        codex.classList.add('codex-visible');
      });
    }
  });
})();
