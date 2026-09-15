document.querySelectorAll("[data-slider]").forEach((slider) => {
    const slides = Array.from(
        slider.querySelectorAll("[data-slide]")
    );

    if (slides.length < 2) return;

    const previousButton = slider.querySelector("[data-prev]");
    const nextButton = slider.querySelector("[data-next]");
    const counter = slider.querySelector("[data-counter]");

    let currentIndex = 0;

    function showSlide(index) {
        currentIndex = (index + slides.length) % slides.length;

        slides.forEach((slide, slideIndex) => {
            slide.hidden = slideIndex !== currentIndex;
        });

        counter.textContent =
            `${currentIndex + 1} / ${slides.length}`;
    }

    previousButton.addEventListener("click", () => {
        showSlide(currentIndex - 1);
    });

    nextButton.addEventListener("click", () => {
        showSlide(currentIndex + 1);
    });
});

(() => {
    const launcher = document.getElementById("social-launcher");
    const panel = document.getElementById("social-panel");
    const closeButton = document.getElementById("social-close");

    if (!launcher || !panel || !closeButton) return;

    const tabs = Array.from(
        panel.querySelectorAll('[role="tab"]')
    );

    const feeds = Array.from(
        panel.querySelectorAll('[role="tabpanel"]')
    );

    function activateTab(selectedTab, moveFocus = false) {
        tabs.forEach((tab) => {
            const selected = tab === selectedTab;

            tab.setAttribute(
                "aria-selected",
                String(selected)
            );

            tab.tabIndex = selected ? 0 : -1;
        });

        const activePanelId =
            selectedTab.getAttribute("aria-controls");

        feeds.forEach((feed) => {
            feed.hidden = feed.id !== activePanelId;
        });

        panel.querySelector(".social-panel-body").scrollTop = 0;

        if (moveFocus) {
            selectedTab.focus();
        }
    }

    function openPanel() {
        panel.hidden = false;
        launcher.setAttribute("aria-expanded", "true");

        const activeTab = tabs.find(
            (tab) => tab.getAttribute("aria-selected") === "true"
        );

        if (activeTab) {
            activeTab.focus();
        } else {
            closeButton.focus();
        }
    }

    function closePanel() {
        panel.hidden = true;
        launcher.setAttribute("aria-expanded", "false");
        launcher.focus();
    }

    launcher.addEventListener("click", () => {
        if (panel.hidden) {
            openPanel();
        } else {
            closePanel();
        }
    });

    closeButton.addEventListener("click", closePanel);

    panel.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            event.preventDefault();
            closePanel();
        }
    });

    tabs.forEach((tab, index) => {
        tab.addEventListener("click", () => {
            activateTab(tab);
        });

        tab.addEventListener("keydown", (event) => {
            let nextIndex = index;

            if (event.key === "ArrowRight") {
                nextIndex = (index + 1) % tabs.length;
            } else if (event.key === "ArrowLeft") {
                nextIndex = (index - 1 + tabs.length) % tabs.length;
            } else if (event.key === "Home") {
                nextIndex = 0;
            } else if (event.key === "End") {
                nextIndex = tabs.length - 1;
            } else {
                return;
            }

            event.preventDefault();
            activateTab(tabs[nextIndex], true);
        });
    });
})();