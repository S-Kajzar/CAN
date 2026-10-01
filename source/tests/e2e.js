// Tests navigateur : node source/tests/e2e.js [dossier-captures]
"use strict";
const path = require("path");
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const URL = "file://" + path.join(__dirname, "..", "..", "index.html");
const SHOTS = process.argv[2] || null;
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });

const RIGHT = {
  q1_1: "4 bits", q1_2: "16", q1_3: "0,25 ms", q1_4: "4 kHz", q1_5: "0,25 V", q1_6: "64 bits",
  q1_7: "4 800 000 bits", q1_8: "585,94 ko", q2_1: "32", q2_2: "0,125 V", q2_4: "80 bits",
  q2_5: "6 000 000 bits", q2_6: "750 000 octets", q2_7: "732,42 ko", q3_1: "0,125 ms", q3_3: "160 bits",
  q3_4: "12 000 000 bits", q3_5: "1 500 000 octets", q3_6: "1 464,84 ko", q3_7: "2,5",
};

let fail = 0;
function check(cond, msg) { if (!cond) { fail++; console.log("ÉCHEC :", msg); } else console.log("ok :", msg); }

async function newPage(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("dialog", (d) => d.accept());
  await page.goto(URL);
  return { ctx, page, errors };
}

async function drawOn(page, id) {
  await page.locator("#" + id + " canvas").scrollIntoViewIfNeeded();
  const box = await page.locator("#" + id + " canvas").boundingBox();
  await page.mouse.move(box.x + box.width * 0.2, box.y + box.height * 0.3);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.5, box.y + box.height * 0.3, { steps: 6 });
  await page.mouse.up();
  const n = await page.evaluate((k) => window.__app__.sketches[k].strokes.length, id);
  check(n > 0, id + " : trait enregistré sur le canvas");
}

