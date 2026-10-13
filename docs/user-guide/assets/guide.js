(() => {
    const $ = (s, r = document) => r.querySelector(s);
    const $$ = (s, r = document) => [...r.querySelectorAll(s)];
    const store = {
        get(k) { try { return localStorage.getItem(k); } catch { return null; } },
        set(k, v) { try { localStorage.setItem(k, v); } catch { /* storage unavailable */ } },
    };
    // Page strings: the page's lang attribute picks the language
    const STR = {
        "en": {
            "copyLink": "Copy link",
            "linkCopied": "Link copied",
            "done": "done",
            "noMatch": "No match. Try another word.",
            "tour": [
                [
                    "Open a new task",
                    "Leaves this task and returns to the home screen. Save a draft first if you want to resume."
                ],
                [
                    "Task name",
                    "The thin section and the field of view you are annotating, for example GDX-22-PI / FOV_1."
                ],
                [
                    "Batch navigation",
                    "Shown only when you work through a batch. <b>Previous</b> goes back to the previous task. <b>1 / 2</b> is your position in the batch. <b>Next</b> saves and exports this task for every lighting variant, then opens the next task not yet annotated."
                ],
                [
                    "Finish and profile",
                    "Finish ends the session and offers to save. The badge next to it shows your username; click it to edit your profile."
                ],
                [
                    "Undo and redo",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-undo\"/></svg></span><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-redo\"/></svg></span> Step back or forward through your last 50 actions. The tooltip names the step."
                ],
                [
                    "Tools",
                    "From top to bottom, in the <i>Separators</i> layout shown here:<br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-pointer\"/></svg></span> Pointer <kbd>V</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-select-add\"/></svg></span> Add point <kbd>S</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-select-remove\"/></svg></span> Remove point <kbd>X</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-bbox\"/></svg></span> Bounding box <kbd>B</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-freeform\"/></svg></span> Freeform draw <kbd>F</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-polygon\"/></svg></span> Polygon lasso <kbd>P</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-slic\"/></svg></span> Superpixels (SLIC) <kbd>L</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-zoom-in\"/></svg></span><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-zoom-out\"/></svg></span> Zoom in / out <kbd>+</kbd> <kbd>−</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-grab\"/></svg></span> Pan <kbd>G</kbd><br>With the default <i>Flyout menus</i> layout, the three SAM tools share one button <span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-sam-group\"/></svg></span>."
                ],
                [
                    "Lighting pills",
                    "Switch between PPL and XPL. When compensator images exist, γ1, γ-1 and γ0 pills appear under XPL."
                ],
                [
                    "Display and help",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-borders\"/></svg></span> shows the objects as tinted areas or as outlines only. <span class=\"ti q\" aria-hidden=\"true\">?</span> opens the list of keyboard shortcuts."
                ],
                [
                    "Customize",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-cog\"/></svg></span> Language, toolbar layout and mask display."
                ],
                [
                    "Image badges",
                    "The modality, compensator and rotation of the image on screen."
                ],
                [
                    "Minimap",
                    "The whole image with your current view. Press M to show or hide it."
                ],
                [
                    "Zoom locked",
                    "Keeps the zoom and position when you switch between lighting variants. Click to change to Zoom reset."
                ],
                [
                    "Annotation panel",
                    "Lists your objects with their three mineral hypotheses. Hover a name to highlight the grain; click it to edit the grain. At the bottom: Save draft and Export annotation (current image)."
                ]
            ],
            "mods": {
                "PPL": "plane polarized",
                "XPL": "cross polarized",
                "RL": "reflected",
                "FL": "fluorescence",
                "TR": "transmitted"
            },
            "comps": {
                "add": "+λ compensator (γ1)",
                "sous": "−λ compensator (γ-1)",
                "na": "no compensator (γ0)"
            },
            "seg": {
                "prefix": "prefix",
                "extra": "extra token",
                "mod": "modality",
                "comp": "compensator",
                "rot": "rotation",
                "ext": "extension"
            },
            "dec": {
                "modBad": "mod must use letters and digits only.",
                "modNote": "Modality {v}",
                "modOdd": " (not a standard modality)",
                "compBad": "comp must use letters and digits only.",
                "compNote": "Compensator {v}",
                "compOdd": " (expected add, sous or na)",
                "rotBad": "rot must be a whole number of degrees, for example 45 or -45.",
                "rotNote": "Stage rotation {v}°",
                "twice": "The token {k} appears twice.",
                "missing": "The _{k}- token is missing.",
                "noExt": "The name has no file extension.",
                "badExt": ".{e} is not an accepted format. Use {list}.",
                "notTokens": "After the prefix, every part must be a _key-value token.",
                "empty": "Type a file name.",
                "bad": "The app will not read this file.",
                "ok": "The app reads this file."
            },
            "kbIn": "In the app: ",
            "kbNone": "{k} has no shortcut in the app.",
            "idleCount": "Closing in",
            "backToWork": "Back to work",
            "pause": "Pause",
            "play": "Play",
            "pauseAria": "Pause animation",
            "playAria": "Play animation",
            "fill": "Fill",
            "erase": "Erase",
            "cancel": "Cancel",
            "apply": "Apply",
            "slicKept": "SLIC superpixels — {k} / {n} kept",
            "tool": {
                "polygon": "P  Polygon lasso",
                "freeform": "F  Freeform draw",
                "slic": "L  Superpixels (SLIC)",
                "add": "S  Add point",
                "remove": "X  Remove point",
                "box": "B  Bounding box"
            },
            "cap": {
                "polygon": [
                    "Click along the edge to place vertices",
                    "Click the first vertex to close",
                    "Closed: a new object"
                ],
                "freeform": [
                    "Hold the button and draw around the grain",
                    "Release: the stroke closes and fills"
                ],
                "fill": [
                    "The object is selected and Fill is on",
                    "Draw the missing part, overlapping the object",
                    "Fill: the shape joins the object"
                ],
                "erase": [
                    "The object is selected and Erase is on",
                    "Draw around the inclusion",
                    "Erase: the loop is cut out and leaves a hole"
                ],
                "slic": [
                    "Drag a box around the area",
                    "Computing SLIC...",
                    "Click each patch outside the grain",
                    "Click Apply",
                    "The kept patches form a new object"
                ],
                "point": [
                    "Press S and click inside the grain",
                    "SAM outlines part of the grain",
                    "Click again in the missing part",
                    "The outline spills onto a neighbour",
                    "Press X and click the part to exclude",
                    "The outline now fits the grain"
                ],
                "box": [
                    "Press B and drag a box around the grain",
                    "Release: SAM looks inside the box",
                    "One box gives the whole crystal"
                ]
            },
            "openBrowser": "Your browser opens the annotator",
            "processing": "Processing..."
        },
        "fr": {
            "copyLink": "Copier le lien",
            "linkCopied": "Lien copié",
            "done": "faites",
            "noMatch": "Aucun résultat. Essayez un autre mot.",
            "tour": [
                [
                    "Ouvrir une nouvelle tâche",
                    "Quitte cette tâche et revient à l'accueil. Enregistrez d'abord un brouillon si vous voulez reprendre."
                ],
                [
                    "Nom de la tâche",
                    "La lame mince et le champ de vision que vous annotez, par exemple GDX-22-PI / FOV_1."
                ],
                [
                    "Navigation dans le lot",
                    "Affichée seulement quand vous annotez un lot. <b>Précédente</b> revient à la tâche précédente. <b>1 / 2</b> indique votre position dans le lot. <b>Suivante</b> enregistre et exporte cette tâche pour chaque variante d'éclairage, puis ouvre la tâche suivante non annotée."
                ],
                [
                    "Terminer et profil",
                    "Terminer clôt la session et propose d'enregistrer. Le badge à côté affiche votre nom d'utilisateur ; cliquez dessus pour modifier votre profil."
                ],
                [
                    "Annuler et rétablir",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-undo\"/></svg></span><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-redo\"/></svg></span> Reculez ou avancez parmi vos 50 dernières actions. L'infobulle nomme l'étape."
                ],
                [
                    "Outils",
                    "De haut en bas, avec la disposition <i>Séparateurs</i> montrée ici :<br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-pointer\"/></svg></span> Pointeur <kbd>V</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-select-add\"/></svg></span> Ajouter un point <kbd>S</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-select-remove\"/></svg></span> Retirer un point <kbd>X</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-bbox\"/></svg></span> Boîte englobante <kbd>B</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-freeform\"/></svg></span> Dessin libre <kbd>F</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-polygon\"/></svg></span> Lasso polygone <kbd>P</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-slic\"/></svg></span> Superpixels (SLIC) <kbd>L</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-zoom-in\"/></svg></span><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-zoom-out\"/></svg></span> Zoom avant / arrière <kbd>+</kbd> <kbd>−</kbd><br><span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-grab\"/></svg></span> Déplacer <kbd>G</kbd><br>Avec la disposition par défaut <i>Menus déroulants</i>, les trois outils SAM partagent un bouton <span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-sam-group\"/></svg></span>."
                ],
                [
                    "Pastilles d'éclairage",
                    "Passez de PPL à XPL et inversement. Quand le dossier contient des images avec compensateur, les pastilles γ1, γ-1 et γ0 apparaissent sous XPL."
                ],
                [
                    "Affichage et aide",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-borders\"/></svg></span> affiche les objets en zones teintées ou en contours seulement. <span class=\"ti q\" aria-hidden=\"true\">?</span> ouvre la liste des raccourcis clavier."
                ],
                [
                    "Personnaliser",
                    "<span class=\"ti\" aria-hidden=\"true\"><svg><use href=\"#i-cog\"/></svg></span> Langue, disposition de la barre d'outils et affichage des masques."
                ],
                [
                    "Badges de l'image",
                    "La modalité, le compensateur et la rotation de l'image affichée."
                ],
                [
                    "Minicarte",
                    "L'image entière avec la zone affichée. Appuyez sur M pour l'afficher ou la masquer."
                ],
                [
                    "Zoom verrouillé",
                    "Conserve le zoom et la position quand vous changez de variante d'éclairage. Cliquez pour passer à Zoom réinitialisé."
                ],
                [
                    "Panneau d'annotation",
                    "Liste vos objets avec leurs trois hypothèses minérales. Survolez un nom pour mettre le grain en évidence ; cliquez dessus pour le modifier. En bas : Enregistrer le brouillon et Exporter l'annotation (image actuelle)."
                ]
            ],
            "mods": {
                "PPL": "polarisé plan",
                "XPL": "polarisé croisé",
                "RL": "réfléchi",
                "FL": "fluorescence",
                "TR": "transmis"
            },
            "comps": {
                "add": "compensateur +λ (γ1)",
                "sous": "compensateur −λ (γ-1)",
                "na": "sans compensateur (γ0)"
            },
            "seg": {
                "prefix": "préfixe",
                "extra": "jeton en plus",
                "mod": "modalité",
                "comp": "compensateur",
                "rot": "rotation",
                "ext": "extension"
            },
            "dec": {
                "modBad": "mod n'accepte que des lettres et des chiffres.",
                "modNote": "Modalité {v}",
                "modOdd": " (modalité non standard)",
                "compBad": "comp n'accepte que des lettres et des chiffres.",
                "compNote": "Compensateur {v}",
                "compOdd": " (attendu : add, sous ou na)",
                "rotBad": "rot doit être un nombre entier de degrés, par exemple 45 ou -45.",
                "rotNote": "Rotation de la platine {v}°",
                "twice": "Le jeton {k} apparaît deux fois.",
                "missing": "Le jeton _{k}- est absent.",
                "noExt": "Le nom n'a pas d'extension.",
                "badExt": ".{e} n'est pas un format accepté. Utilisez {list}.",
                "notTokens": "Après le préfixe, chaque partie doit être un jeton _clé-valeur.",
                "empty": "Saisissez un nom de fichier.",
                "bad": "L'application ne lira pas ce fichier.",
                "ok": "L'application lit ce fichier."
            },
            "kbIn": "Dans l'application : ",
            "kbNone": "{k} n'a pas de raccourci dans l'application.",
            "idleCount": "Fermeture dans",
            "backToWork": "Retour au travail",
            "pause": "Pause",
            "play": "Lecture",
            "pauseAria": "Mettre l'animation en pause",
            "playAria": "Lancer l'animation",
            "fill": "Remplir",
            "erase": "Effacer",
            "cancel": "Annuler",
            "apply": "Appliquer",
            "slicKept": "Superpixels SLIC — {k} / {n} conservés",
            "tool": {
                "polygon": "P  Lasso polygone",
                "freeform": "F  Dessin libre",
                "slic": "L  Superpixels (SLIC)",
                "add": "S  Ajouter un point",
                "remove": "X  Retirer un point",
                "box": "B  Boîte englobante"
            },
            "cap": {
                "polygon": [
                    "Cliquez le long du bord pour placer les sommets",
                    "Cliquez sur le premier sommet pour fermer",
                    "Fermé : un nouvel objet"
                ],
                "freeform": [
                    "Maintenez le bouton et dessinez autour du grain",
                    "Relâchez : le tracé se ferme et se remplit"
                ],
                "fill": [
                    "L'objet est sélectionné et Remplir est actif",
                    "Dessinez la partie manquante, en chevauchant l'objet",
                    "Remplir : la forme rejoint l'objet"
                ],
                "erase": [
                    "L'objet est sélectionné et Effacer est actif",
                    "Dessinez autour de l'inclusion",
                    "Effacer : la boucle est retirée et laisse un trou"
                ],
                "slic": [
                    "Tracez une boîte autour de la zone",
                    "Calcul SLIC...",
                    "Cliquez chaque zone hors du grain",
                    "Cliquez sur Appliquer",
                    "Les zones conservées forment un nouvel objet"
                ],
                "point": [
                    "Appuyez sur S et cliquez dans le grain",
                    "SAM délimite une partie du grain",
                    "Cliquez de nouveau dans la partie manquante",
                    "Le contour déborde sur un voisin",
                    "Appuyez sur X et cliquez sur la partie à exclure",
                    "Le contour suit maintenant le grain"
                ],
                "box": [
                    "Appuyez sur B et tracez une boîte autour du grain",
                    "Relâchez : SAM cherche dans la boîte",
                    "Une seule boîte donne le cristal entier"
                ]
            },
            "openBrowser": "Votre navigateur ouvre l'annotateur",
            "processing": "Traitement..."
        }
    };
    const T = STR[document.documentElement.lang.startsWith("fr") ? "fr" : "en"];
    const fmt = (str, vars) => str.replace(/\{(\w+)\}/g, (_, k) => vars[k]);

    function toast(msg) {
        const el = document.createElement("div");
        el.className = "toast"; el.textContent = msg;
        document.body.append(el);
        setTimeout(() => el.remove(), 1600);
    }

    // Compare sliders
    $$(".compare").forEach((c) => {
        const r = $("input[type=range]", c);
        r.addEventListener("input", () => c.style.setProperty("--pos", r.value + "%"));
    });

    // Lightbox
    const lb = $("#lightbox");
    $$("figure.shot > img").forEach((img) => img.addEventListener("click", () => {
        $("#lb-img").src = img.src;
        $("#lb-img").alt = img.alt;
        $("#lb-cap").textContent = img.closest("figure").querySelector("figcaption")?.textContent ?? "";
        lb.showModal();
    }));
    $("#lb-close").addEventListener("click", () => lb.close());
    lb.addEventListener("click", (e) => { if (e.target === lb) lb.close(); });


    // Real screenshot when the file exists, redrawn view otherwise
    $$("figure.with-fallback").forEach((fig) => {
        const img = $("img.real", fig), fallback = $(".fallback", fig);
        const useImage = () => { img.hidden = false; fallback.hidden = true; };
        const useFallback = () => { img.hidden = true; fallback.hidden = false; };
        if (img.complete) { img.naturalWidth ? useImage() : useFallback(); }
        img.addEventListener("load", useImage);
        img.addEventListener("error", useFallback);
        img.addEventListener("click", () => {
            $("#lb-img").src = img.src; $("#lb-img").alt = img.alt;
            $("#lb-cap").textContent = fig.querySelector("figcaption")?.textContent ?? "";
            lb.showModal();
        });
    });

    // Language switch keeps the reader on the same section
    $$("[data-lang-link]").forEach((a) => a.addEventListener("click", () => { a.href = a.getAttribute("href").split("#")[0] + location.hash; }));

    // Mobile menu
    const side = $("#side"), menuBtn = $("#menu-open");
    menuBtn.addEventListener("click", () => {
        const open = side.classList.toggle("open");
        menuBtn.setAttribute("aria-expanded", String(open));
    });
    $$("#toc a, .brand").forEach((a) => a.addEventListener("click", () => side.classList.remove("open")));

    // Scroll-spy
    const links = new Map($$("#toc a").map((a) => [a.getAttribute("href").slice(1), a]));
    const spy = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
            if (!e.isIntersecting) return;
            links.forEach((a) => a.classList.remove("active"));
            links.get(e.target.id)?.classList.add("active");
        });
    }, {rootMargin: "-30% 0px -65% 0px"});
    $$("section.chapter").forEach((s) => spy.observe(s));

    // Copy-link buttons on chapter titles
    $$(".chap-head").forEach((h) => {
        const id = h.closest("section").id;
        const b = document.createElement("button");
        b.type = "button"; b.className = "copy-link"; b.textContent = T.copyLink;
        b.addEventListener("click", () => {
            const url = location.href.split("#")[0] + "#" + id;
            navigator.clipboard?.writeText(url).then(() => toast(T.linkCopied), () => toast(url));
        });
        h.append(b);
    });

    // Quick start checklist
    const qs = $$(".quick input[type=checkbox]");
    const qsUpdate = () => {
        const n = qs.filter((c) => c.checked).length;
        $("#quick-progress").textContent = `${n} / ${qs.length} ${T.done}`;
    };
    qs.forEach((c) => {
        c.checked = store.get(c.id) === "1";
        c.addEventListener("change", () => { store.set(c.id, c.checked ? "1" : "0"); qsUpdate(); });
    });
    $("#quick-reset").addEventListener("click", () => { qs.forEach((c) => { c.checked = false; store.set(c.id, "0"); }); qsUpdate(); });
    qsUpdate();

    // Search
    const index = [];
    $$("section.chapter").forEach((sec) => {
        const chapter = sec.dataset.title;
        index.push({id: sec.id, title: chapter, chapter, text: sec.textContent.toLowerCase()});
        const heads = $$("h3", sec);
        $$("h3[id]", sec).forEach((h) => {
            // A Range, not siblings: a heading's text can continue in the next .col block.
            const r = document.createRange(), next = heads[heads.indexOf(h) + 1];
            r.setStartAfter(h);
            next ? r.setEndBefore(next) : r.setEnd(sec, sec.childNodes.length);
            const text = r.toString();
            index.push({id: h.id, title: h.textContent, chapter, text: (h.textContent + " " + text).toLowerCase()});
        });
    });
    const q = $("#q"), results = $("#results");
    let hits = [], sel = 0;
    function renderResults() {
        const term = q.value.trim().toLowerCase();
        if (!term) { results.hidden = true; return; }
        const words = term.split(/\s+/).map((w) => new RegExp("(^|[^a-z0-9])" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
        hits = index
            .filter((e) => words.every((w) => w.test(e.text)))
            .map((e) => ({...e, score: words.reduce((s, w) => s + (w.test(e.title.toLowerCase()) ? 3 : 0), e.id === e.chapter ? 0 : 1)}))
            .sort((a, b) => b.score - a.score)
            .slice(0, 8);
        sel = 0;
        results.innerHTML = hits.length
            ? hits.map((h, i) => `<a href="#${h.id}" class="${i === 0 ? "on" : ""}">${h.title}<small>${h.chapter}</small></a>`).join("")
            : `<p>${T.noMatch}</p>`;
        results.hidden = false;
    }
    q.addEventListener("input", renderResults);
    q.addEventListener("keydown", (e) => {
        const items = $$("a", results);
        if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            if (!items.length) return;
            sel = (sel + (e.key === "ArrowDown" ? 1 : items.length - 1)) % items.length;
            items.forEach((a, i) => a.classList.toggle("on", i === sel));
        } else if (e.key === "Enter" && items[sel]) {
            e.preventDefault(); items[sel].click();
        } else if (e.key === "Escape") {
            q.value = ""; results.hidden = true; q.blur();
        }
    });
    results.addEventListener("click", (e) => {
        if (e.target.closest("a")) { results.hidden = true; q.value = ""; side.classList.remove("open"); }
    });
    document.addEventListener("click", (e) => { if (!e.target.closest(".search")) results.hidden = true; });

    // Tool tabs: each tab shows its text panel and the wide figure block tied to it
    const tabs = $$('[role="tab"]');
    function selectTab(tab) {
        tabs.forEach((t) => {
            const on = t === tab;
            t.setAttribute("aria-selected", String(on));
            t.tabIndex = on ? 0 : -1;
            const id = t.getAttribute("aria-controls");
            $("#" + id).hidden = !on;
            $$(`[data-for="${id}"]`).forEach((w) => { w.hidden = !on; });
        });
    }
    tabs.forEach((t, i) => {
        t.addEventListener("click", () => selectTab(t));
        t.addEventListener("keydown", (e) => {
            if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
            const next = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
            selectTab(next); next.focus();
        });
    });
    selectTab(tabs[0]);


    // Content above an anchor settles after the browser's initial jump; jump again once it has.
    const jumpToHash = () => {
        const target = location.hash && document.getElementById(location.hash.slice(1));
        if (!target) return;
        const tabPanel = target.closest('[role="tabpanel"]');
        if (tabPanel) selectTab($(`[aria-controls="${tabPanel.id}"]`));
        target.scrollIntoView({behavior: "instant", block: "start"});
    };
    if (document.readyState === "complete") jumpToHash(); else addEventListener("load", jumpToHash);
    document.fonts?.ready.then(jumpToHash);

    // Editor tour. Positions are percentages of the 1600×900 batch-mode screenshot.
    const SPOT_POS = [[3.8, 2], [48.5, 2], [57, 2], [94, 2], [4.6, 7.6], [4.6, 29], [4.6, 48.5], [4.6, 54], [4.6, 97], [82, 6], [7.5, 92.8], [81, 97], [92, 22]];
    const spots = SPOT_POS.map(([x, y], i) => ({x, y, t: T.tour[i][0], d: T.tour[i][1]}));
    const stage = $("#tour-stage"), legend = $("#tour-legend");
    let cur = 0;
    spots.forEach((s, i) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "hot"; b.textContent = i + 1;
        b.style.left = s.x + "%"; b.style.top = s.y + "%";
        b.setAttribute("aria-label", `${i + 1}. ${s.t}`);
        b.addEventListener("click", () => show(i));
        stage.append(b);
        const li = document.createElement("li");
        li.innerHTML = `<button type="button"><span>${i + 1}</span>${s.t}</button>`;
        li.firstChild.addEventListener("click", () => show(i));
        legend.append(li);
    });
    function show(i) {
        cur = (i + spots.length) % spots.length;
        $$(".hot", stage).forEach((h, j) => h.classList.toggle("on", j === cur));
        $("#tour-count").textContent = `${cur + 1} / ${spots.length}`;
        $("#tour-title").textContent = spots[cur].t;
        $("#tour-text").innerHTML = spots[cur].d;
    }
    $("#tour-prev").addEventListener("click", () => show(cur - 1));
    $("#tour-next").addEventListener("click", () => show(cur + 1));
    show(0);

    // File name checker. Mirrors the rule on the home screen.
    const FORMATS = ["jpg", "jpeg", "png", "tif", "tiff", "bmp"];
    const MODS = T.mods;
    const COMPS = T.comps, D = T.dec;
    const fname = $("#fname"), anatomy = $("#anatomy"), verdict = $("#verdict");
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
    function decode() {
        const name = fname.value.trim();
        const segs = [], problems = [], notes = [];
        const dot = name.lastIndexOf(".");
        const stem = dot > 0 ? name.slice(0, dot) : name;
        const ext = dot > 0 ? name.slice(dot + 1) : "";
        const m = stem.match(/^(.+?)((?:_[A-Za-z0-9]+-[^_]+)+)$/);
        let prefix = stem, tokens = [];
        if (m) { prefix = m[1]; tokens = m[2].slice(1).split("_"); }
        segs.push({k: "prefix", v: prefix, l: T.seg.prefix});
        const seen = {};
        tokens.forEach((tok) => {
            const i = tok.indexOf("-");
            const key = tok.slice(0, i), val = tok.slice(i + 1);
            let k = "extra", label = T.seg.extra;
            if (key === "mod") {
                k = /^[A-Za-z0-9]+$/.test(val) ? "mod" : "bad"; label = T.seg.mod;
                if (k === "bad") problems.push(D.modBad);
                else notes.push(fmt(D.modNote, {v: val}) + (MODS[val] ? " — " + MODS[val] : D.modOdd));
            } else if (key === "comp") {
                k = /^[A-Za-z0-9]+$/.test(val) ? "comp" : "bad"; label = T.seg.comp;
                if (k === "bad") problems.push(D.compBad);
                else notes.push(fmt(D.compNote, {v: val}) + (COMPS[val] ? " — " + COMPS[val] : D.compOdd));
            } else if (key === "rot") {
                k = /^-?\d+$/.test(val) ? "rot" : "bad"; label = T.seg.rot;
                if (k === "bad") problems.push(D.rotBad);
                else notes.push(fmt(D.rotNote, {v: val}));
            }
            if (key in seen) problems.push(fmt(D.twice, {k: key}));
            seen[key] = true;
            segs.push({k, v: "_" + tok, l: label});
        });
        if (ext) segs.push({k: FORMATS.includes(ext.toLowerCase()) ? "extra" : "bad", v: "." + ext, l: T.seg.ext});
        problems.unshift(...["mod", "comp", "rot"].filter((t) => !seen[t]).map((t) => fmt(D.missing, {k: t})));
        if (!ext) problems.push(D.noExt);
        else if (!FORMATS.includes(ext.toLowerCase())) problems.push(fmt(D.badExt, {e: ext, list: FORMATS.map((f) => "." + f).join(", ")}));
        if (!m && name) problems.push(D.notTokens);
        anatomy.innerHTML = segs.map((s) => `<span class="seg k-${s.k}"><i>${esc(s.v)}</i><small>${s.l}</small></span>`).join("");
        if (!name) { verdict.className = "verdict"; verdict.textContent = D.empty; return; }
        verdict.className = "verdict " + (problems.length ? "bad" : "ok");
        verdict.innerHTML = problems.length
            ? `${D.bad}<ul>${problems.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>`
            : `${D.ok}<ul>${notes.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>`;
    }
    fname.addEventListener("input", decode);
    $$(".examples button").forEach((b) => b.addEventListener("click", () => { fname.value = b.dataset.ex; decode(); }));
    decode();

    // Shortcut table: filter and live key lookup
    const rows = $$("#kb-table tbody tr");
    $("#kb-filter").addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase();
        rows.forEach((r) => { r.hidden = !r.textContent.toLowerCase().includes(term); });
    });
    const kbSection = $("#shortcuts");
    document.addEventListener("keydown", (e) => {
        const tag = e.target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA") return;
        if (e.key === "/" ) { e.preventDefault(); q.focus(); return; }
        const r = kbSection.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) return;
        let key = e.key.toLowerCase();
        if (e.ctrlKey || e.metaKey) {
            if (key === "z" || key === "y") e.preventDefault();
            key = "ctrl+" + (e.shiftKey ? "shift+" : "") + key;
        }
        const row = rows.find((tr) => tr.dataset.k.split(" ").includes(key));
        rows.forEach((tr) => tr.classList.remove("hit"));
        if (row) {
            row.classList.add("hit");
            $("#kb-live").textContent = T.kbIn + row.cells[1].textContent;
        } else if (!["shift", "control", "meta", "alt"].includes(key)) {
            $("#kb-live").textContent = fmt(T.kbNone, {k: e.key});
        }
    });


    // "Still there?" replica countdown (the app's grace period is 2 minutes)
    let idleLeft = 120;
    const idleCount = $("#idle-count");
    const idleRender = () => { idleCount.textContent = `${T.idleCount} ${Math.floor(idleLeft / 60)}:${String(idleLeft % 60).padStart(2, "0")}`; };
    setInterval(() => { idleLeft = idleLeft > 0 ? idleLeft - 1 : 120; idleRender(); }, 1000);
    $("#idle-stay").addEventListener("click", () => { idleLeft = 120; idleRender(); toast(T.backToWork); });

    // Tool animations: scripted replays drawn over a real crop of the micrograph.
    // Colours and line styles follow src/canvas/canvas-theme.ts.
    const AW = 960, AH = 600, DPR = Math.min(2, window.devicePixelRatio || 1);
    const COL = {amber: "#F59E0B", orange: "#f97316", red: "#EF4444", blue: "#4FC3F7"};
    const base = new Image();
    base.src = "img/anim-base.jpg";
    const clamp01 = (u) => Math.max(0, Math.min(1, u));
    const ease = (u) => (u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2);
    const mix = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
    const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
    const toPath = (pts, closed = true) => {
        const p = new Path2D();
        pts.forEach(([x, y], i) => (i ? p.lineTo(x, y) : p.moveTo(x, y)));
        if (closed) p.closePath();
        return p;
    };
    const smooth = (pts, n = 10) => {
        const out = [];
        for (let i = 0; i < pts.length; i++) {
            const p0 = pts[(i - 1 + pts.length) % pts.length], p1 = pts[i], p2 = pts[(i + 1) % pts.length], p3 = pts[(i + 2) % pts.length];
            for (let k = 0; k < n; k++) {
                const t = k / n, t2 = t * t, t3 = t2 * t;
                out.push([0, 1].map((d) => 0.5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3)));
            }
        }
        return out;
    };
    const inside = (pt, poly) => {
        let c = false;
        for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
            const [xi, yi] = poly[i], [xj, yj] = poly[j];
            if ((yi > pt[1]) !== (yj > pt[1]) && pt[0] < ((xj - xi) * (pt[1] - yi)) / (yj - yi) + xi) c = !c;
        }
        return c;
    };
    const offscreen = (w = AW, h = AH) => {
        const c = document.createElement("canvas");
        c.width = w * DPR; c.height = h * DPR;
        return c;
    };

    // Shapes on the crop (image pixels of anim-base.jpg)
    const CRYSTAL = [[325, 95], [380, 82], [450, 80], [520, 85], [552, 95], [558, 180], [556, 280], [552, 380], [548, 470], [530, 505], [470, 522], [400, 525], [345, 515], [322, 480], [320, 380], [322, 260], [322, 160]];
    const CHLORITE = [[236, 284], [270, 268], [318, 262], [323, 300], [320, 380], [306, 444], [284, 450], [266, 418], [240, 380], [222, 330]];
    const OPAQUE = smooth([[856, 314], [895, 296], [938, 306], [952, 345], [931, 400], [880, 406], [846, 389], [848, 350]], 12);
    const LOWER = [[323, 350], [556, 345], [552, 380], [548, 470], [530, 505], [470, 522], [400, 525], [345, 515], [322, 480], [320, 410]];
    const INCLUSION = smooth([[440, 250], [478, 242], [505, 262], [502, 300], [470, 318], [438, 305], [428, 276]], 12);
    const CUT_BELOW = [[0, 370], [AW, 370], [AW, AH], [0, AH]];

    // Mask renderer: fill layers add, hole layers cut; outline = dilated mask minus mask
    const maskBuf = offscreen(), ringBuf = offscreen();
    function drawMask(ctx, layers, color) {
        const m = maskBuf.getContext("2d"), r = ringBuf.getContext("2d");
        m.setTransform(DPR, 0, 0, DPR, 0, 0);
        m.clearRect(0, 0, AW, AH);
        m.fillStyle = color;
        layers.forEach((l) => {
            m.globalCompositeOperation = l.hole ? "destination-out" : "source-over";
            if (l.canvas) m.drawImage(l.canvas, 0, 0, AW, AH);
            else m.fill(toPath(l.pts));
        });
        m.globalCompositeOperation = "source-in";
        m.fillRect(0, 0, AW, AH);
        m.globalCompositeOperation = "source-over";
        r.setTransform(1, 0, 0, 1, 0, 0);
        r.clearRect(0, 0, ringBuf.width, ringBuf.height);
        const w = 2.5 * DPR;
        for (let a = 0; a < 16; a++) r.drawImage(maskBuf, Math.cos(a * Math.PI / 8) * w, Math.sin(a * Math.PI / 8) * w);
        r.globalCompositeOperation = "destination-out";
        r.drawImage(maskBuf, 0, 0);
        r.globalCompositeOperation = "source-over";
        ctx.save();
        ctx.globalAlpha = 0.22;
        ctx.drawImage(maskBuf, 0, 0, AW, AH);
        ctx.globalAlpha = 1;
        ctx.drawImage(ringBuf, 0, 0, AW, AH);
        ctx.restore();
    }

    function drawCursor(ctx, [x, y], pressed) {
        ctx.save();
        ctx.translate(x, y);
        ctx.beginPath();
        ctx.moveTo(0, 0); ctx.lineTo(0, 19); ctx.lineTo(5, 14.5); ctx.lineTo(8.5, 22); ctx.lineTo(11.5, 20.8); ctx.lineTo(8, 13.5); ctx.lineTo(14.5, 13.5); ctx.closePath();
        ctx.fillStyle = pressed ? "#ffe9a8" : "#fff";
        ctx.strokeStyle = "#000"; ctx.lineWidth = 1.3;
        ctx.fill(); ctx.stroke();
        ctx.restore();
    }
    function drawRipple(ctx, [x, y], age) {
        if (age < 0 || age > 0.45) return;
        ctx.save();
        ctx.strokeStyle = `rgba(255,255,255,${1 - age / 0.45})`;
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(x, y, 5 + age * 45, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
    }
    const iconCache = {};
    const iconImage = (id, color = "#4FC3F7") => {
        const key = id + color;
        if (!iconCache[key]) {
            const sym = document.getElementById("i-" + id);
            const img = new Image();
            img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${sym.getAttribute("viewBox")}" width="44" height="44" color="${color}">${sym.innerHTML}</svg>`);
            iconCache[key] = img;
        }
        return iconCache[key];
    };
    function chip(ctx, x, y, text, {bg = "rgba(18,18,18,.82)", fg = "#fff", border = "rgba(255,255,255,.25)", align = "left", icon, iconColor} = {}) {
        ctx.save();
        ctx.font = "600 17px system-ui, -apple-system, sans-serif";
        const pad = icon ? 30 : 0;
        const w = ctx.measureText(text).width + 24 + pad, h = 32;
        const left = align === "right" ? x - w : align === "center" ? x - w / 2 : x;
        ctx.beginPath(); ctx.roundRect(left, y, w, h, 8);
        ctx.fillStyle = bg; ctx.fill();
        ctx.strokeStyle = border; ctx.lineWidth = 1; ctx.stroke();
        if (icon) {
            const img = iconImage(icon, iconColor);
            if (img.complete && img.naturalWidth) ctx.drawImage(img, left + 10, y + 6, 20, 20);
        }
        ctx.fillStyle = fg; ctx.textBaseline = "middle";
        ctx.fillText(text, left + 12 + pad, y + h / 2 + 1);
        ctx.restore();
    }
    const MODE = {
        fill: {bg: "rgba(59,130,246,.30)", fg: "#93c5fd", border: "rgba(96,165,250,.6)"},
        erase: {bg: "rgba(239,68,68,.30)", fg: "#fca5a5", border: "rgba(248,113,113,.6)"},
    };

    // Polygon phase: cursor walks the vertices, one click each, last click on the first vertex closes
    function polygonPhase(ctx, t, V, {start, step = 0.5, from, erase = false}) {
        const n = V.length;
        if (t < start) {
            const cur = mix(from, V[0], ease(clamp01(t / start)));
            return {cur, closed: false, click: -1};
        }
        const k = (t - start) / step;
        if (k >= n) return {cur: V[0], closed: true, click: (k - n) * step};
        const placed = Math.floor(k) + 1, u = ease(clamp01((k - Math.floor(k) - 0.15) / 0.75));
        const cur = mix(V[placed - 1], V[placed % n], u);
        const pts = V.slice(0, placed).concat([cur]);
        ctx.save();
        ctx.fillStyle = erase ? "rgba(239,68,68,0.10)" : "rgba(245,158,11,0.10)";
        ctx.fill(toPath(pts));
        ctx.strokeStyle = erase ? COL.red : COL.amber;
        ctx.lineWidth = 2;
        if (erase) ctx.setLineDash([8, 5]);
        ctx.stroke(toPath(pts, false));
        ctx.setLineDash([]);
        V.slice(0, placed).forEach(([x, y]) => {
            ctx.beginPath(); ctx.arc(x, y, 4.5, 0, Math.PI * 2);
            ctx.fillStyle = erase ? COL.red : COL.amber; ctx.fill();
        });
        if (placed === n && dist(cur, V[0]) < 15) {
            ctx.beginPath(); ctx.arc(V[0][0], V[0][1], 9, 0, Math.PI * 2);
            ctx.lineWidth = 3; ctx.strokeStyle = erase ? COL.red : COL.amber; ctx.stroke();
        }
        ctx.restore();
        return {cur, closed: false, click: (k - Math.floor(k)) * step};
    }

    // Freeform phase: button held, stroke follows the cursor, release closes the shape
    function freeformPhase(ctx, t, P, {start, dur = 2.6, from, erase = false}) {
        if (t < start) return {cur: mix(from, P[0], ease(clamp01(t / start))), done: false, down: false};
        const u = clamp01((t - start) / dur);
        if (u >= 1) return {cur: P[P.length - 1], done: true, down: false, release: t - start - dur};
        const upto = Math.max(1, Math.floor(u * (P.length - 1)));
        const pts = P.slice(0, upto + 1);
        ctx.save();
        ctx.strokeStyle = erase ? COL.red : COL.orange;
        ctx.lineWidth = 3; ctx.lineJoin = ctx.lineCap = "round";
        if (erase) ctx.setLineDash([8, 5]);
        ctx.stroke(toPath(pts, false));
        ctx.restore();
        return {cur: pts[pts.length - 1], done: false, down: true};
    }

    // SLIC: jittered seeds in the box, nearest-seed labels, contours and dropped-cell shading precomputed
    const BOX = [300, 58, 590, 302];
    const slic = (() => {
        const [x0, y0, x1, y1] = BOX, w = x1 - x0, h = y1 - y0;
        let seed = 7;
        const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
        const seeds = [];
        for (let y = y0 + 15; y < y1; y += 30) for (let x = x0 + 15; x < x1; x += 30) seeds.push([x + (rnd() - 0.5) * 18, y + (rnd() - 0.5) * 18]);
        const label = new Int16Array(w * h);
        for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
            let best = 0, bd = Infinity;
            seeds.forEach(([sx, sy], k) => { const d = (sx - x0 - i) ** 2 + (sy - y0 - j) ** 2; if (d < bd) { bd = d; best = k; } });
            label[j * w + i] = best;
        }
        const keep = seeds.map((sd) => inside(sd, CRYSTAL));
        const drops = seeds.map((sd, k) => [sd, k]).filter(([, k]) => !keep[k]).sort((a, b) => Math.atan2(a[0][1] - 180, a[0][0] - 440) - Math.atan2(b[0][1] - 180, b[0][0] - 440)).map(([, k]) => k);
        const paint = (fn) => {
            const c = document.createElement("canvas"); c.width = w; c.height = h;
            const g = c.getContext("2d"), img = g.createImageData(w, h);
            for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const rgba = fn(i, j, label[j * w + i]); if (rgba) img.data.set(rgba, (j * w + i) * 4); }
            g.putImageData(img, 0, 0);
            return c;
        };
        const contours = paint((i, j, l) => ((i + 1 < w && label[j * w + i + 1] !== l) || (j + 1 < h && label[(j + 1) * w + i] !== l) ? [255, 255, 255, 190] : null));
        const dropCache = new Map();
        const dropped = (count) => {
            if (!dropCache.has(count)) {
                const off = new Set(drops.slice(0, count));
                dropCache.set(count, paint((i, j, l) => (off.has(l) ? [0, 0, 0, 150] : null)));
            }
            return dropCache.get(count);
        };
        const kept = document.createElement("canvas"); kept.width = AW; kept.height = AH;
        kept.getContext("2d").drawImage(paint((i, j, l) => (keep[l] ? [255, 255, 255, 255] : null)), x0, y0);
        return {seeds, drops, contours, dropped, kept, total: seeds.length};
    })();

    // SAM prompt marks: keypoints as in canvas-theme.ts (green +, red −), spinner while the model runs
    function drawKeypoint(ctx, [x, y], positive) {
        ctx.save();
        ctx.beginPath(); ctx.arc(x, y, 7, 0, Math.PI * 2);
        ctx.fillStyle = positive ? "#22c55e" : "#ef4444"; ctx.fill();
        ctx.lineWidth = 2; ctx.strokeStyle = "#fff"; ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(x - 3.5, y); ctx.lineTo(x + 3.5, y);
        if (positive) { ctx.moveTo(x, y - 3.5); ctx.lineTo(x, y + 3.5); }
        ctx.lineWidth = 2; ctx.stroke();
        ctx.restore();
    }
    function drawSpinner(ctx, [x, y], t) {
        ctx.save();
        ctx.lineWidth = 3; ctx.lineCap = "round";
        ctx.strokeStyle = "rgba(255,255,255,.25)";
        ctx.beginPath(); ctx.arc(x + 26, y + 26, 10, 0, Math.PI * 2); ctx.stroke();
        ctx.strokeStyle = "#fff";
        ctx.beginPath(); ctx.arc(x + 26, y + 26, 10, t * 7, t * 7 + 1.6); ctx.stroke();
        ctx.restore();
        chip(ctx, x + 42, y + 10, T.processing);
    }
    const CUT_ABOVE = [[0, 330], [AW, 330], [AW, AH], [0, AH]];

    const SCENES = {
        point: (() => {
            const P1 = [440, 200], P2 = [440, 440], P3 = [272, 360], wait = 0.8;
            const c1 = 0.8, r1 = c1 + wait, m2 = 2.6, c2 = 3.3, r2 = c2 + wait, sw = 5.1, c3 = 5.8, r3 = c3 + wait;
            return {
                dur: r3 + 2.6,
                toolAt: (t) => (t < sw ? {tool: T.tool.add, icon: "select-add"} : {tool: T.tool.remove, icon: "select-remove"}),
                captions: [[0, T.cap.point[0]], [r1, T.cap.point[1]], [m2, T.cap.point[2]], [r2, T.cap.point[3]], [sw, T.cap.point[4]], [r3, T.cap.point[5]]],
                draw(ctx, t) {
                    const color = "#47CFEA";
                    if (t >= r3) drawMask(ctx, [{pts: CRYSTAL}], color);
                    else if (t >= r2) drawMask(ctx, [{pts: CRYSTAL}, {pts: CHLORITE}], color);
                    else if (t >= r1) drawMask(ctx, [{pts: CRYSTAL}, {pts: CUT_ABOVE, hole: true}], color);
                    if (t >= c1) drawKeypoint(ctx, P1, true);
                    if (t >= c2) drawKeypoint(ctx, P2, true);
                    if (t >= c3) drawKeypoint(ctx, P3, false);
                    let cur, click = -1;
                    if (t < c1) cur = mix([200, 140], P1, ease(t / c1));
                    else if (t < m2) { cur = P1; click = t - c1; }
                    else if (t < c2) cur = mix(P1, P2, ease((t - m2) / (c2 - m2)));
                    else if (t < sw) { cur = P2; click = t - c2; }
                    else if (t < c3) cur = mix(P2, P3, ease((t - sw) / (c3 - sw)));
                    else { cur = P3; click = t - c3; }
                    const busy = (t >= c1 && t < r1) || (t >= c2 && t < r2) || (t >= c3 && t < r3);
                    if (busy) drawSpinner(ctx, cur, t);
                    return {cur, click};
                },
            };
        })(),
        box: (() => {
            const A = [305, 66], B = [572, 538], tDrag = 0.8, tUp = 2.0, tDone = tUp + 0.8;
            return {
                icon: "bbox", tool: T.tool.box, dur: tDone + 3,
                captions: [[0, T.cap.box[0]], [tUp, T.cap.box[1]], [tDone, T.cap.box[2]]],
                draw(ctx, t) {
                    if (t >= tDone) drawMask(ctx, [{pts: CRYSTAL}], "#47CFEA");
                    if (t < tDrag) return {cur: mix([180, 200], A, ease(t / tDrag)), click: -1};
                    const end = t < tUp ? mix(A, B, ease((t - tDrag) / (tUp - tDrag))) : B;
                    ctx.save();
                    ctx.strokeStyle = COL.blue; ctx.lineWidth = 2;
                    if (t < tUp) { ctx.fillStyle = "rgba(79,195,247,0.10)"; ctx.setLineDash([6, 3]); ctx.fillRect(A[0], A[1], end[0] - A[0], end[1] - A[1]); }
                    else if (t < tDone) { ctx.fillStyle = "rgba(79,195,247,0.15)"; ctx.fillRect(A[0], A[1], end[0] - A[0], end[1] - A[1]); }
                    ctx.strokeRect(A[0], A[1], end[0] - A[0], end[1] - A[1]);
                    ctx.restore();
                    if (t >= tUp && t < tDone) drawSpinner(ctx, B, t);
                    return {cur: end, down: t < tUp, click: t >= tUp ? t - tUp : -1};
                },
            };
        })(),
        polygon: {
            icon: "polygon", tool: T.tool.polygon, dur: 0.8 + CHLORITE.length * 0.5 + 3,
            captions: [[0, T.cap.polygon[0]], [0.8 + (CHLORITE.length - 1) * 0.5, T.cap.polygon[1]], [0.8 + CHLORITE.length * 0.5, T.cap.polygon[2]]],
            draw(ctx, t) {
                const r = polygonPhase(ctx, t, CHLORITE, {start: 0.8, from: [150, 170]});
                if (r.closed) drawMask(ctx, [{pts: CHLORITE}], "#11A03B");
                return r;
            },
        },
        freeform: {
            icon: "freeform", tool: T.tool.freeform, dur: 0.8 + 2.6 + 3,
            captions: [[0, T.cap.freeform[0]], [3.4, T.cap.freeform[1]]],
            draw(ctx, t) {
                const r = freeformPhase(ctx, t, OPAQUE, {start: 0.8, from: [760, 230]});
                if (r.done) drawMask(ctx, [{pts: OPAQUE}], "#A647EA");
                return {cur: r.cur, down: r.down, click: r.done ? r.release : -1};
            },
        },
        fill: {
            icon: "polygon", tool: T.tool.polygon, mode: "fill", dur: 1.4 + LOWER.length * 0.5 + 3.2,
            captions: [[0, T.cap.fill[0]], [1.4, T.cap.fill[1]], [1.4 + LOWER.length * 0.5, T.cap.fill[2]]],
            draw(ctx, t) {
                const existing = [{pts: CRYSTAL}, {pts: CUT_BELOW, hole: true}];
                const closed = t >= 1.4 + LOWER.length * 0.5;
                drawMask(ctx, closed ? existing.concat([{pts: LOWER}]) : existing, "#11A03B");
                return polygonPhase(ctx, t, LOWER, {start: 1.4, from: [640, 470]});
            },
        },
        erase: {
            icon: "freeform", tool: T.tool.freeform, mode: "erase", dur: 1.4 + 2.4 + 3.2,
            captions: [[0, T.cap.erase[0]], [1.4, T.cap.erase[1]], [3.8, T.cap.erase[2]]],
            draw(ctx, t) {
                const done = t >= 3.8;
                drawMask(ctx, done ? [{pts: CRYSTAL}, {pts: INCLUSION, hole: true}] : [{pts: CRYSTAL}], "#11A03B");
                const r = freeformPhase(ctx, t, INCLUSION, {start: 1.4, dur: 2.4, from: [640, 200], erase: true});
                return {cur: r.cur, down: r.down, click: r.done ? r.release : -1};
            },
        },
        slic: (() => {
            const clicks = 4, tBox = 0.7, tDrag = 1.0, tCalc = 0.6, tShow = tBox + tDrag + tCalc, tClick = 0.65, tSweep = 0.07;
            const tDone = tShow + 0.4 + clicks * tClick + (slic.drops.length - clicks) * tSweep;
            const apply = [BOX[2] - 40, BOX[3] + 30], tApply = tDone + 0.9;
            return {
                icon: "slic", tool: T.tool.slic, dur: tApply + 3,
                captions: [[0, T.cap.slic[0]], [tBox + tDrag, T.cap.slic[1]], [tShow, T.cap.slic[2]], [tDone, T.cap.slic[3]], [tApply, T.cap.slic[4]]],
                draw(ctx, t) {
                    const [x0, y0, x1, y1] = BOX;
                    if (t < tBox) return {cur: mix([200, 300], [x0, y0], ease(t / tBox)), click: -1};
                    if (t < tBox + tDrag) {
                        const cur = mix([x0, y0], [x1, y1], ease((t - tBox) / tDrag));
                        ctx.save();
                        ctx.fillStyle = "rgba(79,195,247,0.10)"; ctx.strokeStyle = COL.blue; ctx.lineWidth = 2; ctx.setLineDash([6, 3]);
                        ctx.fillRect(x0, y0, cur[0] - x0, cur[1] - y0); ctx.strokeRect(x0, y0, cur[0] - x0, cur[1] - y0);
                        ctx.restore();
                        return {cur, down: true, click: -1};
                    }
                    if (t >= tApply) {
                        drawMask(ctx, [{canvas: slic.kept}], "#EA4747");
                        return {cur: apply, click: t - tApply};
                    }
                    ctx.save();
                    ctx.fillStyle = "rgba(0,0,0,0.5)";
                    ctx.fillRect(0, 0, AW, y0); ctx.fillRect(0, y1, AW, AH - y1); ctx.fillRect(0, y0, x0, y1 - y0); ctx.fillRect(x1, y0, AW - x1, y1 - y0);
                    ctx.restore();
                    if (t < tShow) return {cur: [x1, y1], click: -1};
                    let count = 0, cur = [x1, y1], click = -1;
                    const k = t - tShow - 0.4;
                    if (k >= 0) {
                        if (k < clicks * tClick) {
                            const i = Math.floor(k / tClick), u = (k - i * tClick) / tClick;
                            const prev = i ? slic.seeds[slic.drops[i - 1]] : [x1, y1];
                            cur = mix(prev, slic.seeds[slic.drops[i]], ease(clamp01(u / 0.7)));
                            count = i + (u >= 0.7 ? 1 : 0);
                            click = u >= 0.7 ? (u - 0.7) * tClick : -1;
                        } else {
                            count = Math.min(slic.drops.length, clicks + Math.floor((k - clicks * tClick) / tSweep) + 1);
                            cur = slic.seeds[slic.drops[count - 1]];
                            click = 0.1;
                        }
                    }
                    if (t >= tDone) cur = mix(cur, apply, ease(clamp01((t - tDone) / 0.7)));
                    ctx.drawImage(slic.dropped(count), x0, y0);
                    ctx.drawImage(slic.contours, x0, y0);
                    chip(ctx, AW / 2, 20, fmt(T.slicKept, {k: slic.total - count, n: slic.total}), {align: "center"});
                    chip(ctx, apply[0] + 20, apply[1] - 16, `${T.apply} (${slic.total - count})`, {align: "right", bg: t >= tDone ? "#4FC3F7" : "rgba(79,195,247,.35)", fg: "#0b2633", border: "transparent"});
                    chip(ctx, apply[0] - 95, apply[1] - 16, T.cancel, {align: "right"});
                    return {cur, click};
                },
            };
        })(),
    };

    function renderScene(anim, t) {
        const {ctx, scene} = anim;
        ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
        ctx.clearRect(0, 0, AW, AH);
        if (base.complete && base.naturalWidth) ctx.drawImage(base, 0, 0, AW, AH);
        const r = scene.draw(ctx, t) || {};
        const label = scene.toolAt ? scene.toolAt(t) : scene;
        chip(ctx, 16, 16, label.tool, {icon: label.icon});
        if (scene.mode) chip(ctx, AW - 16, 16, scene.mode === "fill" ? T.fill : T.erase, {...MODE[scene.mode], align: "right", icon: scene.mode === "fill" ? "brush" : "eraser", iconColor: MODE[scene.mode].fg});
        const caption = scene.captions.filter(([t0]) => t >= t0).pop();
        if (caption) chip(ctx, AW / 2, AH - 52, caption[1], {align: "center", bg: "rgba(0,0,0,.78)"});
        if (r.cur) {
            drawRipple(ctx, r.cur, r.click ?? -1);
            drawCursor(ctx, r.cur, r.down);
        }
        const fade = scene.dur - t;
        if (fade < 0.35) { ctx.fillStyle = `rgba(17,17,17,${1 - fade / 0.35})`; ctx.fillRect(0, 0, AW, AH); }
    }

    const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const anims = $$("figure.anim").map((fig) => {
        const canvas = $("canvas", fig), btn = $(".anim-toggle", fig);
        canvas.width = AW * DPR; canvas.height = AH * DPR;
        const anim = {fig, canvas, btn, ctx: canvas.getContext("2d"), scene: SCENES[fig.dataset.scene], t: 0, playing: !reduceMotion, visible: false};
        const toggle = () => {
            anim.playing = !anim.playing;
            btn.textContent = anim.playing ? T.pause : T.play;
            btn.setAttribute("aria-label", anim.playing ? T.pauseAria : T.playAria);
        };
        btn.addEventListener("click", toggle);
        canvas.addEventListener("click", toggle);
        if (reduceMotion) { anim.t = anim.scene.dur - 0.4; btn.textContent = T.play; btn.setAttribute("aria-label", T.playAria); }
        return anim;
    });
    const seen = new IntersectionObserver((entries) => entries.forEach((e) => {
        const a = anims.find((x) => x.canvas === e.target);
        if (a) a.visible = e.isIntersecting;
    }));
    anims.forEach((a) => seen.observe(a.canvas));
    let last = performance.now();
    function tick(now) {
        const dt = Math.min(0.1, (now - last) / 1000);
        last = now;
        anims.forEach((a) => {
            if (!a.visible) return;
            if (a.playing) a.t = (a.t + dt) % a.scene.dur;
            renderScene(a, a.t);
        });
        requestAnimationFrame(tick);
    }
    base.decode?.().catch(() => {}).finally(() => anims.forEach((a) => renderScene(a, a.t)));
    requestAnimationFrame(tick);

    // Launcher illustration
    const st = $("#mock-status"), stText = $("#mock-status-text"), start = $("#mock-start"), openBtn = $("#mock-open");
    let running = false;
    start.addEventListener("click", () => {
        if (running) {
            running = false; st.className = "win-status"; stText.textContent = "Server stopped";
            start.textContent = "Start Server"; openBtn.disabled = true; return;
        }
        start.disabled = true; st.className = "win-status starting"; stText.textContent = "Starting… loading the SAM 2 model";
        setTimeout(() => {
            running = true; start.disabled = false; st.className = "win-status running";
            stText.textContent = "Running on http://127.0.0.1:7263"; start.textContent = "Stop Server"; openBtn.disabled = false;
        }, 1800);
    });
    openBtn.addEventListener("click", () => toast(T.openBrowser));
    $("#mock-dataset").addEventListener("click", () => { $("#mock-ds").scrollIntoView({block: "center"}); });
    const gen = $("#mock-gen"), log = $("#mock-log");
    const canGen = () => { gen.disabled = $("#mock-src").textContent.startsWith("No") || $("#mock-dst").textContent.startsWith("No"); };
    $$("[data-pick]").forEach((b) => b.addEventListener("click", () => { $("#" + b.dataset.pick).textContent = b.dataset.path; canGen(); }));
    gen.addEventListener("click", () => {
        const zip = $("#mock-zip").checked;
        log.textContent = "Scanning annotations…";
        setTimeout(() => {
            log.textContent = `Scanning annotations…\nWrote dataset_20261009-1412/annotations.json\nCopied images/  ·  build.log${zip ? "\nCompressed to dataset_20261009-1412.zip" : ""}\nDone.`;
        }, 900);
    });
})();
