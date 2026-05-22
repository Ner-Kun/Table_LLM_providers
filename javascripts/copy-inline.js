if (!window.location.pathname.includes("/changelog")) {
  const processedCodes = new WeakSet();

  function enhanceCodeElement(code) {
    if (processedCodes.has(code)) return;
    if (code.parentNode.hasAttribute("data-inline-code-wrapper")) return;
    if (code.closest(".models-modal")) return;

    processedCodes.add(code);

    const wrapper = document.createElement("span");
    wrapper.style.position = "relative";
    wrapper.style.display = "inline-flex";
    wrapper.style.alignItems = "center";
    wrapper.style.gap = "6px";
    wrapper.setAttribute("data-inline-code-wrapper", "true");

    const parent = code.parentNode;
    parent.insertBefore(wrapper, code);
    wrapper.appendChild(code);

    code.style.cursor = "pointer";
    code.style.transition = "all 0.2s ease";
    code.setAttribute("title", "Click to copy");

    const button = document.createElement("button");
    button.className = "md-clipboard md-icon";
    button.setAttribute("aria-label", "Copy");
    button.setAttribute("data-inline-copy", "true");
    button.style.padding = "4px";
    button.style.minWidth = "1.6em";
    button.style.height = "1.6em";
    button.style.border = "none";
    button.style.background = "transparent";
    button.style.cursor = "pointer";
    button.style.transition = "transform 0.2s ease";
    button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width: 1em; height: 1em;"><path d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12V1Z"/></svg>';

    function copyText(e) {
      e.stopPropagation();
      e.preventDefault();

      const text = code.textContent;
      navigator.clipboard.writeText(text).then(() => {
        button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width: 1em; height: 1em;"><path d="M21 7 9 19l-5.5-5.5 1.41-1.41L9 16.17 19.59 5.59 21 7Z"/></svg>';
        button.style.transform = "scale(1.3)";
        setTimeout(() => {
          button.style.transform = "scale(1)";
        }, 150);
        code.style.backgroundColor = "var(--md-accent-fg-color, #4caf50)";
        code.style.color = "white";
        code.style.transform = "scale(1.05)";

        setTimeout(() => {
          button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="width: 1em; height: 1em;"><path d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12V1Z"/></svg>';
          code.style.backgroundColor = "";
          code.style.color = "";
          code.style.transform = "";
        }, 1500);
      });
    }

    button.addEventListener("click", copyText);
    code.addEventListener("click", copyText);

    wrapper.appendChild(button);
  }

  function processAllCodeElements() {
    document.querySelectorAll("code:not(.highlight code)").forEach((code) => {
      enhanceCodeElement(code);
    });
    document.querySelectorAll('img.twemoji').forEach((emoji) => {
      emoji.removeAttribute('title');
    });
  }

  const style = document.createElement('style');
  style.textContent = `
    button[data-inline-copy]::after {
      display: none !important;
      content: none !important;
    }

    code:not(.highlight code):hover {
      opacity: 0.8;
    }

    button[data-inline-copy]:hover {
      transform: scale(1.2);
    }
  `;
  document.head.appendChild(style);

  processAllCodeElements();

  const observer = new MutationObserver((mutations) => {
    const needsProcessing = mutations.some((m) => m.addedNodes.length > 0);
    if (needsProcessing) {
      processAllCodeElements();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}