(async () => {
  const browser = await chromium.launch();

  // ---------- Accueil ----------
  {
    const { ctx, page, errors } = await newPage(browser);
    check(await page.locator("#home").isVisible(), "accueil visible au chargement");
    check(!(await page.locator("main.page").isVisible()), "sujet masqué tant qu'aucun mode n'est choisi");
    check(!(await page.locator(".banner").isVisible()), "bandeau masqué sur l'accueil");
    const txt = await page.locator("body").innerText();
    check(!/bac|brevet|bts|session|épreuve|cap |sti2d/i.test(txt + (await page.title())), "aucune mention d'origine du sujet");
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, "01-accueil.png"), fullPage: true });
    check(errors.length === 0, "aucune erreur JS (accueil) " + errors.join(" | "));
    await ctx.close();
  }

  // ---------- Entraînement : sujet parfait = 20/20 ----------
  {
    const { ctx, page, errors } = await newPage(browser);
    await page.click("button[data-mode=training]");
    check(await page.locator("main.page").isVisible(), "sujet visible en entraînement");
    check(await page.locator(".btn-print").count() === 1, "un seul bouton « Imprimer ma copie »");

    // Demi-point d'unité puis verrouillage
    await page.fill("#in-q1_3", "0,25");
    await page.click("#q1_3 .btn-validate");
    check(await page.locator("#q1_3").evaluate((e) => e.classList.contains("is-half")), "unité manquante : demi-point (orange)");
    check(/Unité manquante.*ms/.test(await page.locator("#q1_3 .q-unit-msg").innerText()), "message « Unité manquante » nommant ms");
    check(await page.locator("#in-q1_3").isDisabled(), "réponse validée verrouillée");
    check(await page.locator("#q1_3 .btn-validate").isDisabled(), "bouton Valider désactivé");
    check(await page.locator("#q1_3 .q-expl").isVisible(), "démarche affichée après validation");

    // Saisie vide : refus sans verrouillage
    await page.click("#q1_1 .btn-validate");
    check(!(await page.locator("#in-q1_1").isDisabled()) && (await page.locator("#q1_1 .q-msg").innerText()).length > 0,
      "saisie vide refusée sans verrouiller");

    // Tracé validé avant ses dépendances : correction retenue
    await drawOn(page, "sk_q2_3");
    await page.click("#sk_q2_3 .btn-sketch");
    check(!(await page.locator("#sk_q2_3 .selfeval").isVisible()), "correction du tracé masquée avant Q2.1 et Q2.2");
    check(/Q2\.1, Q2\.2/.test(await page.locator("#sk_q2_3 .sk-wait").innerText()), "message d'attente nommant Q2.1, Q2.2");

    // Recharger pour le parcours parfait
    await page.evaluate(() => { window.onbeforeunload = null; });
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await newPage(browser);
    await page.click("button[data-mode=training]");
    for (const [id, v] of Object.entries(RIGHT)) {
      await page.fill("#in-" + id, v);
      await page.click("#" + id + " .btn-validate");
      const ok = await page.locator("#" + id).evaluate((e) => e.classList.contains("is-ok"));
      check(ok, id + " juste avec « " + v + " »");
    }
    for (const id of ["sk_q2_3", "sk_q3_2"]) {
      await drawOn(page, id);
      await page.click("#" + id + " .btn-sketch");
      check(await page.locator("#" + id + " .selfeval").isVisible(), id + " : grille d'auto-évaluation affichée");
      check(await page.locator("#" + id + " .sk-corr-toggle input").isChecked(), id + " : correction superposée");
      if (SHOTS && id === "sk_q3_2") await page.locator("#" + id).screenshot({ path: path.join(SHOTS, "03-trace-corrige.png") });
      const boxes = page.locator("#" + id + " .selfeval input[data-crit]");
      for (let i = 0; i < await boxes.count(); i++) await boxes.nth(i).check();
      await page.click("#" + id + " .btn-self");
    }
    const fin = await page.locator(".recap .final-note").innerText();
    check(fin.replace(/\s/g, "") === "20,0/20", "sujet parfait : note finale " + fin);
    const banner = await page.locator("#score-val").innerText();
    check(/^20,0/.test(banner), "bandeau : " + banner.replace(/\n/g, ""));
    const rows = await page.locator("#recap-body tr").count();
    check(rows === 3, "récapitulatif : 3 parties");
    const weights = await page.locator("#recap-body tr td:nth-child(3)").allInnerTexts();
    check(weights.every((w) => w.replace(/\s/g, "") === "33,3%"), "poids au prorata des durées : " + weights.join(" / "));
    if (SHOTS) {
      await page.locator("#partie-1").screenshot({ path: path.join(SHOTS, "02-partie1-corrigee.png") });
      await page.locator("#recap").screenshot({ path: path.join(SHOTS, "04-recap.png") });
    }
    // Impression : corrections visibles, résumé avec mode et temps
    await page.emulateMedia({ media: "print" });
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    check(await page.locator(".print-summary").isVisible(), "impression : en-tête de copie");
    check(/entraînement/.test(await page.locator(".print-mode").innerText()), "impression : mode indiqué");
    check(/min|s/.test(await page.locator(".print-time").innerText()), "impression : temps de rédaction");
    check(await page.locator("#q1_1 .q-expl").isVisible(), "impression : corrections visibles");
    check(!(await page.locator(".banner").isVisible()) && !(await page.locator(".rail").isVisible()), "impression : bandeau et rail masqués");
    check(await page.locator("#sk_q2_3 .sk-print-corr").isVisible(), "impression : tracé corrigé imprimé");
    if (SHOTS) await page.pdf({ path: path.join(SHOTS, "copie-entrainement.pdf"), format: "A4" });
    await page.emulateMedia({ media: "screen" });

    // Fenêtre « Imprimer les DR »
    await page.evaluate(() => { window.print = () => {}; });
    const [popup] = await Promise.all([page.waitForEvent("popup"), page.click("#sk_q2_3 [data-act=drprint]")]);
    await popup.waitForLoadState();
    await popup.evaluate(() => { window.print = () => {}; });
    const sheets = await popup.locator(".sheet").count();
    check(sheets === 2, "Imprimer les DR : " + sheets + " feuilles");
    check(/2 pages/.test(await popup.locator(".bar p").innerText()), "Imprimer les DR : nombre de pages annoncé");
    check(/DR1/.test(await popup.locator(".sheet").first().innerText()) && /Nom/.test(await popup.locator(".sheet").first().innerText()),
      "Imprimer les DR : en-tête et ligne Nom");
    if (SHOTS) await popup.screenshot({ path: path.join(SHOTS, "05-dr.png") });
    check(errors.length === 0, "aucune erreur JS (entraînement) " + errors.join(" | "));
    await ctx.close();
  }

  // ---------- Examen ----------
  {
    const { ctx, page, errors } = await newPage(browser);
    await page.click("button[data-mode=exam]");
    check(!(await page.locator("#q1_1 .btn-validate").isVisible()), "examen : pas de bouton Valider");
    check(await page.locator(".exam-state").isVisible() && !(await page.locator(".score-block").isVisible()), "examen : note masquée");
    const answers = Object.entries(RIGHT).slice(0, 10);
    for (const [id, v] of answers) await page.fill("#in-" + id, v);
    await page.fill("#in-q1_1", "4");          // demi-point
    await page.fill("#in-q1_1", "4");
    await page.fill("#in-q1_2", "12");          // modifiable puis corrigée
    await page.fill("#in-q1_2", "16");
    await drawOn(page, "sk_q2_3");
    check(!(await page.locator("#q1_1 .q-expl").isVisible()), "examen : aucune correction pendant la composition");

    await page.emulateMedia({ media: "print" });
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    check(await page.locator(".print-nograde").isVisible(), "impression avant remise : « Copie non corrigée »");
    check(!(await page.locator("#q1_1 .q-expl").isVisible()), "impression avant remise : aucun corrigé");
    check(!(await page.locator(".print-note-line").isVisible()), "impression avant remise : aucune note");
    check(!(await page.locator("#sk_q2_3 .sk-print-corr").isVisible()), "impression avant remise : pas de tracé corrigé");
    await page.emulateMedia({ media: "screen" });

    await page.click("#exam-submit");
    const warn = await page.locator("#exam-warn").innerText();
    check(/10 réponse\(s\) encore vide/.test(warn), "confirmation en deux temps : " + warn);
    await page.click("#exam-submit");
    check(await page.locator("#in-q1_2").isDisabled(), "après remise : tout est verrouillé");
    check(await page.locator("#q1_1").evaluate((e) => e.classList.contains("is-half")), "après remise : demi-point d'unité");
    check(await page.locator("#q1_1 .q-expl").isVisible(), "après remise : corrections affichées");
    check(await page.locator("#sk_q2_3 .selfeval").isVisible(), "après remise : auto-évaluation proposée");
    const t1 = await page.locator("#timer-val").innerText();
    await page.waitForTimeout(1300);
    check(t1 === await page.locator("#timer-val").innerText(), "après remise : chronomètre arrêté (" + t1 + ")");
    const fin = await page.locator(".recap .final-note").innerText();
    console.log("   note examen partielle :", fin);
    check(await page.locator("#recap-graded").isVisible(), "après remise : récapitulatif affiché");
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, "06-examen-corrige.png") });
    check(errors.length === 0, "aucune erreur JS (examen) " + errors.join(" | "));
    await ctx.close();
  }

  // ---------- Mobile ----------
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    await page.goto(URL);
    await page.click("button[data-mode=training]");
    check(await page.locator("#btn-docs").isVisible(), "mobile : bouton Documents");
    const sw = await page.evaluate(() => document.documentElement.scrollWidth);
    check(sw <= 390, "mobile : pas de défilement horizontal (" + sw + ")");
    if (SHOTS) await page.screenshot({ path: path.join(SHOTS, "07-mobile.png") });
    await ctx.close();
  }

  await browser.close();
  console.log(fail ? fail + " échec(s)" : "tous les tests passent");
  process.exit(fail ? 1 : 0);
})();
