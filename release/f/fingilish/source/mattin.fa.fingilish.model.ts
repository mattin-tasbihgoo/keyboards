const source: LexicalModelSource = {
  format: "trie-1.0",
  wordBreaker: { use: "default" },
  sources: ["words/fingilish.wordlist.tsv"],
  punctuation: {
    insertAfterWord: " ",
  },
};

export default source;