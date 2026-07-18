#!/usr/bin/env bash
# Fingilish keyboard — canonical build script
# Single source of truth: this repo (github.com/mattin-tasbihgoo/keyboards, branch fingilish).
#
# Encodes two hard-won ordering rules:
#  1. Dictionary pipeline order matters for the LEXICON (wordlist must be
#     BiDi-wrapped only after build_lexicon); build_dict.py is order-safe
#     since 2026-07-07 (strips BiDi on read).
#  2. kmc writes compiled output NEXT TO THE SOURCE unless --out-file is
#     given; the .kps packages from ../build/, so artifacts must be staged
#     into build/ before the .kps is compiled.
#
# Usage:
#   ./build.sh              # rebuild engine + keyboard + model packages
#   ./build.sh --lexicon    # also regenerate wordlist from raw CSVs first
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "--lexicon" ]]; then
  ( cd source/words && python3 build_lexicon.py && python3 wrap_bidi.py )
fi

# 1. Dictionary + conversion engine
# e2e harness (test_calljs.mjs) gates the build: non-zero exit aborts under set -e
( cd source/words && python3 build_dict.py && python3 build_calljs.py && node test_calljs.mjs )

# 1b. Custom-1.0 model sources: emit dict/fns from the converter's own build
#     products (single source, doc-04 L3/L4/L6)
( cd source/words && python3 model_emit.py )
cp source/words/ConvertWord.call_js source/ConvertWord.call_js

# 2. Compile keyboards (kmc drops outputs next to source)
mkdir -p build
# NOTE: both .kmn files declare VISUALKEYBOARD 'fingilish.kvks', so each
# compile emits a source/fingilish.kvk — stage fingilish's own artifacts
# BEFORE compiling fingilishlatin, then discard the latter's stray kvk.
kmc build source/fingilish.kmn
mv -f source/fingilish.js source/fingilish.kmx source/fingilish.kvk build/
kmc build source/fingilishlatin.kmn
mv -f source/fingilishlatin.js source/fingilishlatin.kmx build/ 2>/dev/null || true
rm -f source/fingilish.kvk source/fingilishlatin.kvk

# 3. Package keyboard (.kps reads from ../build/)
kmc build source/fingilish.kps --out-file build/fingilish.kmp

# 4. Lexical model
kmc build source/mattin.fa.fingilish.model.ts --out-file build/mattin.fa.fingilish.model.js
# Gate: the COMPILED model artifact must pass the predict() battery
node source/words/test_custom_model.mjs build/mattin.fa.fingilish.model.js
kmc build source/mattin.fa.fingilish.model.kps --out-file build/mattin.fa.fingilish.model.kmp

echo
echo "Artifacts:"
ls -la build/fingilish.kmp build/mattin.fa.fingilish.model.kmp
echo
echo "Deploy: cp build/*.kmp ~/Documents/fingilish/FingilishApp/Keyboards/"
echo "        then bump installFlag version in KeyboardViewController.swift"
