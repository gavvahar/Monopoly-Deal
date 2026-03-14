/**
 * Monopoly Deal — play page interactivity
 * Handles the targeting modal, form submission, and auto-refresh.
 */

// Populated by the template via a <script> block
let GAME_DATA = {};

// Cards that require targeting (beyond a simple direct play)
const TARGETED_ACTIONS = {
  Repo_Notice: ["target_player"],
  Garage_Upgrade: ["own_color"],
  Luxury_Showroom: ["own_color"],
  Garage_Takeover: ["target_player", "steal_color"],
  Sneak_Swap: ["target_player", "target_card"],
  Tow_Trade: ["target_player", "target_card", "own_card"],
};

// Normalise a card name to a key used in TARGETED_ACTIONS
function actionKey(name) {
  return name.replace(/\s+/g, "_");
}

// Current modal state
const mstate = {
  cardIdx: null,
  cardName: null,
  cardType: null,
  cardColors: null,
  form: null,
  targetPlayer: null,
  targetCardIdx: null,
  targetColor: null,
  ownCardIdx: null,
};

// ─── Entry point ─────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  // Auto-refresh when it's not our turn
  if (
    typeof IS_MY_TURN !== "undefined" &&
    !IS_MY_TURN &&
    typeof GAME_STARTED !== "undefined" &&
    GAME_STARTED
  ) {
    startRefreshCountdown(6);
  }

  // Close modal when clicking the backdrop
  const dlg = document.getElementById("play-modal");
  if (dlg) {
    dlg.addEventListener("click", (e) => {
      if (e.target === dlg) closeModal();
    });
  }
});

function startRefreshCountdown(seconds) {
  const el = document.getElementById("refresh-countdown");
  if (!el) {
    setTimeout(() => location.reload(), seconds * 1000);
    return;
  }
  let remaining = seconds;
  el.textContent = `↻ ${remaining}s`;
  const interval = setInterval(() => {
    remaining--;
    if (remaining <= 0) {
      clearInterval(interval);
      location.reload();
    } else {
      el.textContent = `↻ ${remaining}s`;
    }
  }, 1000);
}

// ─── Play button handler ──────────────────────────────────────────────────────

function handlePlay(button, cardIdx, cardName, cardType, cardColors) {
  mstate.cardIdx = cardIdx;
  mstate.cardName = cardName;
  mstate.cardType = cardType;
  mstate.cardColors = cardColors;
  mstate.form = button.closest("form");
  mstate.targetPlayer = null;
  mstate.targetCardIdx = null;
  mstate.targetColor = null;
  mstate.ownCardIdx = null;

  if (!requiresModal(cardName, cardType, cardColors)) {
    mstate.form.submit();
    return;
  }

  openModal(cardName, cardType, cardColors);
}

function requiresModal(cardName, cardType, cardColors) {
  if (cardType === "wild" && cardColors && cardColors.length > 1) return true;
  if (cardType === "rent") return true;
  return !!TARGETED_ACTIONS[actionKey(cardName)];
}

// ─── Modal ────────────────────────────────────────────────────────────────────

const SECTION_IDS = [
  "section-wild-color",
  "section-rent-color",
  "section-target-player",
  "section-steal-color",
  "section-own-color",
  "section-target-card",
  "section-own-card",
];

function openModal(cardName, cardType, cardColors) {
  // Hide all targeting sections
  SECTION_IDS.forEach((id) => hide(id));

  document.getElementById("modal-title").textContent = `Play: ${cardName}`;
  document.getElementById("btn-confirm").disabled = true;

  if (cardType === "wild") {
    buildWildColors(cardColors);
  } else if (cardType === "rent") {
    buildRentSection(cardName);
  } else {
    buildActionSections(cardName);
  }

  document.getElementById("play-modal").showModal();
}

function closeModal() {
  document.getElementById("play-modal").close();
}

// ─── Section builders ─────────────────────────────────────────────────────────

function buildWildColors(colors) {
  const container = clearContainer("wild-color-options");
  colors.forEach((color) => {
    container.appendChild(
      makeColorBtn(color, color, () => {
        selectOnly(container, null);
        mstate.targetColor = color;
        refreshConfirm();
      })
    );
  });
  show("section-wild-color");
}

