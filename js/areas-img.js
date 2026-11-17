// Compartido por el panel del propietario y el del administrador
// Ilustración de cada área según su nombre (las áreas nuevas usan una genérica)
const _IMAGENES_AREA = [
    ['salon', 'img/sum.png'], ['usos multiples', 'img/sum.png'], ['parrilla', 'img/parrilla.png'],
    ['gimnasio', 'img/gym.png'], ['gym', 'img/gym.png'], ['cowork', 'img/cowork.png'],
    ['pet', 'img/petzone.png'], ['mascota', 'img/petzone.png']
];

function imagenArea(nombre) {
    const n = (nombre || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const par = _IMAGENES_AREA.find(([clave]) => n.includes(clave));
    return par ? par[1] : 'img/logo.png';
}
