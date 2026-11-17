// ========================================
// INTERFAZ MODERNA: íconos de línea y barra superior con saludo
// Se carga al final de cada página; no cambia la lógica existente.
// ========================================
(function () {
    const P = {
        home: '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
        dashboard: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
        users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        wallet: '<path d="M20 12V8H6a2 2 0 0 1 0-4h12v4"/><path d="M4 6v12a2 2 0 0 0 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
        recibo: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
        reloj: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
        check: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m22 4-10 10.01-3-3"/>',
        tarjeta: '<rect x="2" y="5" width="20" height="14" rx="2.5"/><path d="M2 10h20"/><path d="M6 15h4"/>',
        calendario: '<rect x="3" y="4" width="18" height="18" rx="2.5"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
        bot: '<rect x="3" y="8" width="18" height="12" rx="3"/><path d="M12 8V4"/><circle cx="12" cy="3" r="1"/><path d="M9 13v2M15 13v2"/><path d="M1 13v2M23 13v2"/>',
        megafono: '<path d="m3 11 15-6v14L3 13z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/><path d="M21 9v4"/>',
        ajustes: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
        info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
        lista: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        salir: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
        campana: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
        escudo: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
        edificio: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
        menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
        refrescar: '<path d="M21 12a9 9 0 0 0-15-6.7L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 15 6.7l3-2.7"/><path d="M16 16h5v5"/>',
        usuario: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        candado: '<rect x="4" y="11" width="16" height="10" rx="2.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        correo: '<rect x="2" y="4" width="20" height="16" rx="2.5"/><path d="m22 7-10 6L2 7"/>',
        filtro: '<path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z"/>',
        chevron: '<path d="m6 9 6 6 6-6"/>',
        basura: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M10 11v6M14 11v6"/>',
        ojo: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
        cerrarx: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
        deshacer: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
        confirmar: '<path d="M20 6 9 17l-5-5"/>',
        lupa: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
        descargar: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
        imprimir: '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8" rx="1"/>',
        mas: '<path d="M12 5v14M5 12h14"/>',
        enviar: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
        borrador: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
        subir: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
        ojooff: '<path d="M9.9 4.2A10 10 0 0 1 12 4c6.5 0 10 8 10 8a17 17 0 0 1-2.2 3.2"/><path d="M6.6 6.6A17 17 0 0 0 2 12s3.5 8 10 8a10 10 0 0 0 5.4-1.6"/><path d="m2 2 20 20"/>',
        carpeta: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
        pdf: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 15h6M9 18h4"/>',
        lapiz: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/>'
    };

    const svg = (n, cls = '') =>
        `<svg class="ico ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[n] || P.info}</svg>`;
    window.iconoSvg = svg;

    const norm = t => (t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

    // ---- Íconos del menú lateral (según el texto de cada opción) ----
    const MENU = [
        ['dashboard', 'dashboard'], ['inicio', 'home'], ['mi informacion', 'home'], ['informacion', 'lista'],
        ['acerca', 'info'], ['propietarios', 'users'], ['gastos', 'wallet'], ['recibos pendientes', 'reloj'],
        ['recibos pagados', 'check'], ['recibos', 'recibo'], ['pagos y reservas', 'tarjeta'], ['reservas', 'calendario'],
        ['asistente', 'bot'], ['documentos', 'carpeta'], ['anuncios', 'megafono'], ['comunicados', 'megafono'], ['perfil', 'ajustes']
    ];
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => {
        const icono = btn.querySelector('.nav-icon');
        if (!icono) return;
        const texto = norm(btn.textContent);
        const par = MENU.find(([clave]) => texto.includes(clave));
        icono.innerHTML = svg(par ? par[1] : 'info');
    });

    // Acciones de recibos (admin) e íconos de los campos del login
    document.querySelectorAll('.recibo-action-icon').forEach((el, i) => { el.innerHTML = svg(i === 0 ? 'recibo' : 'refrescar'); });
    document.querySelectorAll('.input-wrapper').forEach(w => {
        const icono = w.querySelector('.input-icon');
        const input = w.querySelector('input');
        if (!icono || !input) return;
        icono.innerHTML = svg(input.type === 'password' ? 'candado' : input.type === 'email' ? 'correo' : 'usuario');
    });

    document.querySelectorAll('.chat-avatar').forEach(el => { el.innerHTML = svg('bot'); });
    document.querySelectorAll('.pago-online-banner > span:first-child').forEach(el => { el.innerHTML = svg('tarjeta'); });

    // Botones con emoji fijos en el HTML
    document.querySelectorAll('#btnEditarContacto').forEach(b => { b.innerHTML = svg('lapiz') + ' Editar'; });

    const salir = document.querySelector('.btn-logout');
    if (salir) salir.innerHTML = svg('salir');
    const toggle = document.querySelector('.menu-toggle');
    if (toggle) toggle.innerHTML = svg('menu');

    // ---- Íconos de las tarjetas de indicadores ----
    const STAT = [['propietario', 'users'], ['pendiente', 'reloj'], ['gasto', 'wallet'], ['pagado', 'check']];
    document.querySelectorAll('.stat-card, .stat-mini-card').forEach(card => {
        const icono = card.querySelector('.stat-icon, .stat-mini-icon');
        const label = norm(card.querySelector('.stat-label, .stat-mini-label')?.textContent);
        const par = STAT.find(([clave]) => label.includes(clave));
        if (icono && par) icono.innerHTML = svg(par[1]);
    });

    // ---- Login: íconos de tipo de acceso ----
    document.querySelectorAll('.user-type-btn').forEach(btn => {
        const icono = btn.querySelector('.user-type-icon');
        if (icono) icono.innerHTML = svg(btn.dataset.type === 'Administrador' ? 'escudo' : 'edificio');
    });

    // ---- Íconos en los botones de acción (también en los que se dibujan después) ----
    const ICONO_BOTON = [
        [/^eliminar/, 'basura'], [/^editar/, 'lapiz'], [/^(ver|cuenta)\b/, 'ojo'],
        [/^cancelar/, 'cerrarx'], [/^devolver/, 'deshacer'], [/^pagar garantia/, 'tarjeta'],
        [/^pagar total/, null], [/^pagar\b/, 'tarjeta'], [/^(guardar|confirmar|registrar|publicar|listo)/, 'confirmar'],
        [/^(buscar|consultar|filtrar)/, 'lupa'], [/^ocultar/, 'ojooff'], [/^(exportar|descargar)/, 'descargar'], [/^subir/, 'subir'], [/^imprimir/, 'imprimir'],
        [/^(agregar|nuevo|\+)/, 'mas'], [/^recalcular|^intentar de nuevo/, 'refrescar'], [/^generar/, 'recibo'],
        [/^enviar/, 'enviar'], [/^limpiar/, 'borrador'], [/^marcar leido/, 'check'], [/^reservar/, 'calendario'],
        [/^cambiar contrasena/, 'candado']
    ];
    const EMOJI_INICIAL = /^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\uFE0F\s]+/u;

    function iconizarBotones(raiz) {
        raiz.querySelectorAll('button.btn, label.btn, a.btn').forEach(btn => {
            if (btn.dataset.ico || btn.closest('.recibos-vista-toggle')) return;
            if (btn.querySelector('svg')) {
                if (btn.closest('td') && !btn.textContent.trim()) {
                    btn.classList.add('btn-icono');
                    btn.removeAttribute('style');
                }
                btn.dataset.ico = '1';
                return;
            }
            const texto = btn.textContent.replace(EMOJI_INICIAL, '').trim();
            if (!texto) return;
            const n = norm(texto).replace(/^\+\s*/, '+');
            const par = ICONO_BOTON.find(([re]) => re.test(n));
            btn.dataset.ico = '1';
            if (!par || !par[1]) return;
            // conserva nodos hijos (p. ej. el input de archivo dentro de "Importar CSV")
            [...btn.childNodes].forEach(nodo => {
                if (nodo.nodeType === Node.TEXT_NODE) nodo.textContent = nodo.textContent.replace(EMOJI_INICIAL, '').replace(/^\+\s*/, '');
            });
            btn.insertAdjacentHTML('afterbegin', svg(par[1]));
            btn.classList.add('btn-con-icono');
            // En las tablas solo queda el ícono (con tooltip), salvo las acciones de dinero
            // de la pasarela y las reservas: Pagar, Pagar garantía y Devolver garantía.
            if (btn.closest('td') && /^cancelar/.test(n)) {
                btn.classList.add('btn-cancelar-fila');          // "Cancelar" se queda con texto y en rojo
                btn.title = 'Cancelar reserva';
            } else if (btn.closest('td, .doc-card-acciones') && !/^(pagar|devolver)/.test(n)) {
                const etiqueta = /^cuenta/.test(n) ? 'Ver estado de cuenta' : texto;
                [...btn.childNodes].forEach(nodo => { if (nodo.nodeType === Node.TEXT_NODE) nodo.remove(); });
                btn.title = etiqueta;
                btn.setAttribute('aria-label', etiqueta);
                btn.classList.add('btn-icono');
            }
        });
    }
    iconizarBotones(document);
    let pendiente = false;
    new MutationObserver(() => {
        if (pendiente) return;
        pendiente = true;
        requestAnimationFrame(() => { pendiente = false; iconizarBotones(document); });
    }).observe(document.body, { childList: true, subtree: true });

    // ---- Zonas de filtros: plegadas en un panel desplegable con ícono de filtro ----
    function contarActivos(panel) {
        return [...panel.querySelectorAll('input, select')]
            .filter(el => el.type !== 'button' && el.type !== 'file' && String(el.value || '').trim() !== '').length;
    }

    function plegarFiltros(contenido, opciones = {}) {
        if (!contenido || contenido.closest('.filtro-panel')) return;
        const wrap = document.createElement('div');
        wrap.className = 'filtro-wrap';
        const barra = document.createElement('div');
        barra.className = 'filtro-barra';
        const boton = document.createElement('button');
        boton.type = 'button';
        boton.className = 'filtro-toggle';
        boton.setAttribute('aria-expanded', 'false');
        boton.innerHTML = `${svg('filtro')}<span>${opciones.titulo || 'Filtros'}</span><span class="filtro-badge hidden">0</span>${svg('chevron', 'filtro-chevron')}`;
        const panel = document.createElement('div');
        panel.className = 'filtro-panel';
        panel.hidden = true;

        contenido.parentNode.insertBefore(wrap, contenido);
        barra.appendChild(boton);
        if (opciones.extra) barra.appendChild(opciones.extra);   // controles que siguen visibles (p. ej. Ver: Pendientes/Pagados)
        wrap.appendChild(barra);
        wrap.appendChild(panel);
        panel.appendChild(contenido);

        const badge = boton.querySelector('.filtro-badge');
        const actualizar = () => {
            const n = contarActivos(panel);
            badge.textContent = n;
            badge.classList.toggle('hidden', n === 0);
            boton.classList.toggle('con-filtros', n > 0);
        };
        boton.addEventListener('click', () => {
            panel.hidden = !panel.hidden;
            boton.setAttribute('aria-expanded', String(!panel.hidden));
            wrap.classList.toggle('abierto', !panel.hidden);
            if (!panel.hidden) panel.querySelector('input:not([type=hidden]), select')?.focus({ preventScroll: true });
        });
        ['input', 'change', 'click'].forEach(ev => panel.addEventListener(ev, () => setTimeout(actualizar, 0)));
        actualizar();
    }

    // tarjetas de filtros simples (propietarios, gastos, recibos pagados, comunicados)
    document.querySelectorAll('.recibos-control-card').forEach(card => {
        const titulo = card.querySelector('.recibos-search-title');
        if (!titulo) return;
        const texto = titulo.textContent.trim();
        titulo.remove();
        card.classList.add('filtro-contenido');
        plegarFiltros(card, { titulo: /buscar/i.test(texto) ? 'Buscar y filtrar' : 'Filtros' });
    });
    // recibos (admin): el filtro por mes se pliega, el selector Pendientes/Pagados queda visible
    document.querySelectorAll('.recibos-filter-bar').forEach(barra => {
        const grupo = barra.querySelector('.recibos-filter-group');
        const vista = barra.querySelector('.recibos-vista-toggle');
        if (!grupo) return;
        const contenedor = document.createElement('div');
        contenedor.className = 'filtro-contenido';
        barra.parentNode.insertBefore(contenedor, barra);
        contenedor.appendChild(grupo);
        plegarFiltros(contenedor, { extra: vista });
        barra.remove();
    });
    // pagos y reservas (admin)
    document.querySelectorAll('.filtros-enlinea').forEach(f => { f.classList.add('filtro-contenido'); plegarFiltros(f); });
    // búsqueda avanzada de recibos: mismo estilo de panel
    document.querySelectorAll('details.recibos-advanced > summary').forEach(sm => {
        sm.innerHTML = `${svg('filtro')}<span>${sm.textContent.replace(/^\W+/, '').trim()}</span>${svg('chevron', 'filtro-chevron')}`;
        sm.classList.add('filtro-toggle');
    });

    // ---- Barra superior con saludo (paneles) ----
    const panel = document.querySelector('.panel-content');
    const datos = typeof getUserData === 'function' ? getUserData() : null;
    if (panel && datos) {
        const h = new Date().getHours();
        const saludo = h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches';
        const nombre = datos.perfil?.nombre || datos.usuario || '';
        const rol = datos.tipo === 'Administrador' ? 'Administrador' : 'Propietario';
        const detalle = datos.perfil?.nro_departamento
            ? `Depto. ${datos.perfil.nro_departamento} · Torre ${datos.perfil.torre}` : rol;
        const iniciales = (datos.perfil ? `${datos.perfil.nombre || ''} ${datos.perfil.apellido || ''}` : nombre)
            .trim().split(/\s+/).slice(0, 2).map(p => p[0] || '').join('').toUpperCase() || 'CX';
        const fecha = new Date().toLocaleDateString('es-PE', { weekday: 'long', day: 'numeric', month: 'long' });
        const esc = t => String(t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

        const barra = document.createElement('header');
        barra.className = 'topbar';
        barra.innerHTML = `
            <div class="topbar-saludo">
                <h1>${saludo}, ${esc(nombre)}</h1>
                <p>${fecha.charAt(0).toUpperCase() + fecha.slice(1)} · Esto es lo que pasa hoy en tu condominio</p>
            </div>
            <div class="topbar-acciones">
                ${rol === 'Propietario' ? `<button class="icon-btn" type="button" title="Comunicados" id="topbarCampana">${svg('campana')}<span class="punto hidden" id="topbarPunto"></span></button>` : ''}
                <div class="user-chip">
                    <span class="avatar">${esc(iniciales)}</span>
                    <span class="user-chip-txt"><b>${esc(nombre)}</b><small>${esc(detalle)}</small></span>
                </div>
            </div>`;
        panel.prepend(barra);

        // avatares con iniciales en lugar del emoji
        document.querySelectorAll('.sidebar-user .user-avatar, .profile-avatar').forEach(a => {
            a.textContent = iniciales;
            a.classList.add('avatar-iniciales');
        });

        const campana = document.getElementById('topbarCampana');
        if (campana) {
            campana.addEventListener('click', () => {
                const btn = document.querySelector('.nav-item[data-section="comunicados"]');
                if (btn) btn.click();
            });
            // replica el contador de comunicados no leídos del menú
            const badge = document.getElementById('badgeComunicados');
            const punto = document.getElementById('topbarPunto');
            if (badge && punto) {
                const sync = () => punto.classList.toggle('hidden', badge.classList.contains('hidden'));
                new MutationObserver(sync).observe(badge, { attributes: true, childList: true });
                sync();
                // carga el contador al entrar, sin esperar a abrir la sección de comunicados
                if (typeof cargarComunicados === 'function') cargarComunicados();
            }
        }
    }
})();
