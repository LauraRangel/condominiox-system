// ========================================
// DOCUMENTOS DEL CONDOMINIO (PDF guardados en PostgreSQL)
// Compartido por el panel del administrador y el del propietario.
// ========================================

let _documentos = [];
let _reglamento = null;
let _pdfActual = { url: null, nombre: '' };

function _escD(t) {
    return String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
const _esAdminDoc = () => getUserData()?.tipo === 'Administrador';

async function cargarDocumentos() {
    if (!_esAdminDoc() && !_reglamento) cargarReglamento();
    const { response, data } = await apiFetch('/documentos');
    if (!response.ok) return;
    _documentos = data.items || [];
    _pintarDocumentos();
}

function _pintarDocumentos() {
    const cont = document.getElementById('listaDocumentos');
    if (!cont) return;
    if (!_documentos.length) {
        cont.innerHTML = `<p class="empty-state">${_esAdminDoc() ? 'Aún no hay documentos. Sube el primero.' : 'La administración aún no publicó documentos.'}</p>`;
        return;
    }
    const admin = _esAdminDoc();
    cont.innerHTML = _documentos.map(d => `
        <article class="doc-card ${d.publico ? '' : 'privado'}">
            <div class="doc-card-ico">PDF</div>
            <div class="doc-card-cuerpo">
                <span class="doc-cat">${_escD(d.categoria_label)}</span>
                <h4>${_escD(d.titulo)}</h4>
                ${d.descripcion ? `<p>${_escD(d.descripcion)}</p>` : ''}
                <small>${formatDate(d.fecha)} · ${d.paginas} pág. · ${d.tamano_kb} KB</small>
                <div class="doc-flags">
                    ${admin ? `<span class="estado-chip ${d.publico ? 'confirmada' : 'cancelada'}">${d.publico ? 'Público' : 'Privado'}</span>` : ''}
                    ${d.tiene_texto ? (admin ? '<span class="estado-chip pagado">Lo lee el asistente IA</span>' : '')
                                    : '<span class="estado-chip pendiente">Escaneado: sin texto</span>'}
                </div>
            </div>
            <div class="doc-card-acciones">
                <button class="btn btn-secondary btn-sm" onclick="verPdf(${d.id})" title="Ver">Ver</button>
                <button class="btn btn-secondary btn-sm" onclick="descargarPdf(${d.id})" title="Descargar">Descargar</button>
                ${admin ? `
                <button class="btn btn-secondary btn-sm" onclick="alternarPublico(${d.id})" title="${d.publico ? 'Ocultar a propietarios' : 'Publicar'}">${d.publico ? 'Ocultar' : 'Publicar'}</button>
                <button class="btn btn-danger btn-sm" onclick="eliminarDocumento(${d.id})" title="Eliminar">Eliminar</button>` : ''}
            </div>
        </article>`).join('');
}

// ---------- Ver y descargar (con token: el PDF no queda expuesto por URL) ----------

async function _blobPdf(id) {
    const resp = await fetch(`${API_URL}/documentos/${id}/archivo`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
    });
    if (!resp.ok) throw new Error('No se pudo abrir el documento');
    return resp.blob();
}

async function verPdf(id) {
    const doc = _documentos.find(d => d.id === id);
    try {
        const blob = await _blobPdf(id);
        if (_pdfActual.url) URL.revokeObjectURL(_pdfActual.url);
        _pdfActual = { url: URL.createObjectURL(blob), nombre: doc?.nombre_archivo || 'documento.pdf' };
        document.getElementById('visorTitulo').textContent = doc?.titulo || 'Documento';
        document.getElementById('visorFrame').src = _pdfActual.url;
        document.getElementById('modalVisorPdf').classList.remove('hidden');
    } catch (e) {
        showToast(e.message, 'error');
    }
}

function cerrarVisorPdf() {
    document.getElementById('modalVisorPdf').classList.add('hidden');
    document.getElementById('visorFrame').src = 'about:blank';
}

