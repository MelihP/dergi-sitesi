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