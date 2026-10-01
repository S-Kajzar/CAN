// Tests unitaires de la correction : node source/tests/grading.test.js
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "..", "..", "index.html"), "utf8");
const grading = html.slice(html.indexOf("/*GRADING-START*/"), html.indexOf("/*GRADING-END*/"));
const config = html.match(/<script>(window\.__PARTS__[\s\S]*?)<\/script>/)[1];
const ctx = { window: {}, module: { exports: {} } };
vm.createContext(ctx);
vm.runInContext(grading + "\nthis.Grading = Grading;", ctx);
vm.runInContext(config, ctx);
const G = ctx.Grading;
const Q = ctx.window.__QCFG__;

// [id, saisie, score attendu]
const CASES = [
  ["q1_1", "4 bits", 1], ["q1_1", "4", 0.5], ["q1_1", "n = 4 bit", 1], ["q1_1", "16 bits", 0], ["q1_1", "4 octets", 0.5],
  ["q1_2", "16", 1], ["q1_2", "16 valeurs", 1], ["q1_2", "15", 0], ["q1_2", "2^4 = 16", 1],
  ["q1_3", "0,25 ms", 1], ["q1_3", "Te = 0.25ms", 1], ["q1_3", "250 µs", 1], ["q1_3", "250 μs", 1], ["q1_3", "250 us", 1],
  ["q1_3", "2,5×10^-4 s", 1], ["q1_3", "0,00025 s", 1], ["q1_3", "0,25", 0.5], ["q1_3", "0,25 s", 0.5],
  ["q1_3", "250", 0], ["q1_3", "0,27 ms", 0], ["q1_3", "4 ms", 0],
  ["q1_4", "4 kHz", 1], ["q1_4", "4000 Hz", 1], ["q1_4", "4 000 hz", 1], ["q1_4", "fe = 4 KHZ", 1], ["q1_4", "4", 0.5],
  ["q1_4", "4 Hz", 0.5], ["q1_4", "4000", 0], ["q1_4", "8 kHz", 0],
  ["q1_5", "0,25 V", 1], ["q1_5", "0.25 volt", 1], ["q1_5", "250 mV", 1], ["q1_5", "0,25", 0.5], ["q1_5", "0,27 V", 0],
  ["q1_5", "0,25 mV", 0.5],
  ["q1_6", "64 bits", 1], ["q1_6", "64", 0.5], ["q1_6", "64 octets", 0.5], ["q1_6", "16", 0],
  ["q1_7", "4 800 000 bits", 1], ["q1_7", "4800000 bits", 1], ["q1_7", "4,8×10^6 bits", 1], ["q1_7", "4,8.10^6 bits", 1],
  ["q1_7", "4,8 Mbit", 1], ["q1_7", "4,8 millions de bits", 1], ["q1_7", "4 800 000", 0.5], ["q1_7", "4,8", 0],
  ["q1_7", "1 200 000 bits", 0], ["q1_7", "4.8E6 bits", 1],
  ["q1_8", "585,94 ko", 1], ["q1_8", "585.94 Ko", 1], ["q1_8", "585,9375 kio", 1], ["q1_8", "585,94 kilo-octets", 1],
  ["q1_8", "585,94", 0.5], ["q1_8", "586 ko", 0], ["q1_8", "600 ko", 0], ["q1_8", "585,93 ko", 0], ["q1_8", "585,94 Mo", 0.5],
  ["q2_1", "32", 1], ["q2_1", "31", 0], ["q2_1", "2^5", 0],
  ["q2_2", "0,125 V", 1], ["q2_2", "125 mV", 1], ["q2_2", "0,125", 0.5], ["q2_2", "0,13 V", 0], ["q2_2", "0,129 V", 0],
  ["q2_4", "80 bits", 1], ["q2_4", "80", 0.5], ["q2_4", "64 bits", 0],
  ["q2_5", "6 000 000 bits", 1], ["q2_5", "6.10^6 bits", 1], ["q2_5", "6 Mbits", 1], ["q2_5", "6000000", 0.5], ["q2_5", "6", 0],
  ["q2_6", "750 000 octets", 1], ["q2_6", "750000 o", 1], ["q2_6", "0,75.10^6 octets", 1], ["q2_6", "750 000", 0.5],
  ["q2_6", "750 000 bits", 0.5], ["q2_6", "6 000 000 octets", 0],
  ["q2_7", "732,42 ko", 1], ["q2_7", "732,42", 0.5], ["q2_7", "732,4 ko", 0], ["q2_7", "750 ko", 0],
  ["q3_1", "0,125 ms", 1], ["q3_1", "125 µs", 1], ["q3_1", "1,25×10^-4 s", 1], ["q3_1", "0,125", 0.5], ["q3_1", "0,25 ms", 0],
  ["q3_1", "0,5 ms", 0],
  ["q3_3", "160 bits", 1], ["q3_3", "160", 0.5], ["q3_3", "80 bits", 0],
  ["q3_4", "12 000 000 bits", 1], ["q3_4", "1,2×10^7 bits", 1], ["q3_4", "12 Mbit", 1], ["q3_4", "12000000", 0.5],
  ["q3_4", "24 000 000 bits", 0],
  ["q3_5", "1 500 000 octets", 1], ["q3_5", "1,5.10^6 octets", 1], ["q3_5", "1500000", 0.5], ["q3_5", "1 500 000 bits", 0.5], ["q3_5", "750 000 octets", 0],
  ["q3_6", "1 464,84 ko", 1], ["q3_6", "1464.84 ko", 1], ["q3_6", "1464,84", 0.5], ["q3_6", "1464,85 ko", 0], ["q3_6", "1500 ko", 0],
  ["q3_7", "2,5", 1], ["q3_7", "x 2,5", 1], ["q3_7", "2.5 fois", 1], ["q3_7", "2", 0], ["q3_7", "1,25", 0],
];

let fail = 0;
const seen = new Set();
for (const [id, ans, want] of CASES) {
  seen.add(id);
  const r = G.grade(ans, Q[id].grader);
  const got = r.invalid ? "invalide" : r.score;
  if (got !== want) { fail++; console.log("ÉCHEC", id, JSON.stringify(ans), "attendu", want, "obtenu", got, JSON.stringify(r)); }
}
// Messages d'unité : « manquante » et « incorrecte »
const miss = G.grade("0,25", Q.q1_3.grader), wrong = G.grade("0,25 s", Q.q1_3.grader);
if (miss.unit !== "missing" || miss.unitLabel !== "ms") { fail++; console.log("ÉCHEC unité manquante", miss); }
if (wrong.unit !== "wrong") { fail++; console.log("ÉCHEC unité incorrecte", wrong); }
// Saisie vide refusée sans verrouiller
if (!G.grade("  ", Q.q1_1.grader).invalid) { fail++; console.log("ÉCHEC saisie vide"); }
if (!G.grade("je ne sais pas", Q.q1_3.grader).invalid) { fail++; console.log("ÉCHEC saisie sans nombre"); }
// Chaque question a au moins un cas juste et un cas faux
for (const id of Object.keys(Q)) {
  const mine = CASES.filter((c) => c[0] === id);
  if (!mine.some((c) => c[2] === 1) || !mine.some((c) => c[2] === 0)) { fail++; console.log("ÉCHEC couverture", id); }
}
console.log(CASES.length + 4 + " vérifications, " + fail + " échec(s)");
process.exit(fail ? 1 : 0);