function _guardarBlob(url, nombre) {
    const a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function descargarPdfActual() {
    if (_pdfActual.url) _guardarBlob(_pdfActual.url, _pdfActual.nombre);
}

async function descargarPdf(id) {
    const doc = _documentos.find(d => d.id === id);
    try {
        const url = URL.createObjectURL(await _blobPdf(id));
        _guardarBlob(url, doc?.nombre_archivo || 'documento.pdf');
        setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (e) {
        showToast(e.message, 'error');
    }
}

// ---------- Admin: subir, publicar/ocultar, eliminar ----------

let _archivoDoc = null;

function archivoElegido(file) {
    const error = document.getElementById('docError');
    error.style.display = 'none';
    if (!file) return;
    if (!/\.pdf$/i.test(file.name) || (file.type && file.type !== 'application/pdf')) {
        error.textContent = 'Solo se aceptan archivos PDF';
        error.style.display = 'block';
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        error.textContent = 'El archivo supera el máximo de 5 MB';
        error.style.display = 'block';
        return;
    }
    _archivoDoc = file;
    document.getElementById('docDropTexto').innerHTML = `<b>${_escD(file.name)}</b><br><small>${(file.size / 1024).toFixed(1)} KB · listo para subir</small>`;
    document.getElementById('docDrop').classList.add('con-archivo');
    const titulo = document.getElementById('docTitulo');
    if (!titulo.value) titulo.value = file.name.replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ');
}

async function subirDocumento(event) {
    event.preventDefault();
    const error = document.getElementById('docError');
    const btn = document.getElementById('btnSubirDoc');
    if (!_archivoDoc) {
        error.textContent = 'Primero elige un archivo PDF';
        error.style.display = 'block';
        return;
    }
    const form = new FormData();
    form.append('archivo', _archivoDoc);
    form.append('titulo', document.getElementById('docTitulo').value.trim());
    form.append('categoria', document.getElementById('docCategoria').value);
    form.append('descripcion', document.getElementById('docDescripcion').value.trim());
    form.append('publico', document.getElementById('docPublico').checked ? 'true' : 'false');
    btn.disabled = true;
    const { response, data } = await apiFetch('/documentos', { method: 'POST', body: form });
    btn.disabled = false;
    if (!response.ok) {
        error.textContent = data.error || 'No se pudo subir el documento';
        error.style.display = 'block';
        return;
    }
    error.style.display = 'none';
    _archivoDoc = null;
    event.target.reset();
    document.getElementById('docDrop').classList.remove('con-archivo');
    document.getElementById('docDropTexto').innerHTML = '<b>Elige un PDF</b> o arrástralo aquí<br><small>Máximo 5 MB</small>';
    showToast(data.aviso || `${data.paginas} página(s) procesadas`, data.aviso ? 'warning' : 'success', 'Documento subido');
    cargarDocumentos();
}

async function alternarPublico(id) {
    const d = _documentos.find(x => x.id === id);
    if (!d) return;
    const { response, data } = await apiFetch(`/documentos/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ titulo: d.titulo, categoria: d.categoria, descripcion: d.descripcion, publico: !d.publico })
    });
    if (!response.ok) { showToast(data.error || 'No se pudo actualizar', 'error'); return; }
    showToast(data.publico ? 'Ahora lo ven los propietarios y el asistente' : 'Documento oculto', 'success');
    cargarDocumentos();
}

async function eliminarDocumento(id) {
    const ok = await confirmModal('Se eliminará el documento y el asistente dejará de usarlo.', 'Eliminar documento');
    if (!ok) return;
    const { response, data } = await apiFetch(`/documentos/${id}`, { method: 'DELETE' });
    if (!response.ok) { showToast(data.error || 'No se pudo eliminar', 'error'); return; }
    showToast('Documento eliminado', 'success');
    cargarDocumentos();
}

// Arrastrar y soltar
document.addEventListener('DOMContentLoaded', () => {
    const zona = document.getElementById('docDrop');
    if (!zona) return;
    ['dragenter', 'dragover'].forEach(ev => zona.addEventListener(ev, e => { e.preventDefault(); zona.classList.add('arrastrando'); }));
    ['dragleave', 'drop'].forEach(ev => zona.addEventListener(ev, e => { e.preventDefault(); zona.classList.remove('arrastrando'); }));
    zona.addEventListener('drop', e => archivoElegido(e.dataTransfer.files[0]));
});

// ---------- Propietario: reglamento navegable ----------

function tabDocumentos(tab) {
    document.querySelectorAll('.doc-tab').forEach(b => b.classList.toggle('activo', b.dataset.tab === tab));
    document.getElementById('docTabReglamento').classList.toggle('hidden', tab !== 'reglamento');
    document.getElementById('docTabArchivos').classList.toggle('hidden', tab !== 'archivos');
}

async function cargarReglamento() {
    const { response, data } = await apiFetch('/reglamento');
    if (!response.ok) return;
    _reglamento = data;
    filtrarReglamento();
}

function filtrarReglamento() {
    if (!_reglamento) return;
    const norm = t => (t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    const q = norm(document.getElementById('reglBuscar')?.value || '').trim();
    const arts = _reglamento.articulos.filter(a => !q || norm(`${a.titulo} ${a.contenido}`).includes(q));
    document.getElementById('reglIndice').innerHTML = arts.map(a =>
        `<a href="#art-${a.numero}" onclick="irArticulo(${a.numero});return false;"><b>${a.numero}</b> ${_escD(a.titulo)}</a>`).join('')
        || '<p class="empty-state">Sin resultados</p>';
    const resaltar = t => q ? _escD(t).replace(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'), '<mark>$1</mark>') : _escD(t);
    document.getElementById('reglArticulos').innerHTML = `
        ${!q ? `<h3 class="regl-titulo">${_escD(_reglamento.titulo)}</h3><p class="regl-nota">${_escD(_reglamento.nota || '')}</p>` : ''}
        ${arts.map(a => `
            <article id="art-${a.numero}" class="regl-art">
                <h4>Artículo ${a.numero}. ${_escD(a.titulo)}</h4>
                <p>${resaltar(a.contenido)}</p>
            </article>`).join('')}`;
}

function irArticulo(numero) {
    const el = document.getElementById(`art-${numero}`);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.add('destacado');
    setTimeout(() => el.classList.remove('destacado'), 1600);
}

// Abre la fuente que citó el asistente
async function abrirFuente(tipo, ref) {
    const btn = document.querySelector('.nav-item[data-section="documentos"]');
    if (tipo === 'documento') {
        if (!_documentos.length) await cargarDocumentos();
        verPdf(ref);
    } else if (tipo === 'reglamento' && btn) {
        btn.click();
        tabDocumentos('reglamento');
        if (!_reglamento) await cargarReglamento();
        setTimeout(() => irArticulo(ref), 150);
    }
}
