// Keep the home menu briefly in view, then fade it as the reader scrolls.
(() => {
    if (!document.body.classList.contains("home-with-slider-gap")) return;

    const header = document.querySelector(".site-header");
    if (!header) return;

    const socialBar = document.querySelector(".social-bar");
    const menu = header.querySelector("[data-menu]");
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let socialBarHeight = socialBar?.offsetHeight || 0;
    let framePending = false;

    const update = () => {
        framePending = false;
        const interacting = menu?.classList.contains("is-open") ||
            header.querySelector(":focus-visible");
        const distance = Math.max(0, window.scrollY - socialBarHeight);
        const progress = interacting ? 0 : Math.min(1, Math.max(0, (distance - 110) / 220));
        const fade = progress * progress * (3 - 2 * progress);

        header.style.setProperty("--home-menu-opacity", String(1 - fade));
        header.style.setProperty("--home-menu-shift", `${reducedMotion.matches ? 0 : -16 * fade}px`);
        header.classList.toggle("is-scroll-hidden", progress === 1);
    };

    const scheduleUpdate = () => {
        if (framePending) return;
        framePending = true;
        window.requestAnimationFrame(update);
    };

    window.addEventListener("scroll", scheduleUpdate, { passive: true });
    window.addEventListener("resize", () => {
        socialBarHeight = socialBar?.offsetHeight || 0;
        scheduleUpdate();
    });
    window.addEventListener("pageshow", scheduleUpdate);
    header.addEventListener("focusin", scheduleUpdate);
    header.addEventListener("focusout", scheduleUpdate);
    header.addEventListener("click", scheduleUpdate);
    header.addEventListener("keydown", scheduleUpdate);
    reducedMotion.addEventListener("change", scheduleUpdate);
    update();
})();

(() => {
    const menuButton = document.querySelector("[data-menu-toggle]");
    const menu = document.querySelector("[data-menu]");

    if (!menuButton || !menu) return;

    const closeMenu = () => {
        menuButton.setAttribute("aria-expanded", "false");
        menu.classList.remove("is-open");
    };

    menuButton.addEventListener("click", () => {
        const willOpen =
            menuButton.getAttribute("aria-expanded") !== "true";

        menuButton.setAttribute(
            "aria-expanded",
            String(willOpen)
        );

        menu.classList.toggle("is-open", willOpen);
    });

    menu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 980) {
            closeMenu();
        }
    });
})();