function buildRentSection(cardName) {
  const rentColors = GAME_DATA.rentCardColorMap[cardName] || [];
  const myColors = Object.keys(GAME_DATA.viewingStats.properties_by_color || {});
  const eligible = rentColors.filter((c) => myColors.includes(c));

  const container = clearContainer("rent-color-options");
  if (eligible.length === 0) {
    container.innerHTML =
      '<p class="empty-option">No matching properties owned.</p>';
  } else {
    eligible.forEach((color) => {
      const count =
        (GAME_DATA.viewingStats.properties_by_color[color] || []).length;
      container.appendChild(
        makeColorBtn(color, `${color} (${count} owned)`, () => {
          selectOnly(container, null);
          mstate.targetColor = color;
          refreshConfirm();
        })
      );
    });
  }
  show("section-rent-color");

  if (cardName === "Rent Wild (Any Collection)") {
    buildTargetPlayerSection("Charge wild rent to:");
  }
}

function buildActionSections(cardName) {
  const needs = TARGETED_ACTIONS[actionKey(cardName)] || [];

  if (needs.includes("target_player")) {
    const labels = {
      Repo_Notice: "Collect 5M from:",
      Garage_Takeover: "Steal complete set from:",
      Sneak_Swap: "Steal a property from:",
      Tow_Trade: "Swap a property with:",
    };
    buildTargetPlayerSection(labels[actionKey(cardName)] || "Target opponent:");
  }

  if (needs.includes("own_color")) {
    buildOwnColorSection(cardName);
  }

  if (needs.includes("own_card")) {
    buildOwnCardSection();
  }
}

function buildTargetPlayerSection(label) {
  setText("target-player-label", label);
  const container = clearContainer("target-player-buttons");

  GAME_DATA.opponentPlayers.forEach((opp) => {
    const stats = GAME_DATA.allPlayerStats[opp.name];
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-player-option";
    btn.dataset.player = opp.name;
    btn.innerHTML = `
      <span class="pop-name">${opp.name}</span>
      <span class="pop-stats">💰 ${stats.bank_total}M &nbsp;·&nbsp; ✅ ${stats.complete_sets}/3 &nbsp;·&nbsp; 🃏 ${opp.hand_count}</span>`;
    btn.onclick = () => {
      selectOnly(container, btn);
      mstate.targetPlayer = opp.name;
      mstate.targetCardIdx = null;
      mstate.targetColor = null;
      onTargetPlayerChosen(opp.name);
      refreshConfirm();
    };
    container.appendChild(btn);
  });

  show("section-target-player");
}

function onTargetPlayerChosen(playerName) {
  const key = actionKey(mstate.cardName);
  if (key === "Garage_Takeover") buildStealColorSection(playerName);
  if (key === "Sneak_Swap" || key === "Tow_Trade")
    buildTargetCardSection(playerName);
}

function buildStealColorSection(playerName) {
  setText("steal-color-label", `${playerName}'s complete sets:`);
  const container = clearContainer("steal-color-options");
  const oppStats = GAME_DATA.allPlayerStats[playerName];
  const complete = Object.entries(oppStats.color_progress || {})
    .filter(([, info]) => info.complete)
    .map(([c]) => c);

  if (complete.length === 0) {
    container.innerHTML =
      '<p class="empty-option">No complete sets to steal.</p>';
  } else {
    complete.forEach((color) => {
      container.appendChild(
        makeColorBtn(color, color, () => {
          selectOnly(container, null);
          mstate.targetColor = color;
          refreshConfirm();
        })
      );
    });
  }
  show("section-steal-color");
}

function buildTargetCardSection(playerName) {
  const container = clearContainer("target-card-options");
  const opp = GAME_DATA.opponentPlayers.find((p) => p.name === playerName);
  if (!opp) return;
  const oppStats = GAME_DATA.allPlayerStats[playerName];
  let shown = 0;

  (opp.properties || []).forEach((prop, idx) => {
    const color = prop.color || "";
    if (color && oppStats.color_progress?.[color]?.complete) return; // can't steal from complete set
    container.appendChild(
      makePropBtn(prop, () => {
        selectOnly(container, null);
        mstate.targetCardIdx = idx;
        refreshConfirm();
      })
    );
    shown++;
  });

  if (shown === 0) {
    container.innerHTML =
      '<p class="empty-option">No stealable properties (all in complete sets).</p>';
  }
  show("section-target-card");
}

