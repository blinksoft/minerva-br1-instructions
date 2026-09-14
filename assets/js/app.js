/* Minerva BR-1 assembly guide — progress, theme, lightbox.
   Progress is stored in this browser only (localStorage); nothing is sent anywhere. */
(function () {
  "use strict";
  var KEY = "minerva-br1-v1";

  /* ---- storage (never let a blocked/full store break the page) ---- */
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; }
    catch (err) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (err) { /* private mode */ }
  }
  var state = load();

  /* ---- checkboxes ---- */
  var boxes = Array.prototype.slice.call(document.querySelectorAll(".js-chk, .js-step"));
  var steps = Array.prototype.slice.call(document.querySelectorAll(".js-step"));
  var counter = document.getElementById("counter");
  var bar = document.getElementById("bar");

  function paint(box) {
    var card = box.closest(".step");
    if (card) card.classList.toggle("done", box.checked);
  }
  function tally() {
    var done = steps.filter(function (b) { return b.checked; }).length;
    if (counter) counter.textContent = done + " / " + steps.length;
    if (bar) bar.style.width = (steps.length ? (done / steps.length) * 100 : 0) + "%";
  }

  boxes.forEach(function (box) {
    box.checked = !!state[box.dataset.key];
    paint(box);
    box.addEventListener("change", function () {
      if (box.checked) { state[box.dataset.key] = 1; } else { delete state[box.dataset.key]; }
      save(state); paint(box); tally();
    });
  });
  tally();

  var reset = document.getElementById("reset");
  if (reset) reset.addEventListener("click", function () {
    if (!window.confirm("Clear every checkmark on this device?")) return;
    state = {}; save(state);
    boxes.forEach(function (b) { b.checked = false; paint(b); });
    tally();
  });

  /* ---- theme ---- */
  var themeBtn = document.getElementById("theme");
  var stored = null;
  try { stored = localStorage.getItem(KEY + ":theme"); } catch (err) { /* ignore */ }
  if (stored) document.documentElement.setAttribute("data-theme", stored);
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var root = document.documentElement;
    var isDark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    var next = isDark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem(KEY + ":theme", next); } catch (err) { /* ignore */ }
  });

  /* ---- lightbox ---- */
  var lb = document.getElementById("lb"),
      lbimg = document.getElementById("lbimg"),
      lbcap = document.getElementById("lbcap"),
      lbclose = document.getElementById("lbclose");

  function open(src, cap) {
    lbimg.src = src; lbimg.alt = cap; lbcap.textContent = cap;
    lb.classList.add("open"); document.body.style.overflow = "hidden";
  }
  function close() {
    lb.classList.remove("open"); lbimg.src = ""; document.body.style.overflow = "";
  }

  document.addEventListener("click", function (ev) {
    var wrap = ev.target.closest && ev.target.closest(".imgwrap");
    if (wrap) {
      var img = wrap.querySelector("img");
      if (img) open(img.src, img.alt || "");
      return;
    }
    if (ev.target === lb || ev.target === lbclose) close();
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape" && lb.classList.contains("open")) close();
  });
})();
