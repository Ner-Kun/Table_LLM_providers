const tooltip = document.createElement("div");
tooltip.id = "provider-tooltip";
tooltip.className = "provider-tooltip";
tooltip.setAttribute("role", "tooltip");
tooltip.setAttribute("aria-hidden", "true");
tooltip.innerHTML = '<div class="provider-tooltip__content"></div>';
document.body.appendChild(tooltip);

const content = tooltip.querySelector(".provider-tooltip__content");
let activeTrigger = null;
let pinned = false;

let longPressTimer = null;
let longPressStartX = 0;
let longPressStartY = 0;
const LONG_PRESS_MS = 500;
const LONG_PRESS_MOVE_PX = 5;

function cancelLongPress() {
  if (longPressTimer) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }
}

document.addEventListener("pointerdown", (event) => {
  const trigger = event.target.closest(".provider-meta__warning");
  if (!trigger) return;

  longPressStartX = event.clientX;
  longPressStartY = event.clientY;

  longPressTimer = setTimeout(() => {
    longPressTimer = null;
    hideTooltip();
    const href = trigger.getAttribute("href");
    if (href) {
      window.location.href = href;
    }
  }, LONG_PRESS_MS);
}, true);

document.addEventListener("pointerup", cancelLongPress, true);
document.addEventListener("pointercancel", cancelLongPress, true);

document.addEventListener("pointermove", (event) => {
  if (!longPressTimer) return;
  const dx = event.clientX - longPressStartX;
  const dy = event.clientY - longPressStartY;
  if (Math.abs(dx) > LONG_PRESS_MOVE_PX || Math.abs(dy) > LONG_PRESS_MOVE_PX) {
    cancelLongPress();
  }
}, true);

function getTooltipText(trigger) {
  return (
    trigger.getAttribute("data-tooltip") ||
    trigger.getAttribute("aria-label") ||
    ""
  ).trim();
}

function setTooltipPosition(trigger) {
  const triggerRect = trigger.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();
  const viewportWidth = window.innerWidth;
  const gap = 10;
  const horizontalPadding = 8;

  const centeredLeft = triggerRect.left + triggerRect.width / 2;
  const maxLeft = viewportWidth - tooltipRect.width / 2 - horizontalPadding;
  const minLeft = tooltipRect.width / 2 + horizontalPadding;
  const left = Math.max(minLeft, Math.min(centeredLeft, maxLeft));

  const fitsAbove = triggerRect.top - tooltipRect.height - gap >= horizontalPadding;
  const top = fitsAbove
    ? triggerRect.top - gap
    : triggerRect.bottom + gap;

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
  tooltip.style.transform = fitsAbove
    ? "translate(-50%, -100%)"
    : "translate(-50%, 0)";
  tooltip.dataset.side = fitsAbove ? "top" : "bottom";
}

function hideTooltip() {
  if (!tooltip.classList.contains("provider-tooltip--visible")) {
    return;
  }

  tooltip.classList.remove("provider-tooltip--visible");
  tooltip.classList.remove("provider-tooltip--pinned");
  tooltip.setAttribute("aria-hidden", "true");

  if (activeTrigger) {
    activeTrigger.removeAttribute("aria-describedby");
    activeTrigger.setAttribute("aria-expanded", "false");
  }

  activeTrigger = null;
  pinned = false;
}

function showTooltip(trigger, shouldPin) {
  const text = getTooltipText(trigger);
  if (!text) {
    return;
  }

  activeTrigger = trigger;
  pinned = Boolean(shouldPin);
  content.textContent = text;

  tooltip.classList.add("provider-tooltip--visible");
  tooltip.classList.toggle("provider-tooltip--pinned", pinned);
  tooltip.setAttribute("aria-hidden", "false");
  tooltip.style.visibility = "hidden";

  setTooltipPosition(trigger);

  tooltip.style.visibility = "";
  trigger.setAttribute("aria-describedby", tooltip.id);
  trigger.setAttribute("aria-expanded", "true");
}

document.addEventListener(
  "pointerover",
  (event) => {
    if (event.pointerType === "touch") {
      return;
    }

    const trigger = event.target.closest("[data-tooltip]");
    if (!trigger) {
      return;
    }

    if (trigger === activeTrigger && tooltip.classList.contains("provider-tooltip--visible")) {
      return;
    }

    showTooltip(trigger, false);
  },
  true
);

document.addEventListener(
  "pointerout",
  (event) => {
    if (event.pointerType === "touch") {
      return;
    }

    const trigger = event.target.closest("[data-tooltip]");
    if (!trigger || trigger !== activeTrigger || pinned) {
      return;
    }

    const relatedTarget = event.relatedTarget;
    if (relatedTarget && (trigger.contains(relatedTarget) || tooltip.contains(relatedTarget))) {
      return;
    }

    hideTooltip();
  },
  true
);

document.addEventListener("focusin", (event) => {
  const trigger = event.target.closest("[data-tooltip]");
  if (!trigger) {
    return;
  }

  showTooltip(trigger, false);
});

document.addEventListener("focusout", (event) => {
  const trigger = event.target.closest("[data-tooltip]");
  if (!trigger || trigger !== activeTrigger || pinned) {
    return;
  }

  hideTooltip();
});

document.addEventListener(
  "click",
  (event) => {
    const trigger = event.target.closest("[data-tooltip]");
    if (trigger) {
      const text = getTooltipText(trigger);
      if (!text) {
        return;
      }

      if (activeTrigger === trigger && tooltip.classList.contains("provider-tooltip--visible") && pinned) {
        hideTooltip();
      } else {
        showTooltip(trigger, true);
      }

      event.preventDefault();
      event.stopPropagation();
      return;
    }

    if (tooltip.classList.contains("provider-tooltip--visible") && !tooltip.contains(event.target)) {
      hideTooltip();
    }
  },
  true
);

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape" || !tooltip.classList.contains("provider-tooltip--visible")) {
    return;
  }

  const trigger = activeTrigger;
  hideTooltip();

  if (trigger) {
    trigger.focus();
  }
});

window.addEventListener("resize", () => {
  if (tooltip.classList.contains("provider-tooltip--visible") && activeTrigger) {
    setTooltipPosition(activeTrigger);
  }
});

const scrollThreshold = 50;
let lastScrollY = window.scrollY;

window.addEventListener(
  "scroll",
  () => {
    if (!tooltip.classList.contains("provider-tooltip--visible")) return;
    const scrollDelta = Math.abs(window.scrollY - lastScrollY);
    if (scrollDelta >= scrollThreshold) {
      hideTooltip();
      lastScrollY = window.scrollY;
    }
  },
  { passive: true }
);