function buildOwnColorSection(cardName) {
  const progress = GAME_DATA.viewingStats.color_progress || {};
  const idxStr = String(GAME_DATA.viewingPlayerIdx);
  const houses = GAME_DATA.houses[idxStr] || {};
  const hotels = GAME_DATA.hotels[idxStr] || {};
  const buildEligible = GAME_DATA.buildEligible || [];
  const key = actionKey(cardName);

  const eligible = Object.keys(progress).filter((c) => {
    if (!progress[c].complete || !buildEligible.includes(c)) return false;
    if (key === "Garage_Upgrade") return !houses[c] && !hotels[c];
    if (key === "Luxury_Showroom") return houses[c] && !hotels[c];
    return false;
  });

  const label =
    key === "Garage_Upgrade" ? "Add house (+3M rent) to:" : "Add hotel (+4M rent) to:";
  setText("own-color-label", label);
  const container = clearContainer("own-color-options");

  if (eligible.length === 0) {
    const msg =
      key === "Garage_Upgrade"
        ? "No complete sets available for a house."
        : "No complete sets with a house (and no hotel yet).";
    container.innerHTML = `<p class="empty-option">${msg}</p>`;
  } else {
    eligible.forEach((color) => {
      container.appendChild(
        makeColorBtn(color, color, () => {
          selectOnly(container, null);
          mstate.targetColor = color;
          refreshConfirm();
        })
      );
    });
  }
  show("section-own-color");
}

function buildOwnCardSection() {
  const container = clearContainer("own-card-options");
  const myProps = GAME_DATA.viewingProperties || [];
  const myStats = GAME_DATA.viewingStats;
  let shown = 0;

  myProps.forEach((prop, idx) => {
    const color = prop.color || "";
    if (color && myStats.color_progress?.[color]?.complete) return;
    container.appendChild(
      makePropBtn(prop, () => {
        selectOnly(container, null);
        mstate.ownCardIdx = idx;
        refreshConfirm();
      })
    );
    shown++;
  });

  if (shown === 0) {
    container.innerHTML =
      '<p class="empty-option">No swappable properties (all in complete sets).</p>';
  }
  show("section-own-card");
}

// ─── Confirm & submit ─────────────────────────────────────────────────────────

function confirmPlay() {
  const f = mstate.form;
  f.querySelector(".field-target-player").value = mstate.targetPlayer || "";
  f.querySelector(".field-target-card").value =
    mstate.targetCardIdx !== null ? mstate.targetCardIdx : "";
  f.querySelector(".field-target-color").value = mstate.targetColor || "";
  f.querySelector(".field-own-card").value =
    mstate.ownCardIdx !== null ? mstate.ownCardIdx : "";
  closeModal();
  f.submit();
}

function refreshConfirm() {
  const btn = document.getElementById("btn-confirm");
  if (!btn) return;

  const {
    cardName,
    cardType,
    cardColors,
    targetPlayer,
    targetCardIdx,
    targetColor,
    ownCardIdx,
  } = mstate;
  let ok = false;

  if (cardType === "wild") {
    ok = targetColor !== null;
  } else if (cardType === "rent") {
    ok = targetColor !== null;
    if (cardName === "Rent Wild (Any Collection)") ok = ok && targetPlayer !== null;
  } else {
    const needs = TARGETED_ACTIONS[actionKey(cardName)] || [];
    ok = needs.every((n) => {
      if (n === "target_player") return targetPlayer !== null;
      if (n === "steal_color" || n === "own_color") return targetColor !== null;
      if (n === "target_card") return targetCardIdx !== null;
      if (n === "own_card") return ownCardIdx !== null;
      return true;
    });
  }

  btn.disabled = !ok;
}

// ─── DOM helpers ──────────────────────────────────────────────────────────────

function makeColorBtn(color, label, onClick) {
  const hex = (GAME_DATA.colorMap || {})[color] || "#888";
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn-color-option";
  btn.style.cssText = `--chip-color: ${hex};`;
  btn.textContent = label;
  btn.onclick = () => {
    selectOnly(btn.parentElement, btn);
    onClick();
  };
  return btn;
}

function makePropBtn(prop, onClick) {
  const color = prop.color || "";
  const hex = color ? (GAME_DATA.colorMap || {})[color] || "#888" : "#888";
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn-prop-option";
  btn.style.cssText = `--chip-color: ${hex};`;
  btn.innerHTML = `<strong>${prop.name}</strong><small>${color || "Wild"} · ${prop.value}M</small>`;
  btn.onclick = () => {
    selectOnly(btn.parentElement, btn);
    onClick();
  };
  return btn;
}

function selectOnly(container, activeBtn) {
  if (!container) return;
  container.querySelectorAll("button").forEach((b) => b.classList.remove("selected"));
  if (activeBtn) activeBtn.classList.add("selected");
}

function clearContainer(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = "";
  return el;
}

function show(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "";
}

function hide(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "none";
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}
