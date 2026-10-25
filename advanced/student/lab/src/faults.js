// Управляемые дефекты. Исправляйте по контрактам DOCX, не удаляйте сценарии.
export function acceptSearch(active, response) { return true; }
export function persistQueue(storage, queue) { /* намеренно потеряна запись */ }
export function readCache(snapshot, version) { return snapshot.records; }
export function closeTop(stack) { return []; }
