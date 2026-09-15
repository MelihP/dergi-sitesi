document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.querySelector(
        ".rich-editor-source"
    );

    if (!textarea) return;

    const form = textarea.closest("form");

    const wrapper = document.createElement("div");
    wrapper.className = "dergi-editor";

    textarea.before(wrapper);
    wrapper.append(textarea);

    const message = document.createElement("p");
    message.className = "editor-message";
    message.setAttribute("role", "status");

    if (!window.Quill) {
        textarea.readOnly = true;

        message.textContent =
            "Editör yüklenemedi. İnternet bağlantını kontrol edip sayfayı yenile.";

        wrapper.append(message);

        form.addEventListener("submit", (event) => {
            event.preventDefault();

            alert(
                "Editör yüklenemediği için kayıt yapılmadı. Sayfayı yenile."
            );
        });

        return;
    }

    const container = document.createElement("div");
    wrapper.append(container);

    const editor = new Quill(container, {
        theme: "snow",

        formats: [
            "header",
            "bold",
            "italic",
            "underline",
            "strike",
            "blockquote",
            "list",
            "link",
        ],

        modules: {
            toolbar: [
                [{ header: [2, 3, false] }],
                ["bold", "italic", "underline", "strike"],
                [
                    { list: "ordered" },
                    { list: "bullet" },
                ],
                ["blockquote", "link"],
                ["clean"],
            ],
        },
    });

    editor.clipboard.dangerouslyPasteHTML(
        textarea.value
    );

    textarea.hidden = true;
    textarea.required = false;

    editor.root.setAttribute(
        "aria-label",
        "Yazı metni"
    );

    editor.root.setAttribute(
        "aria-multiline",
        "true"
    );

    editor.root.setAttribute(
        "role",
        "textbox"
    );

    message.textContent =
        "H2: ana ara başlık · H3: alt başlık · Normal: paragraf";

    wrapper.append(message);

    form.addEventListener("submit", () => {
        textarea.value = editor.getSemanticHTML();
    });
});