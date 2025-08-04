/**
 * Funciones de utilidad para manejar fechas
 */

/**
 * Formatea una fecha ISO a un formato legible
 * @param {string} dateString - Fecha en formato ISO (YYYY-MM-DDTHH:mm:ssZ)
 * @returns {string} - Fecha formateada (DD Mes, YYYY)
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'Fecha desconocida';

  const date = new Date(dateString);
  if (isNaN(date.getTime())) return 'Fecha inválida';

  const options = {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  };

  return date.toLocaleDateString('es-ES', options);
};

/**
 * Formatea una hora ISO a un formato legible
 * @param {string} dateString - Fecha en formato ISO (YYYY-MM-DDTHH:mm:ssZ)
 * @returns {string} - Hora formateada (HH:MM)
 */
export const formatTime = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';

  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Formatea una duración en segundos a un formato legible
 * @param {number} seconds - Duración en segundos
 * @returns {string} - Duración formateada (HH:MM:SS o MM:SS)
 */
export const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

/**
 * Calcula la diferencia en días entre dos fechas
 * @param {string|Date} date1 - Primera fecha
 * @param {string|Date} date2 - Segunda fecha (por defecto, la fecha actual)
 * @returns {number} - Diferencia en días
 */
export const daysBetween = (date1, date2 = new Date()) => {
  const d1 = new Date(date1);
  const d2 = new Date(date2);

  // Convertir a UTC para evitar problemas con horario de verano
  const utc1 = Date.UTC(d1.getFullYear(), d1.getMonth(), d1.getDate());
  const utc2 = Date.UTC(d2.getFullYear(), d2.getMonth(), d2.getDate());

  // Calcular diferencia en milisegundos y convertir a días
  const MS_PER_DAY = 1000 * 60 * 60 * 24;
  return Math.floor((utc2 - utc1) / MS_PER_DAY);
};

/**
 * Formatea una fecha relativa (hoy, ayer, hace X días)
 * @param {string} dateString - Fecha en formato ISO
 * @returns {string} - Fecha relativa formateada
 */
export const formatRelativeDate = (dateString) => {
  if (!dateString) return '';

  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';

  const days = daysBetween(date);

  if (days === 0) return 'Hoy';
  if (days === 1) return 'Ayer';
  if (days < 7) return `Hace ${days} días`;

  return formatDate(dateString);
}; 