document.querySelectorAll("[data-slider]").forEach((slider) => {
    const slides = Array.from(
        slider.querySelectorAll("[data-slide]")
    );

    if (slides.length < 2) return;

    const previousButton =
        slider.querySelector("[data-prev]");

    const nextButton =
        slider.querySelector("[data-next]");

    const pauseButton =
        slider.querySelector("[data-pause]");

    const pauseIcon =
        slider.querySelector("[data-pause-icon]");

    const counter =
        slider.querySelector("[data-counter]");

    const dots = Array.from(
        slider.querySelectorAll("[data-dot]")
    );

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    const interval =
        Number(slider.dataset.autoplay) || 6000;

    let currentIndex = 0;
    let timer = null;
    let userPaused = reducedMotion.matches;
    let pointerStartX = null;


    const showSlide = (index) => {
        currentIndex =
            (index + slides.length) % slides.length;

        slides.forEach((slide, slideIndex) => {
            const isActive =
                slideIndex === currentIndex;

            slide.hidden = !isActive;

            slide.setAttribute(
                "aria-hidden",
                String(!isActive)
            );
        });

        dots.forEach((dot, dotIndex) => {
            dot.setAttribute(
                "aria-current",
                String(dotIndex === currentIndex)
            );
        });

        if (counter) {
            counter.textContent =
                `${currentIndex + 1} / ${slides.length}`;
        }
    };


    const stopAutoplay = () => {
        window.clearInterval(timer);
        timer = null;
    };


    const startAutoplay = () => {
        stopAutoplay();

        const isInteracting =
            slider.matches(":hover") ||
            slider.contains(document.activeElement);

        if (
            userPaused ||
            reducedMotion.matches ||
            document.hidden ||
            isInteracting
        ) {
            return;
        }

        timer = window.setInterval(() => {
            showSlide(currentIndex + 1);
        }, interval);
    };


    const resetAutoplay = () => {
        stopAutoplay();
        startAutoplay();
    };


    const updatePauseButton = () => {
        if (!pauseButton || !pauseIcon) return;

        if (reducedMotion.matches) {
            pauseButton.disabled = true;

            pauseButton.setAttribute(
                "aria-label",
                "Hareket azaltma ayarı nedeniyle otomatik geçiş kapalı"
            );

            pauseIcon.textContent = "▶";
            return;
        }

        pauseButton.disabled = false;

        pauseButton.setAttribute(
            "aria-label",
            userPaused
                ? "Otomatik geçişi başlat"
                : "Otomatik geçişi durdur"
        );

        pauseIcon.textContent =
            userPaused ? "▶" : "Ⅱ";
    };


    previousButton?.addEventListener("click", () => {
        showSlide(currentIndex - 1);
        resetAutoplay();
    });


    nextButton?.addEventListener("click", () => {
        showSlide(currentIndex + 1);
        resetAutoplay();
    });


    dots.forEach((dot) => {
        dot.addEventListener("click", () => {
            showSlide(
                Number(dot.dataset.slideTo)
            );

            resetAutoplay();
        });
    });


    pauseButton?.addEventListener("click", () => {
        userPaused = !userPaused;

        updatePauseButton();

        if (userPaused) {
            stopAutoplay();
        } else {
            startAutoplay();
        }
    });


    slider.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") {
            showSlide(currentIndex - 1);
            resetAutoplay();
        } else if (event.key === "ArrowRight") {
            showSlide(currentIndex + 1);
            resetAutoplay();
        }
    });


    slider.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "touch") {
            pointerStartX = event.clientX;
        }
    });


    slider.addEventListener("pointerup", (event) => {
        if (pointerStartX === null) return;

        const distance =
            event.clientX - pointerStartX;

        pointerStartX = null;

        if (Math.abs(distance) < 50) return;

        showSlide(
            currentIndex + (distance < 0 ? 1 : -1)
        );

        resetAutoplay();
    });


    slider.addEventListener(
        "mouseenter",
        stopAutoplay
    );

    slider.addEventListener(
        "mouseleave",
        startAutoplay
    );

    slider.addEventListener(
        "focusin",
        stopAutoplay
    );

    slider.addEventListener("focusout", (event) => {
        if (!slider.contains(event.relatedTarget)) {
            window.setTimeout(
                startAutoplay,
                0
            );
        }
    });


    document.addEventListener(
        "visibilitychange",
        () => {
            if (document.hidden) {
                stopAutoplay();
            } else {
                startAutoplay();
            }
        }
    );


    reducedMotion.addEventListener?.(
        "change",
        () => {
            updatePauseButton();

            if (reducedMotion.matches) {
                stopAutoplay();
            } else {
                startAutoplay();
            }
        }
    );


    showSlide(0);
    updatePauseButton();
    startAutoplay();
});
(() => {
    const launcher = document.getElementById("social-launcher");
    const panel = document.getElementById("social-panel");
    if (!launcher || !panel) return;
    const closeButton = document.getElementById("social-close");
    const tabs = Array.from(panel.querySelectorAll('[role="tab"]'));
    const scripts = new Map();
    const loadEmbedScript = (provider) => {
        if (scripts.has(provider)) return scripts.get(provider);
        const promise = new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = provider === "instagram"
                ? "https://www.instagram.com/embed.js"
                : "https://platform.twitter.com/widgets.js";
            script.async = true;
            const fail = () => {
                window.clearTimeout(timeout);
                script.remove();
                reject(new Error("Gönderi önizlemesi yüklenemedi."));
            };
            const timeout = window.setTimeout(fail, 15000);
            script.onload = () => { window.clearTimeout(timeout); resolve(); };
            script.onerror = fail;
            document.head.appendChild(script);
        });
        scripts.set(provider, promise);
        promise.catch(() => scripts.delete(provider));
        return promise;
    };
    const loadEmbeds = (feed) => {
        if (!feed || feed.hidden || panel.hidden) return;
        const embeds = Array.from(feed.querySelectorAll("[data-social-embed]"));
        const providers = new Set(embeds.map((embed) => embed.dataset.socialEmbed));
        providers.forEach((provider) => {
            if (!["x", "instagram"].includes(provider)) return;
            loadEmbedScript(provider).then(() => {
                if (feed.hidden || panel.hidden) return;
                if (provider === "x" && !window.twttr?.widgets?.load) return;
                if (provider === "instagram" && !window.instgrm?.Embeds?.process) return;
                embeds.filter((embed) => embed.dataset.socialEmbed === provider).forEach((embed) => {
                    if (embed.dataset.initialized) return;
                    const blockquote = document.createElement("blockquote");
                    const link = document.createElement("a");
                    link.href = embed.dataset.postUrl;
                    link.textContent = provider === "x" ? "X gönderisini görüntüle ↗" : "Instagram gönderisini görüntüle ↗";
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    blockquote.appendChild(link);
                    if (provider === "instagram") {
                        blockquote.className = "instagram-media";
                        blockquote.setAttribute("data-instgrm-permalink", embed.dataset.postUrl);
                        blockquote.setAttribute("data-instgrm-version", "14");
                    } else {
                        blockquote.className = "twitter-tweet";
                        blockquote.setAttribute("data-lang", "tr");
                        blockquote.setAttribute("data-dnt", "true");
                        blockquote.setAttribute("data-conversation", "none");
                    }
                    embed.replaceChildren(blockquote);
                    embed.dataset.initialized = "true";
                });
                if (provider === "instagram") window.instgrm.Embeds.process();
                else window.twttr.widgets.load(feed);
            }).catch(() => {
                // Keep the original post link if the platform is unavailable.
            });
        });
    };
    const selectTab = (tab) => {
        tabs.forEach((item) => {
            const selected = item === tab;
            item.setAttribute("aria-selected", String(selected));
            item.tabIndex = selected ? 0 : -1;
            document.getElementById(item.getAttribute("aria-controls")).hidden = !selected;
        });
        loadEmbeds(document.getElementById(tab.getAttribute("aria-controls")));
    };
    const close = (restoreFocus = false) => {
        panel.hidden = true;
        launcher.setAttribute("aria-expanded", "false");
        launcher.setAttribute("aria-label", "Son sosyal medya paylaşımlarını aç");
        if (restoreFocus) launcher.focus();
    };
    launcher.addEventListener("click", () => {
        if (!panel.hidden) { close(); return; }
        panel.hidden = false;
        launcher.setAttribute("aria-expanded", "true");
        launcher.setAttribute("aria-label", "Sosyal medya panelini kapat");
        const activeTab = tabs.find((tab) => tab.getAttribute("aria-selected") === "true");
        activeTab?.focus();
        if (activeTab) loadEmbeds(document.getElementById(activeTab.getAttribute("aria-controls")));
    });
    closeButton?.addEventListener("click", () => close(true));
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !panel.hidden) close(true);
    });
    document.addEventListener("click", (event) => {
        if (!panel.hidden && !panel.contains(event.target) && !launcher.contains(event.target)) {
            close(panel.contains(document.activeElement));
        }
    });
    tabs.forEach((tab, index) => {
        tab.addEventListener("click", () => selectTab(tab));
        tab.addEventListener("keydown", (event) => {
            let target;
            if (event.key === "ArrowRight") target = tabs[(index + 1) % tabs.length];
            if (event.key === "ArrowLeft") target = tabs[(index - 1 + tabs.length) % tabs.length];
            if (event.key === "Home") target = tabs[0];
            if (event.key === "End") target = tabs[tabs.length - 1];
            if (target) { event.preventDefault(); selectTab(target); target.focus(); }
        });
    });
})();
